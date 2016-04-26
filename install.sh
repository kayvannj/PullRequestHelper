#!/bin/sh
cp prh.py /usr/local/bin/prh
chmod +x /usr/local/bin/prh
<<<<<<< HEAD
username=$1
token=$2
echo "github.com:
- user: $username
  oauth_token: $token
  protocol: https" > ~/.config/hub
=======
hub --version
>>>>>>> master
