#!/bin/bash
# this is used to install tuned into a venv or tox env
# for testing purposes

set -euo pipefail

if [ -n "$1" ] ; then
    SITE_PKG_DIR=$1
fi
if [ -n "${2:-}" ] ; then
    TUNED_VERSION=$2
else
    TUNED_VERSION=${TUNED_VERSION:-2.13.0}
fi

TUNED_BASE_URL=${TUNED_BASE_URL:-https://github.com/redhat-performance/tuned/archive}
TUNED_FULL_URL=${TUNED_FULL_URL:-${TUNED_BASE_URL}/v${TUNED_VERSION}.tar.gz}

if [ "${REINSTALL:-false}" = true ] ; then
    rm -rf $SITE_PKG_DIR/tuned
fi
if [ ! -d $SITE_PKG_DIR/tuned ] ; then
    curl -s -L -o $SITE_PKG_DIR/tuned.tgz $TUNED_FULL_URL
    # extract only the tuned python code
    tar -C $SITE_PKG_DIR -x -z -f $SITE_PKG_DIR/tuned.tgz --strip-components=1 tuned-${TUNED_VERSION}/tuned
    rm -rf $SITE_PKG_DIR/tuned.tgz
    echo Installed tuned-$TUNED_VERSION in $SITE_PKG_DIR/tuned
else
    echo Using already installed tuned-$TUNED_VERSION in $SITE_PKG_DIR/tuned
fi
