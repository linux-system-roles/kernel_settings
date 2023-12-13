#!/usr/bin/env bash
# this is used to install tuned into a venv or tox env
# for testing purposes

set -euo pipefail

# import from utils.sh
. "${LSR_SCRIPTDIR}/utils.sh"

function ks_lsr_get_site_packages_dir() {
  python -c 'import sys; print([xx for xx in sys.path if xx.endswith("site-packages")][0])'
}

function ks_lsr_install_tuned() {
  local pyver="$1"
  local site_pkg_dir="$2"
  local tunedver
  case $pyver in
    2.*) tunedver=2.11.0;;
    3.*) tunedver=2.15.0;;
    *) echo unknown python version "$pyver"; exit 1;;
  esac
  # these are required in order to install pip packages from source
  pip install --upgrade pip setuptools wheel
  # extra requirements for tuned
  pip install -r "$TOPDIR/tuned_requirements.txt"
  if [ "${REINSTALL:-false}" = true ] ; then
      rm -rf "$site_pkg_dir/tuned"
  fi
  if [ ! -d "$site_pkg_dir/tuned" ] ; then
    curl -s -L -o "$site_pkg_dir/tuned.tgz" "${TUNED_FULL_URL:-${TUNED_BASE_URL}/v${tunedver}.tar.gz}"
    # extract only the tuned python code
    tar -C "$site_pkg_dir" -x -z -f "$site_pkg_dir/tuned.tgz" --strip-components=1 "tuned-${tunedver}/tuned"
    rm -rf "$site_pkg_dir/tuned.tgz"
    echo Installed "tuned-$tunedver" in "$site_pkg_dir/tuned"
  else
    echo Using already installed "tuned-$tunedver" in "$site_pkg_dir/tuned"
  fi
}

TUNED_BASE_URL="${TUNED_BASE_URL:-https://github.com/redhat-performance/tuned/archive}"
# install tuned only where needed
KS_LSR_PYVER=$(lsr_get_python_version "$(type -p python)")
if lsr_compare_versions "$KS_LSR_PYVER" -lt 2.7 ; then
  # tuned is not supported on python 2.6 when installing the dependencies
  # from pypi - for some of the dependencies, such as PyGObject, there are
  # no versions which are available on pypi that work on python 2.6
  lsr_info kernel_settings tests not supported on python "$KS_LSR_PYVER" - skipping
  exit 0
fi
KS_LSR_NEED_TUNED=0
case "${LSR_TOX_ENV_NAME:-}" in
  pylint) KS_LSR_NEED_TUNED=1 ;;
  py*) KS_LSR_NEED_TUNED=1 ;;
  coveralls) KS_LSR_NEED_TUNED=1 ;;
  flake8) KS_LSR_NEED_TUNED=1 ;;
esac
if [ "$KS_LSR_NEED_TUNED" = 1 ] ; then
  ks_lsr_install_tuned "$KS_LSR_PYVER" "$(ks_lsr_get_site_packages_dir)"
fi
