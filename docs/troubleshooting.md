# Troubleshooting

## App not in the desktop menu

Re-export the launcher:

```bash
distrobox enter -n chatgpt -- distrobox-export --app chatgpt --export-label '(Distrobox)'
```

If necessary, log out and back in to refresh the desktop menu. A terminal launch
can reveal errors:

```bash
distrobox enter -n chatgpt -- chatgpt
```

## Duplicate ChatGPT entries

Native, Flatpak, and Distrobox installations can each export a launcher and run
their own bundled Codex backend. Quit unused copies before testing. Removing
the Flatpak does not remove a manually exported Distrobox launcher for it;
inspect `~/.local/share/applications/` and remove only the obsolete entry. Keep
the launcher that runs `distrobox-enter -n chatgpt -- chatgpt`.

## ujust update skips ChatGPT

Run `uupd config-dump` and check that `modules.distrobox.disable` is `false`.
The helper in the README enables this setting without replacing other settings.
This requires a host administrator password. For one app update, use:

```bash
distrobox enter -n chatgpt -- sudo dnf upgrade --refresh chatgpt
```

If an update fails, read the Distrobox section in `ujust update` output. Enabling
the module does not guarantee a container with broken repositories can update.

## Unsupported existing container

The installer accepts Fedora 44. For another distribution or release, use a
different container name, such as `./install.sh --name chatgpt-test`. It does
not replace or delete an existing container.

## Wayland, shortcuts, files, and host tools

Keep Electron's sandbox enabled. OpenAI currently documents XWayland as the
default and native Wayland as experimental. To try native Wayland, quit the app:

```bash
distrobox enter -n chatgpt -- chatgpt --ozone-platform=wayland
```

The desktop may ask permission for global shortcuts. Approve a suitable shortcut
or cancel it. Home files are shared with the container; software installed only
on the host is not necessarily available on the container's PATH. Verify login,
file access, voice, and any host integrations in an interactive session.

See [OpenAI's Linux guide](https://learn.chatgpt.com/docs/linux/linux-app).
