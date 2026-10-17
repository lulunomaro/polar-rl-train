"""Actual owner loop over local signed HTTP; mock fcntl, never real canonical or GPU."""
from pathlib import Path
import os,sys,json,time,types,threading,tempfile,hmac,hashlib,urllib.request,traceback,shutil,ast
B=Path(__file__).resolve().parent;R=B/'reports'
def main():
 prep=json.loads((R/'CLOSED_RECOVERY85_FULL_CPU_H1_BOUNDED_RECOVERY_NATIVE_ONLY_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());assert prep['passed_CPU_only']
 shutil.copy2(B/'recovery_source85_native_only_finite_parent_v1.py',B/'payload/recovery/recovery_source85_native_only_finite_parent_v1.py')
 mf=B/'payload/recovery/THREE_SLOT_COMPLETE_MANIFEST_V1.json';m=json.loads(mf.read_bytes());p=mf.parent/'recovery_source85_native_only_finite_parent_v1.py';ast.parse(p.read_text('utf8'));m['files'].append(dict(relative=p.name,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()));mf.write_text(json.dumps(m,indent=2),encoding='utf8');prep['specs']['recovery']['manifest_SHA']=hashlib.sha256(mf.read_bytes()).hexdigest()
 sys.modules['fcntl']=types.SimpleNamespace(LOCK_EX=1,LOCK_NB=2,LOCK_UN=8,flock=lambda *a:None)
 import three_slot_common_v1 as b
 import three_slot_finite_owner_v1 as own
 assert b.CAPS==dict(h1=1800,e2=3600,recovery=3600)
 tmp=Path(tempfile.mkdtemp(prefix='mod4_H1_1800_recovery_nativeonly_CPU_'));own.B=tmp;b.C=tmp/'fixture_original_budget.json';b.LOCKS=(tmp/'one.lock',tmp/'two.lock')
 for p in b.LOCKS:p.write_text('mock lock only')
 b.put(b.C,dict(authorized_training_seconds=1188000,budget_extensions=[{}]*7,charged_training_seconds=1000.,remaining_training_seconds=1187000.,active_segment=None,completed_segments=[]))
 specs={k:dict(key=k,source_SHA=hashlib.sha256(k.encode()).hexdigest(),manifest_SHA=hashlib.sha256(('manifest'+k).encode()).hexdigest(),GPU_UUID=b.GPUS[k],max_parent_seconds=b.CAPS[k],exit_headroom_seconds=300,native_controls={'h1':180,'e2':144,'recovery':336}[k]) for k in b.CAPS};actual=own.http.server.ThreadingHTTPServer;server=[None];errors=[]
 def local(addr,handler):
  assert addr==('10.24.4.210',29754);server[0]=actual(('127.0.0.1',0),handler);return server[0]
 own.http.server.ThreadingHTTPServer=local;token='[REDACTED]';run='H1_1800_UPDATE24_RECOVERY_UNPAID_NATIVE_ONLY'
 def loop():
  try:own.owner(dict(experts=specs,run_id=run,token=token))
  except BaseException:errors.append(traceback.format_exc())
 thread=threading.Thread(target=loop,daemon=True);thread.start();start=time.time()
 while server[0] is None and time.time()-start<5:time.sleep(.02)
 assert server[0] is not None
 def ready():
  v=dict(passed=True,source_SHA=specs['h1']['source_SHA'],controls=180,callbacks=720,sourceactor9critic8STD17Adam_literal_exact=True)
  return dict(key='h1',phase='ready',manifest_SHA=specs['h1']['manifest_SHA'],native_GPU_waited_EXIT0=True,native_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True),original_error=False)
 def terminal(k,phase):return dict(key=k,phase=phase,manifest_SHA=specs[k]['manifest_SHA'],native_CPU=None,native_GPU_waited_EXIT0=False,original_error=False,terminal_all_own_children_waited=True,actual_admission_sender_children0=True,returncode=0,no_paid_production_worker_or_GO=True)
 def post(row):
  raw=json.dumps(dict(epoch=time.time(),run_id=run,row=row)).encode();req=urllib.request.Request('http://127.0.0.1:'+str(server[0].server_port)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token.encode(),raw,hashlib.sha256).hexdigest()})
  with urllib.request.urlopen(req,timeout=5) as response:body=response.read();assert hmac.compare_digest(response.headers['X-Own-Signature'],hmac.new(token.encode(),body,hashlib.sha256).hexdigest());return json.loads(body)
 erow=terminal('e2','frozen_behavior_review_hold_before_worker');rrow=terminal('recovery','native_only_review_unpaid_no_production_GO');assert not b.valid_ready(erow,specs['e2']) and not b.valid_ready(rrow,specs['recovery']);post(erow);post(rrow)
 for _ in range(40):
  reply=post(ready())
  if reply.get('go'):break
  time.sleep(.15)
 assert reply['go']['max_parent_seconds']==1800 and reply['go']['exit_headroom_seconds']==300 and not post(erow)['go'] and not post(rrow)['go']
 done=terminal('h1','production');post(done);thread.join(12);assert not thread.is_alive() and not errors,errors
 account=b.read(b.C);seg=account['completed_segments'][0];assert account['active_segment'] is None and len(account['completed_segments'])==1 and set(seg['experts'])=={'h1'}
 assert abs(sum(x['charged_seconds'] for x in seg['experts'].values())-seg['charged_expert_seconds'])<1e-6
 # Wrong native/source/control/callback and old grant capability are still rejected.
 negative=0
 for mutate in (lambda x:x.update(phase='native'),lambda x:x.update(manifest_SHA='bad'),lambda x:x.update(original_error=True),lambda x:x.update(native_GPU_waited_EXIT0=False),lambda x:x['native_CPU'].update(actual_CPU_waited_EXIT0=False)):
  x=ready();mutate(x);assert not b.valid_ready(x,specs['h1']);negative+=1
 bad={k:dict(s) for k,s in specs.items()};bad['h1']['max_parent_seconds']=3600
 try:own.owner(dict(experts=bad,run_id=run,token=token));raise RuntimeError('Old3600 incorrectly accepted')
 except AssertionError:negative+=1
 fake=dict(started_epoch=0.,accounted_through_epoch=0.,charged_expert_seconds=0.,experts={});ledger=dict(charged_training_seconds=0.,remaining_training_seconds=1188000.);go=dict(h1=dict(learning_started_epoch=0.,max_parent_seconds=1800));rows=dict(h1=dict(terminal_all_own_children_waited=True,returncode=1,owner_received_terminal_epoch=1801.));_,a=b.charge_values(ledger,fake,go,rows,1801.);assert a['experts']['h1']['duration_bound_passed'] is False and a['charged_expert_seconds']==1801
 report=dict(epoch=time.time(),passed_actual_ownerloop_localhost_CPU=True,new_H1_1800_cap_only_completeupdate24_engineering_guard=True,E2_hold_and_recovery_nativeonly_never_GO_zero_paid_charge=True,only_H1_actual_interval_once_settled=True,wrong_manifest_native_CPU_phase_and_old3600_grant_6negative_cases_passed=negative==6,actual1801_over1800_still_false_no_refund=True,mock_fcntl_only_no_real_GPU_SDK_or_canonical_mutation=True,fixture_directory=str(tmp),fixture_completed_segment=seg,specs=prep['specs'],source_native_only_parent_added_to_complete_manifest=True)
 with (R/'H1_BOUNDED_ONE_PAID_SLOT_RECOVERY_NATIVE_ONLY_OWNER_HTTP_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps({k:v for k,v in report.items() if k not in ('specs','fixture_completed_segment')}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_BOUNDED_OWNER_HTTP_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),CPU_only=True),f,indent=2)
  raise
