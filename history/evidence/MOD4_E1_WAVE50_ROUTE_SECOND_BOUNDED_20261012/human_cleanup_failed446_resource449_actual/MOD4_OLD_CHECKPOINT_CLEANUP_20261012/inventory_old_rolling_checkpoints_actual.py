"""Inventory only: earliest superseded rolling checkpoints, conservative reference protection."""
from cleanup_io import *

def main():
    save('HUMAN_OLD_OBSOLETE_CHECKPOINT_CLEANUP_AUTHORIZATION.json',dict(epoch=time.time(),human_text='远古一些废旧检查点可以清理',authorization_scope='old_obsolete_checkpoint_files_only',supersedes_prior_blanket_weight_retention_only_for_confirmed_obsolete_old_files=True,no_report_source_environment_cache_raw_active_accepted_or_restore_source_deletion=True,goal='restore_durable_save_capacity_then_continue_authorized_route_second1800'))
    n,w=io.connect_both()
    try:
      v=run(n,r'''from pathlib import Path
from datetime import datetime,timezone,timedelta
import os,re,json,time,shutil,stat
B=Path('/home/egde/rl_candidates').resolve();cutoff=datetime(2026,10,1,tzinfo=timezone(timedelta(hours=8))).timestamp();refs=set();reference_files=0;models=[];active_paths=[]
pattern=re.compile(rb'model_[0-9]+\.pt')
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  argv=[x.decode(errors='replace') for x in p.read_bytes().split(b'\0') if x];cwd=(p.parent/'cwd').resolve()
  if any(str(B) in x for x in argv):
   active_paths.append(dict(pid=int(p.parent.name),cwd=str(cwd),argv=argv))
 except (OSError,ValueError):pass
for root,dirs,names in os.walk(B,followlinks=False):
 dirs[:]=[x for x in dirs if x not in ('__pycache__','.git') and not Path(root,x).is_symlink()]
 for name in names:
  p=Path(root,name)
  if p.is_symlink():continue
  if re.fullmatch(r'model_[0-9]+\.pt',name):
   s=p.stat();models.append(dict(path=str(p),name=name,run=str(p.parent),bytes=s.st_size,allocated_bytes=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,device=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,mtime_epoch=s.st_mtime))
  elif p.suffix.lower() in ('.json','.md','.py','.txt'):
   try:
    with p.open('rb') as f:
     tail=b''
     for block in iter(lambda:f.read(1048576),b''):
      data=tail+block;refs.update(x.decode() for x in pattern.findall(data));tail=data[-128:]
    reference_files+=1
   except OSError:pass
byrun={}
for x in models:byrun.setdefault(x['run'],[]).append(x)
keepers=set()
for run,rows in byrun.items():
 rows.sort(key=lambda x:int(x['name'][6:-3]));keepers.add(rows[0]['path']);keepers.update(x['path'] for x in rows[-3:])
candidates=[];protected=[]
for x in models:
 p=Path(x['path']);reasons=[]
 if x['mtime_epoch']>=cutoff:reasons.append('recent_20261001_or_later')
 if x['path'] in keepers:reasons.append('run_first_or_last3_checkpoints_retained')
 if x['name'] in refs:reasons.append('filename_referenced_in_saved_source_report_plan_or_receipt')
 if x['nlink']!=1:reasons.append('nonunique_hardlink')
 if not p.relative_to(B).parts[0].startswith('MOD4_'):reasons.append('not_named_MOD4_owned_root')
 if any(k in str(p).lower() for k in ('reference','artifacts','official','pretrained','assets')):reasons.append('reference_or_artifact_or_asset_scope')
 for proc in active_paths:
  roots=[]
  for a in proc['argv']:
   if a.startswith(str(B)+'/'):
    q=Path(a);roots.append(B/q.relative_to(B).parts[0])
  if any(p.is_relative_to(q) for q in roots):reasons.append('currently_running_process_own_root');break
 if reasons:protected.append(dict(path=x['path'],bytes=x['bytes'],reasons=reasons))
 else:x['reason']='old_before20261001_unreferenced_superseded_rolling_checkpoint';candidates.append(x)
candidates.sort(key=lambda x:(x['mtime_ns'],x['path']))
print(json.dumps(dict(epoch=time.time(),inventory_only_no_deletion=True,root=str(B),cutoff_local='2026-10-01 00:00:00 +08:00',durable_free_bytes=shutil.disk_usage(B).free,total_model_files=len(models),total_model_bytes=sum(x['bytes'] for x in models),scanned_reference_files=reference_files,referenced_model_basenames=len(refs),actual_active_processes=active_paths,protected=protected,candidates=candidates,candidate_bytes=sum(x['bytes'] for x in candidates),candidate_allocated_bytes=sum(x['allocated_bytes'] for x in candidates),all_reports_sources_env_cache_raw_noncheckpoint_files_untouched=True)))
''')
      p=save('OLD_ROLLING_CHECKPOINT_INVENTORY_'+str(time.time_ns())+'.json',v)
      print(json.dumps(dict(report=str(p),model_files=v['total_model_files'],candidate_count=len(v['candidates']),candidate_bytes=v['candidate_bytes'],free_bytes=v['durable_free_bytes'],earliest_candidates=v['candidates'][:5])))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('OLD_CHECKPOINT_INVENTORY_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_deletion_or_GPU_or_budget_write=True));raise
