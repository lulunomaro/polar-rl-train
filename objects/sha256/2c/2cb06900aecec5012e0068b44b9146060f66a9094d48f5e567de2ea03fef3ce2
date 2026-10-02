"""Extract and verify ONLY the uploaded independent package; source check is read-only."""
import hashlib, json, pathlib, subprocess, tarfile
root=pathlib.Path('/home/egde/rl_repair_packages')
name='MOD4_RL_FIX_20260913_1500'
archive=root/(name+'.tar.gz')
expected='e4c39e4fbd3b6c85b393f6a19fad11c2016408e88c189557a98c00dd14cd11b6'
actual=hashlib.sha256(archive.read_bytes()).hexdigest()
if actual!=expected:raise ValueError('archive checksum mismatch')
target=root/name
if root.resolve()!=root or target.exists():raise ValueError('unsafe/existing extraction directory')
with tarfile.open(archive,'r:gz') as tf:
 members=tf.getmembers()
 if sum(m.size for m in members)>100_000_000:raise ValueError('unexpected expanded size')
 for m in members:
  rel=pathlib.PurePosixPath(m.name)
  if rel.is_absolute() or '..' in rel.parts or rel.parts[0]!=name or not m.isfile():
   raise ValueError('unexpected archive member')
  if target not in (root/m.name).resolve().parents:raise ValueError('path escape')
 # Each member is a regular file with a checked destination; no symlink/hardlink extraction.
 for m in members:
  out=root/m.name;out.parent.mkdir(parents=True,exist_ok=True)
  with out.open('xb') as f:f.write(tf.extractfile(m).read())
checked=0
for line in (target/'SHA256SUMS').read_text().splitlines():
 digest,rel=line.split('  ',1);p=target/rel
 if target not in p.resolve().parents:raise ValueError('checksum path escape')
 if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('file checksum mismatch: '+rel)
 checked+=1
# No --create flag: this call ONLY reads source/runtime/package hashes.
check=subprocess.run(['python3',str(target/'tools/stage_candidate.py')],capture_output=True,text=True,timeout=30)
result={'package_directory':str(target),'archive':str(archive),'archive_sha256':actual,
 'files_verified':checked,'source_check_rc':check.returncode,
 'source_check_stdout':check.stdout,'source_check_stderr':check.stderr,
 'applied_to_training':False,'gpu_simulation_started':False}
(root/(name+'_upload_receipt.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
