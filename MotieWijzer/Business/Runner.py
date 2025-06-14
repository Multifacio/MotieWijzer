""" Randomly selects a motion (Dutch: motie) in the new way. """
from collections import Counter as counter
from datetime import date
from sys import platform
from typing import Counter, List, Tuple
import subprocess

from colorama import Back, Style
from pandas import DataFrame
import pandas as pd
import requests

PDF_OUTPUT_FILE_PATH = "MotieWijzer/Data/output.pdf"  # The path in which the motion PDF is stored.


def show_motion(motion: pd.Series):
    """ Download and show the PDF file of the motion.

    :param motion: The motion row data of which the PDF is downloaded and shown.
    """
    response = requests.get(url=motion["Url"], timeout=60)
    with open(PDF_OUTPUT_FILE_PATH, "wb") as f:
        f.write(response.content)

    if platform == "linux" or platform == "linux2":
        subprocess.Popen([f"xdg-open {PDF_OUTPUT_FILE_PATH}"], shell=True)
    else:
        subprocess.Popen([PDF_OUTPUT_FILE_PATH], shell=True)


def show_additional_motion_info(motion: pd.Series):
    """ Show additional motion info. """
    subject = motion["Subject"]
    vote_time = motion["VoteTime"].date()
    url = motion["Url"]
    status = "Aangenomen" if motion["Accepted"] else "Verworpen"
    num_proponents = motion["NumProponents"]
    num_opponents = motion["NumOpponents"]
    num_absentees = motion["NumAbsentees"]
    proponents = motion["Proponents"].replace(",", ", ")
    opponents = motion["Opponents"].replace(",", ", ")
    absentees = motion["Absentees"].replace("nan", "").replace(",", ", ")
    petitioners = motion["Petitioners"].replace(",", ", ")

    print(Back.GREEN + f"Motie titel: {subject}" + Style.RESET_ALL)
    print(f"Gestemd op: {vote_time}")
    print(f"URL: {url}")
    print(f"Status: {status}")
    print(f"Aantal stemmen voor: {num_proponents}")
    print(f"Aantal stemmen tegen: {num_opponents}")
    print(f"Aantal afwezige stemmen: {num_absentees}")
    print(f"Voorstanders: {proponents}")
    print(f"Tegenstanders: {opponents}")
    print(f"Afwezige partijen: {absentees}")
    print(f"Indiener(s): {petitioners}")
    print()


def show_result(scores: Counter[str], totals: Counter[str], included_parties: List[str]):
    """ Show the resemblance with the different parties. """
    relative_scores = counter({p: round(scores[p] / t, 3) * 100 for p, t in totals.items()})
    for p, rs in relative_scores.most_common():
        if p in included_parties:
            print("{}: {}/{} = {:.1f}%".format(p, scores[p], totals[p], rs))
    print()


def update_scores(motion: pd.Series, accepted: bool, scores: Counter[str], totals: Counter[str]) -> \
    Tuple[Counter[str], Counter[str]]:
    """ Update scores based on whether the user accepts/rejects the motion. """
    proponents = [] if not isinstance(motion["Proponents"], str) else motion["Proponents"].split(",")
    absentees = [] if not isinstance(motion["Absentees"], str) else motion["Absentees"].split(",")
    opponents = [] if not isinstance(motion["Opponents"], str) else motion["Opponents"].split(",")
    existing_parties = proponents + absentees + opponents

    totals.update(existing_parties)
    if accepted:
        scores.update(proponents)
    else:
        scores.update(opponents)

    return scores, totals


def ask_user_input_motion(motion: pd.Series, scores: Counter[str], totals: Counter[str], included_parties: List[str])\
        -> Tuple[Counter[str], Counter[str]]:
    """ Ask the user what to do with the motion. """
    while True:
        subject = motion["Subject"]
        print(Back.GREEN + f"Motie titel: {subject}" + Style.RESET_ALL)
        print("Kies het volgende: ")
        print("'i': Om extra informatie over de motie te laten zien.")
        print("'o': Opnieuw openen van de motie in PDF.")
        print("'r': Overeenkomst tot nu toe laten zien met de verschillende partijen.")
        print("'+': Voor de motie stemmen en naar de volgende motie gaan.")
        print("'0': Geen mening over de motie hebben en naar de volgende motie gaan.")
        print("'-': Tegen de motie stemmen en naar de volgende motie gaan.")
        user_input = input()
        print()
        if user_input == "i":
            show_additional_motion_info(motion)
        elif user_input == "o":
            show_motion(motion)
        elif user_input == "r":
            show_result(scores, totals, included_parties)
        elif user_input == "+":
            return update_scores(motion, True, scores, totals)
        elif user_input == "0":
            return scores, totals
        elif user_input == "-":
            return update_scores(motion, False, scores, totals)


def ask_user_input_no_motion(scores: Counter[str], totals: Counter[str], included_parties: List[str])\
        -> Tuple[Counter[str], Counter[str]]:
    """ Ask the user what to do after all motions are displayed. """
    while True:
        print(Back.YELLOW + f"Er zijn geen nieuwe moties meer." + Style.RESET_ALL)
        print("Kies het volgende: ")
        print("'r': Overeenkomst tot nu toe laten zien met de verschillende partijen.")
        user_input = input()
        print()
        if user_input == "r":
            show_result(scores, totals, included_parties)


def run(motions: DataFrame, start_date: date, end_date: date, regex: str, included_parties: List[str], seed: int):
    """ Run the random motion selecter. """
    motions = motions.sample(frac=1.0, random_state=seed)  # Shuffle the motions in a random order.
    scores = counter()
    totals = counter()

    # Loop over all motions.
    print()
    for _, motion in motions.iterrows():
        show_motion(motion)
        scores, totals = ask_user_input_motion(motion, scores, totals, included_parties)

    while True:
        ask_user_input_no_motion(scores, totals, included_parties)
