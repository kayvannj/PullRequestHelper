#!/bin/sh
cp prh.py /usr/local/bin/prh
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
