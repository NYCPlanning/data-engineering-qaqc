#!/bin/sh

apk add git-subtree
/bin/setup-ssh
git config --global --add safe.directory /__w/data-engineering-qaqc/data-engineering-qaqc
git push "$GIT_REMOTE_URL" `git subtree split --prefix test` --force
