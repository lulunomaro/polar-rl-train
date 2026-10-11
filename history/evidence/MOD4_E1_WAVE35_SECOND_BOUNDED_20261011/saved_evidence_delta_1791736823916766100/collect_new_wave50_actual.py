"""Read completed newly published50mm frozen scope; no GPU replay or learning."""
from second_io import *
sys.path.insert(0,str(W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011'))
from slope8_worker_actual import worker_actual
from curb_io import WIN
def main():
 published=json.loads((R/'WAVE50_FROZEN_PUBLISHED.json').read_bytes());n,w=io.connect_both();cases={};pending=[];files=[]
 try:
  with n.open_sftp() as nf,w.open_sftp() as wf:
   actual=worker_actual(w,wf)
   for manifest in published['jobs']:
    jid=manifest['job_id'];folder=R/'cases'/jid
    try:r=json.loads(wf.open(WIN+'/jobs/'+jid+'/result.json').read())
    except FileNotFoundError:pending.append(dict(job_id=jid,phase='result_not_yet_generated'));continue
    if r['phase']!='complete' or r['exit_code'] or r['errors'] or r['error_files']:
     pending.append(dict(job_id=jid,result=r,actual_not_passed=True));continue
    received={}
    for name in ('probe.json','result.json'):
     raw=wf.open(WIN+'/jobs/'+jid+'/'+name).read()
     try:back=nf.open(io.E+'/eval_results/'+jid+'/'+name).read()
     except FileNotFoundError:break
     if raw!=back:break
     received[name]=raw
    if len(received)!=2:pending.append(dict(job_id=jid,phase='Windows_complete_bridge_bytes_pending'));continue
    folder.mkdir(parents=True,exist_ok=True);row=dict(manifest=manifest)
    for name,raw in {**received,'manifest.json':json.dumps(manifest,indent=2).encode()}.items():
     p=folder/name
     if p.exists():assert p.read_bytes()==raw
     else:p.write_bytes(raw)
     if name!='manifest.json':row[name[:-5]]=json.loads(raw);files.append(dict(job_id=jid,name=name,bytes=len(raw),sha256=H(raw),two_host_byteSHA_exact=True))
    rawinfo=row['probe']['full_route_raw'];p=folder/rawinfo['name']
    if not p.exists():
     part=p.with_suffix(p.suffix+'.partial');wf.get(WIN+'/jobs/'+jid+'/'+rawinfo['name'],str(part));assert part.stat().st_size==rawinfo['bytes'] and H(part.read_bytes())==rawinfo['sha256'];part.rename(p)
    assert p.stat().st_size==rawinfo['bytes'] and H(p.read_bytes())==rawinfo['sha256'];row['raw_SHA_exact']=True;cases[jid]=row
    files.append(dict(path=str(p.resolve()),source=WIN+'/jobs/'+jid+'/'+rawinfo['name'],bytes=rawinfo['bytes'],sha256=rawinfo['sha256'],large_index_only=True,original_retained=True))
   out=save('WAVE50_ACTUAL_COLLECTED_'+str(time.time_ns())+'.json',dict(epoch=time.time(),published=str(R/'WAVE50_FROZEN_PUBLISHED.json'),cases=cases,pending=pending,files=files,actual_worker=actual,no_GPU_PPO_queue_or_budget_write=True))
   print(json.dumps(dict(report=str(out),complete=list(cases),pending=pending,attention=actual['attention'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE50_COLLECTION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True,no_blind_replay=True));raise
