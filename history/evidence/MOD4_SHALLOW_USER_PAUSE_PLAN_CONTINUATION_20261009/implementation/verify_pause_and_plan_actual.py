from pathlib import Path
import sys,json,base64,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
w=connect_eval();W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 with w.open_sftp() as f:
  get=lambda n:json.loads(f.open(W+'/'+n).read())
  started=get('PLAN_CONTINUATION_WORKER_STARTED.json');state=get('PLAN_CONTINUATION_WORKER_STATE.json')
  try:attention=get('PLAN_CONTINUATION_WORKER_ATTENTION.json')
  except FileNotFoundError:attention=None
  assert attention is None and state['pid']==started['pid']
  worker_raw=f.open(W+'/eval_worker_plan_continuation_review.py').read();assert worker_raw==(D/'eval_worker_plan_continuation_review.py').read_bytes()
  rows=[]
  for j in read(R/'USER_PAUSE_EXECUTED.json')['paused_jobs']:
   result=get('jobs/'+j+'/result.json');row={'job_id':j,'original_result':result}
   for n in ('probe.json','trajectory.npz','probe.log'):
    try:
     path=W+'/jobs/'+j+'/'+n;st=f.stat(path)
     row[n]={'path':path,'bytes':st.st_size}
     if n=='probe.json':
      b=f.open(path).read();(R/j).mkdir(exist_ok=True);(R/j/n).write_bytes(b)
      row[n].update(sha256=hashlib.sha256(b).hexdigest(),not_independently_reviewed_or_admitted=True)
    except FileNotFoundError:pass
   rows.append(row)
   assert j not in state['jobs'] and j in started['human_paused_shallow_jobs']
 ps="""$ErrorActionPreference='Stop'; $rows=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'} | ForEach-Object {[pscustomobject]@{pid=$_.ProcessId;ppid=$_.ParentProcessId;argv=$_.CommandLine;creation=([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});$task=Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_plan_continuation_review';$xml=Export-ScheduledTask -TaskName $task.TaskName; [pscustomobject]@{processes=$rows;task=$task.TaskName;state=$task.State.ToString();triggers=([xml]$xml).Task.Triggers.ChildNodes.Count;old_task_state=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_shallow_boundary_review').State.ToString()}|ConvertTo-Json -Compress -Depth 6"""
 _,o,e=w.exec_command('powershell -NoProfile -EncodedCommand '+base64.b64encode(ps.encode('utf-16-le')).decode(),timeout=40)
 b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');actual=json.loads(b)
 process=[p for p in actual['processes'] if p['pid']==started['pid']]
 assert len(process)==1 and 'eval_worker_plan_continuation_review.py' in process[0]['argv'] and abs(process[0]['creation']-started['epoch'])<1
 assert actual['triggers']==0 and actual['old_task_state']=='Disabled'
 assert not any('eval_worker_shallow_boundary_review.py' in p['argv'] or any(j in p['argv'] for j in started['human_paused_shallow_jobs']) for p in actual['processes'])
 a=read(D.parent/'MOD4_D7_FULL_CONTRACT_20261009/reports/D7_CURRENT_ACTUAL.json')
 assert a['attention'] is None and a['actual_child'] and time.time()-a['epoch']<600
 v={'epoch':time.time(),'human_request':read(R/'USER_PAUSE_EXECUTED.json')['human_instruction'],'paused_scope':'Optional synthetic shallow-terrain zero-shot tests; main training and approved curriculum continue.','user_pause_executed':read(R/'USER_PAUSE_EXECUTED.json'),'retained_case_status':rows,'current_eval_started':started,'current_eval_processes':actual,'current_eval_source_SHA':hashlib.sha256(worker_raw).hexdigest(),'current_attention':attention,'normal_plan_queue_continues':True,'valid_complete_not_replayed':True,'no_new_shallow_cases_published':True,'no_scope_graduation_or_large_jump':True,'main_actual':{k:a[k] for k in ('epoch','actual_owner','actual_child','actual_guardian','actual_tail_adjusted_remaining_seconds')},'main_own_save':a['current']['checkpoint'],'main_frozen_source_count':277,'main_own_snapshot_count':a['current']['snapshot_count'],'main_PPO_log_updates':a['current']['PPO_log_updates'],'main_runtime_GPU_PPO_canonical_transactions':0,'master_SHA_unchanged':'812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'}
 (R/'SHALLOW_USER_PAUSE_PLAN_CONTINUED_REVIEW.json').write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf8')
 print(json.dumps({'pause_verified':True,'eval_worker':process[0],'main_trainer':a['actual_child']['pid'],'main_iterations':v['main_PPO_log_updates'],'paused_cases':[{'job':r['job_id'],'original_phase':r['original_result']['phase']} for r in rows]},ensure_ascii=False))
finally:w.close()
