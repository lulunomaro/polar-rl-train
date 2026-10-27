"""Unused remote helper source. Reads only owned small text/source metadata."""
def observe_target_readonly(v):
 from pathlib import Path
 import hashlib,json,psutil,subprocess,sys,time,traceback
 B=Path(v['root']);s=v['spec'];reader_errors={};files={}
 def small(path):
  try:
   if not path.is_file():return None
   assert not path.is_symlink() and path.resolve().is_relative_to(B.resolve())
   assert path.suffix in ('.json','.jsonl','.log','.txt')
   if path.suffix=='.json':
    assert path.stat().st_size<8000000
    return json.loads(path.read_bytes())
   with path.open('rb') as stream:
    size=path.stat().st_size;stream.seek(max(0,size-120000));raw=stream.read(120000)
   return dict(bytes=size,text_tail=raw.decode('utf8',errors='replace'),truncated=size>len(raw))
  except Exception as exc:
   error=dict(reader_error=type(exc).__name__+': '+str(exc));reader_errors[str(path)]=error;return error
 out=B/'job0/production'
 selected=[B/name for name in ('NODE_IDENTITY.json','NODE_CURRENT.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','node_CONSOLE.log')]
 selected+=[B/'job0/GO_PRODUCTION.json',B/'job0/production_WORKER.log']
 selected+=sorted(B.glob('NODE_CONTROL_ORIGINAL_ERROR_*.json'))+sorted(B.glob('NODE_TERMINAL_HANDOFF_ORIGINAL_ERROR_*.json'))
 selected+=sorted(out.glob('*ERROR*.json'))
 for path in dict.fromkeys(selected):
  value=small(path)
  if value is not None:files[str(path.relative_to(B))]=value
 row=v.get('row') or (files.get('NODE_CURRENT.json') or {}).get('row') or {}
 base=dict(epoch=time.time(),key=s['key'],row=row,passed_live_identity=False,existing_own_small_receipts=files,
   existing_small_errors={k:value for k,value in files.items() if 'ERROR' in k or k.endswith('.log')},
   reader_errors=reader_errors,no_PT_raw_or_checkpoint_hash_read=True,no_signal_or_retry=True,
   not_FINAL_or_skill_or_continuous_alive=True)
 for key,relative in (('first_positive','FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json'),
    ('actual_GPU_precontrol','NATIVE87_ACTUAL_GPU_PRECONTROL_ADMISSION.json'),
    ('trace_index','control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'),
    ('phase_optional','NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json'),
    ('curve_tail','ACTUAL_H1_CONVERGENCE_CURVE.jsonl')):base[key]=small(out/relative)
 try:
  manifest_path=B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';raw=manifest_path.read_bytes()
  assert hashlib.sha256(raw).hexdigest()==s['manifest_SHA']
  pins={r['relative']:r['SHA'] for r in json.loads(raw)['files']}
  for name in ('native87_closed_source_CPU_v1.py','source/native_own_fudan87_training.py'):
   assert hashlib.sha256((B/name).read_bytes()).hexdigest()==pins[name]
  sys.path.insert(0,str(B));from native87_closed_source_CPU_v1 import expected_exec_identity
  def identity(record,logical):
   expected=expected_exec_identity(s,logical,B)
   if not isinstance(record,dict) or not isinstance(record.get('pid'),int) or not record.get('creation'):
    return dict(passed=False,status='missing_recorded_identity',expected=expected)
   try:
    p=psutil.Process(record['pid']);creation=p.create_time()
    if creation!=record['creation']:
     # Never inspect exe/argv of a recycled pid belonging to another process.
     return dict(passed=False,status='pid_creation_mismatch',recorded_pid=record['pid'],recorded_creation=record['creation'],actual_creation=creation)
    actual=dict(pid=p.pid,creation=creation,argv=p.cmdline(),exe=p.exe(),root=p.cwd())
    passed=all(actual[k]==expected[k] for k in ('argv','exe','root')) and record.get('argv')==expected['argv']
    return dict(passed=passed,status='exact_live_identity' if passed else 'exact_identity_mismatch',actual=actual,expected=expected)
   except psutil.NoSuchProcess:
    return dict(passed=False,status='actual_process_out',actual_out=True,recorded=record,expected=expected)
  node=files.get('NODE_IDENTITY.json');base['node']=node
  base['node_identity']=identity(node,[s['python'],'-u','-B',str(B/'three_slot_finite_node_v1.py')])
  worker=row.get('worker')
  logical=[s['python'],'-u','-B',str(B/s['production_script']),'--slot',s['key'],'--phase','production','--num-envs','4096','--seed',str(s['seed']),'--source-scope','policy_only_fresh_environment']
  base['worker_identity']=identity(worker,logical)
  if not base['node_identity']['passed'] or not base['worker_identity']['passed'] or row.get('original_error'):
   base['status']='node_or_worker_out_error_or_identity_not_proven';return base
  go=files.get('job0/GO_PRODUCTION.json');base['GO']=go
  assert go['run_id']==v['run_id'] and go['source_SHA']==s['source_SHA'] and go['manifest_SHA']==s['manifest_SHA'] and go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
  pid=base['worker_identity']['actual']['pid']
  compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
  own=[line for line in compute.splitlines() if line.split(',')[1].strip()==str(pid)]
  assert own and all(line.split(',')[0].strip()==s['GPU_UUID'] for line in own)
  source=(B/'source/native_own_fudan87_training.py').read_text('utf8')
  assert "publication['policy_updates']>0" in source and "checkpoint['before_control']==trace.total" in source and "checkpoint['SHA']==publication['SHA']" in source and "checkpoint['bytes']==publication['bytes']" in source
  base.update(passed_live_identity=True,status='exact_own_live_identity',worker_actual=base['worker_identity']['actual'],own_GPU=own,publication_positive_and_same_source_guard_pinned=True)
  return base
 except Exception:
  base.update(status='target_observation_original_error_preserved',observation_error=traceback.format_exc())
  return base
