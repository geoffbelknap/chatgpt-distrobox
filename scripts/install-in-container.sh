#!/usr/bin/env bash
set -euo pipefail

if [[ -z ${CONTAINER_ID:-} ]]; then
    echo "This script must run inside Distrobox via install.sh." >&2
    exit 1
fi
# shellcheck disable=SC1091
source /etc/os-release
if [[ $ID != fedora || $VERSION_ID != 44 ]]; then
    echo "Expected Fedora 44; refusing to modify this container." >&2
    exit 1
fi
key=${1:?Path to bundled OpenAI signing key required}
[[ -r $key ]] || {
    echo "Signing key is not readable. Keep the checkout in your shared home." >&2
    exit 1
}
case $(uname -m) in
    x86_64) arch=x86_64 ;;
    aarch64) arch=aarch64 ;;
    *) echo "Unsupported architecture." >&2; exit 1 ;;
esac
sudo dnf install -y curl ca-certificates
download_dir=$(mktemp -d)
trap 'rm -rf -- "$download_dir"' EXIT
curl --proto '=https' --proto-redir '=https' --tlsv1.2 --fail --location --retry 3 \
    --output "$download_dir/chatgpt.rpm" \
    "https://persistent.oaistatic.com/codex-app-prod/linux/rpm/latest/chatgpt.$arch.rpm"
# Import the official public key in the container's RPM database only.
# DNF normally exempts local RPMs from GPG checking; explicitly enable it.
sudo rpm --import "$key"
sudo dnf --setopt=localpkg_gpgcheck=1 install -y "$download_dir/chatgpt.rpm"
distrobox-export --app chatgpt --export-label '(Distrobox)'
rpm -q chatgpt
