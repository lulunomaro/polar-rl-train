from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;S=W/'MOD4_REPLAY_WASTE_AUDIT_CLEANUP_AUTHORIZED_20261025';R=S/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 auth=json.loads((R/'HUMAN_NEW_REPLAY_WASTE_AUDIT_CLEANUP_AUTH_ACTUAL.json').read_bytes());assert auth['human_request'].startswith('继续详细排查')
 code=(S/'remote_owned_replay_storage_metadata_v1.py').read_text('utf8');put('TWO_HOST_NEW_REPLAY_METADATA_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=__import__('os').getpid(),argv=sys.argv,source_SHA=hashlib.sha256(code.encode()).hexdigest(),new_instruction_only_no_old_cleanup_reexecution=True))
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(spec);spec.loader.exec_module(memory);secret=memory.recover()
 runs=[dict(host='210',roots=['/mnt/mod4_linux_durable_20261013','/home/egde/rl_candidates','/home/egde/rl_audits','/home/egde/.cache','/home/egde/anaconda3/pkgs'],out='/home/egde/rl_candidates/REPLAY_WASTE_NEW_METADATA_20261025'),dict(host='72',roots=['/home/lc01/Zonglin Li/zonglin2/tasks','/home/lc01/Zonglin Li/zonglin2/forensic_originals','/home/lc01/Zonglin Li/zonglin2/replay_diagnostics','/home/lc01/Zonglin Li/zonglin2/.cache','/home/lc01/Zonglin Li/zonglin2/pkgs'],out='/home/lc01/Zonglin Li/zonglin2/audit/REPLAY_WASTE_NEW_METADATA_20261025')]
 for v in runs:
  c=d.t.connect() if v['host']=='210' else d.connect72(secret)
  try:
   q=d.code(c,d.t.PY if v['host']=='210' else d.PY72,code,dict(v,source_code=code),timeout=210);put('HOST'+v['host']+'_NEW_REPLAY_STORAGE_METADATA_ACTUAL.json',q)
   artifact=q['metadata_artifact'];p=R/('HOST'+v['host']+'_ALL_OWNED_PROJECT_FILE_METADATA.jsonl');assert not p.exists();sf=c.open_sftp();sf.get_channel().settimeout(120)
   try:sf.get(artifact['path'],str(p))
   finally:sf.close()
   assert p.stat().st_size==artifact['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==artifact['SHA'];put('HOST'+v['host']+'_METADATA_TEXT_TWOHOST_SHA_ACTUAL.json',dict(epoch=time.time(),path=str(p),bytes=p.stat().st_size,SHA=artifact['SHA'],twohost_complete_SHA=True,no_binary_originals_read=True))
   print(json.dumps(dict(host=v['host'],files=q['files'],complete=q['complete_within_explicit_roots'],logical_bytes=q['total_logical_bytes'],disks=q['filesystem_snapshots'],groups=q['groups'][:12],errors=q['errors'][:5])),flush=True)
  finally:c.close()
 secret=None
except BaseException:
 put('NEW_REPLAY_TWOHOST_METADATA_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_deletion_or_GPU_or_budget_write=True));raise
