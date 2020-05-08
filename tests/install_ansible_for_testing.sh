#!/bin/bash
# this is used to install ansible into a venv or tox env
# for testing purposes

set -euo pipefail

if [ -n "$1" ] ; then
    INSTALL_DIR=$1
fi
if [ -n "${2:-}" ] ; then
    ANSIBLE_VERSION=$2
else
    ANSIBLE_VERSION=${ANSIBLE_VERSION:-devel}
fi

ANSIBLE_FULL_URL=${ANSIBLE_FULL_URL:-https://github.com/ansible-collection-migration/ansible-base.git}

if [ "${REINSTALL:-false}" = true ] ; then
    rm -rf $INSTALL_DIR
fi
if [ ! -d $INSTALL_DIR ] ; then
    git clone $ANSIBLE_FULL_URL -b $ANSIBLE_VERSION $INSTALL_DIR
    # install dependencies required for ansible
    pip install -r$INSTALL_DIR/requirements.txt
else
    echo Using already installed ansible-$ANSIBLE_VERSION in $INSTALL_DIR
fi
