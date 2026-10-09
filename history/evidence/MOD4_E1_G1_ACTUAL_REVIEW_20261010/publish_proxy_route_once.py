"""Publish only two new frozen route cases; no training authority or canonical writes."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sha=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G1_REPAIR_20261009'
def main():
 start=R/'PROXY_ROUTE_PUBLISH_STARTED.json';assert not start.exists();start.write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-PROXY-ROUTE-PUBLISH-02',no_retry_old_once=True)),encoding='utf8')
 v=json.loads((R/'FULL_ROUTE_PROXY_CPU_PREPARED.json').read_bytes());assert v['CPU']['passed'];pkg=v['package'];assert sha(Path(pkg['path']).read_bytes())==pkg['sha256']
 collected=json.loads(sorted(R.glob('COLLECTED_*.json'))[-1].read_bytes());assert json.loads((R/'E1_FULL_ROUTE_REVIEW_WORKER_ADMITTED.json').read_bytes())['admission']['shared_GPU_lock_was_free']
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as sf:
   before=sf.open('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read();ledger=json.loads(before);assert ledger['active_segment'] is None
   state=json.loads(sf.open(ROOT+'/reports/E1_STATE.json').read());assert state['phase']=='E1_G1_repair_saved_review_ready' and state['child'] is None
   path=E+'/artifacts/'+Path(pkg['path']).name
   try:sf.stat(path)
   except FileNotFoundError:
    sf.put(pkg['path'],path+'.partial');assert sha(sf.open(path+'.partial').read())==pkg['sha256'];sf.rename(path+'.partial',path)
   else:assert sha(sf.open(path).read())==pkg['sha256']
   runtime=dict(path=path,bytes=pkg['bytes'],sha256=pkg['sha256']);jobs=[]
   template=collected['publications'][0]['jobs'][0]
   for role,source in [('anchor32053',collected['publications'][0]['source']),('candidate32098',collected['publications'][1]['source'])]:
    assert sha(sf.open(source['path']).read())==source['sha256']
    m=json.loads(json.dumps(template));jid='clk2500-closure-episode-d3-120-e1-g1-fullroute-'+role+'-flat'
    m.update(job_id=jid,published_epoch=time.time(),actual_behavior_scope='same G1 derived10mm entire wave segment, disjoint actual wave-family tiles, before/after support; frozen no-learning route correction',role=role,protocol=v['protocol'],scope_pending_actual_review=True,not_user_paused93_94=True,no_learning=True,canonical_write_authority=False)
    m['artifacts']['runtime']=runtime;m['artifacts']['checkpoint']=source
    dest=E+'/eval_queue/'+jid+'.json';raw=json.dumps(m,indent=2).encode()
    with sf.open(dest+'.partial','wbx') as out:out.write(raw)
    assert sf.open(dest+'.partial').read()==raw;sf.rename(dest+'.partial',dest);assert sf.open(dest).read()==raw;jobs.append(m)
   assert sf.open('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read()==before
  report=dict(epoch=time.time(),trial_id='E1-G1-PROXY-ROUTE-PUBLISH-02',runtime=runtime,jobs=jobs,actual_results_pending=True,CPU_static_admission_only=True,old117_118_cases_not_reissued=True,failed32098_not_selected_for_PPO=True,failed_worker_replaced_after_actual_exit_lockfree=True,canonical_bytes_unchanged=True,no_4090_runtime_or_GPU_PPO_mutation=True,new_budget_seconds=0)
  (R/'PROXY_ROUTE_PUBLISHED.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(published=[x['job_id'] for x in jobs],runtime=runtime,no_learning=True,new_budget_seconds=0),ensure_ascii=True))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  (R/'PROXY_ROUTE_PUBLISH_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-PROXY-ROUTE-PUBLISH-02',error=traceback.format_exc(),do_not_blindly_republish_existing_jobs=True),indent=2),encoding='utf8');raise
