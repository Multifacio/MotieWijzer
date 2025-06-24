""" Creates the command line interface. """
import os
from collections import Counter as counter
from datetime import date, datetime
import random
import re

import pandas as pd
from colorama import Fore, Back, Style
from typer import Typer, Argument, Option

from MotieWijzer.Business import MOTIONS_DATA_PATH, DATA_DIRECTORY
from MotieWijzer.Business.InfoRetriever import retrieve_info, filter_motions, get_all_parties
from MotieWijzer.Business.Downloader import run_downloader
from MotieWijzer.Business.Runner import run, load


profile_names = []
if os.path.isdir(DATA_DIRECTORY):
    for file in os.listdir(DATA_DIRECTORY):
        if file.endswith(".json"):
            profile_names.append(file[:-5])
            
if profile_names:
    profile_names = "', '".join(profile_names)
    profile_names = f"'{profile_names}'"
else:
    profile_names = ""

app = Typer(
    add_completion=False,
    help="De MotieWijzer laat je willekeurige moties zien die in de tweede kamer ingediend zijn waarvoor je mag "
         "bepalen of je het eens bent, oneens of geen mening hebt. Vervolgens bekijkt deze tool met welke partij "
         "je het meest overeenkomst hebt op de moties waar je het mee eens en oneens bent."
)

@app.command(
    help="Download alle motie metadata. Deze stap moet als eerste uitgevoerd worden, voordat de tool gebruikt kan "
         "worden. Voorbeeld: 'python MotieWijzer download --start 2022-02 --eind 2024-06'"
)
def download(
    start: str = Option(
        default="2008-09",
        help="Vanaf het begin van welke maand moties gedownload moeten worden. Bijvoorbeeld: '2022-02' betekent dat "
             "alle moties vanaf begin februari 2022 gedownload worden. Als dit argument leeg gelaten wordt zal de "
             "eerste maand waarvoor motie metadata beschikbaar is gepakt worden, dat is '2008-09'. Let op het "
             "downloaden van de moties kan meer dan een uur duren."
    ),
    eind: str = Option(
        default="",
        help="Tot het eind van welke maand moties gedownload moeten worden. Bijvoorbeeld: '2024-06' betekent dat alle "
             "moties tot en met het einde van juni 2024 gedownload worden. Als dit argument leeg gelaten wordt zullen "
             "alle moties tot de dag van vandaag gedownload worden."
    )
):
    start = re.fullmatch(r"(\d{4})-(\d{2})", start)
    if start is None:
        print(Fore.WHITE + Back.RED + "Start parameter is incorrect. Het moet eruit zien als '2022-02'." +
              Style.RESET_ALL)
        return
    start = start.groups()
    start_date = date(year=int(start[0]), month=int(start[1]), day=1)

    if eind == "":
        end_date = date.today()
    else:
        eind = re.fullmatch(r"(\d{4})-(\d{2})", eind)
        if eind is None:
            print(Fore.WHITE + Back.RED + "Eind parameter is incorrect. Het moet eruit zien als '2024-06'." +
                  Style.RESET_ALL)
            return
        eind = eind.groups()
        end_date = date(year=int(eind[0]), month=int(eind[1]), day=1)

    run_downloader(start_date, end_date)

@app.command(
    help="Start de MotieWijzer en bepaal welke partij in de tweede kamer het beste bij je past op basis van "
         "willekeurige moties. Let op: Je moet eerst alle motie metadata downloaden. Als een partij afwezig was bij "
         "de stemming van de motie en jij wel voor/tegen de motie bent wordt beschouwd dat de afwezige partij "
         "tegenstrijdig met jou heeft gestemd. Als een partij niet bestond bij de stemming telt het niet mee voor "
         "zijn score. Voorbeeld 'python MotieWijzer start --start 2022-02 --eind 2024-06 "
         "--inclusief 'VVD,CDA,GroenLinks-PvdA'"
)
def start(
    start: str = Option(
        default="2008-09-01",
        help="Vanaf welke dag moties getoond moeten worden. Bijvoorbeeld: '2022-02-11' betekent dat alle moties vanaf "
             "11 februari 2022 getoond worden. Als dit argument leeg gelaten wordt zullen alle moties vanaf het begin "
             "van de metadata getoond worden."
    ),
    eind: str = Option(
        default="",
        help="Tot en met welke dag moties getoond moeten worden. Bijvoorbeeld: '2024-06-23' betekent dat alle moties "
             "tot en met 23 juni 2024 getoond worden. Als dit argument leeg gelaten wordt zullen alle moties tot en "
             "met de dag van vandaag getoond worden."
    ),
    regex: str = Option(
        default=".*",
        help="Regex filtering die toegepast moet worden op de motie titels. Hierdoor kun je moties selecteren die "
             "over een specifiek thema gaan. Voorbeeld: '.*(?i:bus|trein|infrastructuur|mobiliteit|auto|fiets).*' laat "
             "voornamelijk moties zien die over vervoer gaan. Regex queries zijn in principe hoofdlettergevoelig, "
             "tenzij (?i) gebruikt wordt. De syntax voor regex staat beschreven in: "
             "https://docs.python.org/3/library/re.html"
    ),
    inclusief: str = Option(
        default="",
        help="Van welke partijen bijgehouden moeten worden hoeveel overeenkomst ze met je hebben gescheiden door een "
             "komma. Als dit argument leeg gelaten wordt zullen van alle partijen de overeenkomst bijgehouden worden. "
             "Voorbeeld: 'VVD,CDA,GroenLinks-PvdA' betekent dat alleen je overeenkomst met de VVD, CDA en "
             "GroenLinks-PVDA getoond wordt."
    ),
    seed: int = Option(
        default=-1,
        help="De random seed die gebruikt moeten worden. Bij het gebruik van dezelfde seed zullen de moties in "
             "dezelfde volgorde getoond worden. Voorbeeld: '724756689' Als dit argument leeg gelaten wordt zal een "
             "willekeurige random seed gepakt worden."
    )
):
    start = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", start)
    if start is None:
        print(Fore.WHITE + Back.RED + "Start parameter is incorrect. Het moet eruit zien als '2022-02-11'." +
              Style.RESET_ALL)
        return
    start = start.groups()
    start_date = datetime(year=int(start[0]), month=int(start[1]), day=int(start[2]))

    if eind == "":
        today = date.today()
        end_date = datetime(year=today.year, month=today.month, day=today.day)
    else:
        eind = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", eind)
        if eind is None:
            print(Fore.WHITE + Back.RED + "Eind parameter is incorrect. Het moet eruit zien als '2024-06-23'." +
                  Style.RESET_ALL)
            return
        eind = eind.groups()
        end_date = datetime(year=int(eind[0]), month=int(eind[1]), day=int(eind[2]))

    try:
        re.compile(regex)
    except:
        print(Fore.WHITE + Back.RED + "De gegeven regex string voldoet niet aan het formaat." +
              Style.RESET_ALL)
        return

    motions = pd.read_csv(MOTIONS_DATA_PATH, sep="|")
    motions = filter_motions(motions, start_date, end_date, regex)
    all_parties = get_all_parties(motions)
    if inclusief == "":
        included_parties = all_parties.copy()
    else:
        included_parties = inclusief.split(",")
        missing_parties = [p for p in included_parties if p not in all_parties]
        if missing_parties:
            missing_parties = ", ".join(missing_parties)
            print(Fore.WHITE + Back.RED + f"De volgende partijen in de inclusief parameter bestaan niet: "
                                          f"{missing_parties}" + Style.RESET_ALL)
            return

    if seed < 0:
        seed = random.randint(0, 2 ** 31)

    run(motions, start_date, end_date, regex, included_parties, seed, counter(), counter(), 0)


@app.command(
    help="Ga verder met de MotieWijzer vanaf een opgeslagen profiel. Voorbeeld: 'python MotieWijzer laden profiel_naam'"
)
def laden(
    profiel: str = Argument(
        default="",
        help=f"De naam van het opgeslagen profiel dat geladen wordt. Je kunt kiezen uit: {profile_names}"
    )
):
    file_name = f"{DATA_DIRECTORY}/{profiel}.json"
    if not os.path.isfile(file_name):
        print(Fore.WHITE + Back.RED + f"De file '{file_name}' bestaat niet" + Style.RESET_ALL)
        return

    load(file_name)


@app.command(
    help="Laat algemene informatie zien over de motie metadata, waaronder hoeveel moties er zijn, welke partijen er "
         "zijn en welke partijen deels niet bestonden (en bij hoeveel moties ze niet bestonden) en op welke dag de "
         "eerste en laatste moties waren. Voorbeeld 'python MotieWijzer info --start 2022-02 --eind 2024-06 "
         "--regex '.*(?i:bus|trein|infrastructuur|mobiliteit|auto|fiets).*'"
)
def info(
    start: str = Option(
        default="2008-09-01",
        help="Vanaf welke dag motie informatie getoond moet worden. Bijvoorbeeld: '2022-02-11' betekent dat alle "
             "motie informatie vanaf 2022-02-11 getoond worden. Als dit argument leeg gelaten wordt zal alle motie "
             "informatie vanaf het begin van de metadata getoond worden."
    ),
    eind: str = Option(
        default="",
        help="Tot en met welke dag motie informatie getoond moet worden. Bijvoorbeeld: '2024-06-23' betekent dat alle "
             "motie informatie tot en met 2024-06-23 getoond worden. Als dit argument leeg gelaten wordt zal alle "
             "motie informatie tot en met de dag van vandaag getoond worden."
    ),
    regex: str = Option(
        default=".*",
        help="Regex filtering die toegepast moet worden op de motie titels. Hierdoor kun je moties selecteren die "
             "over een specifiek thema gaan. Voorbeeld: '.*(?i:bus|trein|infrastructuur|mobiliteit|auto|fiets).*' laat "
             "voornamelijk moties zien die over vervoer gaan. Regex queries zijn in principe hoofdlettergevoelig, "
             "tenzij (?i) gebruikt wordt. De syntax voor regex staat beschreven in: "
             "https://docs.python.org/3/library/re.html"
    ),
):
    start = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", start)
    if start is None:
        print(Fore.WHITE + Back.RED + "Start parameter is incorrect. Het moet eruit zien als '2022-02-11'." +
              Style.RESET_ALL)
        return
    start = start.groups()
    start_date = datetime(year=int(start[0]), month=int(start[1]), day=int(start[2]))

    if eind == "":
        today = date.today()
        end_date = datetime(year=today.year, month=today.month, day=today.day)
    else:
        eind = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", eind)
        if eind is None:
            print(Fore.WHITE + Back.RED + "Eind parameter is incorrect. Het moet eruit zien als '2024-06-23'." +
                  Style.RESET_ALL)
            return
        eind = eind.groups()
        end_date = datetime(year=int(eind[0]), month=int(eind[1]), day=int(eind[2]))

    try:
        re.compile(regex)
    except:
        print(Fore.WHITE + Back.RED + "De gegeven regex string voldoet niet aan het formaat." +
              Style.RESET_ALL)
        return

    retrieve_info(start_date, end_date, regex)

if __name__ == "__main__":
    app()