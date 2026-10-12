import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012'))
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012'))
from wave_direction_io import *
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012'
def save(name,value):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p

sys.path.insert(0,str(previous.old.PRIOR));from wave50_worker_actual import worker_actual
from curb_io import WIN
def store(p,raw):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==raw
 else:p.write_bytes(raw)
def main():
 n,w=io.connect_both();cases={};pending=[];files=[]
 try:
  with n.open_sftp() as nf,w.open_sftp() as wf:
   actual=worker_actual(w,wf)
   try:published=json.loads(nf.open(ROOT+'/reports/E1_WAVE50_ASYNC_PUBLISHED.json').read());own=json.loads(nf.open(ROOT+'/reports/e1_WAVE50_route_lifecycle_observation_PASSED.json').read())
   except FileNotFoundError:published=None;own=None;pending.append(dict(phase='awaiting_own_fullsave_and_actual_publication'))
   for m in published['jobs'] if published else []:
    jid=m['job_id'];folder=R/'cases'/jid
    try:r=json.loads(wf.open(WIN+'/jobs/'+jid+'/result.json').read())
    except FileNotFoundError:pending.append(dict(job_id=jid,phase='result_not_generated'));continue
    if r['phase']!='complete' or r['exit_code'] or r['errors'] or r['error_files']:pending.append(dict(job_id=jid,result=r,actual_not_passed=True));continue
    received={}
    for name in ('probe.json','result.json'):
     raw=wf.open(WIN+'/jobs/'+jid+'/'+name).read()
     try:back=nf.open(io.E+'/eval_results/'+jid+'/'+name).read()
     except FileNotFoundError:break
     if back!=raw:break
     received[name]=raw
    if len(received)!=2:pending.append(dict(job_id=jid,phase='completed_bridge_bytes_pending'));continue
    row=dict(manifest=m)
    for name,raw in {**received,'manifest.json':json.dumps(m,indent=2).encode()}.items():
     store(folder/name,raw)
     if name!='manifest.json':row[name[:-5]]=json.loads(raw);files.append(dict(job_id=jid,name=name,bytes=len(raw),sha256=H(raw),two_host_byteSHA_exact=True))
    if 'full_route_raw' in row['probe']:
     rawinfo=row['probe']['full_route_raw'];query=row['probe']['route_scope']['query_worldmesh_evidence']
     for item in (rawinfo,dict(query,name=Path(query['path']).name)):
      p=folder/item['name']
      if not p.exists():
       part=p.with_suffix(p.suffix+'.partial');wf.get(WIN+'/jobs/'+jid+'/'+item['name'],str(part));assert part.stat().st_size==item['bytes'] and H(part.read_bytes())==item['sha256'];part.rename(p)
      assert p.stat().st_size==item['bytes'] and H(p.read_bytes())==item['sha256'];files.append(dict(path=str(p.resolve()),bytes=item['bytes'],sha256=item['sha256'],large_original_index_only=True))
     row['raw_SHA_exact']=True;qp=folder/Path(query['path']).name
     try:back=nf.open(io.E+'/eval_results/'+jid+'/'+qp.name).read()
     except FileNotFoundError:pending.append(dict(job_id=jid,phase='query_NPZ_bridge_pending'));continue
     assert qp.read_bytes()==back;row['query_evidence_local']=str(qp);row['query_two_host_byteSHA_exact']=True
    cases[jid]=row
   out=save('ROUTE443_CANDIDATE_COLLECTED_'+str(time.time_ns())+'.json',dict(epoch=time.time(),own=own,published=published,cases=cases,pending=pending,files=files,actual_worker=actual,no_GPU_PPO_queue_budget_write=True))
   print(json.dumps(dict(report=str(out),complete=list(cases),pending=pending,attention=actual['attention'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('CANDIDATE_COLLECTION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True,partial_evidence_retained=True));raise
