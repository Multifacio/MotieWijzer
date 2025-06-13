""" The Scraper is responsible for downloading all motion (Dutch: motie) metadata in a given date range. """
import os
from datetime import date
from typing import Any, Dict, List, Tuple

from dateutil.relativedelta import relativedelta
from progress.bar import Bar
from pytz import timezone
from tkapi import tkapi
from tkapi.besluit import Besluit
from tkapi.filter import Filter
from tkapi.zaak import ZaakActorRelatieSoort, Zaak, ZaakSoort
import pandas as pd

from MotieWijzer.Business import DATA_DIRECTORY, MOTIONS_DATA_PATH


def init_data_directory():
    """ Create the data directory if it does not exist yet. """
    if not os.path.isdir(DATA_DIRECTORY):
        os.mkdir(DATA_DIRECTORY)

def get_year_month_combinations(start_date: date, end_date: date) -> List[Tuple[str, str]]:
    """ Get all year month combinations for which we scrap all motions (Dutch: moties).

    :return: A list of tuples where the first element is the year number (expressed as string) and the second element is
        the month number (expressed as string) for which we extract all motions.
    """
    time = start_date
    year_month_combinations = []
    while time <= end_date:
        year_month_combinations.append((str(time.year), str(time.month)))
        time += relativedelta(months=1)

    return year_month_combinations


def scrap_motions(year: str, month: str) -> List[Besluit]:
    """ Scrap all motions using the TkApi for a given year and month.

    :param year: The year for which the motions are scrapped.
    :param month: The month for which the motions are scrapped.
    :return: A list of Besluit objects from the TkApi which represent the motions.
    """
    api = tkapi.TKApi()
    filter = Filter()
    filter.add_filter_str("StemmingsSoort eq 'Met handopsteken'")
    filter.add_filter_str(f"year(GewijzigdOp) eq {str(year)}")
    filter.add_filter_str(f"month(GewijzigdOp) eq {str(month)}")
    return api.get_besluiten(filter=filter)


def parse_basic_info(motion: Besluit, zaak: Zaak) -> Dict[str, Any]:
    """ Parse the basic information for a motion (Dutch: motie), which are the Id, Subject, VoteTime, Url and Size.

    :param motion: The scrapped motion from which the basic information is extracted.
    :param zaak: The zaak object corresponding to the motion.
    :return: This information parsed or an empty dictionary if it wasn't discussed in the Tweede Kamer, if it wasn't a
        motion, if there were no documents or if the motion was neither accepted (Dutch: aangenomen) or rejected
        (Dutch: verworpen).
    """
    if zaak.get_property_or_none("Organisatie") != "Tweede Kamer":
        return dict()

    if zaak.soort != ZaakSoort.MOTIE:
        return dict()

    if len(zaak.documenten) == 0:
        return dict()

    accepted = motion.tekst
    if accepted == "Aangenomen.":
        accepted = True
    elif accepted == "Verworpen.":
        accepted = False
    else:
        return dict()

    document = zaak.documenten[0]
    id = document.get_property_or_empty_string("Id")
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/document/{id}/resource"
    size = int(document.get_property_or_empty_string("ContentLength"))
    time_zone = timezone("Europe/Amsterdam")
    vote_time = motion.gewijzigd_op
    vote_time = vote_time.replace(tzinfo=time_zone)
    return {"Id": id, "Subject": zaak.onderwerp, "VoteTime": vote_time, "Url": url, "Size": size, "Accepted": accepted}


def parse_vote_info(motion: Besluit) -> Dict[str, Any]:
    """ Parse voting info, which are how many members of the Tweede Kamer voted in favor, against and did not vote.
    Also parse which parties voted in favor, against and did not vote.

    :param motion: The scrapped motion from which the basic information is extracted.
    :return: The parsed voting data or empty if odd voting data is encountered.
    """
    num_proponents = 0
    proponents = []
    num_absentees = 0
    absentees = []
    num_opponents = 0
    opponents = []
    error = False
    for vote in motion.stemmingen:
        if vote.soort == "Voor":
            num_proponents += vote.fractie_size
            proponents += [vote.actor_fractie]
        elif vote.soort == "Niet deelgenomen":
            num_absentees += vote.fractie_size
            absentees += [vote.actor_fractie]
        elif vote.soort == "Tegen":
            num_opponents += vote.fractie_size
            opponents += [vote.actor_fractie]
        else:
            error = True
            break
    if error:
        return dict()

    return {"NumProponents": num_proponents, "Proponents": ",".join(proponents), "NumAbsentees": num_absentees,
            "Absentees": ",".join(absentees), "NumOpponents": num_opponents, "Opponents": ",".join(opponents)}


def parse_petitioners_info(zaak: Zaak) -> Dict[str, Any]:
    """ Parse the info about the petitioners (Dutch: indieners) of the motion (Dutch: motie).

    :param zaak: The zaak object corresponding to the motion.
    :return: The parsed petitioners data.
    """
    petitioners = []
    for actor in zaak.actors:
        relatie = actor.relatie
        if relatie == ZaakActorRelatieSoort.INDIENER or relatie == ZaakActorRelatieSoort.MEDEINDIENER:
            petitioner = actor.naam
            if petitioner is None:
                break
            fractie = actor.get_property_or_none("ActorFractie")
            petitioners.append(f"{petitioner} ({fractie})")

    return {"Petitioners": ",".join(petitioners)}


def parse_motion(motion: Besluit) -> Dict[str, Any]:
    """ Parse the scraped data for a single motion (Dutch: motie) into a Dictionary mapping the column names to their
    respective values.

    :param motion: A single scrapped motion (Dutch: motie).
    :return: A dictionary mapping the following column names to the following values:
        - Id: The id of the document of the motion.
        - Subject: The subject of the motion.
        - VoteTime: The time at which was voted for this motion.
        - Url: The url from which we can extract the PDF with the corresponding motion text.
        - Size: The size in bytes of the PDF motion file.
        - Accepted: If the motion is accepted (Dutch: aangenomen) then it is true, otherwise (Dutch: verworpen)
        - NumProponents: How many members of the Tweede Kamer voted in favor of the motion.
        - Proponents: A list of parties (Dutch: fractie) that voted in favor of the motion, separated by a comma ','.
        - NumAbsentees: How many members of the Tweede Kamer didn't vote for the motion.
        - Absentees: A list of parties that didn't vote for the motion, separated by a comma ','.
        - NumOpponents: How many members of the Tweede Kamer voted against the motion.
        - Opponents: A list of parties that voted against the motion, separated by a comma ','.
        - Petitions (Dutch: Indieners): The members of the Tweede Kamer that submitted the vote, which is formatted by
            $member_name ($party_name),$member_name_2 ($party_name_2),...
    """
    zaak = motion.zaak
    basic_info = parse_basic_info(motion, zaak)
    if not basic_info:
        return dict()

    vote_info = parse_vote_info(motion)
    if not vote_info:
        return dict()

    petitioners_info = parse_petitioners_info(zaak)
    return {**basic_info, **vote_info, **petitioners_info}


def run_scraper(start_date: date, end_date: date):
    """ Run the scraper. """
    rows = []
    init_data_directory()
    year_month_combinations = get_year_month_combinations(start_date, end_date)
    for year, month in year_month_combinations:
        motions = scrap_motions(year, month)
        if not motions:
            continue
        progress_bar = Bar(f"Moties voor {year}-{month} geparsed: ", max=len(motions))
        progress_bar.start()
        for motion in motions:
            row = parse_motion(motion)
            if row:
                rows.append(row)
            progress_bar.next()
        progress_bar.finish()
    new_data = pd.DataFrame(rows)

    if os.path.isfile(MOTIONS_DATA_PATH):
        old_data = pd.read_csv(MOTIONS_DATA_PATH, sep="|")
        old_data = old_data[~old_data["Id"].isin(new_data["Id"])]
        new_data = pd.concat([old_data, new_data])

    new_data.to_csv(MOTIONS_DATA_PATH, sep="|", index=False)
    print("Het downloaden van motie metadata is gelukt.")
