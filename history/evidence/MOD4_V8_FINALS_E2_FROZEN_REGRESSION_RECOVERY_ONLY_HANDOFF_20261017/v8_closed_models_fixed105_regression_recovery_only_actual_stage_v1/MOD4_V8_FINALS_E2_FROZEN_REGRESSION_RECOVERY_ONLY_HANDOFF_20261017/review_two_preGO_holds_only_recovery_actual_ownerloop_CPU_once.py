"""Actual unchanged owner loop, localhost mock nodes, H1 resource rejection before GO."""
from pathlib import Path
import sys,types,time,json,hashlib,hmac,threading,urllib.request,traceback,tempfile
F=Path(__file__).resolve().parent;R=F/'reports'
def main():
 sys.modules['fcntl']=types.SimpleNamespace(LOCK_EX=1,LOCK_NB=2,LOCK_UN=8,flock=lambda *a:None)
 import three_slot_common_v1 as b
 import three_slot_finite_owner_v1 as own
 temp=Path(tempfile.mkdtemp(prefix='mod4_H1_storage_preGO_CPU_'));own.B=temp;b.B=temp;b.C=temp/'fixture_budget.json';b.LOCKS=(temp/'lock1',temp/'lock2')
 for p in b.LOCKS:p.write_text('Mock fcntl only')
 b.put(b.C,dict(authorized_training_seconds=1188000,budget_extensions=[{}]*7,charged_training_seconds=1000.,remaining_training_seconds=1187000.,active_segment=None,completed_segments=[]))
 actual=own.http.server.ThreadingHTTPServer;server=[None];errors=[]
 def local(addr,handler):
  assert addr==('10.24.4.210',29754);server[0]=actual(('127.0.0.1',0),handler);return server[0]
 own.http.server.ThreadingHTTPServer=local;token='[REDACTED]';run='CPU_H1_STORAGE_E2_BEHAVIOR_HOLD_RECOVERY_ONLY'
 fields={'h1':'sourceactor9critic8STD17Adam_literal_exact','e2':'source_actor9_critic8_STD17Adam_literal_bytes_exact','recovery':'all_original_core_tensor_bytes_exact'}
 specs={k:dict(key=k,source_SHA=hashlib.sha256(k.encode()).hexdigest(),manifest_SHA=hashlib.sha256(('m'+k).encode()).hexdigest(),GPU_UUID=b.GPUS[k],max_parent_seconds=3600,exit_headroom_seconds=300,native_controls={'h1':180,'e2':144,'recovery':336}[k]) for k in b.CAPS}
 def run_owner():
  try:own.owner(dict(role='owner',experts=specs,token=token,run_id=run))
  except BaseException:errors.append(traceback.format_exc())
 thread=threading.Thread(target=run_owner,daemon=True);thread.start();start=time.time()
 while server[0] is None and time.time()-start<5:time.sleep(.02)
 assert server[0] is not None
 def row(key,ready=False,terminal=False):
  s=specs[key];v=dict(passed=True,source_SHA=s['source_SHA'],controls=s['native_controls'],callbacks=s['native_controls']*4);v[fields[key]]=True
  return dict(key=key,phase='resource_admission_rejected' if key=='h1' else ('production' if terminal else ('ready' if ready else 'native')),manifest_SHA=s['manifest_SHA'],native_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True) if ready else None,native_GPU_waited_EXIT0=ready,terminal_all_own_children_waited=terminal,returncode=(1 if key=='h1' else 0) if terminal else None,original_error=key=='h1')
 def post(v):
  raw=json.dumps(dict(epoch=time.time(),run_id=run,row=v)).encode();req=urllib.request.Request('http://127.0.0.1:'+str(server[0].server_port)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token.encode(),raw,hashlib.sha256).hexdigest()})
  with urllib.request.urlopen(req,timeout=5) as response:body=response.read();assert hmac.compare_digest(response.headers['X-Own-Signature'],hmac.new(token.encode(),body,hashlib.sha256).hexdigest());return json.loads(body)
 rejected=row('h1',terminal=True);assert not b.valid_ready(rejected,specs['h1']);assert not post(rejected)['go'];assert b.read(b.C)['active_segment'] is None
 held=row('e2',terminal=True);held.update(phase='frozen_behavior_review_hold_before_worker',native_CPU=None,native_GPU_waited_EXIT0=False,original_error=False,actual_own_children_count=0);assert not b.valid_ready(held,specs['e2']) and not post(held)['go'];assert b.read(b.C)['active_segment'] is None;post(row('recovery'))
 def go(k):
  started=time.time()
  while time.time()-started<12:
   reply=post(row(k,True))
   if reply.get('go'):assert not reply['stop'];return reply['go']
   time.sleep(.2)
  raise AssertionError(k+' mock GO missing')
 go('recovery');assert not post(rejected)['go'] and not post(held)['go'];post(row('recovery',terminal=True));thread.join(12);assert not thread.is_alive() and not errors,errors
 c=b.read(b.C);assert c['active_segment'] is None and len(c['completed_segments'])==1;a=c['completed_segments'][0];assert set(a['experts'])=={'recovery'} and set(a['actual_terminal_rows'])==set(specs);assert 'h1' not in a['experts'] and 'e2' not in a['experts'];assert abs(sum(v['charged_seconds'] for v in a['experts'].values())-a['charged_expert_seconds'])<1e-6
 files=[dict(path=str(p),bytes=p.stat().st_size,SHA=b.H(p),value=b.read(p)) for p in temp.glob('*.json')]
 out=dict(epoch=time.time(),passed_CPU_localhost_only=True,unchanged_actual_owner_loop=True,H1_declared_resource_rejection_registered_terminal_before_any_GO=True,H1_never_ready_never_GO_zero_charge=True,only_recovery_ready_proceeds_H1_and_E2_no_GO_zero_charge=True,one_fixture_original_writer_exact_distinct_interval_settlement=True,no_real_GPU_SDK_OS_lock_or_canonical_mutation=True,mock_fcntl_only=True,fixture_directory=str(temp),files=files)
 with (R/'H1_STORAGE_E2_BEHAVIOR_HOLD_RECOVERY_ONLY_UNCHANGED_OWNER_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps({k:v for k,v in out.items() if k!='files'}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('RECOVERY_ONLY_H1_E2_PREGO_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),CPU_only=True),f,indent=2)
  raise
