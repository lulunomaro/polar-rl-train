"""Block on only this attempt's own metadata waiter/supervisor, collect own logs."""
from pathlib import Path
import datetime,json,shlex,sys
ROOT=Path(__file__).resolve().parent.parent;LOCAL=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'


def main():
    current=json.loads((LOCAL/'ATTEMPT2_CURRENT.json').read_bytes());job=current['remote_job'];waiter=current['waiter']
    assert job.startswith(BASE+'/tasks/MOD4V1_E0_FRESH80_ATTEMPT2_')
    result=dict(remote_job=job,waiter=waiter,canonical_access=False,model_opens=0,files={},reader_errors=[])
    client=connect72();sf=None
    try:
        client.get_transport().set_keepalive(30)
        code='''import pathlib,json,psutil
B=pathlib.Path(%r)
def wait_own(pid,creation,seconds):
 try:p=psutil.Process(pid)
 except psutil.NoSuchProcess:return {'already_exited':True}
 if abs(p.create_time()-creation)>.5:return {'PID_reused_not_waited':True}
 return {'own_wait_return':p.wait(timeout=seconds)}
row={'waiter':wait_own(%d,%r,1830)}
if (B/'ACTUAL_SDK_SUPERVISOR_DISPATCH.json').is_file():
 d=json.loads((B/'ACTUAL_SDK_SUPERVISOR_DISPATCH.json').read_bytes());row['SDK_supervisor']=wait_own(d['pid'],d['epoch'],750)
print(json.dumps(row))
'''%(job,waiter['waiter_pid'],waiter['creation'])
        i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=2630);i.close();result['wait_stdout']=o.read().decode('utf-8',errors='replace');result['wait_stderr']=e.read().decode('utf-8',errors='replace');result['wait_rc']=o.channel.recv_exit_status()
        sf=client.open_sftp();stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');out=ROOT/'reports'/('E0_attempt2_final_collect_'+stamp);out.mkdir(exist_ok=False)
        names=['RESOURCE_WAITER_STARTED.json','RESOURCE_WAIT_CHECKS.json','RESOURCE_WAITER_FINAL.json','RESOURCE_WAITER_ORIGINAL_ERROR.json','AUTHORIZED_SOURCE_SCOPE_EXIT_OBSERVED.json','SDK_DISPATCH_ONCE.json','ACTUAL_SDK_SUPERVISOR_DISPATCH.json','PARENT_STARTED.json','WAIT_RESOURCE.json','CHILDREN.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','FINAL.json','TERMINAL_ROWS.json','gpu1/RESOURCE_ACTUAL.json','gpu1/E0_FRESH80_D0_D7_BEFORE_CONTROL.json','gpu1/E0_FRESH80_NATIVE24_COMPLETE.json','gpu1/E0_FRESH80_ORIGINAL_ERROR.json','gpu1/ENV_CLOSE_RETURNED.json','gpu1/APP_CLOSING.json']
        for name in names:
            try:
                with sf.open(job+'/'+name,'r') as f:raw=f.read()
            except FileNotFoundError:continue
            target=out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            try:result['files'][name]=json.loads(raw)
            except Exception as error:result['reader_errors'].append(dict(file=name,error_type=type(error).__name__,error=str(error),raw_retained=str(target)))
        for name in ['RESOURCE_WAITER_STDOUT_STDERR.log','SUPERVISOR_FULL_STDOUT_STDERR.log','gpu1/SDK_FULL_STDOUT_STDERR.log']:
            try:
                target=out/name;target.parent.mkdir(parents=True,exist_ok=True);sf.get(job+'/'+name,str(target))
            except FileNotFoundError:continue
        for name in sf.listdir(job):
            if name.startswith('PARENT_EXIT_SCOPE_READER_RAW_'):sf.get(job+'/'+name,str(out/name))
        report=out/'COLLECTION.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        keys=['RESOURCE_WAITER_FINAL.json','ACTUAL_SDK_SUPERVISOR_DISPATCH.json','WAIT_RESOURCE.json','PARENT_ORIGINAL_ERROR.json','FINAL.json','PARENT_EXIT_SCOPE.json']
        print(json.dumps(dict(remote_job=job,report=str(report),actual={k:result['files'][k] for k in keys if k in result['files']},reader_errors=result['reader_errors']),ensure_ascii=False,indent=2))
    finally:
        if sf is not None:sf.close()
        client.close()


if __name__=='__main__':main()
