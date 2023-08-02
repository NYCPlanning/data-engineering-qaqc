#!/bin/sh
set -e

mkdir -p ~/.ssh
echo "$ssh_private_key" | tr -d '\r' > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh

ssh_port=22

echo "Generating SSH_HOST_KEY from ssh-keyscan against $dokku_host:$ssh_port"
ssh-keyscan -t rsa "${dokku_host}:22" >> ~/.ssh/known_hosts
chmod 600 "~/.ssh/known_hosts"

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

git_remote_url="ssh://dokku@${dokku_host}:22/${app_name}"

ssh -T "dokku@${dokku_host}"

git push "$git_remote_url" `git subtree split --prefix test` --force
