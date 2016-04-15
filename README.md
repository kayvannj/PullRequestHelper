# PullRequestHelper
A tool to help creating PullRequests on Github easier and automate some of the steps
<br><br>
Assume you are on master branch and you make some changes but you want your changes to be code reviewd or for any other reason you want them in its own pull-request.<br>
With ```prh``` you can create a new branch, add the changed files, commit them, push the branch to origin, and create a pull-request from the new branch to your main branch with just one command:<br>
```prh -b my_new_branch -a path/to/my/first/changed/file path/to/my/second/changed/file```<br>

## Dependency
python 2.7 https://www.python.org/download/releases/2.7/<br>
hub https://github.com/github/hub<br>

## Install
Use install.sh by running
```chmod +x install.sh & ./install.sh```
you are good to go :)

## Options
```-b``` the new branch name for this PR<br>
```-a``` to add changed files to the branch and incloud in the PR
