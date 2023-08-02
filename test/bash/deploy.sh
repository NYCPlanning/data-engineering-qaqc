#!/bin/sh

mv $APP_DIR/Dockerfile ./Dockerfile

git config --global --add safe.directory $(PWD)

/bin/setup-ssh

git config --local user.email "action@github.com"
git config --local user.name "GitHub Action"
git add .
git commit -m "deployment commit"

git push "$GIT_REMOTE_URL" "HEAD:refs/heads/$APP_REMOTE_BRANCH" --force 
