#!/bin/sh

apk add git-subtree
/bin/setup-ssh
git config --global --add safe.directory /__w/data-engineering-qaqc/data-engineering-qaqc
git push --force "$GIT_REMOTE_URL" `git subtree split --prefix test`:main
