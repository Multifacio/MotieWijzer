""" Randomly selects a motion (Dutch: motie) in the new way. """
import json
import os
import re
import subprocess
from collections import Counter as counter
from datetime import date, datetime
from sys import platform
from typing import Counter, List, Tuple

from colorama import Back, Style, Fore
from pandas import DataFrame
import pandas as pd
import requests

from MotieWijzer.Business import DATA_DIRECTORY, MOTIONS_DATA_PATH
from MotieWijzer.Business.InfoRetriever import filter_motions

PDF_OUTPUT_FILE_PATH = f"{DATA_DIRECTORY}/output.pdf"  # The path in which the motion PDF is stored.


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
    proponents = str(motion["Proponents"]).replace(",", ", ")
    opponents = str(motion["Opponents"]).replace(",", ", ")
    absentees = str(motion["Absentees"]).replace("nan", "").replace(",", ", ")
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


def save(start_date: date, end_date: date, regex: str, included_parties: List[str], seed: int, scores: Counter[str],
         totals: Counter[str], index: int):
    """ Save the results so far into a file. """
    while True:
        user_input = input("Profiel naam: ")
        print()

        file_name = f"{DATA_DIRECTORY}/{user_input}.json"
        try:
            json_object = json.dumps({
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "regex": regex,
                "included_parties": included_parties,
                "seed": seed,
                "scores": scores,
                "totals": totals,
                "index": index
            })
            with open(file_name, "w") as f:
                f.write(json_object)

            return
        except:
            print(Fore.WHITE + Back.RED + f"Kon {file_name} niet opslaan." + Style.RESET_ALL)
            print()


def ask_user_input_motion(motion: pd.Series, scores: Counter[str], totals: Counter[str], included_parties: List[str],
                          start_date: date, end_date: date, regex: str, seed: int, index: int) -> Tuple[Counter[str], Counter[str]]:
    """ Ask the user what to do with the motion. """
    while True:
        print("Kies het volgende: ")
        print("'i': Om extra informatie over de motie te laten zien.")
        print("'o': Opnieuw openen van de motie in PDF.")
        print("'r': Overeenkomst tot nu toe laten zien met de verschillende partijen.")
        print("'s': Sla de resultaten zo ver op in een profiel.")
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
        elif user_input == "s":
            save(start_date, end_date, regex, included_parties, seed, scores, totals, index)
        elif user_input == "+":
            return update_scores(motion, True, scores, totals)
        elif user_input == "0":
            return scores, totals
        elif user_input == "-":
            return update_scores(motion, False, scores, totals)


def ask_user_input_no_motion(scores: Counter[str], totals: Counter[str], included_parties: List[str], start_date: date,
                             end_date: date, regex: str, seed: int, index: int) -> Tuple[Counter[str], Counter[str]]:
    """ Ask the user what to do after all motions are displayed. """
    while True:
        print("Kies het volgende: ")
        print("'r': Overeenkomst tot nu toe laten zien met de verschillende partijen.")
        print("'s': Sla de resultaten zo ver op in een profiel.")
        user_input = input()
        print()
        if user_input == "r":
            show_result(scores, totals, included_parties)
        elif user_input == "s":
            save(start_date, end_date, regex, included_parties, seed, scores, totals, index)


def run(motions: DataFrame, start_date: date, end_date: date, regex: str, included_parties: List[str], seed: int,
        scores: Counter[str], totals: Counter[str], index: int):
    """ Run the random motion selecter. """
    motions = motions.sample(frac=1.0, random_state=seed)  # Shuffle the motions in a random order.
    motions = motions[index:]
    print()
    for _, motion in motions.iterrows():
        subject = motion["Subject"]
        print(Back.GREEN + f"Motie titel: {subject}" + Style.RESET_ALL)
        show_motion(motion)
        scores, totals = ask_user_input_motion(motion, scores, totals, included_parties, start_date, end_date, regex,
                                               seed, index)
        index += 1

    print(Back.YELLOW + f"Er zijn geen nieuwe moties meer." + Style.RESET_ALL)
    ask_user_input_no_motion(scores, totals, included_parties, start_date, end_date, regex, seed, index)


def load(file_name: str):
    """ Load a profile and continue from there. """
    with open(file_name, "r") as f:
        json_objects = json.load(f)

    start_date = json_objects["start_date"]
    start_date = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", start_date)
    start_date = start_date.groups()
    start_date = datetime(year=int(start_date[0]), month=int(start_date[1]), day=int(start_date[2]))

    end_date = json_objects["end_date"]
    end_date = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", end_date)
    end_date = end_date.groups()
    end_date = datetime(year=int(end_date[0]), month=int(end_date[1]), day=int(end_date[2]))

    regex = json_objects["regex"]
    included_parties = json_objects["included_parties"]
    seed = json_objects["seed"]
    scores = counter(json_objects["scores"])
    totals = counter(json_objects["totals"])
    index = json_objects["index"]

    motions = pd.read_csv(MOTIONS_DATA_PATH, sep="|")
    motions = filter_motions(motions, start_date, end_date, regex)

    return run(motions, start_date, end_date, regex, included_parties, seed, scores, totals, index)