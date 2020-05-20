#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Rich Megginson <rmeggins@redhat.com>
# SPDX-License-Identifier: GPLv2+
#
""" Manage kernel settings using tuned via a wrapper """

import os
import logging
import re
import tempfile
import shutil
import shlex
import contextlib
import atexit  # for testing
import copy
import configobj
import six
from six.moves import shlex_quote

from ansible.module_utils.basic import AnsibleModule

# see https://github.com/python/cpython/blob/master/Lib/logging/__init__.py
# for information about logging module internals


class TunedLogWrapper(logging.getLoggerClass()):
    """This wraps the tuned logger so that we can intercept logs and handle them here"""

    def __init__(self, *args, **kwargs):
        super(TunedLogWrapper, self).__init__(*args, **kwargs)
        self.setLevel(logging.DEBUG)
        self.logstack = []

    def handle(self, record):
        self.logstack.append(record)


@contextlib.contextmanager
def save_and_restore_logging_methods():
    """do not allow tuned logging to pollute global logging module or
    ansible logging"""
    save_logging_add_level_name = logging.addLevelName

    def wrapper_add_level_name(_levelval, _levelname):
        """ignore tuned.logging call to logging.addLevelName"""
        # print('addLevelName wrapper ignoring {} {}'.format(levelval, levelname))

    logging.addLevelName = wrapper_add_level_name
    save_logging_set_logger_class = logging.setLoggerClass

    def wrapper_set_logger_class(_clsname):
        """ignore tuned.logging call to logging.setLoggerClass"""
        # print('setLoggerClass wrapper ignoring {}'.format(clsname))

    logging.setLoggerClass = wrapper_set_logger_class
    try:
        yield
    finally:
        logging.addLevelName = save_logging_add_level_name
        logging.setLoggerClass = save_logging_set_logger_class


caught_import_error = None
try:
    with save_and_restore_logging_methods():
        import tuned.logs
    tuned.logs.root_logger = TunedLogWrapper(__name__)
    tuned.logs.get = lambda: tuned.logs.root_logger

    import tuned.consts
    import tuned.utils.global_config
    import tuned.daemon
    from tuned.exceptions import TunedException
except ImportError as ierr:
    # tuned package might not be available in check mode - so just
    # note that this is missing, and do not report in check mode
    caught_import_error = ierr

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: kernel_settings

short_description: Manage kernel settings using tuned via a wrapper

version_added: "2.8"

description:
    - Manage kernel settings using tuned via a wrapper.  The options correspond
      to names of units or plugins in tuned.  For example, the option `sysctl`
      corresponds to the `sysctl` unit or plugin in tuned.  Setting parameters
      works mostly like it does with tuned, except that this module uses Ansible
      YAML format instead of the tuned INI-style profile file format.  This module
      creates a special tuned profile `kernel_settings` which will be applied by
      tuned before any other profiles, allowing the user to configure tuned to
      override settings made by this module.  You should be aware of this if you
      plan to use tuned in addition to using this module.
      NOTE: the options list may be incomplete - the actual options are generated
      dynamically from tuned, for the current options supported by the version
      of tuned, which are the tuned supported plugins.  Only the most common
      options are listed.  See the tuned documentation for the full list and
      more information.
      Each option takes a list or dict of settings.  Each setting is a `dict`.
      The `dict` must have one of the keys `name`, `value`, `state`, or `previous`.
      `state` is used to remove settings or sections of settings.  `previous` is
      used to replace all of values in a section with the given values.  The only case
      where an option takes a dict is when you want to remove a section completely -
      then value for the section is the dict `{"state":"empty"}`.  Example:
      sysctl:
        - name: fs.file-max
          value: 65535
      Add or replace the sysctl `fs.file-max` parameter with the value 65535.  The
      existing settings are not touched.
      Example:
      sysctl:
        state: empty
      This means the existing sysctl section will be deleted.
      Example:
      sysctl:
        - previous: replaced
        - name: fs.file-max
          value: 65535
      This means the existing sysctl section will be cleared and replaced with the
      given settings.
      If you specify multiple settings with the same name in a section, the last one
      will be used.
options:
    sysctl:
        description:
            - list of sysctl settings to apply - this works mostly
              like the `sysctl` module except that `/etc/sysctl.conf` and files
              under `/etc/sysctl.d` are not used.
              e.g.
              sysctl:
                - name: fs.file-max
                  value: 65535
                - name: vm.max_mmap_regions
                  state: absent
        required: false
    sysfs:
        description:
            - key/value pairs of sysfs settings to apply
        required: false
    bootloader:
        description:
            - the `cmdline` option can be used to set, add, or delete
              kernel command line options.  See EXAMPLES for some examples
              of how to use this option.
              Note that this uses the tuned implementation, which adds these
              options to whatever the default bootloader command line arguments
              tuned is historically used to add/delete performance related
              kernel command line arguments e.g. `spectre_v2=off`.  If you need
              more general purpose bootloader configuration, you should use
              a bootloader module/role.
    purge:
        description:
            - Remove the current kernel_settings, whatever they are, and force
              the given settings to be the current and only settings

author:
    - Rich Megginson (rmeggins@redhat.com)
"""

EXAMPLES = """
# add the sysctl vm.max_mmap_regions, and disable spectre/meltdown security
kernel_settings:
  sysctl:
    - name: vm.max_mmap_regions
      value: 262144
  sysfs:
    - name: /sys/kernel/debug/x86/pti_enabled
      value: 0
    - name: /sys/kernel/debug/x86/retp_enabled
      value: 0
    - name: /sys/kernel/debug/x86/ibrs_enabled
      value: 0

# replace the existing sysctl section with the specified section
# delete the /sys/kernel/debug/x86/retp_enabled setting
# completely remove the vm section
# add the bootloader cmdline arguments spectre_v2=off nopti
# remove the bootloader cmdline arguments quiet splash
kernel_settings:
  sysctl:
    - previous: replaced
    - name: vm.max_mmap_regions
      value: 262144
  sysfs:
    - name: /sys/kernel/debug/x86/retp_enabled
      state: absent
  vm:
    state: empty
  bootloader:
    - name: cmdline
      value:
        - name: spectre_v2
          value: off
        - name: nopti
        - name: quiet
          state: absent
        - name: splash
          state: absent
"""

RETURN = """
msg:
    A short text message to say what action this module performed.
new_profile:
    This is the tuned profile in dict format, after the changes, if any,
    have been applied.
reboot_required:
    boolean - default is false - if true, this means a reboot of the
    managed host is required in order for the changes to take effect.
active_profile:
    This is the space delimited list of active profiles as reported
    by tuned.
"""

TUNED_PROFILE = os.environ.get("TEST_PROFILE", "kernel_settings")
NOCHANGES = 0
CHANGES = 1
REMOVE_SECTION_VALUE = {"state": "empty"}
SECTION_TO_REPLACE = "__section_to_replace"
ERR_SECTION_MISSING_NAME = "Error: section [{}] item is missing 'name': {}"
ERR_NAME_NOT_VALID = "Error: section [{}] item name [{}] is not a valid string"
ERR_NO_VALUE_OR_STATE = (
    "Error: section [{}] item name [{}] must have either a 'value' or 'state'"
)
ERR_BOTH_VALUE_AND_STATE = (
    "Error: section [{}] item name [{}] must have only one of 'value' or 'state'"
)
ERR_STATE_ABSENT = (
    "Error: section [{}] item name [{}] state value must be 'absent' not [{}]"
)
ERR_UNEXPECTED_VALUES = "Error: section [{}] item [{}] has unexpected values {}"
ERR_VALUE_ITEM_NOT_DICT = "Error: section [{}] item name [{}] value [{}] is not a dict"
ERR_VALUE_ITEM_PREVIOUS = (
    "Error: section [{}] item name [{}] has invalid value for 'previous' [{}]"
)
ERR_REMOVE_SECTION_VALUE = "Error: to remove the section [{}] specify the value {}"
ERR_ITEM_NOT_DICT = "Error: section [{}] item value [{}] is not a dict"
ERR_ITEM_PREVIOUS = "Error: section [{}] item has invalid value for 'previous' [{}]"
ERR_ITEM_DICT_OR_LIST = "Error: section [{}] value must be a dict or a list"
ERR_LIST_NOT_ALLOWED = "Error: section [{}] item [{}] has unexpected list value {}"
ERR_BLCMD_MUST_BE_LIST = "Error: section [{}] item [{}] must be a list not [{}]"


def get_supported_tuned_plugin_names():
    """get names of all tuned plugins supported by this module"""
    return [
        "bootloader",
        "modules",
        "selinux",
        "sysctl",
        "sysfs",
        "systemd",
        "vm",
    ]


def no_such_profile():
    """see if the last log message was that the profile did not exist"""
    lastlogmsg = tuned.logs.root_logger.logstack[-1].msg
    return re.search("Requested profile .* doesn't exist", lastlogmsg) is not None


def profile_to_dict(profile):
    """convert profile object to dict"""
    ret_val = {}
    for unitname, unit in profile.units.items():
        ret_val[unitname] = unit.options
    return ret_val


def debug_print_profile(profile, amodule):
    """for debugging - print profile as INI"""
    amodule.debug("profile {}".format(profile.name))
    amodule.debug(str(profile_to_dict(profile)))


caught_name_error = None
try:
    EMPTYUNIT = tuned.profiles.unit.Unit("empty", {})
except NameError as nerr:
    # tuned not loaded in check mode
    caught_name_error = nerr


def get_profile_unit_key(profile, unitname, key):
    """convenience function"""
    return profile.units.get(unitname, EMPTYUNIT).options.get(key)


class BLCmdLine(object):
    """A data type for handling bootloader cmdline values."""

    def __init__(self, val):
        self.key_list = []  # list of keys in order - to preserve ordering
        self.key_to_val = {}  # maps key to value
        if val:
            for item in shlex.split(val):
                key, val = self.splititem(item)
                self.key_list.append(key)
                # None or '' means bare key - no value
                self.key_to_val[key] = val

    @classmethod
    def splititem(cls, item):
        """split item in form key=somevalue into key and somevalue"""
        key, _, val = item.partition("=")
        return key, val

    @classmethod
    def escapeval(cls, val):
        """make sure val is quoted as in shell"""
        return shlex_quote(val)

    def __str__(self):
        vallist = []
        for key in self.key_list:
            val = self.key_to_val[key]
            if val:
                vallist.append("{}={}".format(key, self.escapeval(val)))
            else:
                vallist.append(key)
        return " ".join(vallist)

    def add(self, key, val):
        """add/replace the given key & value"""
        if key not in self.key_to_val:
            self.key_list.append(key)
        self.key_to_val[key] = val

    def remove(self, key):
        """remove the given key"""
        if key in self.key_to_val:
            self.key_list.remove(key)
            del self.key_to_val[key]


def apply_bootloader_cmdline_item(item, unitname, current_profile, curvalue):
    """apply a bootloader cmdline item to the current profile"""
    name = item["name"]
    if item.get(SECTION_TO_REPLACE, False):
        blcmd = BLCmdLine("")
    else:
        blcmd = BLCmdLine(curvalue)
    for subitem in item["value"]:
        if "previous" in subitem:
            continue
        if subitem.get("state") == "absent":
            blcmd.remove(subitem["name"])
        else:
            blcmd.add(subitem["name"], subitem.get("value"))
    blcmdstr = str(blcmd)
    if blcmdstr:
        current_profile.units.setdefault(
            unitname, tuned.profiles.unit.Unit(unitname, {})
        ).options[name] = blcmdstr
    elif curvalue:
        del current_profile.units[unitname].options[name]


def apply_item_to_profile(item, unitname, current_profile):
    """apply a specific item from a section to the current_profile"""
    name = item["name"]
    curvalue = get_profile_unit_key(current_profile, unitname, name)
    newvalue = item.get("value")
    if item.get("state", None) == "absent":
        if curvalue:
            del current_profile.units[unitname].options[name]
    elif unitname == "bootloader" and name == "cmdline":
        apply_bootloader_cmdline_item(item, unitname, current_profile, curvalue)
    else:
        current_profile.units.setdefault(
            unitname, tuned.profiles.unit.Unit(unitname, {})
        ).options[name] = str(newvalue)


def is_reboot_required(unitname):
    """Some changes need a reboot for the changes to be applied
       For example, bootloader cmdline changes"""
    # for now, only bootloader cmdline changes need a reboot
    return unitname == "bootloader"


def apply_params_to_profile(params, current_profile, purge):
    """apply the settings from the input parameters to the current profile
    delete the unit if it is empty after applying the parameter deletions
    """
    changestatus = NOCHANGES
    reboot_required = False
    section_to_replace = params.pop(SECTION_TO_REPLACE, {})
    need_purge = set()
    if purge:
        # remove units not specified in params
        need_purge = set(current_profile.units.keys())
    for unitname, items in params.items():
        unit = current_profile.units.get(unitname, None)
        current_options = {}
        if unit:
            current_options = copy.deepcopy(unit.options)
        replace = section_to_replace.get(unitname, purge)
        if replace or (items == REMOVE_SECTION_VALUE):
            if unit:
                unit.options.clear()
                if purge and unitname in need_purge:
                    need_purge.remove(unitname)
            if items == REMOVE_SECTION_VALUE:
                if unit:
                    # we changed the profile
                    changestatus = CHANGES
                reboot_required = reboot_required or is_reboot_required(unitname)
                # we're done - no further processing necessary for this unit
                continue
        for item in items:
            if item and "previous" not in item:
                apply_item_to_profile(item, unitname, current_profile)
        newoptions = {}
        if unitname in current_profile.units:
            newoptions = current_profile.units[unitname].options
        if current_options != newoptions:
            changestatus = CHANGES
            reboot_required = reboot_required or is_reboot_required(unitname)
    for unitname in need_purge:
        del current_profile.units[unitname]
        changestatus = CHANGES
        reboot_required = reboot_required or is_reboot_required(unitname)
    # remove empty units
    for unitname in list(current_profile.units.keys()):
        if not current_profile.units[unitname].options:
            del current_profile.units[unitname]
    return changestatus, reboot_required


def write_profile(current_profile):
    """write the profile to the profile file"""
    # convert profile to configobj to write ini-style file
    # profile.options go into [main] section
    # profile.units go into [unitname] section
    cfg = configobj.ConfigObj(indent_type="")
    cfg.initial_comment = ["File managed by Ansible - DO NOT EDIT"]
    cfg["main"] = current_profile.options
    for unitname, unit in current_profile.units.items():
        cfg[unitname] = unit.options
    profile_base_dir = tuned.consts.LOAD_DIRECTORIES[-1]
    prof_fname = os.path.join(
        profile_base_dir, TUNED_PROFILE, tuned.consts.PROFILE_FILE
    )
    with open(prof_fname, "wb") as prof_f:
        cfg.write(prof_f)


def update_current_profile_and_mode(daemon, profile_list):
    """ensure that the tuned current_profile applies the kernel_settings last"""
    changed = False
    profile, manual = daemon._get_startup_profile()
    # is TUNED_PROFILE in the list?
    profile_list.extend(profile.split())
    if TUNED_PROFILE not in profile_list:
        changed = True
        profile_list.append(TUNED_PROFILE)
    # have to convert to manual mode in order to ensure kernel_settings are applied
    if not manual:
        changed = True
        manual = True
    if changed:
        daemon._save_active_profile(" ".join(profile_list), manual)
    return changed


def setup_for_testing():
    """create an /etc/tuned and /usr/lib/tuned directory structure for testing"""
    test_root_dir = os.environ.get("TEST_ROOT_DIR")
    if test_root_dir is None:
        test_root_dir = tempfile.mkdtemp(suffix=".lsr")
    # copy all of the test configs and profiles
    test_root_dir_tuned = os.path.join(test_root_dir, "tuned")
    test_src_dir = os.environ.get("TEST_SRC_DIR", "tests")
    src_dir = os.path.join(test_src_dir, "tuned")
    shutil.copytree(src_dir, test_root_dir_tuned)
    # patch all of the consts to use the test_root_dir
    orig_consts = {}
    for cnst in (
        "GLOBAL_CONFIG_FILE",
        "ACTIVE_PROFILE_FILE",
        "PROFILE_MODE_FILE",
        "RECOMMEND_CONF_FILE",
        "BOOT_CMDLINE_FILE",
    ):
        orig_consts[cnst] = tuned.consts.__dict__[cnst]
        fname = os.path.join(
            test_root_dir_tuned,
            os.path.relpath(tuned.consts.__dict__[cnst], os.path.sep),
        )
        tuned.consts.__dict__[cnst] = fname
        dname = os.path.dirname(fname)
        if not os.path.isdir(dname):
            os.makedirs(dname)
    orig_load_dirs = []
    for idx, dname in enumerate(tuned.consts.LOAD_DIRECTORIES):
        orig_load_dirs.append(dname)
        newdname = os.path.join(
            test_root_dir_tuned, os.path.relpath(dname, os.path.sep)
        )
        tuned.consts.LOAD_DIRECTORIES[idx] = newdname
        if not os.path.isdir(newdname):
            os.makedirs(newdname)
    orig_rec_dirs = []
    for idx, dname in enumerate(tuned.consts.RECOMMEND_DIRECTORIES):
        orig_rec_dirs.append(dname)
        newdname = os.path.join(
            test_root_dir_tuned, os.path.relpath(dname, os.path.sep)
        )
        tuned.consts.RECOMMEND_DIRECTORIES[idx] = newdname
        if not os.path.isdir(newdname):
            os.makedirs(newdname)
    has_func = bool(
        getattr(tuned.utils.global_config.GlobalConfig.__init__, "__func__", False)
    )
    if has_func:
        orig_gc_init_defaults = (
            tuned.utils.global_config.GlobalConfig.__init__.__func__.__defaults__
        )
        orig_gc_load_config_defaults = (
            tuned.utils.global_config.GlobalConfig.load_config.__func__.__defaults__
        )
        if orig_gc_init_defaults:
            tuned.utils.global_config.GlobalConfig.__init__.__func__.__defaults__ = (
                tuned.consts.GLOBAL_CONFIG_FILE,
            )
        if orig_gc_load_config_defaults:
            tuned.utils.global_config.GlobalConfig.load_config.__func__.__defaults__ = (
                tuned.consts.GLOBAL_CONFIG_FILE,
            )
    else:
        orig_gc_init_defaults = (
            tuned.utils.global_config.GlobalConfig.__init__.__defaults__
        )
        orig_gc_load_config_defaults = (
            tuned.utils.global_config.GlobalConfig.load_config.__defaults__
        )
        if orig_gc_init_defaults:
            tuned.utils.global_config.GlobalConfig.__init__.__defaults__ = (
                tuned.consts.GLOBAL_CONFIG_FILE,
            )
        if orig_gc_load_config_defaults:
            tuned.utils.global_config.GlobalConfig.load_config.__defaults__ = (
                tuned.consts.GLOBAL_CONFIG_FILE,
            )
    # this call fails on ubuntu and containers, so mock it for testing
    import pyudev.monitor

    orig_set_receive_buffer_size = pyudev.monitor.Monitor.set_receive_buffer_size
    pyudev.monitor.Monitor.set_receive_buffer_size = lambda self, size: None

    def test_cleanup():
        import os
        import shutil

        if "TEST_ROOT_DIR" not in os.environ:
            shutil.rmtree(test_root_dir)
        for cnst, val in orig_consts.items():
            tuned.consts.__dict__[cnst] = val
        for idx, dname in enumerate(orig_load_dirs):
            tuned.consts.LOAD_DIRECTORIES[idx] = dname
        for idx, dname in enumerate(orig_rec_dirs):
            tuned.consts.RECOMMEND_DIRECTORIES[idx] = dname
        if has_func:
            tuned.utils.global_config.GlobalConfig.__init__.__func__.__defaults__ = (
                orig_gc_init_defaults
            )
            tuned.utils.global_config.GlobalConfig.load_config.__func__.__defaults__ = (
                orig_gc_load_config_defaults
            )
        else:
            tuned.utils.global_config.GlobalConfig.__init__.__defaults__ = (
                orig_gc_init_defaults
            )
            tuned.utils.global_config.GlobalConfig.load_config.__defaults__ = (
                orig_gc_load_config_defaults
            )
        pyudev.monitor.Monitor.set_receive_buffer_size = orig_set_receive_buffer_size

    if "TEST_ROOT_DIR" not in os.environ:
        atexit.register(test_cleanup)
    return test_cleanup


def get_tuned_config():
    """get the tuned config and set our parameters in it"""
    tuned_config = tuned.utils.global_config.GlobalConfig()
    tuned_config.set("daemon", 0)
    tuned_config.set("reapply_sysctl", 0)
    tuned_config.set("dynamic_tuning", 0)
    return tuned_config


def load_current_profile(tuned_config, tuned_profile, logger):
    """load the current profile"""
    tuned_app = None
    errmsg = "Error loading tuned profile [{}]".format(TUNED_PROFILE)
    try:
        tuned_app = tuned.daemon.Application(tuned_profile, tuned_config)
    except TunedException as tex:
        logger.debug("caught TunedException [{}]".format(tex))
        errmsg = errmsg + ": {}".format(tex)
        tuned_app = None
    except IOError as ioe:
        # for testing this case, need to create a profile with a bad permissions e.g.
        # mkdir ioerror_profile; touch ioerror_profile/tuned.conf; chmod 0000 !$
        logger.debug("caught IOError [{}]".format(ioe))
        errmsg = errmsg + ": {}".format(ioe)
        tuned_app = None
    if (
        tuned_app is None
        or tuned_app.daemon is None
        or tuned_app.daemon.profile is None
        or tuned_app.daemon.profile.units is None
        or tuned_app.daemon.profile.options is None
        or "summary" not in tuned_app.daemon.profile.options
    ):
        tuned_app = None
        if no_such_profile():
            errmsg = errmsg + ": Profile does not exist"
    return tuned_app, errmsg


def validate_and_digest_item(sectionname, item, listallowed=True, allowempty=False):
    """Validate an item - must contain only name, value, and state"""
    tmpitem = item.copy()
    name = tmpitem.pop("name", None)
    value = tmpitem.pop("value", None)
    state = tmpitem.pop("state", None)
    errlist = []
    if name is None:
        errlist.append(ERR_SECTION_MISSING_NAME.format(sectionname, item))
    elif not isinstance(name, six.string_types):
        errlist.append(ERR_NAME_NOT_VALID.format(sectionname, name))
    elif (value is None and not allowempty) and state is None:
        errlist.append(ERR_NO_VALUE_OR_STATE.format(sectionname, name))
    elif value is not None and state is not None:
        errlist.append(ERR_BOTH_VALUE_AND_STATE.format(sectionname, name))
    elif state is not None and state != "absent":
        errlist.append(ERR_STATE_ABSENT.format(sectionname, name, state))
    elif tmpitem:
        errlist.append(ERR_UNEXPECTED_VALUES.format(sectionname, name, tmpitem))
    elif isinstance(value, list):
        if not listallowed:
            errlist.append(ERR_LIST_NOT_ALLOWED.format(sectionname, name, value))
        else:
            for valitem in value:
                if not isinstance(valitem, dict):
                    errlist.append(
                        ERR_VALUE_ITEM_NOT_DICT.format(sectionname, name, valitem)
                    )
                elif "previous" in valitem:
                    if valitem["previous"] != "replaced":
                        errlist.append(
                            ERR_VALUE_ITEM_PREVIOUS.format(
                                sectionname, name, valitem["previous"]
                            )
                        )
                    else:
                        item[SECTION_TO_REPLACE] = True
                else:
                    tmperrlist = validate_and_digest_item(
                        sectionname, valitem, False, True
                    )
                    errlist.extend(tmperrlist)
    elif sectionname == "bootloader" and name == "cmdline":
        errlist.append(ERR_BLCMD_MUST_BE_LIST.format(sectionname, name, value))
    return errlist


def validate_and_digest(params):
    """Validate that params is in the correct format, since we
    are using type `raw`, we have to perform the validation here.
    Also do some pre-processing to make it easier to apply
    the params to profile"""
    errlist = []
    replaces = {}
    for sectionname, items in params.items():
        if isinstance(items, dict):
            if not items == REMOVE_SECTION_VALUE:
                errlist.append(
                    ERR_REMOVE_SECTION_VALUE.format(sectionname, REMOVE_SECTION_VALUE)
                )
        elif isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    errlist.append(ERR_ITEM_NOT_DICT.format(sectionname, item))
                elif not item:
                    continue  # ignore empty items
                elif "previous" in item:
                    if item["previous"] != "replaced":
                        errlist.append(
                            ERR_ITEM_PREVIOUS.format(sectionname, item["previous"])
                        )
                    else:
                        replaces[sectionname] = True
                else:
                    itemerrlist = validate_and_digest_item(sectionname, item)
                    errlist.extend(itemerrlist)
        else:
            errlist.append(ERR_ITEM_DICT_OR_LIST.format(sectionname))
    if replaces:
        params[SECTION_TO_REPLACE] = replaces

    return errlist


def run_module():
    """ The entry point of the module. """

    module_args = dict(
        name=dict(type="str", required=False),
        purge=dict(type="bool", required=False, default=False),
    )
    tuned_plugin_names = get_supported_tuned_plugin_names()
    for plugin_name in tuned_plugin_names:
        # use raw here - type can be dict or list - perform validation
        # below
        module_args[plugin_name] = dict(type="raw", required=False)

    result = dict(changed=False, message="")

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not module.check_mode:
        if os.environ.get("TESTING", "false") == "true":
            _ = setup_for_testing()

    params = module.params
    # remove any non-tuned fields from params and save them locally
    # state = params.pop("state")
    purge = params.pop("purge", False)
    del params["name"]
    # also remove any empty or None
    for key, val in list(params.items()):
        if not val:
            del params[key]
    errlist = validate_and_digest(params)
    if errlist:
        errmsg = "Invalid format for input parameters"
        module.fail_json(msg=errmsg, warnings=errlist, **result)

    # In check_mode, just perform input validation (above), because
    # tuned will not be installed on the remote system
    if module.check_mode:
        module.exit_json(**result)
    elif caught_import_error is not None:
        raise caught_import_error  # pylint: disable-msg=E0702
    elif caught_name_error is not None:
        # name error is usually because tuned module was not imported
        # but just in case, report it here
        raise caught_name_error  # pylint: disable-msg=E0702

    tuned_config = get_tuned_config()
    current_profile = None
    tuned_app, errmsg = load_current_profile(tuned_config, TUNED_PROFILE, module)

    if tuned_app is None:
        module.fail_json(msg=errmsg, **result)
    else:
        current_profile = tuned_app.daemon.profile
        debug_print_profile(current_profile, module)
        errmsg = ""

    result["msg"] = "Kernel settings were updated."

    # apply the given params to the profile - if there are any new items
    # the function will return True we set changed = True
    changestatus, reboot_required = apply_params_to_profile(
        params, current_profile, purge
    )
    profile_list = []
    if update_current_profile_and_mode(tuned_app.daemon, profile_list):
        # profile or mode changed
        if changestatus == NOCHANGES:
            changestatus = CHANGES
            result["msg"] = "Updated active profile and/or mode."
    if changestatus > NOCHANGES:
        try:
            write_profile(current_profile)
            # notify tuned to reload/reapply profile
        except TunedException as tex:
            module.debug("caught TunedException [{}]".format(tex))
            errmsg = "Unable to apply tuned settings: {}".format(tex)
            module.fail_json(msg=errmsg, **result)
        except IOError as ioe:
            module.debug("caught IOError [{}]".format(ioe))
            errmsg = "Unable to apply tuned settings: {}".format(ioe)
            module.fail_json(msg=errmsg, **result)
        result["changed"] = True
    else:
        result["msg"] = "Kernel settings are up to date."
    debug_print_profile(current_profile, module)
    result["new_profile"] = profile_to_dict(current_profile)
    result["active_profile"] = " ".join(profile_list)
    result["reboot_required"] = reboot_required
    if reboot_required:
        result["msg"] = (
            result["msg"] + "  A system reboot is needed to apply the changes."
        )
    module.exit_json(**result)


def main():
    """ The main function! """
    run_module()


if __name__ == "__main__":
    main()

# vim:set ts=4 sw=4 et:
