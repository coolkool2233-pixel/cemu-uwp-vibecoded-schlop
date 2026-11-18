#!/usr/bin/env python3
"""Apply the shipped patch to pristine pinned files and run native selection checks."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile
from package_identity_test import MANIFEST, validate

BASE = "522d3498b5a8b3854d01909950c3738de5c94aa2"
ROOT = Path(__file__).resolve().parents[1]
PATCHES = [ROOT / "patches/0001-botw-full-preload.patch",
           ROOT / "patches/0002-independent-xbox-package.patch"]


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, stdout=subprocess.PIPE).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Cemu-UWP clone containing the pinned commit")
    parser.add_argument("--cxx", default="g++", help="C++17 compiler (default: g++)")
    args = parser.parse_args()
    source = args.source.resolve()
    # Always read committed inputs, so this also works with a patched/dirty checkout.
    run("git", "cat-file", "-e", BASE + "^{commit}", cwd=source)
    with tempfile.TemporaryDirectory(prefix="botw-preload-") as directory:
        tree = Path(directory)
        run("git", "init", "--quiet", cwd=tree)
        old_paths = {name for patch in PATCHES
                     for name in re.findall(r"^--- a/(.+)$", patch.read_text(), flags=re.MULTILINE)}
        for name in old_paths:
            destination = tree / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(run("git", "show", BASE + ":" + name, cwd=source))
        original_manifest = (tree / MANIFEST).read_bytes()
        for patch in PATCHES:
            run("git", "apply", "--check", "--whitespace=error-all", str(patch), cwd=tree)
            run("git", "apply", str(patch), cwd=tree)
        print("PASS: both patches apply cleanly to pinned upstream files", flush=True)
        validate(tree, original_manifest)
        pipeline = (tree / "src/Cafe/HW/Latte/Renderer/D3D12/D3D12PipelineCache.cpp").read_text()
        start = pipeline.index("uint32 D3D12PipelineCache::BeginPreload(")
        end = pipeline.index("\nbool D3D12PipelineCache::UpdatePreload(", start)
        (tree / "begin_preload.inc").write_text(pipeline[start:end])
        executable = tree / "preload-test"
        run(args.cxx, "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
            "-I", str(tree / "src"), "-I", str(tree), str(ROOT / "tests/preload_test.cpp"),
            "-o", str(executable))
        print(run(str(executable)).decode(), end="")
        for patch in reversed(PATCHES):
            run("git", "apply", "--reverse", "--check", str(patch), cwd=tree)
            run("git", "apply", "--reverse", str(patch), cwd=tree)
        assert (tree / MANIFEST).read_bytes() == original_manifest
        print("PASS: both patches reverse in order and restore the original manifest bytes")


if __name__ == "__main__":
    main()
