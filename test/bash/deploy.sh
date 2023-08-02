#!/bin/sh

apk add git-subtree
/bin/setup-ssh

echo "github_sha: $GITHUB_SHA"
echo "rev parse pre-checkout: $(git rev-parse HEAD 2>/dev/null || true)"

git config --global --add safe.directory "$PWD"
git subtree split -P test -b deploy
git checkout deploy

echo "rev parse post-checkout: $(git rev-parse HEAD 2>/dev/null || true)"

git push "$GIT_REMOTE_URL" "deploy:refs/heads/main" --force 

dokku-unlock
