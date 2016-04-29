# PullRequestHelper
A tool to help creating PullRequests on Github easier and automate some of the steps
<br><br>
Assume you are on master branch and you make some changes but you want your changes to be code reviewd or for any other reason you want them in its own pull-request.<br>
With ```prh``` you can create a new branch, add the changed files, commit them, push the branch to origin, and create a pull-request from the new branch to your main branch with just one command:<br>
```prh -b my_new_branch```<br>

You can use prh in two main ways:
1) when you are in a parent branch and want to make a PR that contains your changes to the branch you are at
prh -b <child_branch_name> [-a <file1_path> <file2_path> ...]
2) when you are in a child branch and want to just make a PR to a specific parent branch
prh -upto <parent_branch_name>

if -a  is not used, prh will add all the changed files using 'git add -A'

-a  to add only specified file into the PR
-m  to add a comment message
-pt to customize the PullRequest Title
-pb to append a message to the PullRequest body
-d  run in debug mode which means not executing commands and just printing them
-v  run in verbose mode
-h  show help
--version print the version of the app

## Dependency
python 2.7 https://www.python.org/download/releases/2.7/<br>
hub https://github.com/github/hub<br>

## Install
```bash
git clone git@github.com:kayvannj/PullRequestHelper.git
cd PullRequestHelper
chmod +x install.sh
sudo ./install.sh <github-username> <github-token>
```
you are good to go :)

## Options
```-b``` the new branch name for this PR<br>
