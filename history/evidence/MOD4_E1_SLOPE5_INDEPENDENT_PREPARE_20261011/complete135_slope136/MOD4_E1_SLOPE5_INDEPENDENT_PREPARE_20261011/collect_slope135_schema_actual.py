"""Read only actual135; completed errorfree byteexact and complete NPZ SHA only."""
from slope_io import *
NEW='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'
sys.path.insert(0,str(W/"MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011"))
from curb_io import WIN
from publish_curb132_frozen_once import worker_actual
import traceback

def store(p,raw):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==raw
 else:p.write_bytes(raw)

def main():
 cases={};pending=[];files=[];n,w=connect_both()
 try:
  with n.open_sftp() as nf,w.open_sftp() as wf:
   actual=worker_actual(w,wf)
   try:
    published=json.loads(nf.open(NEW+'/reports/E1_SLOPE135_ASYNC_PUBLISHED.json').read());passed=json.loads(nf.open(NEW+'/reports/e1_SLOPE5_independent_observation_PASSED.json').read())
   except FileNotFoundError:
    p=save('SLOPE135_COLLECTED_'+str(time.time_ns())+'.json',dict(epoch=time.time(),cases={},pending=[dict(phase='own_formal_final_and135publication_not_yet_generated')],actual_worker=actual,no_replay=True));print(json.dumps(dict(report=str(p),pending=True,attention=actual['attention'])));return
   for m in published['jobs']:
    jid=m['job_id'];folder=R/'cases'/jid
    try:result=json.loads(wf.open(WIN+'/jobs/'+jid+'/result.json').read())
    except FileNotFoundError:pending.append(dict(job_id=jid,phase='actual_result_not_yet_generated'));continue
    if result['phase']!='complete' or result['exit_code'] or result['errors'] or result['error_files']:
     pending.append(dict(job_id=jid,result=result,actual_failure_not_relabelled=True));continue
    row=dict(manifest=m,result=result);received={}
    for name in ('probe.json','result.json'):
     raw=wf.open(WIN+'/jobs/'+jid+'/'+name).read()
     try:returned=nf.open(E+'/eval_results/'+jid+'/'+name).read()
     except FileNotFoundError:break
     if returned!=raw:break
     received[name]=raw
    if len(received)!=2:pending.append(dict(job_id=jid,phase='actual_complete_bridge_bytes_pending'));continue
    store(folder/'manifest.json',json.dumps(m,indent=2).encode())
    for name,raw in received.items():
     store(folder/name,raw);row[name[:-5]]=json.loads(raw);files.append(dict(job_id=jid,name=name,bytes=len(raw),sha256=H(raw),Windows_source=WIN+'/jobs/'+jid+'/'+name,returned_source=E+'/eval_results/'+jid+'/'+name,bridge_bytes_exact=True))
    if 'full_route_raw' in row['probe']:
     info=row['probe']['full_route_raw'];p=folder/info['name']
     if not p.exists():
      q=p.with_suffix(p.suffix+'.partial');wf.get(WIN+'/jobs/'+jid+'/'+info['name'],str(q));assert q.stat().st_size==info['bytes'] and H(q.read_bytes())==info['sha256'];q.rename(p)
     assert p.stat().st_size==info['bytes'] and H(p.read_bytes())==info['sha256'];row['raw_SHA_exact']=True;cases[jid]=row
     files.append(dict(job_id=jid,path=str(p.resolve()),source=WIN+'/jobs/'+jid+'/'+info['name'],bytes=info['bytes'],sha256=info['sha256'],large_original_index_only=True))
    else:
     assert row['result']['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==passed['checkpoint']['sha256']
     assert row['probe']['checkpoint'].replace('\\','/').lower()==(WIN+'/jobs/'+jid+'/checkpoint.bin').lower()
     cases[jid]=row
   p=save('SLOPE135_COLLECTED_'+str(time.time_ns())+'.json',dict(epoch=time.time(),trial_id='SLOPE135-ACTUAL-COLLECT-01',cases=cases,pending=pending,files=files,actual_worker=actual,published=published,passed=passed,no_GPU_PPO_or_budget_write=True))
   print(json.dumps(dict(report=str(p),complete=list(cases),pending=pending,attention=actual['attention'],processes=actual['processes'])))
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE135_COLLECTOR_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True));raise
