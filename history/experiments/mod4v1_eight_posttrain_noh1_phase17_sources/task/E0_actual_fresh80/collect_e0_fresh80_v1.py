"""Read only this E0 noPT job's metadata/logs, optionally wait its own supervisor."""
from pathlib import Path
import argparse,datetime,json,shlex,sys
ROOT=Path(__file__).resolve().parent.parent;LOCAL=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--wait',action='store_true');args=parser.parse_args()
    job=json.loads((LOCAL/'CURRENT_NEW_STAGE.json').read_bytes())['remote_job']
    assert job.startswith(BASE+'/tasks/MOD4V1_E0_FRESH80_')
    client=connect72();sf=None
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');out=ROOT/'reports'/('E0_fresh80_collect_'+stamp);out.mkdir(exist_ok=False)
    result=dict(remote_job=job,phase='final_wait' if args.wait else 'progress',canonical_writes=0,model_opens=0,files={},reader_errors=[])
    try:
        if args.wait:
            code="import psutil,json,pathlib;B=pathlib.Path(%r);p=psutil.Process(1420098);assert abs(p.create_time()-1793554795.24)<.1;print(json.dumps({'own_parent_wait_return':p.wait(timeout=730)}))"%job
            i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=750);i.close();result['parent_wait_stdout']=o.read().decode('utf-8',errors='replace');result['parent_wait_stderr']=e.read().decode('utf-8',errors='replace');result['parent_wait_rc']=o.channel.recv_exit_status()
        sf=client.open_sftp()
        names=['PARENT_STARTED.json','WAIT_RESOURCE.json','CHILDREN.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','FINAL.json','TERMINAL_ROWS.json','gpu1/TASK.json','gpu1/RESOURCE_ACTUAL.json','gpu1/E0_FRESH80_D0_D7_BEFORE_CONTROL.json','gpu1/E0_FRESH80_NATIVE24_COMPLETE.json','gpu1/E0_FRESH80_ORIGINAL_ERROR.json','gpu1/ENV_CLOSE_RETURNED.json','gpu1/APP_CLOSING.json']
        for name in names:
            try:
                with sf.open(job+'/'+name,'r') as f:raw=f.read()
            except FileNotFoundError:continue
            dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
            try:result['files'][name]=json.loads(raw)
            except Exception as error:result['reader_errors'].append(dict(file=name,error_type=type(error).__name__,error=str(error),raw_retained=str(dest)))
        for name in ['SUPERVISOR_FULL_STDOUT_STDERR.log','gpu1/SDK_FULL_STDOUT_STDERR.log']:
            try:
                dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);sf.get(job+'/'+name,str(dest))
            except FileNotFoundError:continue
        report=out/'COLLECTION.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        show={k:result['files'].get(k) for k in ('WAIT_RESOURCE.json','CHILDREN.json','PARENT_ORIGINAL_ERROR.json','FINAL.json','PARENT_EXIT_SCOPE.json') if k in result['files']}
        print(json.dumps(dict(remote_job=job,report=str(report),actual=show,reader_errors=result['reader_errors']),ensure_ascii=False,indent=2))
    finally:
        if sf is not None:sf.close()
        client.close()


if __name__=='__main__':main()
