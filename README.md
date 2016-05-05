# PullRequestHelper
A tool to help creating PullRequests on Github easier and automate some of the steps
<br><br>
Assume you are on master branch and you make some changes but you want your changes to be code reviewd or for any other reason you want them in its own pull-request.<br>
With ```prh``` you can create a new branch, add the changed files, commit them, push the branch to origin, and create a pull-request from the new branch to your main branch with just one command:<br>
```prh -b my_new_branch```<br>

You can use prh in three main ways:<br>
1) create a pr from a new branch to current branch<br>
    ```prh -b <child_branch_name> [-a <file1_path> <file2_path> ...]```<br>
2) create a pr from current branch to a different branch<br>
    ```prh -upto <parent_branch_name>```<br>
3) create a pr from a new branch to a different branch<br>
    ```prh -b <child_branch_name> -upto <parent_branch_name>```<br>
<br>

<br>
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
if `-a`  is not used, prh will add all the changed files using `git add -A`<br>

`-b` the new branch name for this PR<br>
`-upto` the parent branch to make a PR into
`-a`  to add only specified file into the PR<br>
`-m`  to add a comment message<br>
`-pt` to customize the PullRequest Title<br>
`-pb` to append a message to the PullRequest body<br>
`-d`  run in debug mode which means not executing commands and just printing them<br>
`-v`  run in verbose mode<br>
`-h`  show help<br>
`--version` print the version of the app<br>
