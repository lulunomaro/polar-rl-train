from pathlib import Path,PurePosixPath
import hashlib,importlib.util,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
s=importlib.util.spec_from_file_location('strict210',W/'MOD4_TWO_LINUX_POLICY50_COHORT_49_20261021/strict_original_Linux_transport_memory.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
REMOTE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,re,shutil,subprocess,time
q=v['inventory'];owned=Path(q['owned']);C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports');eid='USER_ADDITIONAL_CLOSED50_51_52_E2_CLEANUP_20261021_V87';locks=[];H=lambda b:hashlib.sha256(b).hexdigest()
try:
 for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),owned/'H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock'):
  f=p.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 raw=C.read_bytes();c=json.loads(raw);assert H(raw)==q['canonical_SHA'] and c['active_segment'] is None
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True);assert 'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' not in compute
 retained={p for x in q['preserved'] for p in x['retained_checkpoints']};checks=[]
 for x in q['preserved']:
  root=Path(x['root']);assert H((root/'NODE_TERMINAL_ACTUAL.json').read_bytes())==x['terminal_SHA'] and H((root/'NODE_EXIT_ACTUAL.json').read_bytes())==x['exit_SHA'];assert not any(p.pid!=os.getpid() and any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
  for a in x['retained_checkpoints']:assert Path(a).is_file()
 for x in q['candidates']:
  p=Path(x['path']);root=Path(x['root']);assert x['root'] in q['roots'] and str(p) not in retained and re.fullmatch(r'model_update[0-9]+\.pt',p.name) and p.parent==root/'job0/production' and not p.is_symlink() and p.resolve().is_relative_to(owned.resolve()) and p.resolve().is_relative_to((root/'job0/production').resolve());st=p.stat();assert (st.st_size,st.st_mtime_ns,st.st_ino)==(x['bytes'],x['mtime_ns'],x['inode']);checks.append(p)
 marker=E/(eid+'_STARTED.json')
 with marker.open('xb') as f:f.write(json.dumps(dict(epoch=time.time(),authorization=v['authorization'],candidate_inventory_SHA=v['inventory_SHA'],count=len(checks),bytes=q['total_candidate_bytes'],all_closed_source_FINAL_first_latest2_logs_errors_retained=True)).encode());f.flush();os.fsync(f.fileno())
 free_before=shutil.disk_usage(owned).free;deleted=[]
 for p,x in zip(checks,q['candidates']):p.unlink();deleted.append(x)
 assert all(not p.exists() for p in checks) and all(Path(p).is_file() for p in retained) and C.read_bytes()==raw
 out=dict(epoch=time.time(),passed=True,cleanup_id=eid,explicit_human_message=v['authorization'],deleted=deleted,deleted_count=len(deleted),deleted_bytes=sum(x['bytes'] for x in deleted),preserved=q['preserved'],free_before=free_before,free_after=shutil.disk_usage(owned).free,original_two_fcntl_and_E2_private_held=True,all_original_canonical_bytes_unchanged=True,canonical_SHA=H(raw),no_budget_or_training_or_peer_or_recursive_delete=True,original_FINAL_source_first_latest2_logs_errors_retained=True)
 with (E/(eid+'_ACTUAL.json')).open('xb') as f:f.write(json.dumps(out,indent=2).encode());f.flush();os.fsync(f.fileno())
 print(json.dumps(out))
finally:
 for f in reversed(locks):f.close()
'''
try:
 p=R/'CLOSED_E2_INTERMEDIATE_CLEANUP_INVENTORY_ACTUAL.json';raw=p.read_bytes();q=json.loads(raw);assert q['passed'] and q['no_deletion_yet'];retained={x for r in q['preserved'] for x in r['retained_checkpoints']};paths=[x['path'] for x in q['candidates']];assert len(paths)==len(set(paths)) and set(paths).isdisjoint(retained) and all(PurePosixPath(x).is_relative_to(PurePosixPath(q['owned'])) and PurePosixPath(x).parent==PurePosixPath(r['root'])/'job0/production' for x,r in zip(paths,q['candidates']))
 with (R/'CLOSED_E2_CLEANUP_EXACT_TARGETS_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,candidates=len(paths),bytes=q['total_candidate_bytes'],no_recursive_delete=True,only_verified_explicit_unused_intermediate_files=True,all_retained_paths_disjoint=True),f,indent=2)
 with (R/'CLOSED_E2_CLEANUP_DELETE_STARTED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time()),f)
 c=t.connect()
 try:v=t.code(c,REMOTE,dict(inventory=q,inventory_SHA=hashlib.sha256(raw).hexdigest(),authorization='[REDACTED]'),timeout=90)
 finally:c.close()
 with (R/'CLOSED_E2_INTERMEDIATES_DELETE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(passed=v['passed'],deleted_count=v['deleted_count'],reclaimed_bytes=v['deleted_bytes'],free_after=v['free_after'],original_canonical_unchanged=True)))
except BaseException:
 with (R/'CLOSED_E2_CLEANUP_DELETE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
