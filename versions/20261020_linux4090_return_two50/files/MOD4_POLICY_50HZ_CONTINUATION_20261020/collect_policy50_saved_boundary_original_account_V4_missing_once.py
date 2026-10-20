"""Copy to a fresh unused *_once.py for one bounded hourly read; never launch or stop training."""
from pathlib import Path,PurePosixPath
import getpass,hashlib,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;sys.path.insert(0,str(W/'MOD4_AVAILABLE_E2_E3_HOUR18_20261019'));import deploy_available_E2_E3_original_writer_V2_once as d
NAME=Path(__file__).stem;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ="from pathlib import Path\nimport fcntl,json,os,psutil,sys,time\nC=Path(sys.argv[1]);owned=Path('/home/lc01/Zonglin Li/zonglin2');roots=[C.parent,owned/'tasks/E3auto_2010v26',owned/'tasks/E3solo18_2010v25']\ndef own_alive():\n found=[]\n for p in psutil.process_iter(['pid','create_time','cmdline','exe']):\n  try:\n   if p.pid!=os.getpid() and any(any(x.startswith(str(root)+'/') for root in roots) for x in p.info['cmdline'] or []):found.append(p.info)\n  except psutil.Error:pass\n return found\nuntil=time.monotonic()+240\nwhile not (C/'SERIES_EXIT_ACTUAL.json').is_file() or own_alive():\n assert time.monotonic()<until,'Actual saved boundary still not returned; no assumed exits or replay'\n time.sleep(3)\nassert not (C/'SERIES_ORIGINAL_ERROR.json').exists();state=json.loads((C/'SERIES_CURRENT.json').read_bytes());assert state['status']=='requested_stop_at_boundary' and state['active'] is None\npaths=[owned/'state/MOD4_E3_AUTO50_V5_PENDING_SERIES_20261020.json',owned/'state/MOD4_E3_AUTO_PENDING_SERIES_20261020.json',owned/'state/MOD4_SINGLE_E3_OFFLINE_COST_PENDING_20261020.json',owned/'state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',owned/'state/finite_environment_validation.lock'];locks=[]\nfor p in paths:\n with p.open('rb+') as f:\n  fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),actual_fcntl_free=True,original_file_retained=True))\nboundary_handback=dict(epoch=time.time(),all_old_single_100Hz_and_current50Hz_own_processes_actual_out=True,actual_private_shared_and_series_leases_free=locks,original_current_series_exit=json.loads((C/'SERIES_EXIT_ACTUAL.json').read_bytes()),no_model_or_cost_assumed_from_schedule=True)\n\nfrom pathlib import Path\nimport sys,json,hashlib,psutil,os,time,subprocess\nC=Path(sys.argv[1]);already_complete=set(json.loads(sys.argv[2]));base=C.parent;read=lambda p:json.loads(p.read_bytes());series={p.name:read(p) for p in C.glob('*.json') if p.name.startswith('SERIES_')};finals=[];texts=[];allowed={'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv','.bat','.ps1'}\nfor root in [C,*sorted((base/'windows').glob('hour*'))]:\n if root!=C and root.name in already_complete:continue\n for p in sorted(root.rglob('*')):\n  if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p.suffix not in allowed:continue\n  assert p.resolve().is_relative_to(base.resolve());raw=p.read_bytes();texts.append(dict(path=str(p),relative=p.relative_to(base).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))\n if root==C:continue\n proof=root/'CLOSED_FINAL_WHOLE_MODEL_CPU_ACTUAL.json'\n if proof.is_file():\n  q=read(proof);co=read(root/'owner/COHORT_FINAL.json');assert q['passed'] and q['original_canonical_settled'] is False and co['pending_cost_record_complete'];m=q['final'];assert Path(m['path']).resolve().is_relative_to(root.resolve()) and Path(m['path']).stat().st_size==m['bytes'];finals.append(dict(window=root.name,producer_final=m,pending_cost=q['pending_cost'],whole_CPU_proof_path=str(proof),not_rehashed_model_for_collection=True))\nown=[]\nfor p in psutil.process_iter(['pid','create_time','cmdline','exe']):\n try:\n  if p.pid!=os.getpid() and any(s.startswith(str(base)+'/') for s in p.info['cmdline'] or []):own.append(p.info)\n except psutil.Error:pass\nprint(json.dumps(dict(epoch=time.time(),base=str(base),boundary_handback=boundary_handback,previous_complete_windows_not_rehashed=sorted(already_complete),series=series,complete_finals=finals,text_files=texts,actual_own_processes=own,compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),no_training_or_canonical_write=True,no_model_or_raw_rehash=True)))\n"
def main():
 assert NAME.endswith('_once') and 'TEMPLATE' not in NAME;put(NAME+'_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_training_transport=True));dispatch=json.loads((R/'POLICY50_V5_SERIAL_PARENT_DEPLOYED_ACTUAL.json').read_bytes());known={};models={};complete_windows=set()
 for p in R.glob('collect_policy50_*_RETURNED_ACTUAL.json'):
  old=json.loads(p.read_bytes())
  for x in old.get('collected_texts',[]):
   if x.get('actual_local_SHA',x['remote_SHA'])==x['remote_SHA']:known[x['remote_SHA']]=x
  for x in old.get('collected_complete_models',[]):models[x['SHA']]=x
  if old.get('actual_finite_transport_returned'):
   for z in old.get('actual',{}).get('complete_finals',[]):
    m=models.get(z['producer_final']['SHA'])
    if m and Path(m['local_path']).is_file() and Path(m['local_path']).stat().st_size==m['bytes']:complete_windows.add(z['window'])
 pw=getpass.getpass('72 automatic E3 new closed reports only (hidden): ');c=None;sf=None;captured=[];saved=[];changed=[]
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);v=d.a.code(c,d.a.PY,READ,dispatch['root'],json.dumps(sorted(complete_windows)),timeout=300);sf=c.open_sftp();sf.get_channel().settimeout(90);dest=B/'remote_snapshots'/NAME;dest.mkdir(parents=True)
  for row in v['text_files']:
   old=known.get(row['SHA'])
   if old and Path(old['local_path']).is_file() and Path(old['local_path']).stat().st_size==row['bytes']:captured.append(dict(old,remote_path=row['path'],exact_previous_local_capture_reused=True));continue
   rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts;q=dest.joinpath(*rel.parts);q.parent.mkdir(parents=True,exist_ok=True)
   with sf.file(row['path'],'rb') as f:data=f.read()
   q.write_bytes(data);sha=hashlib.sha256(data).hexdigest();captured.append(dict(remote_path=row['path'],remote_SHA=row['SHA'],local_path=str(q),bytes=len(data),actual_local_SHA=sha,snapshot_unchanged=sha==row['SHA']))
   if sha!=row['SHA']:changed.append(dict(remote_path=row['path'],reason='active_text_changed_during_read',inventory_SHA=row['SHA'],captured_SHA=sha))
  for row in v['complete_finals']:
   m=row['producer_final'];old=models.get(m['SHA'])
   if old and Path(old['local_path']).is_file() and Path(old['local_path']).stat().st_size==m['bytes']:saved.append(dict(old,not_redownloaded_or_rehashed=True));continue
   q=B/'actual_closed_auto_E3_models'/row['window']/PurePosixPath(m['path']).name;q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();partial=q.with_suffix(q.suffix+'.partial');sf.get(m['path'],str(partial));assert partial.stat().st_size==m['bytes'] and H(partial)==m['SHA'];partial.replace(q);saved.append(dict(path=m['path'],local_path=str(q),bytes=m['bytes'],SHA=m['SHA'],twohost_complete_SHA=True,producer_whole_CPU_proof=row['whole_CPU_proof_path'],run_id=row['pending_cost']['run_id'],canonical_settled=False))
  put(NAME+'_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual=v,collected_texts=captured,collected_complete_models=saved,active_text_changes_preserved=changed,actual_finite_transport_returned=True,original_canonical_not_opened_or_settled=True,no_new_training_or_stop=True));print(json.dumps(dict(new_closed_windows=len(v['complete_finals']),complete_local_models=len(saved),series_status=v['series'].get('SERIES_CURRENT.json',{}).get('status'),active_text_changes=len(changed))),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put(NAME+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_GPU_or_canonical_write=True));raise
