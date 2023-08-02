#!/bin/sh

apk add git-subtree
/bin/setup-ssh
git config --global --add safe.directory /__w/data-engineering-qaqc/data-engineering-qaqc
git subtree split -P test -b deploy
git checkout deploy
git push "$GIT_REMOTE_URL" main --force 
ssh -p "$SSH_PORT" "dokku@$DOKKU_HOST" apps:unlock "$APP_NAME"
