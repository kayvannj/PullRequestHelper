#!/usr/bin/env python
import re
import subprocess
import sys

from pip._vendor import requests

import prh_config
import os
import pivotal_tracker

APP_VERSION = "1.0.4"

USEAGE = """
    You can use prh in three main ways:<br>
    1) create a pr from a new branch to current branch
        prh -b <child_branch_name> [-a <file1_path> <file2_path> ...]
    2) create a pr from current branch to a different branch
        prh -upto <parent_branch_name>
    3) create a pr from a new branch to a different branch
        prh -b <child_branch_name> -upto <parent_branch_name>


    if -a  is not used, prh will add all the changed files using 'git add -A'

    -a  to add only specified file into the PR
        or if no file mentioned will not add any file and just create a pr for existing commits
    -m  to add a comment message
    -pt to customize the PullRequest Title
    -pb to append a message to the PullRequest body
    -d  run in debug mode which means not executing commands and just printing them
    -v  run in verbose mode
    -s  stay on current branch
    -h  show help
    -l  local only, do not push changes
    --version print the version of the app
"""
DEFAULT_COMMIT_MESSAGE = prh_config.DEFAULT_COMMIT_MESSAGE
DEFAULT_PR_BODY = prh_config.DEFAULT_PULL_REQUEST_BODY
pivotal_tracker_story_id = ""
pivotal_tracker_story_url = ""
debug_is_on = 0
verbose_is_on = 0
local_only_is_on = 0
stay_is_on = 0
is_just_pr = 0
is_in_submodule = 0


def run_command(command, output=0):
    """
    run the given command
    :param command:
    :param output:
    :return: 0 if no error occurs or the error code
    """
    if debug_is_on:
        print_command(command)
        return 0
    else:
        if verbose_is_on:
            print command
        try:
            if output:
                run_output = subprocess.check_output(command)
            else:
                run_output = subprocess.check_call(command)
            if verbose_is_on:
                print "\nOUTPUT:\t" + str(run_output) + "\n"
            return run_output
        except subprocess.CalledProcessError as e:
            return e.returncode


def print_command(command):
    print get_current_branch() + " >>> " + reduce(lambda x, y: x + " " + y, command)


def checkout(branch_name):
    command = ["git", "checkout", branch_name]
    run_command(command)


def add_files(file_paths):
    command = ["git", "add"] + file_paths
    return run_command(command, 1)


def add_all():
    command = ["git", "add", "-A"]
    return run_command(command, 1)


def get_current_branch():
    popen = subprocess.Popen("git status | head -n 1 | cut -f 3 -d ' '", stdin=subprocess.PIPE, shell=True,
                             stdout=subprocess.PIPE)
    return str(popen.communicate()[0]).strip("\n")


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


def ask_if_is_just_pr():
    answer = raw_input(">>> No file has been added, would you like to continue creating PR (y/n)? ")
    if str.lower(answer) == 'y':
        global is_just_pr
        is_just_pr = 1
        return 0
    else:
        return 1


def add_changes(is_add_all, file_paths):
    error = 0

    if file_paths:
        error = add_files(file_paths)

    elif is_add_all:
        list_of_changes = str(run_command(["git", "add", "-A", "-n"], 1)).strip()
        if not list_of_changes:
            return ask_if_is_just_pr()
        else:
            print("\n" + list_of_changes)
            answer = raw_input(">>> Would you like to apply above changes (y/n)? ")
            if str.lower(answer) == 'y':
                error = add_all()
            else:
                return 1
    else:
        return ask_if_is_just_pr()

    if error:
        print("No files to be added!")
        return 1
    else:
        return 0


def delete_branch(branch_name):
    command = ["git", "branch", "-D", branch_name]
    res = run_command(command, 1)
    return res


def create_branch(branch_name):
    command = ["git", "checkout", "-q", "-b", branch_name]
    res = run_command(command, 0)
    if res == 128:
        answer = raw_input(">>> Branch already exists, would you like me to delete it (y/n)? ")
        if str.lower(answer) == 'y':
            delete_branch(branch_name)
            return create_branch(branch_name)
        else:
            return 1
    else:
        return res


def commit(commit_message=DEFAULT_COMMIT_MESSAGE):
    if is_just_pr:
        return 0
    if not commit_message:
        if pivotal_tracker_story_id:
            story_json = pivotal_tracker.get_story(pivotal_tracker_story_id)
            commit_message = story_json["name"]
        else:
            commit_message = prh_config.DEFAULT_COMMIT_MESSAGE

    command = ["git", "commit", "-m", commit_message]
    res = run_command(command)
    return res


def push(branch_name):
    if local_only_is_on:
        return 0

    command = ["git", "push", "--set-upstream", "origin", branch_name]
    res = run_command(command)
    return res


def create_pull_request(from_branch, to_branch, pr_title, pr_body):
    command = ["git", "remote", "show", "origin", "|", "grep", "\"Fetch URL\""]
    fetch_url = run_command(command, 1)
    # Fetch URL: git@github.com:doximity/Android.git
    owner = fetch_url.split(":")[-1].split("/")[0]
    repo = fetch_url.split(":")[-1].split("/")[1].split(".")[0]
    if local_only_is_on:
        return 0

    if not pr_title:
        pr_title = get_current_branch().replace("_", " ")
    if not pr_body:
        pr_body = DEFAULT_PR_BODY
    else:
        pr_body = pr_body + "\n" + DEFAULT_PR_BODY

    if pivotal_tracker_story_url:
        description = pivotal_tracker.get_story(pivotal_tracker_story_id)["description"]
        name = pivotal_tracker.get_story(pivotal_tracker_story_id)["name"]
        pr_body = pr_body + "\n\n**Story:** [" + name + "](" + pivotal_tracker_story_url + ")\n" + description

    # command = ["hub", "pull-request", "-b", to_branch, "-h", from_branch, "-m", pr_title + "\n" + pr_body]
    # pr_url = run_command(command, 1)
    github = "https://api.github.com"
    api = "{}/repos/{}/{}/pulls".format(github, owner, repo)
    data = {
        "title": pr_title,
        "body": pr_body,
        "head": from_branch,
        "base": to_branch
    }
    headers = {"Authorization": "token " + prh_config.GITHUB_API_TOKEN}
    res = requests.post(api, data=data, headers=headers)
    pr_url = res.json()["url"]

    if pr_url and str(pr_url)[:4] == "http":
        launch_browser(pr_url)
        if pivotal_tracker_story_id:
            if pivotal_tracker.finish_and_post_message(pivotal_tracker_story_id, "PR: " + pr_url):
                print "error with pivotal"

        return 0
    elif pr_url:
        return 1
    else:
        return 1


def process_from_child(origin, new, is_add_all, file_paths, commit_message, pr_title, pr_body):
    if create_branch(new):
        return "Failed to create the new branch"

    if add_changes(is_add_all, file_paths):
        return "Failed to add files"

    if commit(commit_message):
        return "Failed to commit changes"

    if push(new):
        return "Failed to push the commit to origin"

    if create_pull_request(new, origin, pr_title, pr_body):
        return "Failed to create pull-request from " + new + " to " + origin

    if stay_is_on:
        checkout(origin)

    return "Done"


def process_to_parent(origin, parent, is_add_all, file_paths, commit_message, pr_title, pr_body):
    if add_changes(is_add_all, file_paths):
        return "Failed to add files"

    if commit(commit_message):
        return "Failed to commit changes"

    if push(origin):
        return "Failed to push the commit to origin"

    if create_pull_request(origin, parent, pr_title, pr_body):
        return "Failed to create pull-request from " + origin + " to " + parent

    return "Done"


def process_from_child_to_parent(branch_origin, branch_child, branch_parent, is_add_all, file_paths, commit_message,
                                 pr_title,
                                 pr_body):
    if create_branch(branch_child):
        return "Failed to create the new branch"

    if add_changes(is_add_all, file_paths):
        return "Failed to add files"

    if commit(commit_message):
        return "Failed to commit changes"

    if push(branch_child):
        return "Failed to push the commit to origin"

    if create_pull_request(branch_child, branch_parent, pr_title, pr_body):
        return "Failed to create pull-request from " + branch_child + " to " + branch_parent

    if stay_is_on:
        checkout(branch_origin)

    return "Done"


def revert_all(branch_origin, branch_child, branch_parent, is_add_all, file_paths):
    if checkout(branch_origin):
        return "Failed to check out original branch"


def main():
    branch_child = ""
    pr_title = ""
    pr_body = ""
    file_paths = []
    # get main branch name
    branch_parent = ""
    commit_message = ""
    submodule = 0
    branch_origin = get_current_branch()
    is_add_all = False
    if "--version" in sys.argv:
        print APP_VERSION
        return

    if "-debug" in sys.argv or "-d" in sys.argv:
        global debug_is_on
        debug_is_on = 1

    if "-v" in sys.argv:
        global verbose_is_on
        verbose_is_on = 1

    if "-s" in sys.argv:
        global stay_is_on
        stay_is_on = 1

    if "-b" in sys.argv:
        branch_child = sys.argv[sys.argv.index("-b") + 1]

    if "-sb" in sys.argv:
        branch_child = branch_origin + "_" + sys.argv[sys.argv.index("-sb") + 1]

    if "-pb" in sys.argv:
        pr_body = sys.argv[sys.argv.index("-pb") + 1]

    if "-pt" in sys.argv:
        pr_title = sys.argv[sys.argv.index("-pt") + 1]

    if "-a" in sys.argv:
        key_index = sys.argv.index("-a")
        for p in sys.argv[key_index + 1:]:
            if os.path.exists(p):
                file_paths.append(p)
            else:
                break
    else:
        is_add_all = True

    if "-upto" in sys.argv:
        branch_parent = sys.argv[sys.argv.index("-upto") + 1]

    if "-sub" in sys.argv:
        submodule = 1

    if "-m" in sys.argv:
        commit_message = str(sys.argv[sys.argv.index("-m") + 1])
        re_search = re.search("http[s]?:\/\/.*pivotaltracker.*/(\d*)", commit_message)

        if re_search:
            full_url = re_search.group(0)
            story_id = re_search.group(1)
            global pivotal_tracker_story_id
            pivotal_tracker_story_id = story_id
            global pivotal_tracker_story_url
            pivotal_tracker_story_url = full_url
            commit_message = commit_message.replace(full_url, "")

    if "-l" in sys.argv:
        global local_only_is_on
        local_only_is_on = 1

    if submodule:
        cd(get_submodule_name())
        global is_in_submodule
        is_in_submodule = 1

    if not branch_child and not branch_parent:
        print USEAGE
        return

    if branch_child and not branch_parent:
        print process_from_child(branch_origin, branch_child, is_add_all, file_paths, commit_message, pr_title, pr_body)
    elif branch_parent and not branch_child:
        print process_to_parent(branch_origin, branch_parent, is_add_all, file_paths, commit_message, pr_title, pr_body)
    elif branch_child and branch_parent:
        print process_from_child_to_parent(branch_origin, branch_child, branch_parent, is_add_all, file_paths,
                                           commit_message,
                                           pr_title,
                                           pr_body)
    else:
        return


if __name__ == "__main__":
    main()
