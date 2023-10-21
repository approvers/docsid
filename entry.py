import argparse
import io
import os
import subprocess
import threading
from typing import Callable

# Envvar names
CI_ENVVAR_NAME = "DOCSID_IS_CI"
TEST_ENVVAR_NAME = "DOCSID_IS_TEST"

# Priority is from bottom ( index 0 ) to top ( index -1 ).
ENVFILES_TO_LOAD_IN_CI = ["./.env.ci"]
ENVFILES_TO_LOAD_IN_TEST = ["./.env.test"]
ENVFILES_TO_LOAD_IN_LOCAL = ["./.env.example", "./.env.local"]


class CommandError(RuntimeError):
    pass


def parse_0_or_1_envvar(name: str) -> bool:
    envvar = os.environ.get(name, None)

    if envvar:
        try:
            result: bool = bool(int(envvar))

        except (ValueError, TypeError):
            raise RuntimeError(
                "RuntimeError: the value of the CI environment variable must be an integer with value 0 or 1."
            )

    # noinspection PyUnboundLocalVariable
    return result


def load_dotenv() -> None:
    try:
        import dotenv

    except ImportError:
        raise RuntimeError(
            "RuntimeError: failed to import 'dotenv'.\n"
            "Please install python-dotenv to use this command."
        )

    envfiles_to_load: list[str]

    if parse_0_or_1_envvar(CI_ENVVAR_NAME):
        envfiles_to_load = ENVFILES_TO_LOAD_IN_CI

    else:
        if parse_0_or_1_envvar(TEST_ENVVAR_NAME):
            envfiles_to_load = ENVFILES_TO_LOAD_IN_TEST

        else:
            envfiles_to_load = ENVFILES_TO_LOAD_IN_LOCAL

    for envfile in envfiles_to_load:
        dotenv.load_dotenv(envfile, verbose=True, override=True)


def stream_reader(stream: io.TextIOBase, callback: Callable[[str], None]) -> None:
    while True:
        line = stream.readline()
        if line:
            callback(line.strip())
        else:
            break


def execute_command(command_list: list) -> None:
    print("Executing command:", " ".join(command_list))

    with subprocess.Popen(
        command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ) as proc:
        # Start threads to read the stdout and stderr streams
        stdout_thread = threading.Thread(
            target=stream_reader, args=(proc.stdout, print)
        )
        stderr_thread = threading.Thread(
            target=stream_reader, args=(proc.stderr, print)
        )

        stdout_thread.start()
        stderr_thread.start()

        stdout_thread.join()
        stderr_thread.join()

        if proc.returncode is None:
            return

        if proc.returncode != 0:
            raise CommandError(
                f"Error in command execution with return code: {proc.returncode}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute a shell command.")
    parser.add_argument("command", nargs="+", help="Command to execute")

    args = parser.parse_args()

    execute_command(args.command)


if __name__ == "__main__":
    main()
