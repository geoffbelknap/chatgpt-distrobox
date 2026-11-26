#!/usr/bin/env bash
# Keep execution inside main so a partial download cannot run setup commands.
main() (
    set -euo pipefail
    if [[ ${1:-} == --help || ${1:-} == -h ]]; then
        echo "Usage: bootstrap.sh [--name CONTAINER] [--enable-ujust-updates]"
        echo "Download and install ChatGPT for Distrobox without Git."
        return 0
    fi
    if ((EUID == 0)); then
        echo "Run this installer as your regular user, without sudo." >&2
        return 1
    fi
    for tool in curl tar python3; do
        command -v "$tool" >/dev/null || {
            echo "Install $tool first." >&2; return 1;
        }
    done
    install_dir="$HOME/.local/share/chatgpt-distrobox"
    mkdir -p -- "$HOME/.local/share"
    stage=$(mktemp -d "$HOME/.local/share/.chatgpt-distrobox.XXXXXX")
    trap 'rm -rf -- "$stage"' EXIT
    # Download a single snapshot before executing anything from it. All files,
    # including the signing key, come from the same repository revision.
    curl --proto '=https' --proto-redir '=https' --tlsv1.2 --fail --location --retry 3 \
        --output "$stage/source.tar.gz" \
        https://codeload.github.com/geoffbelknap/chatgpt-distrobox/tar.gz/refs/heads/main
    mkdir "$stage/source"
    tar -xzf "$stage/source.tar.gz" -C "$stage/source" --strip-components=1 \
        chatgpt-distrobox-main/install.sh \
        chatgpt-distrobox-main/scripts/install-in-container.sh \
        chatgpt-distrobox-main/scripts/enable-ujust-updates.py \
        chatgpt-distrobox-main/keys/openai.asc
    mkdir -p -- "$install_dir"
    cp -R -- "$stage/source/." "$install_dir/"
    bash "$install_dir/install.sh" "$@"
)

main "$@"
