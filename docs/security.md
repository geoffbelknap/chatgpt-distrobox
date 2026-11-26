# Security and verification

The one-command install executes this project's bootstrap script from GitHub.
It downloads the required integration files as one repository snapshot over
HTTPS and fully extracts them before executing setup. They remain under
`~/.local/share/chatgpt-distrobox` for the signing key and update helper. This
trusts this GitHub project to supply installer code; the RPM signature check
verifies the separate application download. Review the bootstrap and installer
or clone the repository first if you prefer inspecting code before execution.

The installer downloads OpenAI's RPM directly from:

`https://persistent.oaistatic.com/codex-app-prod/linux/rpm/latest/chatgpt.<arch>.rpm`

The bundled `keys/openai.asc` is the public key shipped by the official
ChatGPT RPM (`26.1120.50957-1`, installed locally on 2026-11-24). Its full fingerprint is:

```text
3BFA 0E4A E8B8 CC16 A2D9 BA68 4A3B 4A56 6C46 60E4
```

Inspect it yourself:

```bash
gpg --show-keys --with-fingerprint keys/openai.asc
```

The key is imported only into the container's RPM database. The initial local
RPM install explicitly sets `localpkg_gpgcheck=1`, because DNF otherwise may not
check signatures for local files. Normal Fedora repository packages use the
container's Fedora trust configuration. After installation, OpenAI's RPM sets
up `/etc/yum.repos.d/chatgpt.repo` in the container for subsequent updates. Our
tested package enables both package and repository metadata signature checks.

DNF trusts the keys in the container's RPM database, including Fedora's keys;
it does not use an isolated OpenAI-only trust store. This integration bootstraps
OpenAI's signing identity from the public key checked into this project. Review
the scripts and key before installing. A signing-key rotation may require a
reviewed update to this repository. Do not bypass signature checking to work
around a key error.

The Fedora image is pinned to a distribution release, not an immutable digest;
the RPM URL intentionally selects the current OpenAI release. Installations at
different times may therefore get different versions. This project does not
claim reproducible application builds or rebuild the proprietary app.

Distrobox is designed for desktop integration and shares your home and other
host resources. It does not isolate untrusted applications. The uupd helper is
separate from installation because it changes the host update policy for all
Distroboxes. It preserves unrelated JSON settings and keeps a backup.

References: [OpenAI Linux installation and updates](https://learn.chatgpt.com/docs/linux/linux-app),
[Distrobox export](https://distrobox.it/usage/distrobox-export/).
