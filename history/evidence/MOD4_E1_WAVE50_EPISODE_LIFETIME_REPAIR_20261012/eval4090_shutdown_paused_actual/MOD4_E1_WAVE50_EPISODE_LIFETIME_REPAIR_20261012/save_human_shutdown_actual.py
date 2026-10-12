from pathlib import Path
import os, sys, json, time, hashlib, traceback, tomllib
import stage_lifetime_target_CPU_once as io

D=Path(__file__).resolve().parent
TRAIN='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012'
EVAL='/home/egde/rl_candidates/MOD4_WAVE50_EVAL4090_FROZEN_20261012'
SHA='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
STAMP=str(time.time_ns())
BACK=D/('shutdown_backup_'+STAMP)

STATUS=r'''
from pathlib import Path
import json,time,hashlib,fcntl,subprocess,sys
D=Path(TRAIN_TOKEN);V=Path(EVAL_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')]
import supervise_wave50_lifetime_async_reviewed_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=j(D/'reports/E1_STATE.json');passed=j(D/'reports/e1_WAVE50_episode_lifetime_observation_PASSED.json');run=Path(passed['run']);latest=j(run/'latest_complete.json');p=Path(latest['checkpoint'])
assert h(p)==SHA_TOKEN and latest['pid']==3447391
B=own.s.q.ctl.CANONICAL;before=B.read_bytes();budget=j(B);controller=j(own.s.q.ctl.STATE_PATH)
assert budget['active_segment'] is None and not controller.get('active_training')
seg=[v for v in budget['completed_segments'] if v['pid']==latest['pid']];assert len(seg)==1
assert state['phase']=='E1_WAVE50_episode_lifetime_saved_review_ready' and state['child'] is None
batch=j(V/'reports/BATCH_COMPLETE.json');assert batch['all4_actualcomplete_errorfree'] and batch['source_SHA']==SHA_TOKEN
results={p.parent.name:j(p) for p in (V/'jobs').glob('*/result.json')};assert len(results)==4 and all(v['phase']=='complete' and v['exit_code']==0 and not v['errors'] and not v['error_files'] and v['checkpoint']['sha256']==SHA_TOKEN for v in results.values())
locs=[state['owner'],j(D/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=3447391,start_ticks=None),j(V/'reports/BATCH_STARTED.json')['owner']]
locs.extend(j(p)['child'] for p in (V/'jobs').glob('*/ACTIVE.json'))
processes=[dict(expected=x,actual=own.identity(x['pid'])) for x in locs]
assert all(not a['actual'] or a['actual']['state']=='Z' or (a['expected'].get('start_ticks') is not None and a['actual']['start_ticks']!=a['expected']['start_ticks']) for a in processes)
matching=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:
  argv=(q/'cmdline').read_bytes().replace(bytes([0]),b' ').decode('utf8','replace')
  cwd=str((q/'cwd').resolve())
  if str(D) in argv or str(V) in argv or cwd.startswith(str(D)) or cwd.startswith(str(V)):
   ident=own.identity(int(q.name))
   if ident and ident['pid']!=__import__('os').getpid() and ident['state']!='Z':matching.append(ident)
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
# The SSH shell launching this read-only observer embeds the root strings in its command.
owned_live=[p for p in matching if any(s in ' '.join(p.get('argv',[])) for s in ('supervise_wave50_lifetime_async_reviewed_once.py','train_wave50_lifetime','native_e1_wave50_lifetime','eval4090_frozen_batch_once.py','frozen_history_flat.py','frozen_history_spin.py','frozen_history_world.py'))]
assert not owned_live and not own.parent.trainers()
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',own.s.q.P/'autonomy_controller.lock',V/'evaluation_only.lock'):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(q),actual_fcntl_free=True))
gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits']).decode().strip()
assert not gpu
inventory=[];paths=list(run.rglob('*'))+list((D/'reports').rglob('*'))+list((V/'jobs').rglob('*'))+list((V/'reports').rglob('*'))
paths.extend(p for p in D.iterdir() if p.is_file() and p.suffix in ('.log','.json'))
paths.append(V/'eval4090_frozen_batch_once.py')
for q in (V/'runtimes').rglob('*'):
 if q.is_file() and q.name in ('PATH_ADAPTER.json','SOURCE_MANIFEST.json'):paths.append(q)
seen=set()
for q in paths:
 if not q.is_file() or str(q) in seen:continue
 seen.add(str(q));root=D if q.is_relative_to(D) else V;kind='training' if root==D else 'evaluation'
 inventory.append(dict(remote_path=str(q),backup_relative=kind+'/'+q.relative_to(root).as_posix(),bytes=q.stat().st_size,sha256=h(q)))
assert B.read_bytes()==before
print(json.dumps(dict(epoch=time.time(),passed=True,human_paused=True,training_root=str(D),evaluation_root=str(V),own_checkpoint=dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)),formal_final_complete=True,source_count=459,actual_CPU_floating_count=107,actual_module_snapshots=104,unique_completed_segment=seg[0],unique_loadlearnsaveexit_seconds=seg[0]['ended_epoch']-seg[0]['started_epoch'],canonical=dict(path=str(B),sha256=h(B),active_segment=None,remaining_snapshot_seconds=budget['remaining_training_seconds'],authorized_seconds=budget['authorized_training_seconds'],extensions=len(budget['budget_extensions']),snapshot_not_new_budget_authority=True),controller_active_training=None,training_state=state,expected_process_receipts=processes,owned_live_processes=owned_live,three_fcntl_free=locks,GPU_compute_processes=gpu,all4_evaluation_actualcomplete_errorfree=True,evaluation_results=results,complete_behavior_review_pending=True,inventory=inventory,no_signal_restart_GPU_PPO_budgetwrite_or_delete=True)))
'''

def dump(p,v):
 assert not p.exists(),str(p)
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(json.dumps(v,ensure_ascii=False,indent=2).encode());f.flush();os.fsync(f.fileno())

def main():
 settings=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert settings['status']=='PAUSED' and settings['rrule']=='FREQ=HOURLY;INTERVAL=1'
 BACK.mkdir();dump(BACK/'AUTOMATION_PAUSED_ACTUAL.json',dict(epoch=time.time(),id=settings['id'],status=settings['status'],rrule=settings['rrule'],target_thread_id=settings['target_thread_id'],prompt=settings['prompt'],automatic_launch_prohibited_until_human_resume=True))
 n,w=io.connect_linux_only()
 try:
  code=STATUS.replace('TRAIN_TOKEN',repr(TRAIN)).replace('EVAL_TOKEN',repr(EVAL)).replace('SHA_TOKEN',repr(SHA))
  compile(code,'<shutdown-readonly>','exec');v=io.run(n,code)
  dump(BACK/'SHUTDOWN_SAFE_REMOTE_ACTUAL.json',v)
  print(json.dumps(dict(remote_save_exit_idle_verified=True,model_SHA=v['own_checkpoint']['sha256'],files=len(v['inventory']),bytes=sum(x['bytes'] for x in v['inventory']),eval4_complete=True)),flush=True)
  copied=[]
  with n.open_sftp() as s:
   for index,row in enumerate(v['inventory']):
    target=BACK/row['backup_relative'];target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists()
    digest=hashlib.sha256();count=0
    with s.open(row['remote_path'],'rb') as src,target.open('xb') as dst:
     src.prefetch(row['bytes'])
     while True:
      b=src.read(1024*1024)
      if not b:break
      dst.write(b);digest.update(b);count+=len(b)
     dst.flush();os.fsync(dst.fileno())
    assert count==row['bytes'] and digest.hexdigest()==row['sha256'],row['remote_path']
    copied.append(dict(row,local_path=str(target.resolve()),actual_local_bytes=count,actual_local_sha256=digest.hexdigest(),byteexact=True))
    if index%100==0:print(json.dumps(dict(backup_progress_files=index+1,total=len(v['inventory']))),flush=True)
  dump(BACK/'BACKUP_COMPLETE_BYTEEXACT.json',dict(epoch=time.time(),passed=True,files=copied,all_sources_retained_on4090=True,no_new_GPU_or_budget_transaction=True))
  handoff='''# Human requested training pause for shutdown/restart\n\nTraining and the four one-off 4090 frozen evaluations have naturally completed. The exact source459 latest full-state checkpoint has been copied with all own-run source snapshots, startup receipts, health, traces, reports and evaluation raw files; BACKUP_COMPLETE_BYTEEXACT.json binds every original and local path/size/SHA. Source checkpoint SHA d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a; model32264, floating CPU tensors107, lifetime bool/int fields separately retained, source459,104 module snapshots. Formal6updates144controls; unique335.22595477104187s settled once by original parent. Actual parent/guardian/trainer/evaluation children exited, three OS flock locks free, canonical/controller active empty. No kill, restart, clearing ledger or budget transaction.\n\nmod4-10 is PAUSED at the existing hourly schedule and target. No training/evaluation launch or automatic resume until the human explicitly requests continuation. Shutdown/restart itself must be performed by the human. Other AI, environments, previous expert weights and the WASD player are untouched.\n\nAll four new eval4090-lifetime459-d05c jobs are actualcomplete/errorfree and raw files backed up. Complete independent behavioral/query/contact/full-route/retention review is still pending; no 50mm qualification or70mm training claim. Backend is4090 Linux, not cross-host equivalence.3060 currently unavailable per human. No global154 job has been claimed.\n\nSecond same-lifetime parallel training was only partially prepared locally; prepare_same_lifetime_parallel_second_once.py failed with an original SyntaxError before target root/sourcefreeze/CPU/GPU/dispatch. One worker exists under payload_second_parallel; controller/sourceguard uncreated. Preserve original builder/error; do not repair/deploy while paused. Training/evaluation concurrency has not been implemented or demonstrated.\n\nOn explicit human resume, first read fresh /proc identity/cwd/argv, canonical unique accounting and actual OS flock state. Review this source459 own final checkpoint/startup/snapshots and all four backed-up4090 result/raw files under original physical/query/contact/COM/hardware tolerances before deciding an independently admitted bounded second same-lifetime block or diagnosis. Existing old once/main/resume/dispatch/preflights/publish/record/sync/budget transactions must not be rerun. Required new source must strictly restore same geometry-entry-direction-route-lifetime private state, all actor/critic/optimizer/std/D0D7/globalnamed/private CPUCUDA RNG, actual CUDA roundtrip and episode+1; save independent output. Resource guard uses current durable capacity and actual completed output; no deletion/tmpfs/guard relaxation.\n\n005 solecanonical1188000s/330h, seven extensions already applied; local canonical summary is readonly evidence, not another authority. No extension/refund/copy/clearactive/tail. Old719 cleanup and exact failedPID kill approvals are consumed. E0, accepted35b026, CURB20own7b, SLOPE5/8/10 observed scopes frozen; gate untrained, hardware uncalibrated, S8 requires separate approval. All prior failures/false/raw/cost retained. All saved sources, original errors, reports, backup indices, pause/sync/monitor/Git receipts must be committed; weights/rawNPZ/USD/ZIP index only, credentials excluded.\n'''
  p=BACK/'SHUTDOWN_RESUME_HANDOFF.md'
  with p.open('x',encoding='utf8',newline='\n') as f:f.write(handoff);f.flush();os.fsync(f.fileno())
  io.save('HUMAN_SHUTDOWN_BACKUP_COMPLETE_'+STAMP+'.json',dict(epoch=time.time(),passed=True,backup_directory=str(BACK.resolve()),safe_actual=str(BACK/'SHUTDOWN_SAFE_REMOTE_ACTUAL.json'),manifest=str(BACK/'BACKUP_COMPLETE_BYTEEXACT.json'),handoff=str(p),handoff_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),weights_and_raw_originals_retained=True,behavior_review_pending=True,human_resume_required=True))
  print(json.dumps(dict(passed=True,backup=str(BACK),files=len(copied),bytes=sum(x['bytes'] for x in copied),safe_to_restart_owned_workload=True)),flush=True)
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)

if __name__=='__main__':
 try:main()
 except BaseException:io.save('HUMAN_SHUTDOWN_BACKUP_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_new_GPU_or_training_restart=True));raise
