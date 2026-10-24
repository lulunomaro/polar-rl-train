from pathlib import Path,PurePosixPath
import ast,hashlib,importlib.util,json,os,sys,time,traceback,base64
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

READ210="\nfrom pathlib import Path\nimport fcntl,json,os,psutil,subprocess,time\nq=v['q'];owner=Path(q['owner_root']);h1=Path(q['roots']['h1']);until=time.monotonic()+850\nread=lambda p:json.loads(p.read_bytes()) if p.is_file() else None\ndef own():\n out=[]\n for p in psutil.process_iter(['pid','cmdline','create_time']):\n  try:\n   if p.pid!=os.getpid() and any(a.startswith((str(owner)+'/',str(h1)+'/')) for a in p.info['cmdline'] or []):out.append(p.info)\n  except psutil.Error:pass\n return out\nwhile not (owner/'COHORT_FINAL.json').exists() or not (owner/'OWNER_EXIT_ACTUAL.json').exists() or own():\n assert time.monotonic()<until,'Actual owner/H1 closure not completed; no schedule-based FINAL'\n time.sleep(3)\nco=read(owner/'COHORT_FINAL.json');oe=read(owner/'OWNER_EXIT_ACTUAL.json')\nassert co['original_cost_settled'] and oe['original_cost_settled']\nne=read(h1/'NODE_EXIT_ACTUAL.json');nt=read(h1/'NODE_TERMINAL_ACTUAL.json')\nassert ne['actual_all_own_children_waited'] and ne['validation_fcntl_released_if_acquired']\nC=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=read(C)\nassert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9\nsegments=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==q['owner_identity']['pid'] and x['started_epoch']>=q['owner_identity']['creation']]\nassert len(segments)==1 and set(segments[0]['experts'])==set(co['go'])=={'h1','recovery'}\nlocks=[]\nfor p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(q['specs']['h1']['private_lock'])):\n with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),actual_fcntl_free=True))\ntexts=[]\nfor key,root in (('owner',owner),('h1',h1)):\n for p in root.rglob('*'):\n  if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv'):\n   raw=p.read_bytes();texts.append(dict(path=str(p),relative=key+'/'+p.relative_to(root).as_posix(),bytes=len(raw),SHA=__import__('hashlib').sha256(raw).hexdigest()))\nprint(json.dumps(dict(epoch=time.time(),cohort=co,owner_exit=oe,H1_node_exit=ne,H1_terminal=nt,original_segment=segments[0],original_canonical_remaining=c['remaining_training_seconds'],original_locks=locks,all_owner_H1_children_actual_out=True,text_files=texts,no_account_write_or_midwindow_model_hash=True)))\n"
READ72="\nfrom pathlib import Path\nimport fcntl,json,os,psutil,time\nq=v['q'];root=Path(q['roots']['recovery']);until=time.monotonic()+180\ndef own():\n out=[]\n for p in psutil.process_iter(['pid','cmdline']):\n  try:\n   if p.pid!=os.getpid() and any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or []):out.append(p.info)\n  except psutil.Error:pass\n return out\nwhile not (root/'NODE_EXIT_ACTUAL.json').exists() or own():\n assert time.monotonic()<until,'Actual E3 children still active'\n time.sleep(3)\nread=lambda p:json.loads(p.read_bytes());e=read(root/'NODE_EXIT_ACTUAL.json');terminal=read(root/'NODE_TERMINAL_ACTUAL.json')\nassert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'];locks=[]\nfor p in (Path(q['specs']['recovery']['private_lock']),Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')):\n with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),actual_fcntl_free=True))\ntexts=[]\nfor p in root.rglob('*'):\n if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv'):\n  raw=p.read_bytes();texts.append(dict(path=str(p),relative='recovery/'+p.relative_to(root).as_posix(),bytes=len(raw),SHA=__import__('hashlib').sha256(raw).hexdigest()))\nprint(json.dumps(dict(epoch=time.time(),node_exit=e,node_terminal=terminal,locks=locks,all_E3_processes_actual_out=True,text_files=texts,no_account_change=True)))\n"
def capture(c,receipt,models,key):
    sf=c.open_sftp();sf.get_channel().settimeout(90);texts=[];saved=[]
    try:
        for row in receipt['text_files']:
            rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts
            p=N/'benchmark_closed_text'/Path(*rel.parts);p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
            sf.get(row['path'],str(p))
            if p.stat().st_size==row['bytes'] and H(p)==row['SHA']:
                texts.append(dict(row,local_path=str(p)))
            else:
                assert rel.as_posix()=='h1/job0/home/.nvidia-omniverse/logs/omni.processlifetime.log','Unexpected text mismatch; preserve original and stop'
                original=dict(row,local_path=str(p),transferred_bytes=p.stat().st_size,transferred_SHA=H(p),manifest_time_bytes_not_captured=True)
                code="from pathlib import Path;import base64,hashlib,json; p=Path(v['path']); a=p.stat(); raw=p.read_bytes(); b=p.stat(); assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns); print(json.dumps(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),mtime_ns=b.st_mtime_ns,base64=base64.b64encode(raw).decode())))"
                fresh=d.code(c,d.t.PY,code,dict(path=row['path']),timeout=45);raw=base64.b64decode(fresh.pop('base64'));assert len(raw)==fresh['bytes'] and hashlib.sha256(raw).hexdigest()==fresh['SHA']
                fp=p.with_name('omni.processlifetime.fresh_after_manifest_mismatch.log')
                with fp.open('xb') as f:f.write(raw)
                put('PAIR_H1_PROCESSLIFETIME_LOG_MANIFEST_TRANSFER_AND_FRESH_SNAPSHOT_ACTUAL.json',dict(epoch=time.time(),original=original,fresh=dict(fresh,local_path=str(fp)),cause_unknown=True,original_manifest_time_bytes_unavailable=True,no_training_failure_or_refund_inferred=True))
                texts.append(dict(row,bytes=fresh['bytes'],SHA=fresh['SHA'],local_path=str(fp),original_manifest_and_transferred_log_preserved=original,one_fresh_snapshot_only=True))
        for row in models:
            p=N/'current_pair_closed_models'/key/PurePosixPath(row['path']).name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
            part=p.with_suffix('.pt.partial');sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and H(part)==row['SHA'];part.replace(p)
            saved.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
    finally:sf.close()
    return texts,saved

PROGRESS72="from pathlib import Path\nimport json,time\nroot=Path(v['root']);out=root/'job0/production';until=time.monotonic()+180\nread=lambda p:json.loads(p.read_bytes()) if p.is_file() else None\nwhile True:\n rows=read(out/'fp32/TIMING_CURRENT.json')\n errors=list(out.rglob('*ORIGINAL_ERROR*.json'))\n if (rows and len(rows['rows'])>=3) or errors or (root/'NODE_EXIT_ACTUAL.json').exists():break\n assert time.monotonic()<until,'No first measured E3 baseline within bounded180s; original worker continues independently'\n time.sleep(3)\nprint(json.dumps(dict(epoch=time.time(),fp32_timing=rows,protocol=read(out/'PRECISION_BENCHMARK_SOURCE_AND_PROTOCOL_ACTUAL.json'),progress=read(out/'BENCHMARK_PROGRESS_CURRENT.json'),errors={str(p):p.read_text('utf8') for p in errors},preliminary_only_not_whole_benchmark_or_training_qualification=True)))\n"
try:
 q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
 assert all(v['performance_benchmark_only'] for v in q['specs'].values())
 observed=json.loads((R/'BENCHMARK_ACTUAL_GO_WORKER_IDENTITY_AND_PROGRESS_SNAPSHOT_ACTUAL.json').read_bytes())
 assert time.time()-min(v['actual_GO']['learning_started_epoch'] for v in observed['slots'].values())>=300
 put('BENCHMARK_CLOSING_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,owner=q['owner_identity'],benchmark_only_no_model_qualification=True,original_210wait850_72wait180_preserved=True))
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory);secret=memory.recover()
 c=d.connect72(secret)
 try:pre=d.code(c,d.PY72,PROGRESS72,dict(root=q['roots']['recovery']),timeout=210)
 finally:c.close()
 put('BENCHMARK_E3_FIRST_MEASURED_PROFILE_SNAPSHOT_ACTUAL.json',pre)
 print(json.dumps(dict(stage='preliminary_E3_profile',last_row=pre['fp32_timing']['rows'][-1] if pre['fp32_timing'] else None,errors=pre['errors'])),flush=True)
 c=d.t.connect()
 try:
  a=d.code(c,d.t.PY,READ210,dict(q=q),timeout=900);put('BENCHMARK_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json',a);ta,unused=capture(c,a,[],'h1')
 finally:c.close()
 c=d.connect72(secret);secret=None
 try:
  b=d.code(c,d.PY72,READ72,dict(q=q),timeout=210);put('BENCHMARK_CLOSED_TARGET72_ACTUAL.json',b);tb,unused=capture(c,b,[],'recovery')
 finally:c.close()
 segment=a['original_segment'];cost=sum(v['charged_seconds'] for v in segment['experts'].values());assert all(v['duration_bound_passed'] for v in segment['experts'].values())
 result=dict(epoch=time.time(),collector_function_complete=True,owner_node_workers_all_actual_out=True,original_canonical_cost_settled=True,original_actual_cost_sumonce=cost,original_remaining_closed_snapshot=a['original_canonical_remaining'],source210=a,source72=b,all_texts=ta+tb,no_models_downloaded_or_claimed_as_qualified=True,qualified_policy_sources_remain_actual_complete67=True,not_training_failure_in_original67=True,no_budget_refund_second_writer_or_clearactive=True)
 put('BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json',result)
 print(json.dumps(dict(closed=True,texts=len(ta)+len(tb),cost_sumonce=cost,remaining_closed_snapshot=a['original_canonical_remaining'],errors_by_slot={k:v.get('original_error') for k,v in a['cohort']['rows'].items()},not_qualified_training_models=True)))
except BaseException:
 put('BENCHMARK_CLOSING_ORIGINAL_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_force_kill_or_retry_same_once=True));raise
