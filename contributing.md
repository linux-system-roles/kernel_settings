# Contributing to the kernel_settings Linux System Role

## Where to start

The first place to go is [Contribute](https://linux-system-roles.github.io/contribute.html).
This has all of the common information that all role developers need:

* Role structure and layout
* Development tools - How to run tests and checks
* Ansible recommended practices
* Basic git and github information
* How to create git commits and submit pull requests

**Bugs and needed implementations** are listed on
[Github Issues](https://github.com/linux-system-roles/kernel_settings/issues).
Issues labeled with
[**help wanted**](https://github.com/linux-system-roles/kernel_settings/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
are likely to be suitable for new contributors!

**Code** is managed on [Github](https://github.com/linux-system-roles/kernel_settings), using
[Pull Requests](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests).

## Python Code

The Python code needs to be **compatible with the Python versions supported by
the role platform**.

For example, see [meta](https://github.com/linux-system-roles/kernel_settings/blob/main/meta/main.yml)
for the platforms supported by the role.

If the role provides Ansible modules (code in `library/` or `module_utils/`) -
these run on the *managed* node, and typically[1] use the default system python:

* EL6 - python 2.6
* EL7 - python 2.7 or python 3.6 in some cases
* EL8 - python 3.6
* EL9 - python 3.9

If the role provides some other sort of Ansible plugin such as a filter, test,
etc. - these run on the *control* node and typically use whatever version of
python that Ansible uses, which in many cases is *not* the system python, and
may be a modularity release such as python311.

In general, it is a good idea to ensure the role python code works on all
versions of python supported by `tox-lsr` from py36 on, and on py27 if the role
supports EL7, and on py26 if the role supports EL6.[1]

[1] Advanced users may set
[ansible_python_interpreter](https://docs.ansible.com/ansible/latest/reference_appendices/special_variables.html#term-ansible_python_interpreter)
to use a non-system python on the managed node, so it is a good idea to ensure
your code has broad python version compatibility, and do not assume your code
will only ever be run with the default system python.

## Testing kernel_settings modules

It is recommended to use `tox` to set up your `virtualenv` for
development/testing purposes:

```bash
dnf/yum install python-tox
tox -e py38
```

You can also use the virtualenv created by `tox` just like any
other virtualenv created by `python-virtualenv`:

```bash
. .tox/env-py38/bin/activate
python
>>> import package.that.only.exists.in.venv
```

The unit tests and other tests are run by default when you use `tox` by itself
or `tox -e py38` for a specific python versioned environment.  Note that other
operating system packages may be required to be installed in order for `tox`
to use `pip` to install python dependencies e.g. for python packages which
have native components.

I would also strongly encourage you to use an IDE for development. For example,
Visual Studio code python extension auto-discovers tests and allows you to
run and debug unit tests.  However, you may need to create a `.env` file like
this, in order for code navigation, auto-completion, and test discovery to
work correctly:

```bash
PYTHONPATH=/full/path/to/tuned:/full/path/to/linux-system-roles/kernel_settings/library
```

### Testing the module

[Ansible Module Development Guide](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)

Using a tox python virtualenv from the `kernel_settings` directory:

```bash
. .tox/env-py38/bin/activate
TESTING=true [TEST_PROFILE=kernel_settings] python \
  library/kernel_settings.py args.json
```

looks for test profiles under `tests/tuned/etc/tuned`

to run the code in the debugger:

```bash
TESTING=true [TEST_PROFILE=kernel_settings] python -mpdb \
  library/kernel_settings.py args.json
```

Where `args.json` looks like this:

```json
{
    "ANSIBLE_MODULE_ARGS": {
        "name": "kernel_settings",
        "sysctl": [
            {"name": "fs.inotify.max_user_watches", "value": 524288},
            {"name": "kernel.threads-max", "value": 30001}
        ],
        "sysfs": [
            {"name": "/sys/kernel/kexec_crash_size", "value": 337641472}
        ],
        "bootloader": [
            {"name": "cmdline", "value": [
                {"name": "mitigations", "value": "on"},
                {"name": "another"}
                ]
            }
        ],
        "selinux": [
            {"name": "avc_cache_threshold", "value": 512}
        ],
        "purge": false
    }
}
```
