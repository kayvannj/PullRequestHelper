#!/usr/bin/python
import subprocess
import sys

# user is on version branch
# running prh -b "branch" -a <file 1> <file 2> <file 3> ...
USEAGE = """
    prh -b <child_branch_name> [-a <file1_path> <file2_path> ...]
    prh -upto <parent_branch_name>

"""
DEFAULT_COMMIT_MESSAGE = "Commit"
DEFAULT_BRANCH_NAME = "prh_branch"
DEFAULT_PR_TITLE = "PRH"
DEFAULT_PR_BODY = "@doximitystevenlee CR please\n"
debug_is_on = 1 if "-debug" in sys.argv or "-d" in sys.argv else 0
verbose_is_on = 1 if "-v" in sys.argv else 0


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


def commit(commit_message=DEFAULT_COMMIT_MESSAGE):
    if not commit_message:
        commit_message = DEFAULT_COMMIT_MESSAGE
    command = ["git", "commit", "-m", commit_message]
    run_command(command)


def push(branch_name):
    command = ["git", "push", "--set-upstream", "origin", branch_name]
    run_command(command)


def create_pull_request(main_branch, pr_title=DEFAULT_PR_TITLE, pr_body=DEFAULT_PR_BODY):
    if not pr_title:
        pr_title = get_current_branch().replace("_"," ")
    if not pr_body:
        pr_body = DEFAULT_PR_BODY
    else:
        pr_body = pr_body + "\n" + DEFAULT_PR_BODY
    command = ["hub", "pull-request", "-b", main_branch, "-m", pr_title + "\n" + pr_body]
    return run_command(command, 1)


def get_current_branch():
    branches = subprocess.check_output(["git", "branch"])
    for b in branches.split("\n"):
        if (b[0] == "*"):
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


def main():
    branch_name = ""
    pr_title = ""
    pr_body = ""
    file_paths = []
    # get main branch name
    parent_branch = ""
    commit_message = ""
    submodule = 0
    current_branch = get_current_branch()
    is_add_all = False
    if "-debug" in sys.argv or "-d" in sys.argv:
        global debug_is_on
        debug_is_on = 1

    if "-v" in sys.argv:
        global verbose_is_on
        verbose_is_on = 1

    if "-b" in sys.argv:
        branch_name = sys.argv[sys.argv.index("-b") + 1]

    if "-pb" in sys.argv:
        pr_body = sys.argv[sys.argv.index("-pb") + 1]

    if "-pt" in sys.argv:
        pr_title = sys.argv[sys.argv.index("-pt") + 1]

    if "-a" in sys.argv:
        file_paths = sys.argv[sys.argv.index("-a") + 1:]

    if "-parent" in sys.argv:
        parent_branch = sys.argv[sys.argv.index("-parent") + 1]

    if "-sub" in sys.argv:
        submodule = 1

    if "-m" in sys.argv:
        commit_message = sys.argv[sys.argv.index("-m") + 1:]

    if submodule:
        cd(get_submodule_name())

    if child_branch_name:
        create_branch(child_branch_name)
        target_branch_name = current_branch
    elif parent_branch:
        target_branch_name = parent_branch
    else:
        print "Use -h to see the usage"
        return

    # add and commit changes
    add_changes(file_paths, is_add_all)
    commit(commit_message)
    push(get_current_branch())
    pr_url = create_pull_request(target_branch_name, pr_title, pr_body)
    if pr_url[:4] == "http":
        print(pr_url)
        launch_browser(pr_url)
    else:
        if not branch_name:
            print("Useage: prh -b \"branch\" -a <file 1> <file 2> <file 3> ...")
        elif not file_paths:
            print("No files to be added! Use -a <file path> to add files")
        else:
            try:
                # create new branch
                if branch_name:
                    create_branch(branch_name)

                if file_paths:
                    add_files(file_paths)

                if branch_name and file_paths:
                    commit()
                    push(branch_name)

                pr_url = create_pull_request(current_branch, pr_title, pr_body)
                if pr_url:
                    print("\nPull Request URL >>> " + pr_url + "\n")
                    launch_browser(pr_url)

                checkout(current_branch)

            except subprocess.CalledProcessError, e:
                print("Sorry, Failed")


if __name__ == "__main__":
    main()
    # print(get_status())
