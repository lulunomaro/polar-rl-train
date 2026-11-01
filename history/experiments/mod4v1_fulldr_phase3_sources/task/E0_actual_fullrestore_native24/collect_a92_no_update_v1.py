"""Collect only this E0 source-restore eval-only case's metadata/own logs."""
from pathlib import Path
import argparse,datetime,json,shlex,sys
ROOT=Path(__file__).resolve().parent.parent;LOCAL=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--wait',action='store_true');a=parser.parse_args()
    info=json.loads((LOCAL/'CURRENT_NEW_CASE.json').read_bytes());job=info['remote_root'];parent=info['parent']
    assert job.startswith(BASE+'/tasks/MOD4V1_E0_A92_N20K_NATIVE24_NOUPDATE_')
    result=dict(remote_root=job,source_read_purpose=info['source_read_purpose'],collector_source_PT_reads=0,canonical_access=False,files={},reader_errors=[])
    client=connect72();sf=None
    try:
        client.get_transport().set_keepalive(30)
        if a.wait:
            code="import psutil,json;pid=%d;creation=%r;row={};\ntry:\n p=psutil.Process(pid)\n if abs(p.create_time()-creation)<.1:row['own_parent_wait_return']=p.wait(timeout=1230)\n else:row['PID_reused_not_waited']=True\nexcept psutil.NoSuchProcess:row['already_exited']=True\nprint(json.dumps(row))"%(parent['parent_pid'],parent['creation'])
            i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=1250);i.close();result['parent_wait_stdout']=o.read().decode('utf-8',errors='replace');result['parent_wait_stderr']=e.read().decode('utf-8',errors='replace');result['parent_wait_rc']=o.channel.recv_exit_status()
        sf=client.open_sftp();out=ROOT/'reports'/('E0_a92_no_update_'+('final_' if a.wait else 'progress_')+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));out.mkdir(exist_ok=False)
        names=['PARENT_STARTED.json','WAIT_RESOURCE.json','CHILDREN.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','FINAL.json','TERMINAL_ROWS.json','gpu1/RESOURCE_ACTUAL.json','gpu1/E0_N20K_FULLRESTORE_BEFORE_NATIVE24.json','gpu1/E0_N20K_FULLRESTORE_NATIVE24_COMPLETE.json','gpu1/E0_N20K_FULLRESTORE_ORIGINAL_ERROR.json','gpu1/SOURCE_FINAL_READ_COUNTS.json','gpu1/ENV_CLOSE_RETURNED.json','gpu1/APP_CLOSING.json','gpu1/TRAINER_MAIN_CLOSE_RETURNED.json']
        for name in names:
            try:
                with sf.open(job+'/'+name,'r') as f:raw=f.read()
            except FileNotFoundError:continue
            target=out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            try:result['files'][name]=json.loads(raw)
            except Exception as error:result['reader_errors'].append(dict(file=name,error_type=type(error).__name__,error=str(error),raw_retained=str(target)))
        for name in ['SUPERVISOR_FULL_STDOUT_STDERR.log','gpu1/SDK_FULL_STDOUT_STDERR.log']:
            try:
                target=out/name;target.parent.mkdir(parents=True,exist_ok=True);sf.get(job+'/'+name,str(target))
            except FileNotFoundError:continue
        report=out/'COLLECTION.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        keys=['WAIT_RESOURCE.json','CHILDREN.json','PARENT_ORIGINAL_ERROR.json','FINAL.json','PARENT_EXIT_SCOPE.json','gpu1/E0_N20K_FULLRESTORE_ORIGINAL_ERROR.json','gpu1/SOURCE_FINAL_READ_COUNTS.json']
        print(json.dumps(dict(remote_root=job,report=str(report),actual={k:result['files'][k] for k in keys if k in result['files']},reader_errors=result['reader_errors']),ensure_ascii=False,indent=2))
    finally:
        if sf is not None:sf.close()
        client.close()

if __name__=='__main__':main()
