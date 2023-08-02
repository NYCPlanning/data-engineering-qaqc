#!/bin/sh

apk add git-subtree
/bin/setup-ssh
git config --global --add safe.directory "$PWD"
git subtree split -P test -b deploy
git push "$GIT_REMOTE_URL" "deploy:refs/heads/main" --force 

dokku-unlock
