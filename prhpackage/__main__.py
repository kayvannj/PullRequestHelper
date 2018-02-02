#!/usr/bin/env python
import argparse
import json
import os
import re
import subprocess
import sys
import urllib
import json

SLACK_INTEGRATION_URL_KEY = "SLACK_INTEGRATION_URL"
DEFAULT_PULL_REQUEST_BODY_KEY = "DEFAULT_PULL_REQUEST_BODY"
DEFAULT_COMMIT_MESSAGE_KEY = "DEFAULT_COMMIT_MESSAGE"
PIVOTAL_API_TOKEN_KEY = "PIVOTAL_TRACKER_API_TOKEN"
GITHUB_API_TOKEN_KEY = "GITHUB_API_TOKEN"
EMPTY_CONFIG_CONTENT_DIC = {GITHUB_API_TOKEN_KEY: "", PIVOTAL_API_TOKEN_KEY: "",
                            DEFAULT_COMMIT_MESSAGE_KEY: "Commit", DEFAULT_PULL_REQUEST_BODY_KEY: "",
                            SLACK_INTEGRATION_URL_KEY: ""}

REPO_PATH = "/Users/kayvan/Developer/android"  # for debug purposes
PRH_CONFIG_PATH = "/usr/local/etc"
# PRH_CONFIG_PATH = "config_file_path"

PRH_CONFIG_FILE_NAME = "/prh_config"
GIT_CONFIG_PATH = "/config"
GIT_FILE_PATH = ".git"
APP_VERSION = "2.4.0"

DEFAULT_COMMIT_MESSAGE = ""  # prh_config.DEFAULT_COMMIT_MESSAGE
DEFAULT_PR_BODY = ""  # prh_config.DEFAULT_PULL_REQUEST_BODY
NO_ERROR = 0
debug_is_on = 1
verbose_is_on = 1
local_only_is_on = 0
stay_is_on = 0
is_in_submodule = 0
repo_path = ""
pivotal_tracker_api_endpoint = "https://www.pivotaltracker.com/services/v5"
story = ""


class Service:
    import requests

    def __init__(self, token=False, header={}):
        self.token = token
        if token:
            self.header = {"X-TrackerToken": self.token}
        else:
            self.header = header

    def get(self, api):
        response = self.requests.get(api, headers=self.header)
        log("--> %s" % api)
        log("<-- %s\n" % response.json())
        return response

    def post(self, api, data):
        response = self.requests.post(api, data=data, headers=self.header)
        log("--> %s" % api)
        log("<-- %s\n" % response.json())
        return response

    def put(self, api, data):
        response = self.requests.put(api, data=data, headers=self.header)
        log("--> %s" % api)
        log("<-- %s\n" % response.json())
        return response

    @staticmethod
    def log(message):
        if verbose_is_on:
            print message


def storiesResponseToMarkdownText(arrayOfDicts_storyArray, arrayofStrings_orderedFieldNames):
    # Treating each dictionary in our json array as representing a story,
    # gather all of the stories' relevant values
    arrayOfArrayOfString_allStories = []

    # Find each story's relevant values and add them to `allStories`
    for dict_story in arrayOfDicts_storyArray:
        # initialize empty values array
        arrayOfStrings_currentStoryOrderedFieldValues = []

        ## add all values we care about to the field values array
        for string_fieldName in arrayofStrings_orderedFieldNames:

            # if this story json has a value corresponding to `fieldName`,
            # add that value to `currentStoryOrderedFieldValues`.
            if string_fieldName in dict_story:

                value = dict_story[string_fieldName]
                if isinstance(value, int):
                    value = str(value)
                value = value.replace('\n', " ")
                # encode = str(name_).encode("utf-8")
                arrayOfStrings_currentStoryOrderedFieldValues.append(
                    value
                )
            # otherwise, add an empty string to `currentStoryOrderedFieldValues`.
            else:
                arrayOfStrings_currentStoryOrderedFieldValues.append("")

        # add the current story's field relevant values to `allStories` array
        arrayOfArrayOfString_allStories.append(arrayOfStrings_currentStoryOrderedFieldValues)

    # construct the markdown table given our column names and our rows:
    return composeMarkdownTable(arrayofStrings_orderedFieldNames, arrayOfArrayOfString_allStories)


# Given the column names, and the rows (array of string arrays),
# constructs a string representing a markdown table.
def composeMarkdownTable(arrayOfStrings_columnNames, arrayOfArrayOfString_rows):
    arrayOfArrayOfString_markdownTable = []

    # add column names to the table
    arrayOfArrayOfString_markdownTable.append(
        stringArrayToMarkdownTableRow(arrayOfStrings_columnNames)
    )

    # add post-column separators to the table
    arrayOfArrayOfString_markdownTable.append(
        stringArrayToMarkdownTableRow(
            ["--"] * len(arrayOfStrings_columnNames)
        )
    )

    # add the actual rows
    for arrayOfString_row in arrayOfArrayOfString_rows:
        arrayOfArrayOfString_markdownTable.append(
            stringArrayToMarkdownTableRow(arrayOfString_row)
        )

    return "\n".join(arrayOfArrayOfString_markdownTable)


# A markdown table row is a single unbroken string,
# where each column is separated by a " | " string.
def stringArrayToMarkdownTableRow(stringArray):
    string_separatorString = " | "
    return string_separatorString.join(stringArray)


def log(message):
    if verbose_is_on:
        print message


def get_pivotal_story(story_id):
    api = "{}/stories/{}".format(pivotal_tracker_api_endpoint, story_id)
    resp = Service(read_from_config_file()[PIVOTAL_API_TOKEN_KEY]).get(api)
    story = resp.json()
    return story


# /projects/{project_id}/labels/{label_id}
def get_pivotal_label_name(project_id, label_id):
    api = "{}/projects/{project_id}/labels/{label_id}".format(pivotal_tracker_api_endpoint, project_id, label_id)
    resp = Service(read_from_config_file()[PIVOTAL_API_TOKEN_KEY]).get(api)
    story = resp.json()
    return story["name"]


def get_pivotal_stories(project_id, labels, columns):
    global story
    if story:
        return story

    filter_string = " and ".join(["label:{}".format(l) for l in labels])

    urlencode = urllib.urlencode(
        {'filter': filter_string, 'fields': ",".join(columns)})
    api = "{}/projects/{}/stories?{}".format(pivotal_tracker_api_endpoint, project_id, urlencode)
    resp = Service(read_from_config_file()[PIVOTAL_API_TOKEN_KEY]).get(api)

    return resp.json()


def get_pivotal_story_tasks(project_id, story_id):
    """
    [
      {
        "kind": "task",
        "id": 52555419,
        "story_id": 140104217,
        "description": "with some tasks",
        "complete": false,
        "position": 1,
        "created_at": "2017-02-16T23:52:05Z",
        "updated_at": "2017-02-16T23:52:05Z"
      },
      {
        "kind": "task",
        "id": 52555421,
        "story_id": 140104217,
        "description": "task 2",
        "complete": false,
        "position": 2,
        "created_at": "2017-02-16T23:52:09Z",
        "updated_at": "2017-02-16T23:52:09Z"
      }
    ]
    """
    api = "{}/projects/{}/stories/{}/tasks".format(pivotal_tracker_api_endpoint, project_id, story_id)
    resp = Service(read_from_config_file()[PIVOTAL_API_TOKEN_KEY]).get(api)
    return resp.json()


def mark_pivotal_story_finished(project_id, story_id):
    api = "{}/projects/{}/stories/{}".format(pivotal_tracker_api_endpoint, project_id, story_id)
    resp = Service(read_from_config_file()[PIVOTAL_API_TOKEN_KEY]).put(api, {"current_state": "finished"})
    return resp.json()


def post_pivotal_comment(project_id, story_id, text):
    api = "{}/projects/{}/stories/{}/comments".format(pivotal_tracker_api_endpoint, project_id, story_id)
    resp = Service(read_from_config_file()[PIVOTAL_API_TOKEN_KEY]).post(api, {"text": text})
    return resp.json()


class ReleaseConfig:

    def __init__(self, tag_name="", target_commitish="", name="", body="", draft=False, prerelease=False):
        self.tag_name = tag_name
        self.target_commitish = target_commitish
        self.name = name
        self.body = body
        self.draft = draft
        self.prerelease = prerelease


# POST /repos/:owner/:repo/releases
def post_github_release(owner, repo, release_config):
    github = "https://api.github.com"
    api = "{}/repos/{}/{}/releases".format(github, owner, repo)

    data = {
        "tag_name": release_config.tag_name,
        "target_commitish": release_config.target_commitish,
        "name": release_config.name,
        "body": release_config.body,
        "draft": release_config.draft,
        "prerelease": release_config.prerelease
    }
    res = github_api_post(api, data)
    return res


def get_pivotal_project_id(story_id):
    global story
    if story:
        return story["project_id"]

    api = "{}/stories/{}".format(pivotal_tracker_api_endpoint, story_id)
    resp = Service(read_from_config_file()[PIVOTAL_API_TOKEN_KEY]).get(api)
    story = resp.json()
    return story["project_id"]


def finish_and_post_message_to_pivotal(story_id, message):
    project_id = get_pivotal_project_id(story_id)
    if not read_from_config_file()[PIVOTAL_API_TOKEN_KEY]:
        return 1
    if not mark_pivotal_story_finished(project_id, story_id):
        return 1
    if not post_pivotal_comment(project_id, story_id, message):
        return 1
    return NO_ERROR


def run_command_str(command, output=0):
    command_list = str.split(command)
    run_command(command_list, output)


def run_command(command, output=0):
    """
    run the given command
    :param command:
    :param output:
    :return: 0 if no error occurs or the error code

    >>> run_command(["echo","hello world"],1)
    'hello world\\n'
    >>> run_command(["echo","hello world"])
    0
    >>> run_command(["ls","buchofjunck"],1)
    1
    >>> run_command(["ls","buchofjunck"],0)
    1
    """
    if debug_is_on:
        print_command(command)
        return NO_ERROR
    else:
        if verbose_is_on:
            print command
        try:
            if output:
                run_output = subprocess.check_output(command)
            else:
                run_output = subprocess.check_call(command)

            log("\nOUTPUT:\t" + str(run_output))
            return run_output
        except subprocess.CalledProcessError as e:
            return e.returncode


def print_command(command):
    print get_head() + " >>> " + reduce(lambda x, y: x + " " + y, command)


def checkout(branch_name):
    command = ["git", "checkout", branch_name]
    run_command(command)


def add_files(file_paths):
    command = ["git", "add"] + file_paths
    return run_command(command, 1)


def add_all():
    command = ["git", "add", "-A"]
    return run_command(command, 1)


def get_head(current_path=""):
    # read the head from git dir
    with open(get_repo_git_dir(current_path) + "/HEAD") as f:
        ref = f.read()
        keyword = "refs/heads/"
        i = ref.rfind(keyword)
        return ref[i + len(keyword):].strip()


def get_repo_git_dir(current_path=""):
    """
    >>> get_repo_git_dir("/Users/kayvan/Documents/sources/Dox Source/dxCore")
    '../.git/modules/dxCore'
    >>> get_repo_git_dir("/Users/kayvan/Documents/sources/Dox Source")
    '/Users/kayvan/Documents/sources/Dox Source/.git'
    """
    if current_path and not current_path.endswith("/"):
        current_path += "/"
    git_dir_path = current_path + GIT_FILE_PATH
    # in the case of being in a submodule folder
    if os.path.isfile(git_dir_path):
        with open(git_dir_path) as f:
            line = f.readline()
            # gitdir: ../.git/modules/dxCore
            git_dir_path = line.split(":")[1].strip()
    log("git dir path = " + git_dir_path)
    return git_dir_path


def get_submodule_name():
    command = ["git", "submodule"]
    output = run_command(command, True)
    return output.split(" ")[1]


def get_status():
    return subprocess.check_output(["git", "status"])


def launch_browser(url):
    command = ["open", url if url else ""]
    run_command(command)


def cd(path):
    command = ["cd", path]
    run_command(command)


def ask_user(question):
    answer = raw_input(question)
    return str.lower(answer) == 'y'


def add_changes(is_add_all, file_paths):
    if is_add_all:
        error = add_all()
    elif file_paths:
        error = add_files(file_paths)
    else:
        error = "Failed to add files"

    return error


def delete_branch(branch_name):
    command = ["git", "branch", "-D", branch_name]
    res = run_command(command, 1)
    return res


def git_stash():
    command = ["git", "stash"]
    res = run_command(command)
    return res


def git_stash_apply():
    command = ["git", "stash", "apply"]
    res = run_command(command, 1)
    return res


def git_reset_head():
    command = ["git", "reset", "HEAD"]
    res = run_command(command)
    return res


def create_branch(branch_name):
    command = ["git", "checkout", "-q", "-b", branch_name]
    res = run_command(command, 0)
    if res == 128:
        answer = raw_input(">>> Branch '%s' already exists, would you like to check it out (y/n)?" % branch_name)
        if str.lower(answer) == 'y':
            add_all()
            git_stash()
            checkout(branch_name)
            error = git_stash_apply()
            git_reset_head()
            if error:
                return "Error applying changes"

            if ask_user(">>> Proceed with commiting and creating PR (y/n)?"):
                return "Aborted"
        else:
            return "Failed to create the new branch"
    else:
        return res


def has_git_editor_set():
    command = ["git", "config", "--get", "core.editor"]
    return run_command(command, 1)


def commit(user_input):
    if not user_input.commit_message:
        for story_id in user_input.tracker_ids:
            if story_id:
                story_json = get_pivotal_story(story_id)
                user_input.commit_message = story_json["name"]
            else:
                user_input = DEFAULT_COMMIT_MESSAGE

    if has_git_editor_set():
        command = ["git", "commit", "-e", "-m", str(user_input.commit_message)]
    else:
        command = ["git", "commit", "-m", str(user_input.commit_message)]
    res = run_command(command)
    if res:
        return "Failed to commit changes"


def push(branch_name):
    if local_only_is_on:
        return NO_ERROR

    command = ["git", "push", "--set-upstream", "origin", branch_name]
    res = run_command(command)
    if res:
        return "Failed to push the commit to origin"


def find_existing_pr(owner, repo, head, base):
    api = "https://api.github.com/repos/{}/{}/pulls".format(owner, repo)
    res = github_api_get(api)
    if res.status_code < 300:
        matching_pr_list = [a for a in res.json()[:] if a["head"]["ref"] == head and a["base"]["ref"] == base]
        if matching_pr_list:
            return matching_pr_list[0]["html_url"]


def read_pr_template():
    pr_template_file_name = "PULL_REQUEST_TEMPLATE.md"
    pr_template_path = ".github/" + pr_template_file_name

    file_to_read = ""
    if os.path.isfile(pr_template_path):
        file_to_read = pr_template_path
    elif os.path.isfile(pr_template_file_name):
        file_to_read = pr_template_file_name

    if file_to_read:
        with open(file_to_read, mode='r') as f:
            return f.read()


def create_pull_request(from_branch, to_branch, user_input):
    if local_only_is_on:
        return NO_ERROR

    if not user_input.pr_title:
        pr_title = get_head().replace("_", " ")
    if not user_input.pr_body:
        pr_body = DEFAULT_PR_BODY
    else:
        pr_body = user_input.pr_body + "\n" + DEFAULT_PR_BODY

    # Add description of stories to the pr_body
    for i in range(len(user_input.tracker_urls)):
        story = get_pivotal_story(user_input.tracker_ids[i])
        description = name = ""
        if "description" in story:
            description = story["description"]
        if "name" in story:
            name = story["name"]
        pr_body = pr_body + "\n\n**Story:** [" + name + "](" + user_input.tracker_urls[i] + ")\n" + description

    pr_template = read_pr_template()
    if pr_template:
        log("Reading from PR-Template")
        pr_body = pr_body + "\n" + pr_template

    setup_config_dic = read_from_setup_file()
    owner = setup_config_dic["owner"]
    repo = setup_config_dic["repo"]
    if not owner:
        print "run prh setup first"
        return 1

    # https://developer.github.com/v3/pulls/#create-a-pull-request
    github = "https://api.github.com"
    api = "{}/repos/{}/{}/pulls".format(github, owner, repo)
    data = {
        "title": pr_title,
        "body": pr_body,
        "head": from_branch,
        "base": to_branch
    }
    res = github_api_post(api, data)

    if res.status_code == 201:
        pr_url = res.json()["html_url"]
        print "PR created: {}".format(pr_url)
        if pr_url and str(pr_url)[:4] == "http":
            for i in range(len(user_input.tracker_ids)):
                if user_input.tracker_ids[i]:
                    project_id = get_pivotal_project_id(user_input.tracker_ids[i])
                    if post_pivotal_comment(project_id, user_input.tracker_ids[i], "PR: " + pr_url):
                        print "error with pivotal, commenting pr link"

                    if ask_user("Mark story with id=" + user_input.tracker_ids[i] + " as finished?(y/n)"):
                        if mark_pivotal_story_finished(project_id, user_input.tracker_ids[i]):
                            print "error with pivotal, marking story as finished"
            launch_browser(pr_url)
        return NO_ERROR
    else:
        existing_pr_url = find_existing_pr(owner, repo, from_branch, to_branch)
        if existing_pr_url:
            print existing_pr_url
            launch_browser(existing_pr_url)
            return NO_ERROR

        for e in res.json()["errors"]:
            print "Error:", e["message"]
        return "Failed to create pull-request from " + from_branch + " to " + to_branch


def github_api_post(api, data):
    headers = {"Authorization": "token " + read_from_config_file()[GITHUB_API_TOKEN_KEY]}
    response = Service(header=headers).post(api, data=json.dumps(data))
    log("--> %s" % api)
    log("<-- %s\n" % response.json())
    return response


def github_api_get(api):
    headers = {"Authorization": "token " + read_from_config_file()[GITHUB_API_TOKEN_KEY]}
    response = Service(header=headers).get(api)
    log("--> %s" % api)
    log("<-- %s\n" % response.json())
    return response


def verify_file_paths(file_paths):
    # verify all the provided file paths are valid
    if file_paths:
        for p in file_paths:
            if not os.path.exists(p):
                print "Make sure %s exists" % p
                return 1


def verify_parent_in_origin(origin):
    if not os.path.exists(get_repo_git_dir() + "/refs/remotes/origin/%s" % origin):
        print "could not find the parent branch '%s' in your local remote refs, in case of error, make sure you have " \
              "pushed the parent branch" % origin
        return 0


def terminate_on_error(func, args):
    error = func(args)
    if error:
        return error


def parse_commit_message(raw_commit_message):
    # re_search = re.search("http[s]?:\/\/.*pivotaltracker.*/(\d*)", commit_message)
    commit_message = raw_commit_message
    re_res = re.findall("http[s]?:\/\/.*pivotaltracker.*\/(\d*)", commit_message)
    # "https://www.pivotaltracker.com/story/show/140176051 https://www.pivotaltracker.com/story/show/139604723"
    full_urls = story_ids = []
    if re_res:
        for url in re_res:
            full_urls += url[0]
            story_ids += url[1]
            commit_message = commit_message.replace(url[0], "")
    return commit_message, full_urls, story_ids
    # if re_search:
    #     full_url = re_search.group(0)
    #     story_id = re_search.group(1)
    #     global pivotal_tracker_story_id
    #     pivotal_tracker_story_id = story_id
    #     global pivotal_tracker_story_url
    #     pivotal_tracker_story_url = full_url
    #     commit_message = commit_message.replace(full_url, "")


def parse_commit_message(commit_message, full_urls, story_ids):
    """
    Parse the user entered commit message and extract any known urls from it
    :param commit_message:
    :param full_urls:
    :param story_ids:
    :return: (commit_message, full_urls, story_ids)
    """
    re_search = re.search("http[s]?:\/\/\S*pivotaltracker.com\S*\/(\d*)", commit_message)
    if re_search:
        full_urls += [re_search.group(0)]
        story_ids += [re_search.group(1)]
        commit_message = commit_message.replace(re_search.group(0), "")
    else:
        return commit_message, full_urls, story_ids
    return parse_commit_message(commit_message, full_urls, story_ids)


def process_from_child(origin, new, add_all, just_pr, file_paths, user_input):
    return create_branch(new) \
           or (not just_pr and add_changes(add_all, file_paths)) \
           or (not just_pr and commit(user_input)) \
           or push(new) \
           or create_pull_request(new, origin, user_input) \
           or (stay_is_on and checkout(origin)) \
           or "Done"


def process_to_parent(origin, parent, add_all, just_pr, file_paths, user_input):
    return (not just_pr and add_changes(add_all, file_paths)) \
           or (not just_pr and commit(user_input)) \
           or push(origin) \
           or create_pull_request(origin, parent, user_input) \
           or "Done"


def revert_all(branch_origin, branch_child, branch_parent, is_add_all, file_paths):
    if checkout(branch_origin):
        return "Failed to check out original branch"


class UserInput:
    def __init__(self, commit_message="", tracker_urls=[], tracker_ids=[], pr_title="", pr_body=""):
        self.pr_title = pr_title
        self.pr_body = pr_body
        self.tracker_ids = tracker_ids
        self.tracker_urls = tracker_urls
        self.commit_message = commit_message


def release(release_story_id, owner, repo, tag_name):
    if not release_story_id:
        print("Have to provide a pivotal tracker label for this release")
        return

    release_story = get_pivotal_story(release_story_id)
    release_labels = [l["name"] for l in release_story["labels"]]
    release_name = release_story["name"]
    release_project_id = release_story["project_id"]

    #     fetch all the stories with given label
    columns = ["id", "name", "description", "story_type", "url"]
    stories = get_pivotal_stories(release_project_id, release_labels, columns)
    release_body = storiesResponseToMarkdownText(stories, columns)

    post_github_release(owner, repo,
                        ReleaseConfig(tag_name=tag_name, target_commitish="master", name="v%s" % release_name,
                                      body=release_body))


def parse_args(args):
    # there is a syntax error in arguments
    if not args:
        return False

    if args.release:
        re_res = re.findall("http[s]?:\/\/.*pivotaltracker.*\/(\d*)", args.release)

        if args.tag and args.repo and args.owner:
            release(re_res[0], owner=args.owner, repo=args.repo, tag_name=args.tag)
        else:
            print("parameter is missing, have to provide all of: owner, repo, tag")
        return False

    file_paths = []
    branch_child = branch_parent = pr_title = pr_body = is_add_all = is_just_pr = commit_message = ""
    need_to_confirm_empty = need_to_confirm_add_all = ""
    # get main branch name
    branch_origin = get_head()
    working_path = ""
    user_input = UserInput()

    if args.setup:
        setup()
        return

    if args.path:
        working_path = args.path
        if working_path[-1] != "/":
            working_path += "/"

    if args.debug:
        global debug_is_on
        debug_is_on = 1

    if args.verbose:
        global verbose_is_on
        verbose_is_on = 1

    if args.stay_on:
        global stay_is_on
        stay_is_on = 1

    if args.branch:
        branch_child = args.branch

    if args.sub_branch:
        branch_child = branch_origin + "_" + args.sub_branch

    if args.pr_body:
        user_input.pr_body = args.pr_body

    if args.pr_title:
        user_input.pr_title = args.pr_title

    if args.add:
        # -a exists
        for p in args.add:
            file_paths.append(working_path + p)

        # no path to add
        if not file_paths:
            need_to_confirm_empty = 1
    else:
        # no -a
        need_to_confirm_add_all = 1

    if args.empty:
        is_just_pr = True
        is_add_all = False
        need_to_confirm_add_all = False

    if args.upto:
        branch_parent = args.upto

    if args.sub:
        setup_file = read_from_setup_file()
        for pair in setup_file["submodules"]:
            if os.path.exists(pair):
                cd(pair)
                submodule_args = args
                submodule_args["sub"] = 0
                parse_args(submodule_args)

    if args.message:
        commit_message, full_urls, story_ids = parse_commit_message(args.message, [], [])
        user_input.tracker_urls = full_urls
        user_input.tracker_ids = story_ids
        user_input.commit_message = commit_message

    if args.local:
        global local_only_is_on
        local_only_is_on = 1

    # Verification

    error = verify_file_paths(file_paths)
    if error:
        return error

    error = verify_parent_in_origin(branch_parent if branch_parent else branch_origin)
    if error:
        return error

    if need_to_confirm_add_all:
        list_of_changes = str(run_command(["git", "add", "-A", "-n"], 1)).strip()
        if not list_of_changes:
            # list of changes is empty
            need_to_confirm_empty = True
        else:
            print("\n" + list_of_changes)
            if ask_user(">>> Would you like to apply above changes (y/n)? "):
                is_add_all = True
            else:
                return "Either add files using -a or add all the changes"

    if need_to_confirm_empty:
        if ask_user(">>> No file has been added, would you like to continue creating PR (y/n)? "):
            is_just_pr = True
        else:
            return "Either add files using -a or add all the changes"

    if branch_child and not branch_parent:
        print process_from_child(branch_origin, branch_child, is_add_all, is_just_pr, file_paths, user_input)
    elif branch_parent and not branch_child:
        print process_to_parent(branch_origin, branch_parent, is_add_all, is_just_pr, file_paths, user_input)
    else:
        return


def missing_global_config():
    prh_config = read_from_config_file()
    return not prh_config[GITHUB_API_TOKEN_KEY]


def missing_local_config():
    setup_config = read_from_setup_file()
    return not setup_config


def setup():
    print "Running setup"

    prh_config = read_from_config_file()
    github_token = prh_config[GITHUB_API_TOKEN_KEY]
    pivotal_token = prh_config[PIVOTAL_API_TOKEN_KEY]
    # global setup
    config_changed = 0
    if not github_token:
        github_token = raw_input("Please enter your Github API token: ")
        if github_token:
            config_changed = 1

    if not pivotal_token:
        pivotal_token = raw_input("Please enter your PivotalTracker API token: ")
        if pivotal_token:
            config_changed = 1

    if config_changed:
        write_to_config_file({GITHUB_API_TOKEN_KEY: github_token, PIVOTAL_API_TOKEN_KEY: pivotal_token,
                              DEFAULT_COMMIT_MESSAGE_KEY: "Commit", DEFAULT_PULL_REQUEST_BODY_KEY: "",
                              SLACK_INTEGRATION_URL_KEY: ""})
    # local setup

    git_dir = get_repo_git_dir()
    if os.path.isdir(git_dir):
        with open(git_dir + GIT_CONFIG_PATH) as git_config:
            config_string = git_config.read()
            remotes = re.findall('\[remote "(.*)"\].*\n.*url = (git.*\.git).*', config_string)
            # submodules = re.findall('\[submodule "(.*)"\]\n.*url = (.*).*', config_string)
    else:
        print "You should run prh from a git repository directory"
        return

    if not remotes:
        print "Could not find origin url in the .git/config file.\nYour origin URL should be in form of git.*\.git"
        return

    write_to_setup_file(remotes)


def run_popen(command):
    popen = subprocess.Popen(command, stdin=subprocess.PIPE, shell=True, stdout=subprocess.PIPE)
    with popen.stdout as output:
        return output.readline().replace("\n", "")
    return '.'


def get_owner(git_url):
    """
    >>> get_owner("git@github.com:doximity/Android.git")
    'doximity'
    """
    return git_url.split(":")[-1].split("/")[0]


def get_repo(git_url):
    """
    >>> get_repo("git@github.com:doximity/Android.git")
    'Android'
    """
    return git_url.split(":")[-1].split("/")[1].split(".")[0]


def write_to_setup_file(remotes):
    # git@github.com:doximity/Android.git
    index = 1
    selected_remote_index = '1'
    if len(remotes) > 2:
        for i, j in remotes:
            print "%d : %s = %s" % (index, i, j)
            index += 1
        selected_remote_index = raw_input("Which remote to use (enter line number)?")

    owner = get_owner(remotes[int(selected_remote_index) - 1][1])
    repo = get_repo(remotes[int(selected_remote_index) - 1][1])

    submodules_dic = {}
    # for submodule in submodules:
    #     submodules_dic[submodule[0]] = submodule[1]

    # command = ["git rev-parse --show-toplevel"]
    # repo_root_path = run_popen(command)
    out = json.dumps({"owner": owner, "repo": repo, "submodules": submodules_dic})
    with open(repo_path + '/.prh', 'w') as f:
        f.write(out)


def read_from_setup_file():
    """
    Read the REPO Scoped config file of PRH
    :return:
    """
    if os.path.exists(repo_path + '/.prh'):
        with open(repo_path + '/.prh', 'r') as f:
            return json.load(f)


def parse_arguments():
    parser = argparse.ArgumentParser(version=APP_VERSION)
    parser.add_argument("--verbose", help="run in verbose mode", const=True, nargs='?')
    parser.add_argument("-d", "--debug", help="run in debug mode", const=True, nargs='?')
    parser.add_argument("-s", "--stay_on", help="come back to current branch after all is done", const=True, nargs='?')
    parser.add_argument("-b", "--branch", help="Name of child branch", nargs='?')
    parser.add_argument("-sb", "--sub_branch", help="Name of child branch appended to the name of parent branch",
                        nargs='?')
    parser.add_argument("-pb", "--pr_body", help="Overwrite PullRequest Body text", nargs='?')
    parser.add_argument("-pt", "--pr_title", help="OverWrite PullRequest Title text", nargs='?')
    parser.add_argument("-a", "--add",
                        help="Add files with given path, not using the option will add all files",
                        nargs='*')
    parser.add_argument("-e", "--empty",
                        help="not making any commits or adds, just creates the PR",
                        const=True,
                        nargs='?')
    parser.add_argument("-upto", "--upto", help="Name of the parent branch that this PR should point to", nargs='?')
    parser.add_argument("-sub", "--sub", help="WIP", const=True, nargs='?')
    parser.add_argument("-m", "--message",
                        help="Overwrite commit message or add a Pivotal Tracker "
                             "story link to fetch all the details from the story",
                        nargs='?')
    parser.add_argument("-l", "--local",
                        help="Do not push any changes or create a PR, only create the branch and make the commit",
                        const=True, nargs='?')
    parser.add_argument("setup", help="Setup the pull-request helper", const=True, nargs='?')
    parser.add_argument("release",
                        help="URL of the release story on Pivotal tracker that has matching label to all the stories "
                             "in that release. For example, the release story might have '1.2.3' as a label, then all "
                             "the stories that come up from searching the '1.2.3' lable will be included in the "
                             "release",
                        const=True, nargs='?')
    parser.add_argument("-p", "--path")
    parser.add_argument("--owner", help="Repository owner. ex: for doximity/android the owner is doximity")
    parser.add_argument("--repo", help="Repository name. ex: for doximity/android the owner is android")
    parser.add_argument("--tag", help="tag name for the release")

    args = parser.parse_args()

    if not args.branch and not args.upto and not args.sub_branch and not args.setup:
        parser.print_help()
        return False

    return args


def write_to_config_file(dic, to_path=PRH_CONFIG_PATH + PRH_CONFIG_FILE_NAME + ".json"):
    """
    write to the user scoped config file for PRH
    :return:
    """
    with open(to_path, mode='w') as f:
        f.write("{")
        for i in range(len(dic) - 1):
            f.write('"%s":"%s",' % (dic.keys()[i], dic.values()[i]))
        f.write('"%s":"%s"' % (dic.keys()[-1], dic.values()[-1]))
        f.write("}")


def read_from_config_file(file_path=PRH_CONFIG_PATH + PRH_CONFIG_FILE_NAME + ".json"):
    """
    read from the user scoped config file for PRH
    """
    config_path = file_path
    if os.path.isfile(config_path):
        with open(config_path, mode='r') as f:
            return json.load(f)
    else:
        write_to_config_file({
            GITHUB_API_TOKEN_KEY: "",
            PIVOTAL_API_TOKEN_KEY: "",
            DEFAULT_COMMIT_MESSAGE_KEY: "Commit",
            DEFAULT_PULL_REQUEST_BODY_KEY: "",
            SLACK_INTEGRATION_URL_KEY: ""
        })
        return read_from_config_file()


def migrate_config_file(from_path=PRH_CONFIG_PATH + PRH_CONFIG_FILE_NAME + ".py",
                        to_path=PRH_CONFIG_PATH + PRH_CONFIG_FILE_NAME + ".json"):
    old_config_path = from_path
    old_dic = {}
    if os.path.isfile(old_config_path):
        with open(old_config_path, "r") as conf:
            for line in conf.readlines():
                key, value = line.split("=")
                old_dic[key.strip()] = value.strip('"  \n')
        write_to_config_file(old_dic, to_path)
        os.remove(old_config_path)


def main():
    migrate_config_file()

    if REPO_PATH:
        global repo_path
        repo_path = REPO_PATH
    else:
        # get current working dir
        # global repo_path
        repo_path = os.getcwd()

    if missing_global_config() or missing_local_config():
        setup()

    sys.exit(parse_args(parse_arguments()))


if __name__ == "__main__":
    main()
