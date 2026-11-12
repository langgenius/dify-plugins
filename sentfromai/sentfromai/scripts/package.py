"""Package only reviewed runtime files, then verify the official CLI's archive."""

import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
FILES = ("manifest.yaml", "main.py", "requirements.txt", "README.md", "PRIVACY.md", "SENDING_CONTROLS.md", "LICENSE")
DIRECTORIES = {"lib": {".py"}, "provider": {".py", ".yaml"}, "tools": {".py", ".yaml"}, "_assets": {".png"}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", required=True, help="Path to official Dify plugin CLI")
    args = parser.parse_args()
    cli = shutil.which(args.cli)
    if not cli:
        raise SystemExit("Dify CLI not found")
    manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text())
    output = ROOT / "build"
    output.mkdir(exist_ok=True)
    package = output / f"sentfromai-{manifest['version']}.difypkg"
    expected = set(FILES)
    for folder, suffixes in DIRECTORIES.items():
        for file in (ROOT / folder).iterdir():
            if file.is_symlink():
                raise SystemExit("Symlinks are not allowed in runtime directories")
            if file.is_file() and file.suffix in suffixes:
                expected.add(file.relative_to(ROOT).as_posix())
    with tempfile.TemporaryDirectory(prefix="dify-stage-", dir=output) as staging:
        stage = Path(staging) / "sentfromai"
        for name in sorted(expected):
            source = ROOT / name
            if source.is_symlink():
                raise SystemExit("Runtime files must not be symlinks")
            dest = stage / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        subprocess.run([cli, "plugin", "package", str(stage), "-o", str(package)], check=True)
        with zipfile.ZipFile(package) as archive:
            files = [i.filename for i in archive.infolist() if not i.is_dir()]
            if len(files) != len(set(files)) or set(files) != expected:
                raise SystemExit("Archive contents differ from runtime allowlist")
            for name in files:
                if archive.read(name) != (stage / name).read_bytes():
                    raise SystemExit("Archive file differs from reviewed source")
        # Exercise the actual SDK loader against the bytes we will distribute.
        unpacked = Path(staging) / "unpacked"
        with zipfile.ZipFile(package) as archive:
            archive.extractall(unpacked)  # All names already matched the explicit allowlist.
        import sys
        subprocess.run([sys.executable, "-c",
            "from dify_plugin import DifyPluginEnv; "
            "from dify_plugin.core.plugin_registration import PluginRegistration; "
            "r=PluginRegistration(DifyPluginEnv()); "
            "assert len(r.tools_mapping['sentfromai'][2]) == 9; "
            "print('Packaged SDK load: 9 tools passed')"], cwd=unpacked, check=True)
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(f"{digest}  {package.name}\n")
    print(f"Runtime archive: {len(expected)} files; SHA-256 {digest}")


if __name__ == "__main__":
    main()
