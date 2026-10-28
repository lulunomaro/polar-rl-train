"""Local text-only archive checkpoint; does not open model or runtime binaries."""
from pathlib import Path
import hashlib,json,time

B=Path(__file__).resolve().parent
L=B.parent
names=[
 'W35_210_ADAPTED40050_N20K_BOUNDED_SKILL_REGRESSION_SOURCE_V1',
 'W35_210_FIRST_ORIGINAL_GPU_NATIVE24_READONLY_SOURCE_V1',
 'W35_210_V2_PRECLOSE_EXCEPTION_DIAGNOSTIC_SOURCE_V1',
 'W35_210_V2_FIRST_PRECLOSE_EXCEPTION_READONLY_SOURCE_V1',
 'NEW86_CLONED_RUNTIME_CUDA_SMALL_SCENE_SOURCE_V1',
 'NEW86_CLONED_RUNTIME_CUDA_SMALL_SCENE_SOURCE_V2_PROJECT_ENV',
 'NORMAL_H1_PPO86B_400N50_NEW86_SOURCE_PREPARATION_V1',
]
out=B/'COMPLETED_ALL_SOURCE_ERRORS_REPORTS_FROZEN_INDEX_V1.json'
assert not out.exists()
cpu=json.loads((L/names[-1]/'reports/NORMAL_H1_TYPED40050_ORIGINAL_FULLSTATE_CPU_ACTUAL_V1.json').read_text())
assert cpu['passed'] is True
rows=[]
for name in names:
 root=L/name
 assert root.is_dir()
 for p in sorted(root.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts: continue
  if p.suffix.lower()=='.pt':
   # The existing producer receipt supplies the immutable binary evidence.
   witness=cpu['new_source']
   assert p.resolve()==Path(witness['path']).resolve()
   rows.append(dict(path=str(p),bytes=witness['bytes'],SHA=witness['SHA'],handling='existing actual producer witness; binary not opened'))
  else:
   assert p.suffix.lower() in ('.py','.json','.md','.txt','.log'), str(p)
   raw=p.read_bytes()
   rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),handling='complete original text/source'))
value=dict(kind='completed_child_210_and86_evidence_checkpoint_v1',epoch=time.time(),
 source_folders_frozen=names,files=rows,
 actual_status={
 'W35_V1':'actual env construction failed before fullrestore/native24; original missing preclose exception remains false',
 'W35_V2':'actual preclose RuntimeError: Two wheel colliders are required in mild_dr.py:53, before fullrestore/native24; original assertion and physics unchanged',
 'W35_V2_terminal':'worker was Z and supervisor S at the one original reader; final supervisor reap not reobserved by this local checkpoint',
 '86_V1':'refused before execution because explicit project HOME/XDG scope was absent; original source retained',
 '86_V2B':'actual metadata, CUDA tensor, SDK primitive cube 24 physics callbacks passed; not MOD4 native24/fullrestore/PPO/skill proof',
 'normal_H1':'actual typed original PPO86B source CPU migration and inverse fullstate proof passed; runtime, targetSDK, actualCUDA fullrestore/native24/PPO and skill still pending'},
 no_model_or_binary_read=True,no_network_or_GPU_or_ledger=True,
 child_record_experiment_or_trial_tag_calls=0,
 Git='ordinary/archive decision and remote verification owned by root; this checkpoint is local pending',
 next_scopes_explicit_pending=['NORMAL_H1_PPO86B_400N50_NEW86_RUNTIME_SOURCE_V1','W35_210_N1_ASSET_COLLIDER_DIAGNOSTIC_SOURCE_V1'],
 no_old_frozen_file_modified=True)
out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(B/'HANDOFF.md').write_text('All seven source/report folders in the index are now frozen. Earlier source-only UNUSED labels remain original bytes; this new index records the subsequent actual outcomes without overwriting them. W35 V1/V2 did not reach model fullrestore or native24. V2 preserved the true pre-AppClose error: two wheel colliders required. New86 V2B passed CUDA plus primitive SDK scene only. Normal-H1 typed source CPU proof passed with Adam832460 and constructor LR0.00038443359375000017; model binary is indexed solely from its actual producer receipt. No child trial/tag was generated. All source, false/error, complete reader text and tool receipts listed here remain pending root Git verification. Next runtime and N1 diagnostic work uses separate directories; no old once is rearmed.\n',encoding='utf-8')
print(json.dumps(dict(index=str(out),SHA=hashlib.sha256(out.read_bytes()).hexdigest(),files=len(rows),no_binary_read=True)))
