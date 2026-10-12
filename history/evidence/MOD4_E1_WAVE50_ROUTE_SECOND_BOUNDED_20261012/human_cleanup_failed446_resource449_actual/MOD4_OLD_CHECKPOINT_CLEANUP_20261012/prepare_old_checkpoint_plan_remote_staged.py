from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,time,hashlib,stat,shutil
B=Path('/home/egde/rl_candidates').resolve();allowed=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac/').resolve();selected=json.loads(Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/HUMAN_OLD_CHECKPOINT_ROWS_STAGED_20261012.json').read_bytes())["rows"];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for x in selected:
 p=Path(x['path']);assert p.resolve()==p and p.is_relative_to(allowed) and not p.is_symlink()
 s=p.stat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(x['device'],x['inode'],x['bytes'],x['mtime_ns'],x['ctime_ns'])
 assert s.st_mtime<datetime(2026,9,10,tzinfo=timezone(timedelta(hours=8))).timestamp() and int(x['name'][6:-3])%1000!=0
 rows.append(dict(**x,sha256=h(p),deletion_authorized_old_obsolete_intermediate=True,not_a_current_or_accepted_expert_source=True,previous_source_reports_and_cost_not_relabelled=True))
protected={}
for p in (B/'MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json',Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012/learning_logs/2026-10-12_12-52-16_e1_WAVE50_route_lifecycle_observation_1791780538491241968/model_32264.pt')):protected[str(p)]=h(p)
assert list(protected.values())[1]=='68401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5'
v=dict(epoch=time.time(),passed=True,plan_only_no_deletion=True,human_authorization='远古一些废旧检查点可以清理',only_allowed_directory=str(allowed),rows=rows,planned_unlink_bytes=sum(x['bytes'] for x in rows),planned_reclaim_allocated_bytes=sum(x['allocated_bytes'] for x in rows),oldest_mtime=min(x['mtime_epoch'] for x in rows),newest_mtime=max(x['mtime_epoch'] for x in rows),first_last3_every1000_and_all_referenced_checkpoints_retained=True,protected_SHA=protected,durable_free_before=shutil.disk_usage(B).free,reports_source_assets_env_cache_raw_and_recent_checkpoints_untouched=True,only_checkpoint_binary_retention_exception_human_authorized=True)
p=B/'MOD4_MOE_PLAN_EXECUTION_20261007/reports'/'HUMAN_OBSOLETE_INCOMING_CHECKPOINT_CLEANUP_PLAN_STAGED_20261012.json';assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2));v['actual_remote_plan_path']=str(p);v['actual_remote_plan_SHA']=h(p);print(json.dumps(dict(plan_path=str(p),plan_sha256=h(p),files=len(rows),reclaim_bytes=v["planned_reclaim_allocated_bytes"])))
