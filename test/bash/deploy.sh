#!/bin/sh

apk add git-subtree
/bin/setup-ssh
git config --global --add safe.directory /__w/data-engineering-qaqc/data-engineering-qaqc
branch=$(git rev-parse --symbolic-full-name --abbrev-ref HEAD)
git push --force "$GIT_REMOTE_URL" `git subtree split -P test -b $branch`:$APP_REMOTE_BRANCH
ssh -p "$SSH_PORT" "dokku@$DOKKU_HOST" apps:unlock "$APP_NAME"
