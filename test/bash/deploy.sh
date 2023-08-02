#!/bin/sh

apk add git-subtree
/bin/setup-ssh
git config --global --add safe.directory /__w/data-engineering-qaqc/data-engineering-qaqc
git subtree push --prefix test "$GIT_REMOTE_URL" main
