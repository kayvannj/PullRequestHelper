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

####Where to find PivotalTracker API token from? https://www.pivotaltracker.com/help/articles/api_token/
####What permissions are needed for GitHub Api token? 
![permissions](\permissions.png)

## Usage
usage: prh [-h] [-v] [--verbose [VERBOSE]] [-d [DEBUG]] [-s [STAY_ON]]<br>
           [-b [BRANCH]] [-sb [SUB_BRANCH]] [-pb [PR_BODY]] [-pt [PR_TITLE]]<br>
           [-a [ADD [ADD ...]]] [-e [EMPTY]] [-upto [UPTO]] [-sub [SUB]]<br>
           [-m [MESSAGE]] [-l [LOCAL]]<br>
           [setup]<br>
