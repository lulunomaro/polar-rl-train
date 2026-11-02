"""Store each old byte sequence once, verify the ZIP, then remove expanded copies."""
from pathlib import Path
import hashlib, json, os, re, shutil, stat, time, zipfile

scope = Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
root = scope / 'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
root = root.resolve(strict=True)
assert root.is_relative_to(scope.resolve(strict=True) / 'workspace')
assert not root.is_symlink() and not root.is_junction()
receipts = scope / 'receipts'
migration = json.loads((receipts / (root.name + '.verified463.json')).read_bytes())
assert migration['passed'] and migration['bytes'] == 75156369407
assert (receipts / 'MIGRATION462_COMPLETE.json').exists(), 'Wait for the owned migration to finish'
history = scope / 'history'
history.mkdir(exist_ok=True)
archive = history / 'h1_closed_stages_through_20261031.zip'
index = history / 'h1_closed_stages_through_20261031.index.jsonl'
complete = receipts / 'COMPACTION_COMPLETE.json'
assert not archive.exists() and not index.exists() and not complete.exists()

def old_stage(name):
    dates = re.findall(r'2026\d{4}', name)
    return bool(dates and max(dates) < '20261101') or name.startswith((
        'E3_bridge_continuation', 'H1_step270_native32_',
        'full20k_native180_', 'relocated_forensic_originals'))

rows = []
with Path(migration['file_manifest']).open(encoding='utf-8') as f:
    for line in f:
        row = json.loads(line)
        rel = Path(row['relative_path'])
        if len(rel.parts) > 1 and old_stage(rel.parts[0]):
            rows.append(row)
stage_names = sorted({Path(row['relative_path']).parts[0] for row in rows})
unique = {}
for row in rows:
    unique.setdefault(row['SHA256'], row)
assert len(stage_names) == 336 and len(rows) == 381470 and len(unique) == 67543
for name in stage_names:
    path = root / name
    assert path.is_dir() and not path.is_symlink() and not path.is_junction()

started = time.time()
original_bytes = sum(row['bytes'] for row in rows)
with index.open('x', encoding='utf-8') as out:
    for row in rows:
        out.write(json.dumps(row, ensure_ascii=False) + '\n')
text = {'.py', '.json', '.jsonl', '.log', '.md', '.txt', '.xml', '.csv', '.yaml', '.yml', '.toml', '.sh', '.ps1', '.urdf', '.usda'}
total, last = 0, time.monotonic()
with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_STORED, allowZip64=True) as z:
    z.write(index, 'PATHS_SHA256.jsonl', compress_type=zipfile.ZIP_DEFLATED, compresslevel=1)
    for i, (sha, row) in enumerate(unique.items(), 1):
        src = root / row['relative_path']
        assert src.resolve().is_relative_to(root) and not src.is_symlink()
        assert src.stat().st_size == row['bytes'], str(src)
        member = zipfile.ZipInfo('objects/' + sha)
        member.compress_type = zipfile.ZIP_DEFLATED if src.suffix.lower() in text else zipfile.ZIP_STORED
        member._compresslevel = 1
        h = hashlib.sha256()
        with src.open('rb') as inp, z.open(member, 'w', force_zip64=True) as out:
            for block in iter(lambda: inp.read(4 * 1024 * 1024), b''):
                h.update(block)
                out.write(block)
        assert h.hexdigest() == sha, 'Source changed since migration: ' + str(src)
        total += row['bytes']
        if time.monotonic() - last > 15:
            print(json.dumps(dict(status='ARCHIVING_UNIQUE_CONTENTS', objects=i, total_objects=len(unique), bytes=total)), flush=True)
            last = time.monotonic()

print('VERIFY_ARCHIVE_BEFORE_REMOVING_EXPANDED_COPIES', flush=True)
with zipfile.ZipFile(archive) as z:
    assert len(z.infolist()) == len(unique) + 1
    for i, (sha, row) in enumerate(unique.items(), 1):
        h = hashlib.sha256()
        with z.open('objects/' + sha) as inp:
            for block in iter(lambda: inp.read(4 * 1024 * 1024), b''):
                h.update(block)
        assert h.hexdigest() == sha, 'Archive verification failed: ' + sha
        if time.monotonic() - last > 15:
            print(json.dumps(dict(status='VERIFY_ARCHIVE', objects=i, total_objects=len(unique))), flush=True)
            last = time.monotonic()

with (receipts / 'COMPACTION_VERIFIED_BEFORE_DELETE.json').open('x', encoding='utf-8') as f:
    json.dump(dict(passed=True, epoch=time.time(), stages=stage_names, original_files=len(rows), original_bytes=original_bytes,
                   unique_objects=len(unique), unique_bytes=total, archive=str(archive), archive_bytes=archive.stat().st_size,
                   index=str(index), every_archived_object_SHA256_verified=True, model_deserializations=0, physics=0), f, indent=2)

def remove_readonly(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)

deleted = 0
for name in stage_names:
    target = (root / name).resolve(strict=True)
    assert target.parent == root and target.name == name and old_stage(name)
    assert not target.is_symlink() and not target.is_junction()
    shutil.rmtree(target, onexc=remove_readonly)
    deleted += 1
    if deleted % 20 == 0:
        print(json.dumps(dict(status='REMOVING_VERIFIED_EXPANDED_STAGES', stages=deleted, total=len(stage_names))), flush=True)

cache_files, cache_bytes = 0, 0
for directory, dirs, files in os.walk(root, followlinks=False):
    for name in list(dirs):
        if name == '__pycache__':
            cache = Path(directory, name)
            assert cache.resolve().is_relative_to(root) and not cache.is_junction() and not cache.is_symlink()
            for p in cache.rglob('*'):
                if p.is_file(): cache_files += 1; cache_bytes += p.stat().st_size
            shutil.rmtree(cache, onexc=remove_readonly)
            dirs.remove(name)

remaining_files, remaining_bytes = 0, 0
for directory, dirs, files in os.walk(root, followlinks=False):
    for name in files:
        remaining_files += 1
        remaining_bytes += Path(directory, name).stat().st_size
result = dict(passed=True, started_epoch=started, completed_epoch=time.time(), root=str(root),
              previous_files=migration['files'], previous_bytes=migration['bytes'],
              archived_stages=len(stage_names), expanded_old_files_removed=len(rows),
              unique_objects=len(unique), archive=str(archive), archive_bytes=archive.stat().st_size,
              index=str(index), all_archive_objects_SHA256_verified=True,
              remaining_workspace_files=remaining_files, remaining_workspace_bytes=remaining_bytes,
              deleted_cache_files=cache_files, deleted_cache_bytes=cache_bytes,
              net_bytes_reclaimed=original_bytes - archive.stat().st_size - index.stat().st_size + cache_bytes,
              model_deserializations=0, training_or_physics_runs=0, other_workspaces_changed=0,
              historical_failed_reports_and_sources_preserved=True)
with complete.open('x', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result), flush=True)
