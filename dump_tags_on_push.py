from enum import StrEnum
from pathlib import Path
from typing import List

"""Dumps complete and incomplete tags from changelog files
TODO: add logic to detect Resolved in the changelog files and update the tag file accordingly
"""


class Tag(StrEnum):
    QoL = "QoL"
    CQ = "CQ"
    BUG = "BUG"


def parse_line(line: str, file_name: str) -> str:
    """Functions:
    - append changelog file as a markdown link
    - replace the first instance of a `-` with an empty markdown checkbox
    """
    return (
        line.strip().replace("-", "- [ ] ", 1).replace("`", "")
        + f"(../changelog/{file_name})\n"
    )


def dump_tag(tag: Tag, file_name: str, lines: List[str]) -> None:
    """Dumps tags from changelog files into a seperate file"""
    with open(f"tags/{tag.value}.md", "a") as f:
        f.writelines([parse_line(line, file_name) for line in lines])


def main() -> None:
    # init tag buckets
    tag_buckets = {
        Tag.QoL: [],
        Tag.CQ: [],
        Tag.BUG: [],
    }

    # parse changelog files
    changelog_files = [f for f in Path("changelog").iterdir() if f.is_file()]
    for file in changelog_files:
        with open(file, "r") as f:
            for line in f.readlines():
                # avoid markdown titles
                if "#" in line:
                    continue
                if Tag.QoL.value in line:
                    tag_buckets[Tag.QoL].append(line)
                elif Tag.CQ.value in line:
                    tag_buckets[Tag.CQ].append(line)
                elif Tag.BUG.value in line:
                    tag_buckets[Tag.BUG].append(line)
        for tag in Tag:
            dump_tag(tag, file.name, tag_buckets[tag])


if __name__ == "__main__":
    main()
