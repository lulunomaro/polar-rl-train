"""Dispatch only the authorized E0 fresh80 noPT probe in an already NEW stage."""
from pathlib import Path
import ast,datetime,hashlib,json,shlex,sys
ROOT=Path(__file__).resolve().parent.parent;LOCAL=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'
GETTER=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\REFERENCE_TRACKING_BPTT_V300_20261101\source\actual_DR_memory_getter272.py')


def main():
    loc=json.loads((LOCAL/'CURRENT_NEW_STAGE.json').read_bytes());job=loc['remote_job']
    assert job.startswith(BASE+'/tasks/MOD4V1_E0_FRESH80_')
    attempt=LOCAL/'DISPATCH_V1_ATTEMPTED.json'
    with attempt.open('x',encoding='utf-8') as f:json.dump(dict(remote_job=job,scope='fresh80 noPT only'),f,indent=2)
    result=dict(remote_job=job,scope='E0 noPT fresh80 model-free only',canonical_writes=0,model_opens=0)
    client=sf=None
    try:
        files=[('probe_e0_fresh80_no_pt.py',LOCAL/'probe_e0_fresh80_no_pt_v1.py'),('supervise_e0_fresh80.py',LOCAL/'supervise_e0_fresh80_v1.py'),('runtime/isaac/mod4/actual_DR_memory_getter272.py',GETTER)]
        for _,p in files:ast.parse(p.read_text(encoding='utf-8'))
        client=connect72();sf=client.open_sftp()
        with sf.open(job+'/E0_STAGE_SOURCE_INDEX.json','r') as f:rows=json.load(f)['files']
        for relative,local in files:
            raw=local.read_bytes();sf.put(str(local),job+'/'+relative)
            rows.append(dict(relative=relative,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
        query="import subprocess,json;line=subprocess.check_output(['/usr/bin/nvidia-smi','-i','1','--query-gpu=index,uuid,name','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip() for x in line.split(',')];assert a[0]=='1' and a[2]=='NVIDIA GeForce RTX 4090';print(json.dumps({'index':1,'uuid':a[1],'name':a[2]}))"
        i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(query),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr);gpu=json.loads(stdout)
        plan=dict(kind='MOD4V1_E0_FRESH80_FULLDR_NO_PT_PLAN',GPU_index=1,GPU_UUID=gpu['uuid'],num_envs=80,controls=24,parent_limit_s=720,files=rows,asset_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',worker_SHA=hashlib.sha256((LOCAL/'probe_e0_fresh80_no_pt_v1.py').read_bytes()).hexdigest(),no_checkpoint_restore=True,no_production_GO=True,canonical_access=False)
        with sf.open(job+'/E0_FRESH80_PLAN.json','wx') as f:f.write(json.dumps(plan,indent=2))
        code="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);assert not(B/'PARENT_STARTED.json').exists();log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'supervise_e0_fresh80.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();print(json.dumps({'pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'remote_job':str(B),'dispatched_only':True}))"%(job,BASE+'/run-python.sh')
        i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr)
        result.update(status='E0_FRESH80_PARENT_DISPATCHED',parent=json.loads(stdout),gpu=gpu,plan=plan)
    except BaseException as error:
        result.update(status='DISPATCH_ERROR',error_type=type(error).__name__,error=str(error));raise
    finally:
        if sf is not None:sf.close()
        if client is not None:client.close()
        report=ROOT/'reports'/('E0_fresh80_dispatch_v1_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json')
        report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if k!='plan'},ensure_ascii=False,indent=2));print('REPORT',report)


if __name__=='__main__':main()
