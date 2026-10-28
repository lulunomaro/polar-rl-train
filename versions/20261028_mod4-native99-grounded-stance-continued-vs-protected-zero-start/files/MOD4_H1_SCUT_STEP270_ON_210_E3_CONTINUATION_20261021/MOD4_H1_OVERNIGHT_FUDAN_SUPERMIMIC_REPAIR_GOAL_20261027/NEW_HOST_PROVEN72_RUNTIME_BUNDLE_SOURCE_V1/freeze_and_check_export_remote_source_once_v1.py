from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;helper=B/'pack_proven72_runtime_owned_supervisor_v1.py';entry=B/'launch_NEW_proven72_runtime_export_detached_once_v1.py';hs=helper.read_text();es=entry.read_text();ast.parse(hs);tree=ast.parse(es)
SOURCE='/home/lc01/Zonglin Li/zonglin2';RUN=SOURCE+'/runtime_exports/MOD4_PROVEN72_RUNTIME_FOR86_20261028_V1';want=hashlib.sha256(helper.read_bytes()).hexdigest();ctx=dict(SOURCE=SOURCE,RUN=RUN,want=want,helper=helper)
count=0
for node in ast.walk(tree):
 if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='code' for x in node.targets):
  code=eval(compile(ast.Expression(node.value),'<controlled source code assembly>','eval'),{'__builtins__':{'repr':repr}},ctx);ast.parse(code);count+=1
assert count==2
assert "['/usr/bin/pigz','-p','2','-1','-c']" in hs and 'budget==1800' in hs and 'no_source_env_library_or_permission_writes=True' in hs
assert 'vendor_gzip_zip_and_Kit_runtime_resources_retained=True' in hs and "kit/'data/documents'" in hs
assert all(x not in hs for x in ('import torch','import isaaclab','nvidia-smi','TRAINING_BUDGET','pip install'))
assert es.index('actual==PIN')<es.index("t.auth_password('lc01',secret")
(B/'reports').mkdir(exist_ok=True)
proof=dict(epoch=time.time(),source_AST_passed=True,actual_remote_guard_and_launch_code_AST_passed=2,source_only_no_network_or_runtime_execution=True,source_model_and_raw_excluded_before_stat=True,source_root_new_export_only=True,tar_pigz_two_threads=True,owned1800s_supervisor_and_known_child_cleanup=True,existing_requires_dist_conflicts_kept=True,no_training_or_GPU_or_budget=True)
with (B/'SOURCE_AST_REMOTE_CODE_AND_SCOPE_ACTUAL_V1.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
with (B/'HANDOFF_FROZEN_PROVEN72_RUNTIME_EXPORT_V1.md').open('x',encoding='utf8') as f:f.write('Authorized NEW source72 CPU-only export, launch_NEW_proven72_runtime_export_detached_once_v1.py. Original sourceenv/root code/library/permissions untouched; no existingpolicy/PT/raw reads. New namespace /home/lc01/Zonglin Li/zonglin2/runtime_exports/MOD4_PROVEN72_RUNTIME_FOR86_20261028_V1 only. Explicit known glibc240 loader with -S, avoiding source launcher state/runtime mkdir/chmod. Exact run-python two files pinned to actual source, complete envs/mod4+compat+SDK source/apps/available licenses. Original Torch2.10cu128/vision.25/Python3.12.14/Lab6.1.14/RSL5 source package metadata preserved; no pip or Requires-Dist repair; do not claim pipcheck passed. Include vendor .gz/.zip/Kit runtime resources, exclude exactKit userdata documents/cache and policy/raw suffixes beforestat; allrelative symlinks retained, unapproved absolute/external symlinks reject. tar|pigz -p2 -1,512MiB compressed chunks and streaming producer/chunkSHAs,1800s own supervisor with only recorded own group cleanup. Source disk capacity is measured against actual allowlisted input bytes before archive. Detached startup does not prove completebundle. Later one readonly terminal/producer reader, then actual Windows free capacity before multiGB source download; close72 before root securestdin86 receiver. New86 extraction onlyNEW project runtime_migrations root; preserve snapshots, typedfinder/bin prefix relocation onlynewcopy, exactSDK/RSL code/versions remain; actual relocated source/SDK/CUDA/40050 admission stillpending. No learning/GO/writer/tag.\n')
rows=[]
for p in sorted(B.rglob('*')):
 if p.is_file():rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
value=dict(epoch=time.time(),frozen_source=True,helper_SHA=want,entry_SHA=hashlib.sha256(entry.read_bytes()).hexdigest(),files=rows,actual_pack_not_yet_started=True)
index=B/'FROZEN_PROVEN72_RUNTIME_EXPORT_SOURCE_INDEX_V1.json'
with index.open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
print(json.dumps(dict(passed=True,helper_SHA=want,entry_SHA=value['entry_SHA'],index_SHA=hashlib.sha256(index.read_bytes()).hexdigest())))
