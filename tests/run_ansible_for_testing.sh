#!/usr/bin/env bash

set -euxo pipefail

ANSIBLE_DIR="$1" ; shift
source "$ANSIBLE_DIR/hacking/env-setup"
"$@"
