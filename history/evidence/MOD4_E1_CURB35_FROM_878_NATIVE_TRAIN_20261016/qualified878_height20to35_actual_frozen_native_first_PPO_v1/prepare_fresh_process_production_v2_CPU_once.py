"""Reuse successful prechecks/native, keep startup-only zero-clock guards unchanged."""
from pathlib import Path
import os,ast,hashlib,json,shutil,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;B=D/'production_fresh_process_v2_payload';old=D/'payload';assert not B.exists();shutil.copytree(old,B,ignore=shutil.ignore_patterns('__pycache__'))
v=json.loads((D/'reports/POSTPRECHECK_SAME_PROCESS_STARTUP_RESTORE_REJECTION_ACTUAL_CLOSED_CPU_COLLECTION.json').read_bytes());assert not v['actual_own_processes'] and v['canonical']['active'] is None and all(x['actual_fcntl_free'] for x in v['original_locks']);segments=v['canonical']['segments'];assert len(segments)==2;spent=sum(x['charged_seconds'] for x in segments);assert 0<spent<2700-600
native=next(x for x in v['models'] if x['all17Adam']==660400);ck=torch.load(native['local_path'],map_location='cpu',weights_only=False);identity={k:z for k,z in ck['E1_terrain_state'].items() if k not in ('spawn_xy','reset_expected_q','episode')};assert identity['CURB_height_m']==.035
admit=dict(epoch=time.time(),source_SHA='268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1',native144_CPU_passed=True,native_checkpoint_SHA=native['SHA'],prechecks128x2_20kx4_actual_CPU_finite=True,precheck_models=[{k:x[k] for k in ('path','bytes','SHA','all17Adam')} for x in v['models']],admitted_new35_terrain_identity=identity,old_failed_scope_preserved_not_restarted=True,old_parent477807_actual_absent_locksfree_and_settled=True,actual_already_charged_seconds=spent,remaining_same_scope_cap_seconds=2700-spent,no_source_native_or_precheck_replay=True,zero_clock_startup_guard_not_relaxed_or_counter_reset=True,repair='Fresh physical process for production; source878 fullrestore only at original startup zero clock',not_reusing_discarded_weights=True)
(B/'PRIOR_NATIVE_PRECHECK_AND_CLOSED_COST_ACTUAL.json').write_text(json.dumps(admit,indent=2))
for n in ('curb35_production_worker_v2.py','curb35_production_owner_v2.py'):
 s=(D/n).read_text(encoding='utf8');compile(s,n,'exec');shutil.copy2(D/n,B/n)
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='resume_e1_new_episode' for n in ast.walk(ast.parse((B/'curb35_production_worker_v2.py').read_text())))
prior=json.loads((old/'PAYLOAD_MANIFEST.json').read_bytes())['files'];H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for row in prior:assert H(B/row['relative'])==row['SHA']
files=[dict(relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(B.rglob('*')) if p.is_file() and p.name!='PAYLOAD_MANIFEST.json' and '__pycache__' not in p.parts];(B/'PAYLOAD_MANIFEST.json').write_text(json.dumps(dict(files=files),indent=2))
(D/'reports/FRESH_PROCESS_PRODUCTION_V2_SOURCE_NATIVE_PRECHECK_REUSE_CPU_ACTUAL.json').write_text(json.dumps(admit,indent=2));print(json.dumps(dict(old_scope_actual_charged=spent,remaining=2700-spent,all_original435_source_bytes_exact=True,no_Guard_relaxed_native_or_precheck_repeated=True,new_files=3)))
