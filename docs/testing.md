
## Testing

It is recommended to use `tox` to set up your `virtualenv` for
development/testing purposes:
```
dnf/yum install python-tox
tox -e py38
```
You can also use the virtualenv created by `tox` just like any
other virtualenv created by `python-virtualenv`:
```
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
```
PYTHONPATH=/full/path/to/tuned:/full/path/to/linux-system-roles/kernel_settings/library
```

### Testing the module

https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html

Using a tox python virtualenv from the `kernel_settings` directory:

    . .tox/env-py38/bin/activate
    TESTING=true [TEST_PROFILE=kernel_settings] python library/kernel_settings.py args.json

looks for test profiles under `tests/tuned/etc/tuned`

to run the code in the debugger:

    TESTING=true [TEST_PROFILE=kernel_settings] python -mpdb library/kernel_settings.py args.json

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

### Other tests

Use `tox -e molecule` to run the molecule based tests.

Use `tox -e qemu-py27-ansible29` or `tox -e qemu-py38-ansible29` to run the
Ansible based tests against a local virtual machine.  These tests are in
`tests/tests_*.yml`.  See the file `tox.ini` for other `testenv:qemu-*`
environments you can use.
