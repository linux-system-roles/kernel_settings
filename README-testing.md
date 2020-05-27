
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
        "purge": false
    }
}
```

### tox

Run `tox` by itself with no arguments to run all of the default tests.  Use
`tox -a` to list all of the test environments.  Use `tox -e name` to run the
tests in that particular environment.

## Local Virtual Machine based tests

### Setup and running

You must first install the commands
`/usr/share/ansible/inventory/standard-inventory-qcow2` and `/usr/bin/ansible-playbook`.  On Fedora, this is
provided by the `standard-test-roles-inventory-qemu` and `ansible` packages -
`sudo dnf -y install standard-test-roles-inventory-qemu ansible`.
The test playbooks are the files
that match the pattern `tests/tests*.yml`.  You must also have one or more
qcow2 virtual machine images on your local disk somewhere.  For example, http://mirrors.kernel.org/fedora/releases/31/Cloud/x86_64/images/Fedora-Cloud-Base-31-1.9.x86_64.qcow2

To run a test playbook, assuming you have downloaded the virtual machine image somewhere
on your local disk:
```
ANSIBLE_STDOUT_CALLBACK=debug \
TEST_SUBJECTS=/path/to/Fedora-Cloud-Base-31-1.9.x86_64.qcow2 \
ansible-playbook -vv \
-i /usr/share/ansible/inventory/standard-inventory-qcow2 \
tests/tests_simple_settings.yml 2>&1 | tee output
```
Use `ANSIBLE_STDOUT_CALLBACK=debug` to make the output in a more human-readable format.

### How to use test playbooks

Each test consists of 3 phases:
* set the variables used by the test - the input parameters to the role, and the expected values to be verified after the role runs
* run the role - call or import the role with the given input parameters
* verify the role run - call the assert task files

If you are creating a new test playbook `tests/tests_some_behavior.yml`, start with
`tests/tests_simple_settings.yml` and copy it to `tests/tests_some_behavior.yml`.
Modify it as needed.  Next, copy `tests/vars/vars_simple_settings.yml` to `tests/vars/vars_some_behavior.yml` and modify it as needed.  Then modify `tests/tests_some_behavior.yml` to make sure it includes `vars/vars_some_behavior.yml` in the section where the test
parameters are set:
```yaml
- name: set parameters for test
  hosts: all
  tasks:
    - name: set vars used by this test
      include_vars:
        file: vars/vars_some_behavior.yml
```

To specify the input parameters to the role, set the role variables in `tests/vars/vars_NAME.yml`.  These are the role variables documented in the README.md and in `defaults/main.yml` e.g. `kernel_settings_sysctl`, etc.

There are two variables in `tests/vars/vars_NAME.yml` for the expected values:

* `__kernel_settings_profile_file` - this is what you expect the
  `kernel_settings/tuned.conf` to contain after the role runs.
* `__kernel_settings_blcmdline_value` - this is what you expect the
  `/etc/tuned/bootcmdline` value of `TUNED_BOOT_CMDLINE=` to contain after the
  role runs.  This can be omitted if you are not testing `kernel_settings_bootloader_cmdline`

### How test verification works

The task file `tests/tasks/assert_kernel_settings.yml` will verify that the
role modified the system correctly.  It assumes you have set
`__kernel_settings_profile_file` and `__kernel_settings_blcmdline_value` (if
testing `kernel_settings_bootloader_cmdline`).
`tests/tasks/assert_kernel_settings.yml` will do some test setup work, then
call `tests/tasks/assert_kernel_settings_conf_files.yml` to do most of the
work.  It first will compare `/etc/tuned/kernel_settings/tuned.conf` to
`__kernel_settings_profile_file`.  It does this by first writing
`__kernel_settings_profile_file` to a temp file, then compares that temp file
to `/etc/tuned/kernel_settings/tuned.conf` using the `python` module
`ConfigObj`.  We can't use `diff` because we cannot guarantee the order of
sections and values within sections.  It then makes sure that
`/etc/tuned/active_profile` ends with the `kernel_settings` profile.  It then
makes sure that `/etc/tuned/profile_mode` is set to `manual`.  It then checks
the contents of `/etc/tuned/bootcmdline` to make sure they match
`__kernel_settings_blcmdline_value`.

The test tasks do not fail immediately (i.e. they do not "fail-fast", they
"fail-last"). Instead, if a task reports a failure, the variable
`__kernel_settings_success` will set to `true`.  The final tasks in
`tests/tasks/assert_kernel_settings.yml` will report that the test failed. You
can review the test output to look for `FAILED!` to see which test tasks
failed.  Note that some failures may be ignored, so if you see a task which
reported `FAILED!`, check the task to see if it has `ignore_errors: true` set.

## Test FAQ

#### Q: The test ends when first error is reached - what if I need to continue?

Step 1 - At the beginning of your test, define a boolean variable which will
denote if the test was successful:
```yaml
- name: reset success flag
  set_fact:
    __kernel_settings_test_success: true
```

Step 2 - Add `ignore_errors: true` and `register:
__kernel_settings_test_register_NAME` to your test task.  The `ignore_errors:
true` tells Ansible not to fail immediately, and the `register: some_var` will
save the task result in the variable for use later.
```yaml
- name: check that settings are applied correctly
  command: tuned-adm verify -i
  ignore_errors: true
  register: __kernel_settings_test_register_verify
```

Step 3 - Add a task after this one to check the register variable, and set
your success flag to `false` upon failure.  NOTE that the check for the
register variable is different depending on what the check did.  In the
simplest case, if the task reports success or failure, you can use one of the
[Ansible built-in
tests](https://docs.ansible.com/ansible/latest/user_guide/playbooks_tests.html#task-results)
```yaml
- name: verify expected content
  set_fact:
    __kernel_settings_success: false
  when: __kernel_settings_test_register_verify is failed
```
More complex checks could see if a specific string was in the stdout of the command:
```yaml
- name: verify expected content
  set_fact:
    __kernel_settings_test_success: false
  when: __kernel_settings_test_register_verify.stdout is search('ERROR')
```

Step 4 - At the end of your test, check if your success flag is `false`, and
report an error if so:
```yaml
- name: assert success
  assert:
    that: __kernel_settings_test_success | d(true)
    msg: Found errors checking kernel parameters
```

Step 5 - Scan the Ansible output to look for `FAILED` tasks.
