from datetime import datetime
from pathlib import Path
from typing import Generator


# FIXME: works only with unique dates as file names
def find_latest_changelog_file(starting_dir: Path = Path("changelog")) -> Path | None:
    most_recent = max(
        [
            datetime.strptime(file.name.split(".")[0], "%d-%m-%y")
            for file in starting_dir.iterdir()
            if file.is_file()
        ]
    )
    most_recent = most_recent.strftime("%d-%m-%y")
    return Path(f"./changelog/{most_recent}.md").absolute()


def stream_changelog_file(file: Path) -> Generator[str, None, None]:
    with open(file, "r") as fread:
        for line in fread.readlines():
            yield line


def update_readme():
    next_line = stream_changelog_file(find_latest_changelog_file())
    start_idx = 0
    end_idx = 1000
    with open("readme.md", "r") as fread:
        with open("temp", "a") as fwrite:
            for i, line in enumerate(fread.readlines()):
                if "<!-- Project changelog append here -->\n" in line:
                    start_idx = i + 1
                elif "<!-- EOF -->\n" in line:
                    end_idx = i
            fread.seek(0)
            lines = fread.readlines()[:start_idx]
            fwrite.writelines(lines)
            try:
                while next_line:
                    fwrite.write(next(next_line))
            except StopIteration:
                pass

            fwrite.write("\n")
            fread.seek(0)
            remaining_lines = fread.readlines()[end_idx:]
            fwrite.writelines(remaining_lines)

    Path("temp").replace("readme.md")


if __name__ == "__main__":
    update_readme()
