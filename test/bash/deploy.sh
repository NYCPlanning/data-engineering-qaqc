#!/bin/sh
set -e

mkdir -p /root/.ssh
echo "$ssh_private_key" | tr -d '\r' > /root/.ssh/id_rsa
chmod 600 /root/.ssh/id_rsa
chmod 700 /root/.ssh

ssh_port=22

log-info "Generating SSH_HOST_KEY from ssh-keyscan against $dokku_host:$ssh_port"
ssh-keyscan -H -p "$ssh_port" "$dokku_host" >>/root/.ssh/known_hosts
chmod 600 "/root/.ssh/known_hosts"

eval "$(ssh-agent -s)"
ssh-add /root/.ssh/id_rsa

git_remote_url="ssh://dokku@${dokku_host}:22/${app_name}"

git subtree push --prefix test --force "$git_remote_url" "$app_remote_branch"
