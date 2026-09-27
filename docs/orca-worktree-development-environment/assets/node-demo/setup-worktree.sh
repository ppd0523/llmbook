#!/bin/sh
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
. "$NVM_DIR/nvm.sh"
set -eu
nvm use 24
npm ci
