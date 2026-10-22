"""After actual complete closure only: text and directory stat, no raw/PT reads."""
from pathlib import Path
import ast,importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
read=lambda p:json.loads(Path(p).read_bytes())
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CHECK=r'''
from pathlib import Path
import fcntl,json,os,psutil,re,time
root=Path(v['root']);owner=Path(v['owner']);B=root/'job0/production/control_prefix_raw'
assert json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
assert json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
assert not any(p.pid!=os.getpid() and any(a.startswith((str(root)+'/',str(owner)+'/')) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');assert json.loads(C.read_bytes())['active_segment'] is None
for lock in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['private_lock'])):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts={p.name:p.read_text('utf8') for p in B.iterdir() if p.is_file() and p.suffix in ('.json','.partial')}
index=json.loads(texts['CONTROL_VALID_PREFIX_INDEX_ACTUAL.json']);rows=index['index'];status=index['retention_status']
history=json.loads(texts.get('PREFIX_PAIR_RETENTION_HISTORY_ACTUAL.json','{"transactions":[]}'))['transactions']
directory={p.name:dict(path=str(p),bytes=p.stat().st_size,inode=p.stat().st_ino,mtime_ns=p.stat().st_mtime_ns,nlink=p.stat().st_nlink) for p in B.iterdir() if p.is_file() and not p.is_symlink()}
removed={r['path']:r for txn in history for r in txn['removed']};protected=set(range(min(1,len(rows))))|set(range(max(0,len(rows)-2),len(rows)))|{i for i,row in enumerate(rows) if row['controls']<24}
assert len(status)==len(rows)
for i,(row,s) in enumerate(zip(rows,status)):
 raw=Path(row['path']);pre=Path(row['preupdate_source']['path'])
 assert raw.parent==pre.parent==B and raw.name in directory if s['raw_retained'] else raw.name not in directory
 assert s['index']==i and s['path']==str(raw) and s['preupdate_path']==str(pre)
 assert s['raw_retained']==raw.is_file() and s['preupdate_retained']==pre.is_file() and s['protected']==(i in protected)
 for item,p in ((row,raw),(row['preupdate_source'],pre)):
  if p.is_file():assert directory[p.name]['bytes']==item['bytes']
  else:assert str(p) in removed and removed[str(p)]['bytes']==item['bytes'] and removed[str(p)]['SHA']==item['SHA']
 if i in protected:assert raw.is_file() and pre.is_file()
for txn in history:
 assert txn['all_selected_actual_removed'];intent=json.loads(texts[Path(txn['intent']).name])
 expected={(r['path'],r['bytes'],r['SHA']) for pair in intent['selected'] for r in pair['files']}
 assert expected=={(r['path'],r['bytes'],r['SHA']) for r in txn['removed']}
 for r in txn['removed']:assert not Path(r['path']).exists()
all_present=all(s['raw_retained'] and s['preupdate_retained'] for s in status)
assert index['all_success_and_failed_control_prefixes_retained']==all_present
errors=[name for name in texts if 'ORIGINAL_ERROR' in name or name.endswith('.partial')]
failed='ACTUAL_STEP_ORIGINAL_ERROR.json' in texts
if not failed and not errors:assert {i for i,s in enumerate(status) if s['raw_retained'] and s['preupdate_retained']}==protected
print(json.dumps(dict(epoch=time.time(),passed_metadata_consistency=True,retention_completed_without_IO_error=not errors,producer_prefixes=len(rows),retained_complete_pairs=sum(s['raw_retained'] and s['preupdate_retained'] for s in status),protected_indices=sorted(protected),removed_files=len(removed),actual_transactions=len(history),failure_flag=failed,errors=errors,all_raw_retained_truth=all_present,full_texts=texts,directory_stat=directory,no_raw_PT_content_read_hash_download_GPU_or_account_write=True)))
'''
def main():
 proof=read(R/'PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');q=read(R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
 assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
 put('FIRST_BOUNDED_TRACE_METADATA_REVIEW_STARTED_ACTUAL.json',dict(epoch=time.time(),only_after_actual_wholeCPU_cost_allout=True,no_raw_PT_hash_download_or_GPU=True))
 c=d.t.connect()
 try:value=d.code(c,d.t.PY,CHECK,dict(root=q['roots']['h1'],owner=q['owner_root'],private_lock=q['specs']['h1']['private_lock']),timeout=90)
 finally:c.close()
 put('FIRST_BOUNDED_TRACE_CLOSED_INDEX_RECEIPTS_DIRECTORY_ACTUAL.json',value)
 print(json.dumps({k:value[k] for k in ('passed_metadata_consistency','retention_completed_without_IO_error','producer_prefixes','retained_complete_pairs','removed_files','failure_flag')}))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('FIRST_BOUNDED_TRACE_METADATA_REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_rerun_consumed_helper=True));raise
