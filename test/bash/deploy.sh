#!/bin/sh

mv $APP_DIR/Dockerfile ./Dockerfile
git config --local user.email "action@github.com"
git config --local user.name "GitHub Action"
git add .
git commit -m "deployment commit"
