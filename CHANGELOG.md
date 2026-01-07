Changelog
=========

[1.3.8] - 2026-01-07
--------------------

### Other Changes

- ci: bump gha checkout from v5 to v6 (#283)
- ci: add qemu tests for Fedora 43, drop Fedora 41 (#284)
- ci: bump actions/upload-artifact from 5 to 6 (#285)
- refactor: handle INJECT_FACTS_AS_VARS=false by using ansible_facts instead (#286)

[1.3.7] - 2025-11-17
--------------------

### Bug Fixes

- fix: cannot use community-general version 12 - no py27 and py36 support (#281)

### Other Changes

- ci: bump actions/upload-artifact from 4 to 5 (#276)
- ci: bump github/codeql-action from 3 to 4 (#277)
- ci: use versioned upload-artifact instead of master; bump codeql-action to v4; bump upload-artifact to v5 (#278)
- ci: bump tox-lsr to 3.13.0 (#279)
- ci: bump tox-lsr to 3.14.0 - this moves standard-inventory-qcow2 to tox-lsr (#280)

[1.3.6] - 2025-10-21
--------------------

### Other Changes

- ci: bump actions/checkout from 4 to 5 (#263)
- ci: rollout several recent changes to CI testing (#265)
- ci: support openSUSE Leap in qemu/kvm test matrix (#266)
- ci: use the new epel feature to enable EPEL for testing farm (#267)
- refactor: disable ansible-lint invalid jinja error (#268)
- ci: fix markdown formatting for contributing.md to pass markdownlint (#270)
- ci: use tox-lsr 3.12.0 for osbuild_config.yml feature (#271)
- ci: use JSON format for __bootc_validation (#272)
- ci: bump actions/github-script from 7 to 8 (#273)
- ci: bump actions/setup-python from 5 to 6 (#274)

[1.3.5] - 2025-07-02
--------------------

### Other Changes

- ci: Add support for bootc end-to-end validation tests (#259)
- ci: Use ansible 2.19 for fedora 42 testing; support python 3.13 (#260)
- refactor: support Ansible 2.19 (#261)

[1.3.4] - 2025-05-21
--------------------

### Other Changes

- ci: Bump codecov/codecov-action from 4 to 5 (#232)
- ci: Use Fedora 41, drop Fedora 39 (#233)
- ci: Use Fedora 41, drop Fedora 39 - part two (#234)
- ci: ansible-plugin-scan is disabled for now (#236)
- ci: bump ansible-lint to v25; provide collection requirements for ansible-lint (#239)
- refactor: fix python black formatting (#240)
- ci: Check spelling with codespell (#241)
- ci: Add test plan that runs CI tests and customize it for each role (#242)
- test: wip - test image mode (#243)
- test: test image mode (#244)
- test: test 3 image mode (#245)
- test: wip 4 image mode (#246)
- ci: In test plans, prefix all relate variables with SR_ (#249)
- ci: Fix bug with ARTIFACTS_URL after prefixing with SR_ (#250)
- ci: several changes related to new qemu test, ansible-lint, python versions, ubuntu versions (#252)
- ci: use tox-lsr 3.6.0; improve qemu test logging (#253)
- ci: skip storage scsi, nvme tests in github qemu ci (#254)
- ci: bump sclorg/testing-farm-as-github-action from 3 to 4 (#255)
- ci: bump tox-lsr to 3.8.0; rename qemu/kvm tests (#256)
- ci: Add Fedora 42; use tox-lsr 3.9.0; use lsr-report-errors for qemu tests (#257)

[1.3.3] - 2024-10-30
--------------------

### Other Changes

- ci: Add tags to TF workflow, allow more [citest bad] formats (#224)
- ci: ansible-test action now requires ansible-core version (#227)
- ci: add YAML header to github action workflow files (#228)
- refactor: Use vars/RedHat_N.yml symlink for CentOS, Rocky, Alma wherever possible (#230)

[1.3.2] - 2024-08-26
--------------------

### Bug Fixes

- fix: detect profile parent directory (#222)

[1.3.1] - 2024-08-09
--------------------

### Bug Fixes

- fix: Use tuned files instead of using it as a module (#220)

### Other Changes

- ci: Bump sclorg/testing-farm-as-github-action from 2 to 3 (#217)
- ci: Add workflow for ci_test bad, use remote fmf plan (#218)
- ci: Fix missing slash in ARTIFACTS_URL (#219)

[1.3.0] - 2024-08-01
--------------------

### New Features

- Handle reboot for transactional update systems (#215)

### Other Changes

- ci: Add tft plan and workflow (#209)
- ci: Fix tft workflow (#210)
- ci: Replace / with | in status to distinguish with BaseOS CI tests (#211)
- ci: Improve tft plan and workflow (#213)
- ci: Update fmf plan to add a separate job to prepare managed nodes (#214)

[1.2.5] - 2024-07-02
--------------------

### Bug Fixes

- fix: add support for EL10 (#207)

### Other Changes

- ci: ansible-lint action now requires absolute directory (#206)

[1.2.4] - 2024-06-11
--------------------

### Other Changes

- ci: use tox-lsr 3.3.0 which uses ansible-test 2.17 (#198)
- ci: tox-lsr 3.4.0 - fix py27 tests; move other checks to py310 (#201)
- ci: Add supported_ansible_also to .ansible-lint (#203)

[1.2.3] - 2024-04-02
--------------------

### Other Changes

- ci: Bump codecov/codecov-action from 3 to 4 (#193)
- ci: fix python unit test - copy pytest config to tests/unit (#194)
- ci: Bump ansible/ansible-lint from 6 to 24 (#195)
- ci: Bump mathieudutour/github-tag-action from 6.1 to 6.2 (#196)

[1.2.2] - 2024-01-16
--------------------

### Other Changes

- ci: new ansible lint collection (#187)
- ci: Add ALP-Dolomite var file (#188)
- ci: Bump actions/setup-python from 4 to 5 (#189)
- ci: Bump github/codeql-action from 2 to 3 (#190)
- ci: Use supported ansible-lint action; run ansible-lint against the collection (#191)

[1.2.1] - 2023-12-08
--------------------

### Other Changes

- ci: Bump actions/github-script from 6 to 7 (#183)
- refactor: get_ostree_data.sh use env shebang - remove from .sanity* (#184)

[1.2.0] - 2023-11-29
--------------------

### New Features

- feat: support for ostree systems (#180)

[1.1.19] - 2023-11-06
--------------------

### Other Changes

- Bump actions/checkout from 3 to 4 (#170)
- ci: ensure dependabot git commit message conforms to commitlint (#173)
- ci: use dump_packages.py callback to get packages used by role (#175)
- ci: tox-lsr version 3.1.1 (#177)
- ci: Fix implicit octal values in main.yml (#178)

[1.1.18] - 2023-09-08
--------------------

### Other Changes

- ci: Add markdownlint, test_converting_readme, and build_docs workflows (#166)

  - markdownlint runs against README.md to avoid any issues with
    converting it to HTML
  - test_converting_readme converts README.md > HTML and uploads this test
    artifact to ensure that conversion works fine
  - build_docs converts README.md > HTML and pushes the result to the
    docs branch to publish dosc to GitHub pages site.
  - Fix markdown issues in README.md
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

- docs: Make badges consistent, run markdownlint on all .md files (#167)

  - Consistently generate badges for GH workflows in README RHELPLAN-146921
  - Run markdownlint on all .md files
  - Add custom-woke-action if not used already
  - Rename woke action to Woke for a pretty badge
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

- ci: Remove badges from README.md prior to converting to HTML (#168)

  - Remove thematic break after badges
  - Remove badges from README.md prior to converting to HTML
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

[1.1.17] - 2023-07-19
--------------------

### Bug Fixes

- fix: facts being gathered unnecessarily (#163)

### Other Changes

- ci: Add pull request template and run commitlint on PR title only (#158)
- ci: Rename commitlint to PR title Lint, echo PR titles from env var (#159)
- ci: fix python 2.7 CI tests by manually installing python2.7 package (#160)
- ci: ansible-lint - ignore var-naming[no-role-prefix] (#161)
- ci: ansible-test ignores file for ansible-core 2.15 (#162)

[1.1.16] - 2023-05-26
--------------------

### Other Changes

- docs: Consistent contributing.md for all roles - allow role specific contributing.md section
- docs: remove unused Dependencies section in README

[1.1.15] - 2023-04-27
--------------------

### Other Changes

- test: check generated files for ansible_managed, fingerprint
- ci: Add commitlint GitHub action to ensure conventional commits with feedback

[1.1.14] - 2023-04-13
--------------------

### Other Changes

- ansible-lint - use changed_when even if using conditional (#143)

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
