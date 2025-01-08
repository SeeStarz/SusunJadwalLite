from typing import Self
from bs4 import BeautifulSoup
from itertools import combinations

# NOTE: change to appropriate html file path (download from SIAKNG)
FILE_NAME = "jadwal_new.html"
with open(FILE_NAME, "r", encoding="ASCII", errors="ignore") as file:
    content = file.read()

# NOTE: fill this with classes you want to check for conflicts
WANTED = ("Alin", "DDP 2", "POK", "Kalkulus 2", "MPK Terintegrasi")

# NOTE: fill this to ensure classes you took has no conflict
# This can also be empty
TAKEN_CLASSES_DICT = {
    "MPK Terintegrasi": "F",
    "Alin": "A",
    "POK": "B",
    "DDP 2": "E",
    "Kalkulus 2": "A",
}


class Schedule:
    def __init__(
        self,
        day: int,
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

    def is_conflict(self, other: Self) -> bool:
        if self.day != other.day:
            return False

        start = self.start_hour * 60 + self.start_minute
        end = self.end_hour * 60 + self.end_minute
        other_start = other.start_hour * 60 + other.start_minute
        other_end = other.end_hour * 60 + other.end_minute

        if start - other_end <= 0 and other_start - end <= 0:
            return True

        return False


class Class:
    def __init__(self, category: str, identifier: str, schedule: Schedule):
        self.category = category
        self.identifier = identifier
        self.schedule = schedule

    def __str__(self) -> str:
        return f"{self.category} {self.identifier}"

    def __repr__(self) -> str:
        return f"Class({self.category}, {self.identifier}, {self.schedule})"

    def get_conflict(self, other: Self) -> list[int, int]:
        conflicts = []

        for i, schedule in enumerate(self.schedule):
            for j, other_schedule in enumerate(other.schedule):
                if schedule.is_conflict(other_schedule):
                    conflicts.append((i, j))

        return conflicts


def main():
    soup = BeautifulSoup(content, "html.parser")
    siak_classes = (
        soup.body.contents[-2]
        .contents[3]
        .contents[1]
        .contents[1]
        .contents[5]
        .contents[1]
        .contents[13]
        .contents[1]
        .contents[1]
        .contents[1]
        .contents[1]
        .contents[1]
        .contents[1]
        .contents[11]
        .contents[1]
    )

    classes = []

    def to_schedule(string):
        day, time = string.split(",")
        time = time.strip()
        start, end = time.split("-")
        begin_hour, begin_minute = map(int, start.split("."))
        end_hour, end_minute = map(int, end.split("."))
        return Schedule(day, begin_hour, begin_minute, end_hour, end_minute)

    for siak_class in siak_classes:
        try:
            siak_class = siak_class.find_all("td")
        except:
            continue

        if siak_class is None:
            continue

        try:
            class_name = siak_class[1].a.contents[0]
        except:
            continue

        if not any([class_name[:-2] == wanted_class for wanted_class in WANTED]):
            continue

        schedule = [
            to_schedule(single_schedule)
            for single_schedule in siak_class[4].contents
            if isinstance(single_schedule, str)
        ]

        classes.append(Class(class_name[:-2], class_name[-1], schedule))

    # Lists all conflicting classes
    print("LISTING ALL CONFLICTING CLASSES")
    for class1, class2 in combinations(classes, 2):
        if class1.category == class2.category:
            continue

        conflict = class1.get_conflict(class2)
        if len(conflict) > 0:
            print(
                f"Conflict: {class1.category} {class1.identifier} with {class2.category} {class2.identifier}"
            )
            # print(
            #     f"At schedule: {class1.schedule[conflict[0]]} with {class2.schedule[conflict[1]]}"
            # )
            # print()

    print()

    # Checks if any taken class is conflicting
    print("LISTING CONFLICTS FOR TAKEN CLASS")

    all_good = True
    taken_classes = []
    for class_ in classes:
        try:
            if TAKEN_CLASSES_DICT[class_.category] == class_.identifier:
                taken_classes.append(class_)
        except KeyError:
            continue

    print(f"Taken classes dict: {TAKEN_CLASSES_DICT}")
    print(f"Taken classes found: {list(map(str, taken_classes))}")
    if len(taken_classes) != len(TAKEN_CLASSES_DICT):
        print(
            "Inconsistentcy between taken classes dict and taken classes found plase recheck if class names are correct"
        )
        all_good = False

    for class1, class2 in combinations(taken_classes, 2):
        if class1.category == class2.category:
            continue

        conflicts = class1.get_conflict(class2)
        if len(conflicts) != 0:
            print()
            all_good = False
            print(
                f"Taken class has conflict: {class1.category} {class1.identifier} with {class2.category} {class2.identifier}"
            )
            for conflict in conflicts:
                print(
                    f"At schedule: {class1.schedule[conflict[0]]} with {class2.schedule[conflict[1]]}"
                )

    if all_good:
        print("All good :>")


if __name__ == "__main__":
    main()