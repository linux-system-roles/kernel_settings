Changelog
=========

[1.1.13] - 2023-04-06
--------------------

### Other Changes

- Fix issues found by CodeQL (#133)
- Add README-ansible.md to refer Ansible intro page on linux-system-roles.github.io (#140)
- Fingerprint RHEL System Role managed config files (#141)

[1.1.12] - 2023-01-25
--------------------

### New Features

- none

### Bug Fixes

- Cleanup non-inclusive words.

### Other Changes

- none

[1.1.11] - 2023-01-20
--------------------

### New Features

- none

### Bug Fixes

- ansible-lint 6.x fixes (#119)
- Cleanup non-inclusive words.

### Other Changes

- Add check for non-inclusive language (#117)
- add ubuntu requirements for pyunit tests
- add ignore files for ansible-test 2.13 and 2.14

[1.1.10] - 2022-08-03
--------------------

### New Features

- none

### Bug Fixes

- Set the kernel_settings_reboot_required when reboot needed (#93)

Previously the role would only set `kernel_settings_reboot_required`
if the user did not specify `kernel_settings_reboot_ok: true`.
The role will now set `kernel_settings_reboot_required` whenever
the system needs a reboot, and rely on the handler to clear the flag
if the user has set `kernel_settings_reboot_ok: true`.

### Other Changes

- Add "Publish role to Galaxy" to github action changelog_to_tag.yml (#91)

Fix a bash bug in changelog_to_tag.yml, which unexpectedly expanded "*".

- changelog_to_tag action - github action ansible test improvements (#92)

- Use GITHUB_REF_NAME as name of push branch; fix error in branch detection [citest skip] (#94)

We need to get the name of the branch to which CHANGELOG.md was pushed.

Signed-off-by: Rich Megginson <rmeggins@redhat.com>

[1.1.9] - 2022-07-10
--------------------

### New Features

- none

### Bug Fixes

- none

### Other Changes

- make all tests work with gather_facts: false (#82)

Ensure tests work when using ANSIBLE_GATHERING=explicit

- make min_ansible_version a string in meta/main.yml (#83)

The Ansible developers say that `min_ansible_version` in meta/main.yml
must be a `string` value like `"2.9"`, not a `float` value like `2.9`.

- Add CHANGELOG.md (#84)

[1.1.8] - 2022-05-06
--------------------

### New Features

- none

### Bug Fixes

- none

### Other Changes

- bump tox-lsr version to 2.11.0; remove py37; add py310 
- Add tests::reboot tag 

[1.1.7] - 2022-04-14
--------------------

### New features

- support gather\_facts: false; support setup-snapshot.yml 

### Bug Fixes

- none

### Other Changes

- none

[1.1.6] - 2022-02-28
--------------------

### New Features

- none

### Bug Fixes

- none

### Other Changes

- add sysctl for testing - package procps-ng 

[1.1.5] - 2022-02-25
--------------------

### New features

- ensure python-configobj is present 

### Bug Fixes

- none

### Other Changes

- bump tox-lsr version to 2.10.1 

[1.1.4] - 2022-01-27
--------------------

### New features

- none

### Bug Fixes

- make tuned.conf have correct ansible\_managed comment 

### Other Changes

- none

[1.1.3] - 2022-01-11
--------------------

### New Features

- none

### Bug Fixes

- none

### Other Changes

- change recursive role symlink to individual role dir symlinks 
- bump tox-lsr version to 2.8.3 
- Run the new tox test 

[1.1.2] - 2021-11-08
--------------------

### New Features

- make role work with ansible-core-2.11 ansible-lint and ansible-test 
- support ansible-core 2.12; ansible-plugin-scan; py39 

### Bug Fixes

- none

### Other Changes

- update tox-lsr version to 2.7.1 

[1.1.1] - 2021-09-21
--------------------

### New Features

- none

### Bug Fixes

- Use {{ ansible\_managed | comment }} to fix multi-line ansible\_managed 

### Other Changes

- use tox-lsr version 2.5.1 

[1.1.0] - 2021-08-10
--------------------

### New features

- Drop support for Ansible 2.8 by bumping the Ansible version to 2.9 

### Bug Fixes

- none

### Other Changes

- none

[1.0.4] - 2021-07-28
--------------------

### New Features

- none

### Bug fixes

- none

### Other Changes

- disable bootloader tests - fails on rhel9 

[1.0.3] - 2021-04-19
--------------------

### New Features

- none

### Bug Fixes

- Fix ansible-test issues 
- Fix issues found by ansible-test and linters - enable all tests on all repos - remove suppressions 
- kernel\_settings.py - must be quoted 

### Other Changes

- use tuned 2.15 for unit tests 
- update to tox-lsr 2.4.0 - add support for ansible-test with docker 
- CI: Add support for RHEL-9 
- Add a note to each module Doc to indicate it is private 

[1.0.2] - 2021-02-11
--------------------

### New Features

- Add centos8 

### Bug Fixes

- Fix centos6 repos; use standard centos images

### Other Changes

- use tox-lsr 2.2.0 
- use molecule v3, drop v2
- support jinja 2.7 
- Make the var load test compatible with old Jinja2 \(2.7\) 
- remove ansible 2.7 support from molecule 
- use tox for ansible-lint instead of molecule 
- use github actions instead of travis 
- use tox-lsr 

[1.0.1] - 2020-11-11
--------------------

### New Features

- none

### Bug Fixes

- fix black formatting issues 

### Other Changes

- sync collections related changes from template to kernel\_settings role 
- lock ansible-lint version at 4.3.5; suppress role name lint warning 
- install\_tuned\_for\_testing.sh - supporting the collection path. 
- lock ansible-lint on version 4.2.0 

[1.0.0] - 2020-08-26
--------------------

### Initial Release
