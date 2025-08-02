#!/bin/python3

import re
from typing import Self
from collections.abc import Iterable
from bs4 import BeautifulSoup
from bs4.element import Tag
from itertools import combinations, chain

# TODO: change to appropriate html file path (download from SIAKNG)
FILE_NAME = "jadwal.html"

# TODO: fill this with classes you want to check for conflicts
# The names need to match exactly to how it's shown on per class letter basis
WANTED = ("BasDat", "StatProb", "SDA", "Alin", "Sistem Operasi", "PBP")

# TODO: fill this to ensure classes you took has no conflict
# This can also be empty if you are not sure which classes to take
# Right side should be "-" if it is the only class available
# Must be a subset of WANTED
TAKEN_CLASSES_DICT = {
    "PBP": "C",
    "SDA": "E",
    "Alin": "A",
    "StatProb": "B",
    "Sistem Operasi": "C",
}

assert set(WANTED) >= set(TAKEN_CLASSES_DICT.keys()), (
    "WANTED must be a subset of TAKEN_CLASSES_DICT"
)

assert len(set(TAKEN_CLASSES_DICT.keys())) == len(TAKEN_CLASSES_DICT.keys()), (
    "Bro why take the same class twice?"
)


class Schedule:
    def __init__(
        self,
        day: str,
        start_hour: int,
        start_minute: int,
        end_hour: int,
        end_minute: int,
    ):
        self.day = day
        self.start_hour = start_hour
        self.start_minute = start_minute
        self.end_hour = end_hour
        self.end_minute = end_minute

    def __str__(self) -> str:
        return f"{self.day}, {str(self.start_hour).zfill(2)}:{str(self.start_minute).zfill(2)}-{str(self.end_hour).zfill(2)}:{str(self.end_minute).zfill(2)}"

    def __repr__(self) -> str:
        return f"Schedule({self.day}, {str(self.start_hour).zfill(2)}, {str(self.start_minute).zfill(2)}, {str(self.end_hour).zfill(2)}, {str(self.end_minute).zfill(2)})"

    def pretty(self) -> str:
        return f"{str(self.day) + ',':<8} {str(self.start_hour).zfill(2)}:{str(self.start_minute).zfill(2)} - {str(self.end_hour).zfill(2)}:{str(self.end_minute).zfill(2)}"

    def is_conflict(self, other: Self) -> bool:
        if self.day != other.day:
            return False

        start = self.start_hour * 60 + self.start_minute
        end = self.end_hour * 60 + self.end_minute
        other_start = other.start_hour * 60 + other.start_minute
        other_end = other.end_hour * 60 + other.end_minute

        if start <= other_end and other_start <= end:
            return True

        return False


class SiakClass:
    def __init__(self, class_name: str, class_letter: str, schedules: list[Schedule]):
        self.class_name = class_name
        self.class_letter = class_letter
        self.schedules = schedules

    def __str__(self) -> str:
        return f"{self.class_name} {self.class_letter}"

    def __repr__(self) -> str:
        return f"Class({self.class_name}, {self.class_letter}, {self.schedules})"

    def get_conflict(self, other: Self) -> list[tuple[int, int]]:
        conflicts = []

        for i, schedule in enumerate(self.schedules):
            for j, other_schedule in enumerate(other.schedules):
                if schedule.is_conflict(other_schedule):
                    conflicts.append((i, j))

        return conflicts


def to_schedule(string: str) -> Schedule:
    assert re.fullmatch(
        r"(Senin|Selasa|Rabu|Kamis|Jumat), \d{2}\.\d{2}\-\d{2}\.\d{2}", string
    )
    day, time = string.split(",")
    time = time.strip()
    start, end = time.split("-")
    begin_hour, begin_minute = map(int, start.split("."))
    end_hour, end_minute = map(int, end.split("."))
    return Schedule(day, begin_hour, begin_minute, end_hour, end_minute)


def get_siak_class_rows(soup: Tag) -> Iterable[Tag]:
    def is_section_start_text(tag: Tag) -> bool:
        # Every section e.g. Kelas Internal starts with "Kode MK - Nama Mata Kuliah (Kredit, Term); Kurikulum"
        # And the first entry (it's separated into 3) is "Kode MK - "
        try:
            if tag.contents[0] == "Kode MK - ":
                return True
            return False
        except IndexError:
            return False

    # Chain means flatten the lists (or in this case queries)
    # We go up twice because that's where the classes are grouped
    # tr (row entry) is needed because there's a bunch of noise (newline Navigatable Strings)
    sections: list[list[Tag]] = [
        tag.parent.parent.find_all("tr", recurse=False)  # type: ignore[reportOptionalMemberAccess]
        for tag in soup.find_all(is_section_start_text)
    ]  # type: ignore[reportOptionalMemberAccess]
    siak_class_ish_rows: Iterable[Tag] = chain.from_iterable(sections)

    def is_class_row(tag: Tag) -> bool:
        if tag.find(string="Kelas ") is None:
            return False

        assert re.match(
            r".*\/main\/CoursePlan\/ClassInfo.*", str(tag.find("a")["href"])
        )  # type: ignore[reportIndexIssue]
        return True

    return filter(is_class_row, siak_class_ish_rows)


def get_relevant_siak_classes() -> list[SiakClass]:
    with open(FILE_NAME, "r", encoding="ASCII", errors="ignore") as file:
        content = file.read()

    # Idk why it's called soup, it's some sort of tooling to read the file i guess
    soup = BeautifulSoup(content, "html.parser")

    raw_rows: Iterable[Tag] = get_siak_class_rows(soup)

    siak_classes: list[SiakClass] = []
    for raw_row in raw_rows:
        raw_row: Tag

        # The class name with the optional letter identifier
        class_name_and_letter: str = str(raw_row.find_all("td")[1].a.contents[0])  # type: ignore[reportAttributeAccessIssue]

        # Treat lone single character letter suffix as class letter
        if (
            len(class_name_and_letter) > 2
            and class_name_and_letter[-1].isalpha()
            and class_name_and_letter[-2]
            in (
                " ",
                "-",
            )
        ):
            class_name: str = class_name_and_letter[:-2]
            class_letter: str = class_name_and_letter[-1]
        else:
            class_name: str = class_name_and_letter
            class_letter: str = "-"

        if not any([wanted_class == class_name for wanted_class in WANTED]):
            continue

        schedules = [
            to_schedule(single_schedule)
            for single_schedule in raw_row.find_all("td")[4].contents  # type: ignore[reportAttributeAccessIssue]
            if isinstance(single_schedule, str)
        ]

        siak_classes.append(SiakClass(class_name, class_letter, schedules))

    return siak_classes


def main():
    siak_classes = get_relevant_siak_classes()

    # Lists all conflicting classes
    conflicting_siak_classes_pair: list[tuple[SiakClass, SiakClass]] = list(
        filter(
            lambda pair: len(SiakClass.get_conflict(pair[0], pair[1])) > 0
            and pair[0].class_name != pair[1].class_name,
            combinations(siak_classes, 2),
        )
    )

    print("===ALL CONFLICTING CLASSES===")
    for siak_class_1, siak_class_2 in conflicting_siak_classes_pair:
        print(f"{siak_class_1} with {siak_class_2}")
    if len(conflicting_siak_classes_pair) == 0:
        print("No conflicting classes")

    print()

    # We can stop here if we don't know what classes to take yet
    if len(TAKEN_CLASSES_DICT) == 0:
        exit(0)

    # Checks if any taken class is conflicting
    taken_classes: list[SiakClass] = list(
        filter(
            lambda siak_class: siak_class.class_name in TAKEN_CLASSES_DICT
            and siak_class.class_letter == TAKEN_CLASSES_DICT[siak_class.class_name],
            siak_classes,
        )
    )
    conflicting_taken_classes_pair: list[tuple[SiakClass, SiakClass]] = list(
        filter(
            lambda pair: len(SiakClass.get_conflict(pair[0], pair[1])) > 0,
            combinations(taken_classes, 2),
        )
    )

    print("===CONFLICTS FOR TAKEN CLASS===")
    if len(taken_classes) != len(TAKEN_CLASSES_DICT):
        print(
            "Inconsistency between taken classes dict and taken classes found, please recheck if class names are correct"
        )
        print(f"Taken classes dict: {TAKEN_CLASSES_DICT}")
        print(f"Taken classes found: {list(map(str, taken_classes))}")
        exit(1)

    for siak_class_1, siak_class_2 in conflicting_taken_classes_pair:
        print(f"Taken class has conflict: {siak_class_1} with {siak_class_2}")
        conflicts = siak_class_1.get_conflict(siak_class_2)
        for conflict in conflicts:
            print(
                f"At schedule: {siak_class_1.schedules[conflict[0]]} with {siak_class_2.schedules[conflict[1]]}"
            )

    if len(conflicting_taken_classes_pair) == 0:
        print("No conflict for taken classes")

        print()

        print("===SCHEDULE===")
        for taken_class in taken_classes:
            print(
                f"{str(taken_class):<20}",
                " | ".join(map(Schedule.pretty, taken_class.schedules)),
            )

    print()
    print("Bye 💙❤️")


if __name__ == "__main__":
    main()
