# SPDX-License-Identifier: MIT
#
# Use this file to specify custom configuration for a project. Generally, this
# involves the modification of the content of LSR_* environment variables, see
#
#   * .travis/preinstall:
#
#       - LSR_EXTRA_PACKAGES
#
#   * .travis/runtox:
#
#       - LSR_ANSIBLES
#       - LSR_MSCENARIOS
#
#   * .travis/runcoveralls.sh:
#
#       - LSR_PUBLISH_COVERAGE
#
# Environment variables that not start with LSR_* but have influence on CI
# process:
#
#   * run_pylint.py:
#
#       - RUN_PYLINT_INCLUDE
#       - RUN_PYLINT_EXCLUDE
#       - RUN_PYLINT_DISABLED
#
#   * .travis/runblack.sh:
#
#       - RUN_BLACK_INCLUDE
#       - RUN_BLACK_EXCLUDE
#       - RUN_BLACK_DISABLED
#
#   * .travis/runflake8.sh:
#
#       - RUN_FLAKE8_DISABLED
#
#   * .travis/runsyspycmd.sh:
#
#       - function lsr_runsyspycmd_hook
#
#   * .travis/runpytest.sh:
#
#       - RUN_PYTEST_SETUP_MODULE_UTILS
type -f lsr_get_python_version > /dev/null 2>&1 || . ${SCRIPTDIR}/utils.sh

RUN_PYLINT_SETUP_MODULE_UTILS=true
RUN_PYTEST_SETUP_MODULE_UTILS=true

# these are extra packages needed to install and run tuned on the travis machine
LSR_EXTRA_PACKAGES="${LSR_EXTRA_PACKAGES:-} libdbus-1-dev libgirepository1.0-dev python3-dev \
  libssl-dev libcairo2-dev"

# needed by unit tests
export TEST_SRC_DIR=$TOPDIR/tests

function ks_lsr_get_site_packages_dir() {
  python -c 'import sys; print([xx for xx in sys.path if xx.endswith("site-packages")][0])'
}

function ks_lsr_install_tuned() {
  local pyver=$1
  local tunedver
  local req
  case $pyver in
  2.*) tunedver=2.11.0;;
  3.*) tunedver=2.13.0;;
  *) echo unknown python version $pyver for $1; exit 1;;
  esac
  # these are required in order to install pip packages from source
  pip install --upgrade pip setuptools wheel
  # extra requirements for tuned
  pip install -r $TOPDIR/tuned_requirements.txt
  bash $TOPDIR/tests/install_tuned_for_testing.sh $(ks_lsr_get_site_packages_dir) $tunedver
}

# install tuned only where needed
KS_LSR_PYVER=$(lsr_get_python_version $(type -p python))
if lsr_compare_versions $KS_LSR_PYVER -lt 2.7 ; then
  # tuned is not supported on python 2.6 when installing the dependencies
  # from pypi - for some of the dependencies, such as PyGObject, there are
  # no versions which are available on pypi that work on python 2.6
  lsr_info kernel_settings tests not supported on python $KS_LSR_PYVER - skipping
  exit 0
fi
KS_LSR_NEED_TUNED=0
case "$0" in
*/runpytest.sh) KS_LSR_NEED_TUNED=1 ;;
*/runcoveralls.sh) KS_LSR_NEED_TUNED=1 ;;
*/runflake8.sh) KS_LSR_NEED_TUNED=1 ;;
*/runpylint.sh) KS_LSR_NEED_TUNED=1 ;;
esac
if [ $KS_LSR_NEED_TUNED = 1 ] ; then
  ks_lsr_install_tuned $KS_LSR_PYVER
fi
