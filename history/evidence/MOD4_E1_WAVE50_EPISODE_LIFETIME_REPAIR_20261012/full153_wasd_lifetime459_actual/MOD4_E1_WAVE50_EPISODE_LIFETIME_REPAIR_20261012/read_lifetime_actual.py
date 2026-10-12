from pathlib import Path
import os,json,time,traceback
import stage_lifetime_target_CPU_once as io
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012'
def main():
 n,w=io.connect_linux_only()
 try:
  v=io.run(n,r'''from pathlib import Path
import sys,json,time,hashlib
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')]
import supervise_wave50_lifetime_async_reviewed_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();R=D/'reports'
state=j(R/'E1_STATE.json') if (R/'E1_STATE.json').exists() else None;attention=j(R/'E1_ATTENTION.json') if (R/'E1_ATTENTION.json').exists() else None
stages={p.name:j(p) for p in R.glob('*PASSED.json') if 'CPU' not in p.name};runs=[]
for kind in ('learning_logs','discard_logs','fresh_process_resume'):
 for run in ([D/kind] if kind=='fresh_process_resume' else list((D/kind).glob('*'))):
  if not run.is_dir():continue
  mf=j(run/'run_manifest.json') if (run/'run_manifest.json').exists() else None
  latest=j(run/'latest_complete.json') if (run/'latest_complete.json').exists() else None
  health=j(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None
  markers={p.name:j(p) for p in run.glob('*STARTUP_VERIFIED.json')}
  runs.append(dict(path=str(run),kind=kind,manifest_source_count=len(mf['source_map']) if mf else None,manifest_lifetime=mf.get('actual_episode_lifetime') if mf else None,latest_complete=latest,health=health,startup_markers=markers))
locs=[state['owner']] if state else [];locs+=([state['child']] if state and state.get('child') else [])
log=D/'controller.log';b=log.read_bytes() if log.exists() else b''
for p in sorted(D.glob('*.error*')):pass
print(json.dumps(dict(epoch=time.time(),root=str(D),source_count=len(j(R/'SOURCE_FREEZE.json')['sha256']),state=state,attention=attention,actual_processes=[own.identity(x['pid']) for x in locs],actual_stages=stages,runs=runs,publication=j(R/'E1_WAVE50_ASYNC_PUBLISHED.json') if (R/'E1_WAVE50_ASYNC_PUBLISHED.json').exists() else None,publication_pending=j(R/'E1_WAVE50_ASYNC_PUBLICATION_PENDING.json') if (R/'E1_WAVE50_ASYNC_PUBLICATION_PENDING.json').exists() else None,controller_log_index=dict(path=str(log),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()),controller_log_tail=b[-7000:].decode('utf8','replace'),canonical_active_segment=own.s.q.base.budget_state()['active_segment'],no_GPU_or_budget_write_by_reader=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=io.save('LIFETIME_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),source_count=v['source_count'],phase=v['state']['phase'] if v['state'] else None,attention=v['attention'],actual_processes=v['actual_processes'],passed_stages=list(v['actual_stages']),runs=[dict(kind=x['kind'],path=x['path'],has_manifest=x['manifest_source_count'],latest=x['latest_complete'],controls=x['health']['control_steps'] if x['health'] else None,startup=list(x['startup_markers'])) for x in v['runs']],controller_log_tail=v['controller_log_tail'][-1400:])))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:io.save('READ_LIFETIME_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU=True));raise
