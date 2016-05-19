#!/bin/sh
cp prh.py /usr/local/bin/prh
if [ ! -f prh_config.py ]; then
echo "DEFAULT_COMMIT_MESSAGE = \"Commit\"
DEFAULT_PULL_REQUEST_BODY = \"\" # optional
PIVOTAL_TRACKER_API_TOKEN = \"\" # optional
PIVOTAL_TRACKER_PROJECT_ID = \"\" # optional" > prh_config.py
echo "
please modify the prh_config.py and run the install again
"
fi
cp prh_config.py /usr/local/bin/prh_config.py
chmod +x /usr/local/bin/prh
username=$1
token=$2
if [[ ! -z $1 ]]; then
  echo "github.com:
  - user: $username
    oauth_token: $token
    protocol: https" > ~/.config/hub
  else
    echo "
------------------------------------
You have not provided username and token,
Make sure ~/.config/hub contains your credentials.

You can use:  install.sh <username> <token>
to create the file with correct credentials
------------------------------------

prh install was succesful
"
fi
