"""Reusable actual-complete collector; no queue, process, GPU or budget mutation."""
from curb_io import *
from publish_curb132_frozen_once import worker_actual
import traceback
def store(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert path.read_bytes()==raw,str(path)
    else:path.write_bytes(raw)
def main():
    n,w=connect_both();cases={};pending=[];files=[]
    try:
        with n.open_sftp() as nf,w.open_sftp() as wf:
            actual=worker_actual(w,wf)
            published=json.loads((R/'CURB132_PUBLISHED.json').read_bytes())
            for job in published['jobs']:
                jid=job['job_id'];folder=R/'cases'/jid
                try:raw=wf.open(WIN+'/jobs/'+jid+'/result.json').read()
                except FileNotFoundError:
                    pending.append(dict(job_id=jid,phase='result_not_yet_generated'));continue
                result=json.loads(raw)
                if result['phase']!='complete' or result['exit_code'] or result['errors'] or result['error_files']:
                    pending.append(dict(job_id=jid,result=result,not_passed=True));continue
                row=dict(manifest=job);received={}
                for name in ('probe.json','result.json'):
                    b=wf.open(WIN+'/jobs/'+jid+'/'+name).read()
                    try:returned=nf.open(E+'/eval_results/'+jid+'/'+name).read()
                    except FileNotFoundError:break
                    if b!=returned:break
                    received[name]=b
                if len(received)!=2:
                    pending.append(dict(job_id=jid,phase='Windows_complete_bridge_bytes_pending'));continue
                store(folder/'manifest.json',json.dumps(job,indent=2).encode())
                for name,b in received.items():
                    store(folder/name,b);row[name[:-5]]=json.loads(b)
                    files.append(dict(job_id=jid,name=name,bytes=len(b),sha256=H(b),Windows_source=WIN+'/jobs/'+jid+'/'+name,returned_source=E+'/eval_results/'+jid+'/'+name,bridge_bytes_exact=True))
                info=row['probe']['full_route_raw'];p=folder/info['name']
                if not p.exists():
                    partial=p.with_suffix(p.suffix+'.partial')
                    wf.get(WIN+'/jobs/'+jid+'/'+info['name'],str(partial))
                    assert partial.stat().st_size==info['bytes'] and H(partial.read_bytes())==info['sha256']
                    partial.rename(p)
                assert p.stat().st_size==info['bytes'] and H(p.read_bytes())==info['sha256']
                row['raw_SHA_exact']=True;cases[jid]=row
                files.append(dict(job_id=jid,path=str(p.resolve()),source=WIN+'/jobs/'+jid+'/'+info['name'],bytes=info['bytes'],sha256=info['sha256'],large_original_index_only=True))
            v=dict(epoch=time.time(),trial_id='E1-CURB20-132-ACTUAL-COLLECTION-01',cases=cases,pending=pending,files=files,actual_worker=actual,
                no_learning_or_queue_or_canonical_write=True,new_budget_seconds=0)
            p=save('CURB132_COLLECTED_'+str(int(time.time()))+'.json',v)
            print(json.dumps(dict(report=str(p),complete=list(cases),pending=pending,processes=actual['processes'])))
    finally:cleanup(n,w)
if __name__=='__main__':
    try:main()
    except Exception:
        save('CURB132_COLLECT_ERROR_'+str(int(time.time()))+'.json',dict(epoch=time.time(),error=traceback.format_exc(),read_only=True,partial_evidence_retained=True));raise
