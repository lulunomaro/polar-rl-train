from cleanup_io import *

def main():
    p=max(R.glob('OLD_ROLLING_CHECKPOINT_INVENTORY_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));inventory=json.loads(p.read_bytes())
    candidates=inventory['candidates'];canonical='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/'
    key=lambda x:(Path(x['run']).name,x['name'],x['bytes'],x['mtime_ns'])
    keepers={key(x):x for x in candidates if x['path'].startswith(canonical)}
    pairs=[];allocated=0
    for x in candidates:
      if x['path'].startswith(canonical) or key(x) not in keepers:continue
      pairs.append(dict(delete=x,retain=keepers[key(x)]));allocated+=x['allocated_bytes']
      if allocated>=3*1024**3:break
    assert allocated>=3*1024**3,dict(duplicate_only_candidate_bytes=allocated)
    n,w=io.connect_both()
    try:
      v=run(n,r'''from pathlib import Path
import json,time,hashlib,stat,shutil
B=Path('/home/egde/rl_candidates').resolve();pairs=json.loads(PAIRS_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for pair in pairs:
 d,k=pair['delete'],pair['retain'];p,q=Path(d['path']),Path(k['path'])
 assert p.resolve()==p and q.resolve()==q and p.is_relative_to(B) and q.is_relative_to(B) and p!=q
 assert not p.is_symlink() and not q.is_symlink() and q.is_relative_to(B/'MOD4_native_floor_continue10h_20260930')
 for z,row in ((p,d),(q,k)):
  s=z.stat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(row['device'],row['inode'],row['bytes'],row['mtime_ns'],row['ctime_ns'])
 dh,kh=h(p),h(q);assert dh==kh
 rows.append(dict(delete=d,retain=k,sha256=dh,byteidentical_canonical_copy_remains=True,only_old_unreferenced_superseded_rolling_duplicate=True))
protected={}
for name in ('TRAINING_BUDGET_10H.json','SUPERVISOR_STATE.json'):
 p=B/'MOD4_native_floor_continue10h_20260930'/name
 if p.exists():protected[str(p)]=h(p)
source=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012/learning_logs/2026-10-12_12-52-16_e1_WAVE50_route_lifecycle_observation_1791780538491241968/model_32264.pt');assert h(source)=='68401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5';protected[str(source)]=h(source)
v=dict(epoch=time.time(),passed=True,plan_only_no_deletion=True,human_authorization='远古一些废旧检查点可以清理',scope='obsolete_pre20261001_unreferenced_rolling_duplicates_only',rows=rows,planned_unlink_bytes=sum(x['delete']['bytes'] for x in rows),planned_reclaim_allocated_bytes=sum(x['delete']['allocated_bytes'] for x in rows),durable_free_before=shutil.disk_usage(B).free,canonical_checkpoint_copies_all_retained=True,protected_SHA=protected,all_reports_source_assets_environment_cache_raw_kept=True)
p=B/'MOD4_MOE_PLAN_EXECUTION_20261007/reports'/('OLD_OBSOLETE_DUPLICATE_CHECKPOINT_CLEANUP_PLAN_'+str(time.time_ns())+'.json');assert not p.exists();p.write_text(json.dumps(v,indent=2));v['actual_remote_plan_path']=str(p);v['actual_remote_plan_SHA']=h(p);print(json.dumps(v))
'''.replace('PAIRS_TOKEN',repr(json.dumps(pairs))))
      path=save('OBSOLETE_DUPLICATE_CHECKPOINT_CLEANUP_PLAN_ACTUAL.json',v)
      print(json.dumps(dict(report=str(path),files=len(v['rows']),reclaim_bytes=v['planned_reclaim_allocated_bytes'],duplicate_SHA_verified=True,all_canonical_copies_retained=True,no_deletion_yet=True)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('OBSOLETE_CHECKPOINT_PLAN_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_deletion_or_GPU_or_budget_write=True));raise
