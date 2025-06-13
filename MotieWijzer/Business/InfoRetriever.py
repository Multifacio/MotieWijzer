from collections import Counter as counter
from datetime import date
from typing import List, Tuple

import pandas as pd
from pandas import DataFrame

from MotieWijzer.Business import MOTIONS_DATA_PATH

def filter_motions(motions: DataFrame, start_date: date, end_date: date, regex: str):
    """ Filter the motions on date and the title on regex. """
    motions["VoteTime"] = pd.to_datetime(motions["VoteTime"].str.slice(0, 10))
    return motions[
        motions["Subject"].str.match(regex, case=False) &
        (motions["VoteTime"] >= start_date) &
        (motions["VoteTime"] <= end_date)
    ]

def get_all_parties(motions: DataFrame) -> List[str]:
    """ Get all parties that existed during any of the motions. """
    motions["Proponents"] = motions["Proponents"].astype(str)
    motions["Absentees"] = motions["Absentees"].astype(str)
    motions["Opponents"] = motions["Opponents"].astype(str)

    all_parties = set()
    for _, row in motions.iterrows():
        all_parties |= set(row["Proponents"].split(","))
        all_parties |= set(row["Absentees"].split(","))
        all_parties |= set(row["Opponents"].split(","))
    return sorted(all_parties - {"nan"})

def get_partially_missing_parties(motions: DataFrame, all_parties: List[str]) -> List[Tuple[str, int]]:
    """ Get all parties that did not exist during any of these motions. """
    all_parties = set(all_parties)
    partially_missing_parties = counter()
    for _, row in motions.iterrows():
        existing_parties = set()
        existing_parties |= set(row["Proponents"].split(","))
        existing_parties |= set(row["Absentees"].split(","))
        existing_parties |= set(row["Opponents"].split(","))
        partially_missing_parties.update(all_parties - existing_parties)

    return partially_missing_parties.most_common()

def retrieve_info(start_date: date, end_date: date, regex: str):
    """ Run the info retriever. """
    motions = pd.read_csv(MOTIONS_DATA_PATH, sep="|")
    motions = filter_motions(motions, start_date, end_date, regex)

    first_date = motions["VoteTime"].min().date()
    last_date = motions["VoteTime"].max().date()
    all_parties = get_all_parties(motions)
    partially_missing_parties = get_partially_missing_parties(motions, all_parties)
    partially_missing_parties = [f"{p} ({c})" for p, c in partially_missing_parties]
    print(f"Eerste motie: {first_date}")
    print(f"Laatste motie: {last_date}")
    print(f"Aantal moties: {len(motions)}")
    print(f"Alle partijen: {', '.join(all_parties)}")
    print(f"(Deels) ontbrekende partijen: {', '.join(partially_missing_parties)}")
    print()
