# ChatGPT for Distrobox (Unofficial)

Install [OpenAI's official Linux desktop app](https://learn.chatgpt.com/docs/linux/linux-app)
in a Fedora 44 Distrobox and launch it from your desktop menu. Intended for
Bazzite, Fedora Silverblue, Kinoite, and other Linux desktops where installing
the RPM inside a container is more convenient than changing the host OS.

This is an unofficial community integration, not affiliated with, endorsed by,
or supported by OpenAI. The integration is MIT licensed; the application is
proprietary. This project distributes scripts and a public signing key, not
OpenAI's application binaries or a custom container image.

## Install

Prerequisites: Distrobox, Podman or Docker, Git, an internet connection, and an
x86_64 or ARM64 (`aarch64`) Linux desktop. Allow several GB for the container,
application, and temporary download. Run as your regular user, without sudo:

```bash
git clone https://github.com/geoffbelknap/chatgpt-distrobox.git ~/chatgpt-distrobox
cd ~/chatgpt-distrobox
./install.sh
```

Open **ChatGPT (Distrobox)** from your applications menu and sign in. The
installer creates a container named `chatgpt`, installs the latest official RPM,
and exports its launcher. It requests administrator access inside the container
for package installation. Keep the checkout under your home so the container
can read the bundled public key.

If a `chatgpt` container already exists, the installer reuses it only if it is
Fedora 44. It never replaces an existing container. To use a different name:

```bash
./install.sh --name chatgpt-test
```

If you already have ChatGPT installed in Fedora 44 Distrobox, you can keep using
it as-is and follow the update instructions below. No reinstall is necessary.

## Easy updates on Bazzite

`ujust update` can update ChatGPT alongside your other packages. Some systems
disable Distrobox updates in `/etc/uupd/config.json`. To enable them once:

```bash
cd ~/chatgpt-distrobox
sudo python3 scripts/enable-ujust-updates.py
```

The helper changes only `modules.distrobox.disable` to `false`, preserves other
settings, and saves a timestamped backup. It does nothing if already enabled.
It enables updates for **all Distrobox containers**, including scheduled uupd
runs when those are enabled. It does not run an update itself.

Then use your usual command:

```bash
ujust update
```

Quit ChatGPT before updating, then reopen it to use the updated app and bundled
Codex. Verify the effective setting with `uupd config-dump`.

## Updates on other desktops

Update the container and its packages:

```bash
distrobox upgrade chatgpt
```

Or update only ChatGPT:

```bash
distrobox enter -n chatgpt -- sudo dnf upgrade --refresh chatgpt
```

Substitute your container name if you changed it. OpenAI's RPM configures its
signed update repository; later versions come directly from OpenAI. OpenAI
documents Linux updates through the distribution package manager, rather than
an in-app updater. The standalone Codex CLI is a separate installation and
updates independently.

## How it works

The installer uses `registry.fedoraproject.org/fedora-toolbox:44`. Inside that
container it downloads the architecture-appropriate RPM from OpenAI over HTTPS
and requires DNF to verify its signature using the bundled official public key.
It then uses `distrobox-export` to create the host desktop launcher.

Distrobox integrates with your home directory, desktop, devices, and host
environment. Treat the app as having normal user access; this is not a security
sandbox. The app runs inside the container, so tools installed only on the host
may need additional integration. See [troubleshooting](docs/troubleshooting.md)
and [security and verification](docs/security.md).

## Remove

Quit ChatGPT, remove its exported launcher, then remove the container:

```bash
distrobox enter -n chatgpt -- distrobox-export --app chatgpt --delete
distrobox stop chatgpt
distrobox rm chatgpt
```

Removing a container deletes everything installed in it. These commands retain
the app's configuration and work data in your shared home. They do not change
the global uupd setting. Keep any container containing other work you still need.

## Development

See [Contributing](CONTRIBUTING.md). The related
[ChatGPT Flatpak project](https://github.com/geoffbelknap/chatgpt-flatpak) uses a
different installation and update mechanism; this project works independently.
