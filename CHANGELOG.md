v2.2.0

    - Use of editor for commit messages
    - Reading PULL_REQUEST_TEMPLATE and appending it to PR body
    - Asking user to mark story as finished or not
    - Multi story support
    - Cut the Hub dependency and use github api directly using https://developer.github.com/v3/pulls/#create-a-pull-request
    - fix: failed pr if pivotal story doesn't have des #53
    - fix: -a fails with more than 1 path bug #52

v1.0.2

    - Ability to use `-a` in any order with other commands
    - Added integration with Pivotal Tracker
    - Added the `prh_config.py` to hold configurations for user
    - Added `-l --local` for prevent pushing to origin

v1.0.0

    - Initial release
