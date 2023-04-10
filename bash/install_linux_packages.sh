#!/bin/bash
#
# Installs linux packages required for building and testing.
set -e

# Install postgresql client to use psql (postgresql alias)
apt-get update
apt-get --assume-yes install --no-install-recommends postgresql-client gdal-bin
