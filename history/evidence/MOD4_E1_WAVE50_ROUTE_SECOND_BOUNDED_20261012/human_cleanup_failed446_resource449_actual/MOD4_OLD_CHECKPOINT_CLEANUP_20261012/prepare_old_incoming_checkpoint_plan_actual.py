from cleanup_io import *

def main():
    inventory=json.loads(max(R.glob('OLD_ROLLING_CHECKPOINT_INVENTORY_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes())
    prefix='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac/'
    selected=[];allocated=0
    for row in inventory['candidates']:
      if not row['path'].startswith(prefix) or int(row['name'][6:-3])%1000==0:continue
      selected.append(row);allocated+=row['allocated_bytes']
      if allocated>=3*1024**3:break
    assert allocated>=3*1024**3
    n,w=io.connect_both()
    try:
      v=run(n,r'''from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,time,hashlib,stat,shutil
B=Path('/home/egde/rl_candidates').resolve();allowed=Path(PREFIX_TOKEN).resolve();selected=json.loads(ROWS_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for x in selected:
 p=Path(x['path']);assert p.resolve()==p and p.is_relative_to(allowed) and not p.is_symlink()
 s=p.stat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(x['device'],x['inode'],x['bytes'],x['mtime_ns'],x['ctime_ns'])
 assert s.st_mtime<datetime(2026,9,10,tzinfo=timezone(timedelta(hours=8))).timestamp() and int(x['name'][6:-3])%1000!=0
 rows.append(dict(**x,sha256=h(p),deletion_authorized_old_obsolete_intermediate=True,not_a_current_or_accepted_expert_source=True,previous_source_reports_and_cost_not_relabelled=True))
protected={}
for p in (B/'MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json',Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012/learning_logs/2026-10-12_12-52-16_e1_WAVE50_route_lifecycle_observation_1791780538491241968/model_32264.pt')):protected[str(p)]=h(p)
assert list(protected.values())[1]=='68401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5'
v=dict(epoch=time.time(),passed=True,plan_only_no_deletion=True,human_authorization='远古一些废旧检查点可以清理',only_allowed_directory=str(allowed),rows=rows,planned_unlink_bytes=sum(x['bytes'] for x in rows),planned_reclaim_allocated_bytes=sum(x['allocated_bytes'] for x in rows),oldest_mtime=min(x['mtime_epoch'] for x in rows),newest_mtime=max(x['mtime_epoch'] for x in rows),first_last3_every1000_and_all_referenced_checkpoints_retained=True,protected_SHA=protected,durable_free_before=shutil.disk_usage(B).free,reports_source_assets_env_cache_raw_and_recent_checkpoints_untouched=True,only_checkpoint_binary_retention_exception_human_authorized=True)
p=B/'MOD4_MOE_PLAN_EXECUTION_20261007/reports'/('HUMAN_OBSOLETE_INCOMING_CHECKPOINT_CLEANUP_PLAN_'+str(time.time_ns())+'.json');assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2));v['actual_remote_plan_path']=str(p);v['actual_remote_plan_SHA']=h(p);print(json.dumps(v))
'''.replace('PREFIX_TOKEN',repr(prefix)).replace('ROWS_TOKEN',repr(json.dumps(selected))))
      p=save('OBSOLETE_INCOMING_CHECKPOINT_PLAN_ACTUAL.json',v)
      save('DUPLICATE_ONLY_PLAN_INSUFFICIENT_REVIEW.json',dict(epoch=time.time(),passed=True,original_duplicate_only_plan_rejected_before_remote_or_deletion=True,duplicate_only_reclaim_possible_bytes=177766400,human_authorized_old_obsolete_not_only_duplicates=True,independent_incoming_only_plan_prepared=True,unrecoverable_deleted_old_weights_will_be_explicitly_indexed_with_SHA_and_authorization=True,all_old_false_source_reports_cost_retained=True))
      save('LOCAL_WEIGHT_SEARCH_PERMISSION_REVIEW.json',dict(epoch=time.time(),observer_only=True,command='rg --files for old model filenames',inaccessible_path='rmuc2026_work/unpack_verify_4zomhj13',read_error='permission_denied',no_local_backup_availability_claim=True,no_GUI_or_file_change=True))
      print(json.dumps(dict(report=str(p),files=len(v['rows']),reclaim_bytes=v['planned_reclaim_allocated_bytes'],oldest=v['oldest_mtime'],newest=v['newest_mtime'],no_deletion_yet=True)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('OLD_INCOMING_PLAN_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_deletion_or_GPU_or_budget_write=True));raise
