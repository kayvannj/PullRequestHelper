# PullRequestHelper
A tool to help creating PullRequests on Github easier and automate some of the steps
<br><br>
Assume you are on master branch and you make some changes but you want your changes to be code reviewd or for any other reason you want them in its own pull-request.<br>
With `prh` you can create a new branch, add the changed files, commit them, push the branch to origin, and create a pull-request from the new branch to your main branch with just one command:<br>
`prh -b my_new_branch`<br>

You can use prh in two main ways:<br>
1) create a pr from a new branch to current branch<br>
    `prh -b <child_branch_name> [-a <file1_path> <file2_path> ...]`<br>
2) create a pr from current branch to a different branch<br>
    `prh -upto <parent_branch_name>`<br>
<br>
If you are using Pivotal Tracker, you can configure the prh_config.py file with
your project id and api token and then all you need to do is to post a link to
your story in the ```-m``` option along side of your commit message and prh will mark the
story finished and link PR to the story.  
<br>

## Install
Now you can install prh simply by using

```
brew tap kayvannj/prh
brew install prh
```
and you are good to go 🎉

In the first run, `prh` is going to setup some configurations. The setup is also accessable from `prh setup` command

## Update
```
brew unlink prh
brew install prh
```

#### Where to find PivotalTracker API token from?
https://www.pivotaltracker.com/help/articles/api_token/
#### What permissions are needed for GitHub Api token?
Only repo permissions

# Usage
```
usage: prh [-h] [-v] [--verbose [VERBOSE]] [-d [DEBUG]] [-s [STAY_ON]]
           [-b [BRANCH]] [-sb [SUB_BRANCH]] [-pb [PR_BODY]] [-pt [PR_TITLE]]
           [-a [ADD [ADD ...]]] [-e [EMPTY]] [-upto [UPTO]] [-sub [SUB]]
           [-m [MESSAGE]] [-l [LOCAL]]
           [setup]

positional arguments:
  setup                 Setup the pull-request helper

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --verbose [VERBOSE]   run in verbose mode
  -d [DEBUG], --debug [DEBUG]
                        run in debug mode
  -s [STAY_ON], --stay_on [STAY_ON]
                        come back to current branch after all is done
  -b [BRANCH], --branch [BRANCH]
                        Name of child branch
  -sb [SUB_BRANCH], --sub_branch [SUB_BRANCH]
                        Name of child branch appended to the name of parent
                        branch
  -pb [PR_BODY], --pr_body [PR_BODY]
                        Overwrite PullRequest Body text
  -pt [PR_TITLE], --pr_title [PR_TITLE]
                        OverWrite PullRequest Title text
  -a [ADD [ADD ...]], --add [ADD [ADD ...]]
                        Add files with given path, not using the option will
                        add all files
  -e [EMPTY], --empty [EMPTY]
                        not making any commits or adds, just creates the PR
  -upto [UPTO], --upto [UPTO]
                        Name of the parent branch that this PR should point to
  -sub [SUB], --sub [SUB]
  -m [MESSAGE], --message [MESSAGE]
                        Overwrite commit message or add a Pivotal Tracker
                        story link to fetch all the details from the story
  -l [LOCAL], --local [LOCAL]
                        Do not push any changes or create a PR, only create
                        the branch and make the commit
```
