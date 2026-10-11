"""Bounded read of this new scope's actual worker, query log and result only."""
from second_io import *
from wave50_worker_actual import worker_actual
from curb_io import WIN

def main():
    pub=json.loads((R/'WAVE50_WORLDMESH_FROZEN_PUBLISHED.json').read_bytes());jid=pub['jobs'][0]['job_id'];n,w=io.connect_both()
    try:
        with w.open_sftp() as f:
            actual=worker_actual(w,f);names=f.listdir(WIN+'/jobs/'+jid)
            log=f.open(WIN+'/jobs/'+jid+'/probe.log').read() if 'probe.log' in names else b''
            result=json.loads(f.open(WIN+'/jobs/'+jid+'/result.json').read()) if 'result.json' in names else None
            error=f.open(WIN+'/jobs/'+jid+'/probe.json.error.txt').read().decode('utf8','replace') if 'probe.json.error.txt' in names else None
            query=[s for s in log.decode('utf8','replace').splitlines() if 'WORLDMESH_QUERY_ACTUAL' in s]
            out=save('WAVE50_WORLDMESH_CURRENT_ACTUAL_'+str(time.time_ns())+'.json',dict(epoch=time.time(),job_id=jid,actual_worker=actual,files=names,result=result,error=error,actual_query_log=query,probe_log_tail=log[-4096:].decode('utf8','replace'),read_only=True))
            print(json.dumps(dict(report=str(out),result=result,error=error,actual_query=query,attention=actual['attention'],processes=actual['processes'])))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE50_WORLDMESH_CURRENT_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True));raise
