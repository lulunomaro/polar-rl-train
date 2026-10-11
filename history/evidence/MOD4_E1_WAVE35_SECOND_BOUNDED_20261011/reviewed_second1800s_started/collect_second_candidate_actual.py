"""Actual completed4cases only, two-host byte comparison and complete raw SHA."""
from pathlib import Path
import sys
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
from second_io import *
NEW=ROOT
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io
E,B,connect_both,cleanup,H=io.E,io.B,io.connect_both,io.cleanup,io.H
sys.path.insert(0,str(W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011'))
from slope8_worker_actual import worker_actual
from curb_io import WIN
from pathlib import Path
import json,time,traceback
def store(p,raw):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==raw
 else:p.write_bytes(raw)
def main():
 n,w=connect_both();cases={};pending=[];files=[]
 try:
  with n.open_sftp() as nf,w.open_sftp() as wf:
   actual=worker_actual(w,wf)
   try:published=json.loads(nf.open(NEW+'/reports/E1_143-e1-wave35-second-bounded_ASYNC_PUBLISHED.json').read());own=json.loads(nf.open(NEW+'/reports/e1_WAVE35_second_bounded_observation_PASSED.json').read())
   except FileNotFoundError:published=None;own=None;pending.append(dict(phase='awaiting_own_formal_fullsave_and_publication'))
   for m in published['jobs'] if published else []:
    jid=m['job_id'];folder=R/'cases'/jid
    try:r=json.loads(wf.open(WIN+'/jobs/'+jid+'/result.json').read())
    except FileNotFoundError:pending.append(dict(job_id=jid,phase='result_not_yet_generated'));continue
    if r['phase']!='complete' or r['exit_code'] or r['errors'] or r['error_files']:
     pending.append(dict(job_id=jid,result=r,not_passed=True));continue
    row=dict(manifest=m);received={}
    for name in ('probe.json','result.json'):
     b=wf.open(WIN+'/jobs/'+jid+'/'+name).read()
     try:returned=nf.open(E+'/eval_results/'+jid+'/'+name).read()
     except FileNotFoundError:break
     if returned!=b:break
     received[name]=b
    if len(received)!=2:pending.append(dict(job_id=jid,phase='Windows_complete_bridge_bytes_pending'));continue
    store(folder/'manifest.json',json.dumps(m,indent=2).encode())
    for name,b in received.items():
     store(folder/name,b);row[name[:-5]]=json.loads(b);files.append(dict(job_id=jid,name=name,bytes=len(b),sha256=H(b),Windows_source=WIN+'/jobs/'+jid+'/'+name,returned_source=E+'/eval_results/'+jid+'/'+name,bridge_bytes_exact=True))
    if 'full_route_raw' in row['probe']:
     info=row['probe']['full_route_raw'];p=folder/info['name']
     if not p.exists():
      q=p.with_suffix(p.suffix+'.partial');wf.get(WIN+'/jobs/'+jid+'/'+info['name'],str(q));assert q.stat().st_size==info['bytes'] and H(q.read_bytes())==info['sha256'];q.rename(p)
     assert p.stat().st_size==info['bytes'] and H(p.read_bytes())==info['sha256'];row['raw_SHA_exact']=True
     files.append(dict(job_id=jid,path=str(p.resolve()),source=WIN+'/jobs/'+jid+'/'+info['name'],bytes=info['bytes'],sha256=info['sha256'],large_original_index_only=True))
    cases[jid]=row
   v=dict(epoch=time.time(),trial_id='WAVE143-OWN-INDEPENDENT-ACTUAL-COLLECT-01',cases=cases,pending=pending,files=files,passed=own,published=published,actual_worker=actual,no_GPU_queue_or_canonical_write=True)
   p=save('WAVE143_COLLECTED_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(p),complete=list(cases),pending=pending,attention=actual['attention'],processes=actual['processes'])))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE143_COLLECTION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True,original_partial_evidence_retained=True));raise
