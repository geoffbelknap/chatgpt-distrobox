#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: ./install.sh [--name CONTAINER] [--enable-ujust-updates]"
    echo "Install the official ChatGPT RPM in Fedora 44 Distrobox (default: chatgpt)."
}

name=chatgpt
enable_ujust=false
while (($#)); do
    case "$1" in
        --name) [[ $# -ge 2 ]] || { usage >&2; exit 2; }; name=$2; shift 2 ;;
        --enable-ujust-updates) enable_ujust=true; shift ;;
        --help|-h) usage; exit 0 ;;
        *) usage >&2; exit 2 ;;
    esac
done
[[ $name =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]] || {
    echo "Invalid container name: $name" >&2; exit 2;
}
if ((EUID == 0)); then
    echo "Run this installer as your regular user, without sudo." >&2
    exit 1
fi
command -v distrobox >/dev/null || {
    echo "Install Distrobox and Podman (or Docker) first." >&2; exit 1;
}
case $(uname -m) in
    x86_64|aarch64) ;;
    *) echo "Supported architectures: x86_64 and aarch64." >&2; exit 1 ;;
esac
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
containers=$(distrobox list --no-color)
if awk -F '|' -v name="$name" '
    {gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); if ($2 == name) found=1}
    END {exit !found}' <<< "$containers"; then
    echo "Using existing container: $name (its Fedora version will be checked)."
else
    distrobox create --yes --name "$name" \
        --image registry.fedoraproject.org/fedora-toolbox:44
fi

# Distrobox shares the user's home. Keep this checkout under your home directory
# so the container can read the public signing key too.
distrobox enter --name "$name" -- bash -s -- "$project_dir/keys/openai.asc" \
    < "$project_dir/scripts/install-in-container.sh"
echo "Installed. Open ChatGPT (Distrobox) from your applications menu."
echo "Updates: distrobox upgrade $name"
if [[ $enable_ujust == true ]]; then
    sudo python3 "$project_dir/scripts/enable-ujust-updates.py"
elif command -v uupd >/dev/null && [[ -f /etc/uupd/config.json ]]; then
    if python3 -c 'import json; import sys; sys.exit(json.load(open("/etc/uupd/config.json")).get("modules", {}).get("distrobox", {}).get("disable") is not False)'; then
        echo "Distrobox updates are already included in ujust update."
    elif [[ -t 1 ]] && { read -r -p 'Include all Distroboxes in ujust update? [y/N] ' answer </dev/tty; }; then
        case $answer in
            y|Y|yes|YES) sudo python3 "$project_dir/scripts/enable-ujust-updates.py" ;;
            *) echo "Update integration left unchanged." ;;
        esac
    else
        printf 'To enable ujust updates later: sudo python3 %q\n' "$project_dir/scripts/enable-ujust-updates.py"
    fi
fi
