#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: ./install.sh [--name CONTAINER]"
    echo "Install the official ChatGPT RPM in Fedora 44 Distrobox (default: chatgpt)."
}

name=chatgpt
while (($#)); do
    case "$1" in
        --name) [[ $# -ge 2 ]] || { usage >&2; exit 2; }; name=$2; shift 2 ;;
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
echo "On Bazzite, see README.md to include Distroboxes in ujust update."
