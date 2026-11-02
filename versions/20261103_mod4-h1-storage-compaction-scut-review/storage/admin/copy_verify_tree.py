"""Verify a storage relocation without importing models or executing task code."""
from pathlib import Path
import argparse, hashlib, json, os, time

p = argparse.ArgumentParser()
p.add_argument('--source', required=True, type=Path)
p.add_argument('--destination', required=True, type=Path)
p.add_argument('--receipt', required=True, type=Path)
a = p.parse_args()
source, destination = a.source.resolve(strict=True), a.destination.resolve(strict=True)
allowed_source = Path('C:/Users/lulu/Desktop/claude/mjcf').resolve(strict=True)
allowed_destination = Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102/workspace').resolve(strict=True)
assert source.is_relative_to(allowed_source) and source != allowed_source
assert destination.is_relative_to(allowed_destination) and destination != allowed_destination
assert source.name == destination.name and not a.receipt.exists()

def inventory(root):
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            child = Path(directory, name)
            assert not child.is_symlink() and not child.is_junction(), str(child)
            if name == '.git':
                allowed_git = source / 'MOD4_UNISUPERMIMIC_WHEEL_LEG_SINGLE4090_TEST_20261026/upstream/.git'
                assert source.name == 'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
                assert child.relative_to(root) == allowed_git.relative_to(source), 'Unexpected embedded Git repository'
        for name in files:
            file = Path(directory, name)
            assert not file.is_symlink(), str(file)
            st = file.stat()
            result[file.relative_to(root).as_posix()] = (st.st_size, st.st_mtime_ns)
    return result

def sha(file):
    h = hashlib.sha256()
    with file.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

started = time.time()
original = inventory(source)
copied = inventory(destination)
assert set(original) == set(copied), 'Source/destination file inventory differs'
manifest = a.receipt.with_suffix('.files.jsonl')
total = 0
last = time.monotonic()
with manifest.open('x', encoding='utf-8') as out:
    for i, (rel, (size, mtime)) in enumerate(sorted(original.items()), 1):
        src, dst = source / rel, destination / rel
        assert copied[rel][0] == size, rel
        srcsha, dstsha = sha(src), sha(dst)
        assert srcsha == dstsha, rel
        assert (src.stat().st_size, src.stat().st_mtime_ns) == (size, mtime), 'Source changed: ' + rel
        out.write(json.dumps(dict(relative_path=rel, bytes=size, SHA256=srcsha), ensure_ascii=False) + '\n')
        total += size
        if time.monotonic() - last > 10:
            print(json.dumps(dict(status='VERIFYING', files=i, total_files=len(original), bytes=total)), flush=True)
            last = time.monotonic()
assert inventory(source) == original, 'Source mutated during relocation'
assert set(inventory(destination)) == set(original), 'Destination mutated during relocation'
receipt = dict(passed=True, source=str(source), destination=str(destination), files=len(original),
               bytes=total, started_epoch=started, verified_epoch=time.time(),
               verification='All source/destination files have equal SHA256; source inventory and metadata unchanged',
               model_deserializations=0, SDK=0, physics=0, original_files_deleted=False,
               file_manifest=str(manifest), file_manifest_SHA256=sha(manifest))
with a.receipt.open('x', encoding='utf-8') as out:
    json.dump(receipt, out, ensure_ascii=False, indent=2)
print(json.dumps(receipt, ensure_ascii=False), flush=True)
