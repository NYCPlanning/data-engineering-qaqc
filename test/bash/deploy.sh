#!/bin/sh

mv $APP_DIR/Dockerfile ./Dockerfile
git add .
git commit -m "deployment commit"
