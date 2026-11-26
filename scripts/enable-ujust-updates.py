#!/usr/bin/env python3
"""Enable uupd's Distrobox module, preserving other settings and a backup."""

import argparse
import datetime
import json
from pathlib import Path
import shutil
import sys


def enable(config: Path) -> Path | None:
    if config.is_symlink():
        raise ValueError("Refusing to modify a symlink")
    data = json.loads(config.read_text())
    module = data.setdefault("modules", {}).setdefault("distrobox", {})
    if module.get("disable") is False:
        return None
    module["disable"] = False
    # Serialize and validate before touching the existing configuration.
    rendered = json.dumps(data, indent=4) + "\n"
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = config.with_name(config.name + ".backup-" + stamp)
    shutil.copy2(config, backup)
    try:
        config.write_text(rendered)
        assert json.loads(config.read_text())["modules"]["distrobox"]["disable"] is False
    except BaseException:
        shutil.copy2(backup, config)
        raise
    return backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("/etc/uupd/config.json"))
    args = parser.parse_args()
    try:
        backup = enable(args.config)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        print(f"Could not enable Distrobox updates: {exc}", file=sys.stderr)
        return 1
    if backup:
        print(f"Enabled Distrobox updates. Backup: {backup}")
    else:
        print("Distrobox updates are already enabled; no changes needed.")
    print("Your next ujust update will include all Distrobox containers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
