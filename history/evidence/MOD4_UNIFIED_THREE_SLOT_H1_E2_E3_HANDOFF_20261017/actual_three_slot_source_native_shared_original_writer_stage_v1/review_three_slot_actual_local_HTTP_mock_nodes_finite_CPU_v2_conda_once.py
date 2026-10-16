"""Exercise the actual owner loop/HTTP on localhost with simulated nodes only."""
from pathlib import Path
import os,sys,types,time,json,hashlib,hmac,threading,urllib.request,urllib.error,traceback,tempfile,importlib
U=Path(__file__).resolve().parent;R=U/'reports'
def main():
 fake=types.SimpleNamespace(LOCK_EX=1,LOCK_NB=2,LOCK_UN=8,flock=lambda *a:None);sys.modules['fcntl']=fake;import three_slot_common_v1 as b;import three_slot_finite_owner_v1 as own
 temp=Path(tempfile.mkdtemp(prefix='mod4_three_slot_CPU_HTTP_V2_'));own.B=temp;b.B=temp;b.J=temp/'job0';b.C=temp/'fixture_original_budget.json';b.LOCKS=(temp/'fixture_lock1',temp/'fixture_lock2')
 for p in b.LOCKS:p.write_text('CPU fixture; not a real OS lock')
 budget=dict(authorized_training_seconds=1188000,budget_extensions=[{} for _ in range(7)],charged_training_seconds=1000.,remaining_training_seconds=1187000.,active_segment=None,completed_segments=[]);b.put(b.C,budget);real=own.http.server.ThreadingHTTPServer;server=[None]
 def localhost_server(address,handler):
  assert address==('10.24.4.210',29754);v=real(('127.0.0.1',0),handler);server[0]=v;return v
 own.http.server.ThreadingHTTPServer=localhost_server;token='[REDACTED]';run='LOCAL_CPU_HTTP_FIXTURE';fields={'h1':'sourceactor9critic8STD17Adam_literal_exact','e2':'source_actor9_critic8_STD17Adam_literal_bytes_exact','recovery':'all_original_core_tensor_bytes_exact'};specs={k:dict(key=k,source_SHA=hashlib.sha256(k.encode()).hexdigest(),manifest_SHA=hashlib.sha256(('m'+k).encode()).hexdigest(),max_parent_seconds=b.CAPS[k],exit_headroom_seconds=300,native_controls={'h1':180,'e2':144,'recovery':336}[k],GPU_UUID=b.GPUS[k]) for k in b.CAPS};errors=[]
 def launch():
  try:own.owner(dict(role='owner',experts=specs,token=token,run_id=run))
  except BaseException:errors.append(traceback.format_exc())
 thread=threading.Thread(target=launch,daemon=True);thread.start();begin=time.time()
 while server[0] is None and time.time()-begin<5:time.sleep(.02)
 assert server[0] is not None;url='http://127.0.0.1:'+str(server[0].server_port)+'/'
 def row(key,ready=False,terminal=False,failed=False):
  s=specs[key];v=dict(passed=True,source_SHA=s['source_SHA'],controls=s['native_controls'],callbacks=s['native_controls']*4);v[fields[key]]=True;proof=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
  return dict(key=key,phase='production' if terminal else ('ready' if ready else 'native'),native_GPU_waited_EXIT0=ready,native_CPU=proof if ready else None,manifest_SHA=s['manifest_SHA'],terminal_all_own_children_waited=terminal,returncode=(1 if failed else 0) if terminal else None,original_error=failed)
 def post(row,wrong=False):
  raw=json.dumps(dict(epoch=time.time(),run_id=run,row=row)).encode();sig='bad' if wrong else hmac.new(token.encode(),raw,hashlib.sha256).hexdigest();req=urllib.request.Request(url,data=raw,headers={'X-Own-Signature':sig})
  with urllib.request.urlopen(req,timeout=5) as response:
   body=response.read();assert hmac.compare_digest(response.headers['X-Own-Signature'],hmac.new(token.encode(),body,hashlib.sha256).hexdigest());return json.loads(body)
 bad_rejected=False
 try:post(row('h1',True),True)
 except urllib.error.HTTPError as e:assert e.code==403;bad_rejected=True
 assert bad_rejected;post(row('h1',True));assert b.read(b.C)['active_segment'] is None;post(row('e2'));post(row('recovery'))
 def wait_go(key,ready,timeout=12):
  start=time.time()
  while time.time()-start<timeout:
   reply=post(row(key,ready))
   if reply.get('go'):assert not reply['stop'];return reply['go']
   time.sleep(.2)
  raise AssertionError('No mock GO '+key)
 hgo=wait_go('h1',True);assert not post(row('e2'))['go'] and not post(row('recovery'))['go'];post(row('h1',True,True,True));ego=wait_go('e2',True);assert not post(row('e2',True))['stop'];assert not post(row('recovery'))['go'];post(row('recovery',False,True,True));post(row('e2',True,True,False));thread.join(timeout=12);assert not thread.is_alive() and not errors,errors;final=b.read(b.C);assert final['active_segment'] is None and len(final['completed_segments'])==1;a=final['completed_segments'][0];assert set(a['experts'])=={'h1','e2'} and 'recovery' not in a['experts'];assert a['experts']['h1']['actual_returncode']==1 and a['experts']['e2']['actual_returncode']==0;actual=sum(x['charged_seconds'] for x in a['experts'].values());assert abs(actual-a['charged_expert_seconds'])<1e-6 and abs(final['charged_training_seconds']-1000-actual)<1e-6
 for k in a['experts']:
  receipt=a['actual_terminal_rows'][k]['owner_received_terminal_epoch'];assert abs(a['experts'][k]['accounted_through_epoch']-receipt)<1e-6 and abs(a['experts'][k]['charged_seconds']-(receipt-a['experts'][k]['started_epoch']))<1e-6
 files=[]
 for p in temp.glob('*.json'):
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
 out=dict(epoch=time.time(),passed_local_HTTP_simulated_nodes=True,actual_owner_loop_and_signed_HTTP_response_exercised=True,network_only_localhost_not_210_72_249=True,wrong_signature_actual403=True,no_first_GO_until_all_nodes_registered=True,H1_own_native_ready_can_start_before_other_native_reviews=True,E3_mock_preGO_failure_no_charge=True,H1_mock_afterGO_failure_preserved_E2_healthy_continues=True,actual_terminal_receipt_exact_interval_sum_no_stale_row_tail=True,one_fixture_original_writer_only=True,simulated_charge_seconds=actual,fixture_only_not_real_training_or_cost=True,OS_fcntl_stub_no_real_lock_proof=True,no_GPU_SDK_optimizer_or_real_canonical_write=True,all_fixture_originals_retained=True,fixture_directory=str(temp),files=files);p=R/'THREE_SLOT_LOCAL_HTTP_THREE_SIMULATED_NODES_HANDOFF_ISOLATION_CPU_V2_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k!='files'}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THREE_SLOT_LOCAL_HTTP_FIXTURE_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_real_runtime_or_budget_write=True),f,indent=2)
  raise
