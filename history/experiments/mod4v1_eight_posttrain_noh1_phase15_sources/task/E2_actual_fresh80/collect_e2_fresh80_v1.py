"""Read this E2 noPT fresh80 case only; no canonical or checkpoint access."""
from pathlib import Path
import argparse,datetime,json,shlex,sys
ROOT=Path(__file__).resolve().parent.parent;LOCAL=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--wait',action='store_true');a=parser.parse_args()
    job=json.loads((LOCAL/'CURRENT_NEW_STAGE.json').read_bytes())['remote_job'];assert job.startswith(BASE+'/tasks/MOD4V1_E2_FRESH80_')
    c=connect72();sf=None;result=dict(remote_job=job,model_opens=0,canonical_access=False,files={},reader_errors=[])
    try:
        if a.wait:
            code="import psutil,json;row={};\ntry:\n p=psutil.Process(1422987)\n if abs(p.create_time()-1793558316.91)<.1:row['own_parent_wait_return']=p.wait(timeout=750)\n else:row['PID_reused_not_waited']=True\nexcept psutil.NoSuchProcess:row['already_exited']=True\nprint(json.dumps(row))"
            i,o,e=c.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=770);i.close();result['wait_stdout']=o.read().decode();result['wait_stderr']=e.read().decode();result['wait_rc']=o.channel.recv_exit_status()
        sf=c.open_sftp();out=ROOT/'reports'/('E2_fresh80_'+('final_' if a.wait else 'progress_')+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));out.mkdir(exist_ok=False)
        names=['PARENT_STARTED.json','WAIT_RESOURCE.json','CHILDREN.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','FINAL.json','TERMINAL_ROWS.json','gpu1/RESOURCE_ACTUAL.json','gpu1/E2_FRESH80_D0_D7_BEFORE_CONTROL.json','gpu1/E2_FRESH80_NATIVE24_COMPLETE.json','gpu1/E2_FRESH80_ORIGINAL_ERROR.json','gpu1/ENV_CLOSE_RETURNED.json','gpu1/APP_CLOSING.json']
        for name in names:
            try:
                with sf.open(job+'/'+name,'r') as f:raw=f.read()
            except FileNotFoundError:continue
            dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
            try:result['files'][name]=json.loads(raw)
            except Exception as error:result['reader_errors'].append(dict(file=name,error=str(error),raw_retained=str(dest)))
        for name in ['SUPERVISOR_FULL_STDOUT_STDERR.log','gpu1/SDK_FULL_STDOUT_STDERR.log']:
            try:
                dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);sf.get(job+'/'+name,str(dest))
            except FileNotFoundError:continue
        report=out/'COLLECTION.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        keys=['CHILDREN.json','WAIT_RESOURCE.json','PARENT_ORIGINAL_ERROR.json','FINAL.json','PARENT_EXIT_SCOPE.json','gpu1/E2_FRESH80_ORIGINAL_ERROR.json']
        print(json.dumps(dict(remote_job=job,report=str(report),actual={k:result['files'][k] for k in keys if k in result['files']},reader_errors=result['reader_errors']),ensure_ascii=False,indent=2))
    finally:
        if sf is not None:sf.close()
        c.close()

if __name__=='__main__':main()
