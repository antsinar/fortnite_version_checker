from pathlib import Path
import subprocess

"""run scripts and auto commit changes"""


def execute(commands: list, cwd: str = ".") -> None:
    for command in commands:
        try:
            subprocess.run(command, check=True, timeout=60, cwd=cwd, shell=True)
            print(f"[X] Command {command} executed successfully.")
        except FileNotFoundError as exc:
            print(
                "[E]",
                f"Command {command} failed because the process "
                f"could not be found.\n{exc}",
            )
            exit()
        except subprocess.CalledProcessError as exc:
            print(
                "[E]",
                f"Command {command} failed because the process "
                f"did not return a successful return code.\n{exc}",
            )
            exit()
        except subprocess.TimeoutExpired as exc:
            print(f"[E] Command {command} timed out.\n {exc}")
            exit()


def prepare_commands(commit_message: str) -> None:
    update_readme_commands = [
        [
            "python",
            "update_readme_on_push.py",
        ]
    ]

    dump_tags_commands = [
        [
            "python",
            "dump_tags_on_push.py",
        ]
    ]

    git_commands = [
        ["git", "add", f"readme.md"],
        ["git", "add", f"tags/*.md"],
        [
            "git",
            "commit",
            "-m",
            f"{commit_message}",
        ],
        ["git", "push", "-u", "origin", "main"],
    ]

    execute(update_readme_commands)
    execute(dump_tags_commands)
    execute(git_commands)


if __name__ == "__main__":
    import sys

    commit_message = sys.argv[1] if len(sys.argv) > 1 else ""
    if not commit_message:
        print("[E] No commit message provided")
        exit()
    prepare_commands(commit_message)
