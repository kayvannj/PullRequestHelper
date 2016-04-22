#!/usr/bin/python
"""Pull Request Helper

Usage:
  prh2.py child <branch_name> [<commit_message> <pr_title> <pr_body>]
  prh2.py parent <branch_name> [<commit_message> <pr_title> <pr_body>]
  prh2.py config
  prh2.py (-h | --help)
  prh2.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --add         Add files
  -v --verbose  Verbose mode, you see all the command being run
  -d            Debug mode, no action really takes place
"""
from docopt import docopt
import subprocess
import sys

DEFAULT_COMMIT_MESSAGE = "Commit"
DEFAULT_BRANCH_NAME = "prh_branch"
DEFAULT_PR_TITLE = "PRH"
DEFAULT_PR_BODY = "@doximitystevenlee CR please\n"
global debug_is_on
global verbose_is_on


def run_command(command, output=0):
    if debug_is_on:
        print_command(command)
    elif verbose_is_on:
        print command
        if output:
            return subprocess.check_output(command)
        else:
            return subprocess.check_call(command)
    else:
        if output:
            return subprocess.check_output(command)
        else:
            return subprocess.check_call(command)


def print_command(command):
    print reduce(lambda x, y: x + " " + y, command)


def create_branch(branch_name):
    command = ["git", "checkout", "-b", branch_name]
    run_command(command)


def checkout(branch_name):
    command = ["git", "checkout", branch_name]
    run_command(command)


def add_files(file_paths):
    command = ["git", "add"] + file_paths
    run_command(command)


def add_all():
    command = ["git", "add", "-A"]
    run_command(command)


def commit(commit_message=DEFAULT_COMMIT_MESSAGE):
    command = ["git", "commit", "-m", commit_message]
    run_command(command)


def push(branch_name):
    command = ["git", "push", "--set-upstream", "origin", branch_name]
    run_command(command)


def create_pull_request(main_branch, pr_title=DEFAULT_PR_TITLE, pr_body=DEFAULT_PR_BODY):
    if not pr_title:
        pr_title = DEFAULT_PR_TITLE
    if not pr_body:
        pr_body = DEFAULT_PR_BODY
    else:
        pr_body = pr_body + "\n" + DEFAULT_PR_BODY
    command = ["hub", "pull-request", "-b", main_branch, "-m", pr_title + "\n" + pr_body]
    return run_command(command, 1)


def get_current_branch():
    branches = subprocess.check_output(["git", "branch"])
    for b in branches.split("\n"):
        if b[0] == "*":
            current_branch = b.split(" ")[1]
            break
    return current_branch


def get_submodule_name():
    command = ["git", "submodule"]
    output = run_command(command, True)
    return output.split(" ")[1]


def get_status():
    return subprocess.check_output(["git", "status"])


def get_one_switch_value(switch_key):
    return sys.argv[sys.argv.index(switch_key) + 1]


def launch_browser(url):
    command = ["open", url[:-1] if url else ""]
    run_command(command)


def cd(path):
    command = ["cd", path]
    run_command(command)


def main(arguments):
    branch_name = arguments["<branch_name>"]
    pr_title = arguments["pr_title"]
    pr_body = arguments["pr_body"]
    verbose_is_on = arguments["-v"] or arguments["--verbose"]
    debug_is_on = arguments["-d"]
    file_paths = []
    # get main branch name
    parent_branch = ""
    # submodule = arguments["sub"]
    current_branch = get_current_branch()
    is_add_all = True

    # if submodule:
    #     cd(get_submodule_name())

    if arguments["parent"]:
        push(get_current_branch())
        pr_url = create_pull_request(parent_branch, pr_title, pr_body)
        if pr_url[:4] == "http":
            print(pr_url)
            launch_browser(pr_url)
        else:
            print(pr_url)
    elif arguments["child"]:
        if not branch_name:
            print("Useage: prh -b \"branch\" -a <file 1> <file 2> <file 3> ...")
        elif not add_all and not file_paths:
            print("No files to be added! Use -a <file path> to add files")
        else:
            try:
                # create new branch
                if branch_name:
                    create_branch(branch_name)

                if is_add_all:
                    add_all()
                elif file_paths:
                    add_files(file_paths)

                if branch_name and (file_paths or is_add_all):
                    commit()
                    push(branch_name)

                pr_url = create_pull_request(current_branch, pr_title, pr_body)
                if pr_url[:4] == "http":
                    print("\nPull Request URL >>> " + pr_url + "\n")
                    launch_browser(pr_url)
                else:
                    print(pr_url)

                checkout(current_branch)

            except subprocess.CalledProcessError, e:
                print("Sorry, Failed")


if __name__ == '__main__':
    arguments = docopt(__doc__, version='2.0')
    main(arguments)
