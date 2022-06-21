# Changelog

## [1.1.8] - 2022-05-06

### New features

- bump tox-lsr version to 2.11.0; remove py37; add py310 
- Add tests::reboot tag 

## [1.1.7] - 2022-04-14

### New features

- support gather\_facts: false; support setup-snapshot.yml 

## [1.1.6] - 2022-02-28

### New features

- add sysctl for testing - package procps-ng 

## [1.1.5] - 2022-02-25

### New features

- ensure python-configobj is present 
- bump tox-lsr version to 2.10.1 

## [1.1.4] - 2022-01-27

### New features

- make tuned.conf have correct ansible\_managed comment 

## [1.1.3] - 2022-01-11

### New features

- change recursive role symlink to individual role dir symlinks 
- bump tox-lsr version to 2.8.3 
- Run the new tox test 

## [1.1.2] - 2021-11-08

### New features

- update tox-lsr version to 2.7.1 
- support ansible-core 2.12; ansible-plugin-scan; py39 
- make role work with ansible-core-2.11 ansible-lint and ansible-test 

## [1.1.1] - 2021-09-21

### New features

- Use {{ ansible\_managed | comment }} to fix multi-line ansible\_managed 
- use tox-lsr version 2.5.1 

## [1.1.0] - 2021-08-10

### New features

- Drop support for Ansible 2.8 by bumping the Ansible version to 2.9 

## [1.0.4] - 2021-07-28

### Bug fixes

- disable bootloader tests - fails on rhel9 

## [1.0.3] - 2021-04-19

### New features

- use tuned 2.15 for unit tests 
- update to tox-lsr 2.4.0 - add support for ansible-test sanity with docker 
- CI: Add support for RHEL-9 
- Add a note to each module Doc to indicate it is private 
- Fix ansible-test sanity issues 

### Bug fixes

- Fix issues found by ansible-test and linters - enable all tests on all repos - remove suppressions 
- kernel\_settings.py - must be quoted 

## [1.0.2] - 2021-02-11

### New features

- use tox-lsr 2.2.0 
- use molecule v3, drop v2
- support jinja 2.7 
- Make the var load test compatible with old Jinja2 \(2.7\) 
- remove ansible 2.7 support from molecule 
- Fix centos6 repos; use standard centos images; add centos8 
- use tox for ansible-lint instead of molecule 
- use github actions instead of travis 
- use tox-lsr 

## [1.0.1] - 2020-11-11

### New features

- sync collections related changes from template to kernel\_settings role 
- lock ansible-lint version at 4.3.5; suppress role name lint warning 
- install\_tuned\_for\_testing.sh - supporting the collection path. 
- lock ansible-lint on version 4.2.0 

### Bug fixes

- Missed "fi" in .travis/config.sh in the previous commit. 
- fix black formatting issues 

## [1.0.0] - 2020-08-26

### Initial Release
