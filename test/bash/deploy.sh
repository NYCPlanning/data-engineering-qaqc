#!/bin/sh

FILE_DIR=$(dirname "$(readlink -f "$0")")

mv $FILE_DIR/../DockerFile ./DockerFile
