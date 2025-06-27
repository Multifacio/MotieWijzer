# MotieWijzer
De MotieWijzer laat je willekeurige moties zien die in de tweede kamer ingediend zijn waarvoor je mag bepalen of je het eens bent, oneens of geen mening hebt. Vervolgens bekijkt deze tool met welke partij je het meest overeenkomst hebt op de moties waar je het mee eens en oneens bent.

Het voordeel van de MotieWijzer is dat het op een eerlijke manier kijkt welke partij het best bij je past, namelijk hoe partijen echt stemmen op moties. Het nadeel van de MotieWijzer is dat moties soms lastig te begrijpen zijn en alleen van de indieners een motivatie krijgt waarom ze voor de motie zijn.

## Installatie
De MotieWijzer werkt voor nu als nog alleen voor Windows en Linux omgevingen (het is getest op Windows 11 en Ubuntu 24.04). De MotieWijzer kun je als volgt installeren:

### Windows
1. Clone/download het project naar een folder waarin je lees en schrijf rechten hebt (onder Mijn Documenten bijvoorbeeld).
2. Installeer Python. Dit doe je bij voorkeur via de Microsoft Store. Mogelijk moet je hierna de Path variabelen aanpassen, zie https://realpython.com/add-python-to-path, zodat hij Python herkent als command.
3. Open een command prompt in de project folder die je gecloned/gedownload hebt en run het volgende commando `python -m venv .venv`. Dit maakt een nieuwe virtual environment aan.
4. Run het volgende commando `.venv\Scripts\activate` om de virtual environment te activeren.
5. Run het volgende commando `pip install .` om het project te builden met de bijbehorende packages (dit moet opnieuw gedaan worden nadat wijzigingen zijn gemaakt/gepulled).

### Ubuntu (of Debian)
1. Ga met de command line (via `cd`) naar de folder waarin je de repository wil clonen en voer het volgende commando uit: `git clone https://github.com/Multifacio/MotieWijzer.git` en ga de folder in met het commando `cd MotieWijzer`.
2. Installeer Python via het volgende commando: `sudo apt-get install python3`
3. Run het volgende commando `python3 -m venv .venv` om een nieuwe virtual environment aan te maken.
4. Run het volgende commando `source .venv/bin/activate` om de virtual environment te activeren.
5. Run het volgende commando `pip install .` om het project te builden met de bijbehorende packages (dit moet opnieuw gedaan worden nadat wijzigingen zijn gemaakt/gepulled).

## Uitvoeren
Als je de command line weer opnieuw opstart in de folder, waarin je het project gedownload/gecloned hebt, moet je opnieuw de virtual environment activeren via het commando `.venv\Scripts\activate` (Windows) of `source .venv/bin/activate` (Ubuntu of Debian).

### Motie Metadata downloaden
Als je voor het eerste de applicatie uitvoert moet je Motie Metadata downloaden. De Motie Metadata bevat veel informatie over de moties die ingediend zijn, waaronder: 
- Het onderwerp van de motie.
- Welke partijen voor en tegen gestemd hebben en welke partijen afwezig waren bij de stemming.
- De indieners van de motie.
- Of de motie aangenomen/verworpen is.
- Waar de PDF behorende bij de motie gedownload kan worden.
De Motie Metadata bevat dus niet de inhoud van de Motie. Die wordt gedownload als je de MotieWijzer aan het uitvoeren bent.

Om de Motie Metadata te downloaden kun je bijvoorbeeld het volgende commando uitvoeren:
`python MotieWijzer download --start 2024-01 --eind 2024-12`

Om meer informatie over het download commando te krijgen kun je de volgende commando uitvoeren:
`python MotieWijzer download --help`

### MotieWijzer uitvoeren
Als je de MotieWijzer wilt uitvoeren run je het volgende commando:
`python MotieWijzer start`

Eventueel kun je extra argumenten meegeven aan dit commando, zoals bijvoorbeeld een regex om de onderwerpen te filteren op bepaalde thema's. Voor extra informatie over de extra parameters die je kunt meegeven kun je `python MotieWijzer start --help` uitvoeren. Voor meer informatie over Python regexes ga je naar: https://docs.python.org/3/library/re.html.

Als je de MotieWijzer uitvoert zul je alle (gefilterde) moties in willekeurige volgorde te zien krijgen en bij elke motie krijg je vervolgens de optie om voor/tegen te stemmen of neutraal in het geval je geen (sterke) mening over de motie hebt of te complex om te begrijpen is. Naast deze optie heb je ook de volgende opties:
- 'i' typen plus enter om extra informatie te krijgen over de motie, waaronder welke partijen voor/tegen gestemd hebben, welke partijen afwezig waren bij stemming, wie de motie ingediend hebben en of de motie aangenomen of verworpen is.
- 'o' typen plus enter om de PDF van de motie opnieuw te openen (als je hem per ongeluk gesloten hebt).
- 'r' om de overeenkomst tot op heden te laten zien met alle verschillende partijen (op de moties waarover je een mening had).
- 's' om de resultaten van de MotieWijzer op te slaan zo ver in een bestand. Later kun je deze weer laden via `python MotieWijzer laden $naam`, waarbij $naam de naam is waaronder je de resultaten hebt opgeslagen.

### Motie info krijgen
Om algemene informatie te tonen over de moties de je hebt kun je het volgende commando uitvoeren:
`python MotieWijzer info`
Dit commando toont de datum van de eerste en laatste motie, het aantal moties die er zijn en welke partijen bestonden tijdens een van deze moties. Bovendien toont het de (deels) ontbrekende partijen, dat zijn partijen die niet bestonden tijdens een van deze moties en bij hoeveel moties ze niet bestonden (dit is anders dan afwezig zijn bij stemming).

Om alleen specifieke informatie te krijgen over moties over een bepaald thema kun je de regex parameter toevoegen, e.g. `python MotieWijzer info --regex .*(?i:bus|trein|infrastructuur|mobiliteit|auto|fiets).*` toont alleen moties die over vervoer gaan (omdat ze een van deze woorden in hun onderwerp hebben). Voor meer informatie over dit commando kun `python MotieWijzer info --help` uitvoeren.

## Credits
Voor dit project is gebruik gemaakt van:
- tkapi: https://github.com/openkamer/tkapi
- En indirect het Open Data Portaal van de Tweede Kamer: https://opendata.tweedekamer.nl/github

