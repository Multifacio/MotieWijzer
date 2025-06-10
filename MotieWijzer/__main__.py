""" Creates the command line interface. """
from typer import Typer, Argument, Option

app = Typer(
    add_completion=False,
    help="De MotieWijzer laat je willekeurige moties zien die in de tweede kamer ingediend zijn waarvoor je mag "
         "bepalen of je het eens bent, oneens of geen mening hebt. Vervolgens bekijkt deze tool met welke partij "
         "je het meest overeenkomst hebt op de moties waar je het mee eens en oneens bent."
)

@app.command(
    help="Download alle motie metadata. Deze stap moet als eerste uitgevoerd worden, voordat de tool gebruikt kan "
         "worden. Voorbeeld: 'python MotieWijzer download 2022-02 --eind 2024-06'"
)
def download(
    start: str = Argument(
        help="Vanaf het begin van welke maand moties gedownload moeten worden. Bijvoorbeeld: '2022-02' betekent dat "
             "alle moties vanaf begin februari 2022 gedownload worden."
    ),
    eind: str = Option(
        default="",
        help="Tot het eind van welke maand moties gedownload moeten worden. Bijvoorbeeld: '2024-06' betekent dat alle "
             "moties tot en met het einde van juni 2024 gedownload worden. Als dit argument leeg gelaten wordt zullen "
             "alle moties tot de dag van vandaag gedownload worden."
    )
):
    pass

@app.command(
    help="Start de MotieWijzer en bepaal welke partij in de tweede kamer het beste bij je past op basis van "
         "willekeurige moties. Let op: Je moet eerst alle motie metadata downloaden. Als een partij afwezig was bij "
         "de stemming van de motie en jij wel voor/tegen de motie bent wordt beschouwd dat de afwezige partij "
         "tegenstrijdig met jou heeft gestemd. Voorbeeld 'python MotieWijzer start --start 2022-02 --eind 2024-06 "
         "--substitutie '{\"GLPVDA\": \"GL\", \"Omtzigt\": \"CDA\"}'"
)
def start(
    start: str = Option(
        default="",
        help="Vanaf het begin van welke maand moties getoond moeten worden. Bijvoorbeeld: '2022-02' betekent dat "
             "alle moties vanaf begin februari 2022 getoond worden. Als dit argument leeg gelaten wordt zullen alle "
             "moties vanaf het begin van de metadata getoond worden."
    ),
    eind: str = Option(
        default="",
        help="Tot het eind van welke maand moties getoond moeten worden. Bijvoorbeeld: '2024-06' betekent dat alle "
             "moties tot en met het einde van juni 2024 getoond worden. Als dit argument leeg gelaten wordt zullen "
             "alle moties tot de dag van vandaag getoond worden."
    ),
    substitutie: str = Option(
        default="{}",
        help="Als een partij niet bestond ten tijde van de motie dan wordt gekeken naar een alternatieve partij. Als "
             "geen substitutie vermeld wordt en de partij niet bestond ten tijde van een motie dan wordt beschouw dat "
             "die partij tegenstrijdig stemt met jou. Hetzelfde geldt ook als zowel die partij als de substitutie "
             "partij niet bestonden op het moment dat de motie ingediend werd. "
             "Voorbeeld: {\"GLPVDA\": \"GL\", \"Omtzigt\": \"CDA\"} betekent dat zolang GLPVDA niet bestaat wordt "
             "aangenomen dat GLPVDA hetzelfde had gestemd als GL. Idem dito wordt beschouwd dat Omtzigt hetzelfde "
             "stemt als CDA zolang Omtzigt geen aparte partij heeft."
    ),
    regex: str = Option(
        default=".*",
        help="Regex filtering die toegepast moet worden op de motie titels. Hierdoor kun je moties selecteren die over "
             "een specifiek thema gaan. Voorbeeld: '.*(bus|trein|infrastructuur|mobiliteit|auto|fiets).*' laat "
             "voornamelijk moties zien die over vervoer gaan."
    ),
    seed: int = Option(
        default=-1,
        help="De random seed die gebruikt moeten worden. Bij het gebruik van dezelfde seed zullen de moties in "
             "dezelfde volgorde getoond worden. Voorbeeld: '724756689' Als dit argument leeg gelaten wordt zal een "
             "willekeurige random seed gepakt worden."
    )
):
    pass

@app.command(
    help="Ga verder met de MotieWijzer vanaf een opgeslagen profiel. Voorbeeld: 'python MotieWijzer laden profiel_naam'"
)
def laden(
    profiel: str = Argument(
        default="",
        help="De naam van het opgeslagen profiel dat geladen wordt. Je kunt kiezen uit: ''"
    )
):
    pass

@app.command(
    help="Laat algemene informatie zien over de motie metadata, waaronder hoeveel moties er zijn, welke partijen er "
         "zijn en welke partijen niet bestonden. Voorbeeld 'python MotieWijzer info --start 2022-02 --eind 2024-06 "
         "--regex '.*(bus|trein|infrastructuur|mobiliteit|auto|fiets).*'"
)
def info(
    start: str = Option(
        default="",
        help="Vanaf het begin van welke maand motie informatie getoond moet worden. Bijvoorbeeld: '2022-02' betekent "
             "dat alle motie informatie vanaf begin februari 2022 getoond worden. Als dit argument leeg gelaten wordt "
             "zal alle motie informatie vanaf het begin van de metadata getoond worden."
    ),
    eind: str = Option(
        default="",
        help="Tot het eind van welke maand motie informatie getoond moet worden. Bijvoorbeeld: '2024-06' betekent dat "
             "alle motie informatie tot en met het einde van juni 2024 getoond worden. Als dit argument leeg gelaten "
             "wordt zal alle motie informatie tot de dag van vandaag getoond worden."
    ),
    regex: str = Option(
        default=".*",
        help="Regex filtering die toegepast moet worden  op de motie titels. Hierdoor kun je moties selecteren die "
             "over een specifiek thema gaan. Voorbeeld: '.*(bus|trein|infrastructuur|mobiliteit|auto|fiets).*' laat "
             "voornamelijk moties zien die over vervoer gaan."
    ),
):
    pass

if __name__ == "__main__":
    app()