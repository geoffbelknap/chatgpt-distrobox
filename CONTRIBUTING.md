# Contributing

This repository maintains Distrobox integration, not OpenAI's application.
Describe the problem, behavior change, and validation in pull requests.

## Local checks

```bash
bash -n bootstrap.sh install.sh scripts/install-in-container.sh
shellcheck bootstrap.sh install.sh scripts/install-in-container.sh
python3 -m unittest discover -s tests -v
```

Tests cover host update configuration preservation, repeat runs, malformed
input, installer failure paths, and container command construction. They do not
download or install the proprietary app. CI runs these checks without secrets.

## Interactive installation check

For a local checkout, clone this repository under your shared home and run the
installer directly. To exercise bootstrap changes before publication, mock curl
as in `tests/test_bootstrap.py`; the public bootstrap always downloads main.

Use a separate container so normal work is unaffected:

```bash
./install.sh --name chatgpt-test
distrobox enter -n chatgpt-test -- rpm -q chatgpt
distrobox enter -n chatgpt-test -- cat /etc/yum.repos.d/chatgpt.repo
```

Verify launch, login persistence, file access, voice, and desktop integration
manually. Quit the test app before checking `distrobox upgrade chatgpt-test`.
Remove its exported launcher and container using the README commands with
`chatgpt-test` substituted for `chatgpt`. Test both architectures before claiming
both have passed; the installer supports x86_64 and aarch64 but a CI unit test
does not establish successful GUI operation.

For RPM signing key updates, verify the full fingerprint against an official
OpenAI package and update `docs/security.md`. Do not redistribute application
binaries or disable signature or Electron sandbox checks.
