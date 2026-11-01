"""New E0 attempt2 runtime copy + PURE METADATA waiter only. No SDK dispatch here."""
from pathlib import Path
import ast,datetime,hashlib,json,shlex,sys,time
ROOT=Path(__file__).resolve().parent.parent;LOCAL=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'
SOURCE=BASE+'/tasks/MOD4V1_E0_FRESH80_FULLDR_20261102_013149_1793554309234206700'


def main():
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns())
    job=BASE+'/tasks/MOD4V1_E0_FRESH80_ATTEMPT2_'+stamp
    assert not (LOCAL/'ATTEMPT2_CURRENT.json').exists()
    waiter=LOCAL/'waiter_e0_attempt2_v1.py';ast.parse(waiter.read_text(encoding='utf-8'))
    code='''import pathlib,shutil,json,hashlib
B=pathlib.Path(%r);S=pathlib.Path(%r);assert not B.exists();B.mkdir()
SUFFIX={'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc'}
def ignore(path,names):
 out=[]
 for n in names:
  p=pathlib.Path(path)/n
  if n=='__pycache__' or p.suffix.lower() in SUFFIX or n.upper().startswith('TRAINING_BUDGET'):out.append(n);continue
  if p.is_symlink():assert p.resolve().is_relative_to((S/'runtime').resolve()),'Source symlink escaped approved original runtime'
 return out
shutil.copytree(S/'runtime',B/'runtime',ignore=ignore)
old=json.loads((S/'E0_FRESH80_PLAN.json').read_bytes())
assert old['num_envs']==80 and old['controls']==24 and old['GPU_index']==1
for row in old['files']:
 relative=pathlib.PurePosixPath(row['relative']);assert not relative.is_absolute() and '..' not in relative.parts
 if not str(relative).startswith('runtime/'):
  src=S/str(relative);dst=B/str(relative);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for row in old['files']:
 p=B/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['relative']
assert not any(p.suffix.lower() in SUFFIX for p in (B/'runtime').rglob('*') if p.is_file())
assert not any((B/n).exists() for n in ['PARENT_STARTED.json','PARENT_EXIT_SCOPE.json','WAIT_RESOURCE.json','FINAL.json','RESOURCE_WAITER_STARTED.json','SDK_DISPATCH_ONCE.json'])
old['kind']='MOD4V1_E0_FRESH80_ATTEMPT2_NO_PT_PLAN';old['attempt']=2
(B/'E0_FRESH80_PLAN.json').write_text(json.dumps(old,indent=2))
print(json.dumps({'new_root':str(B),'read_only_source_stage':str(S),'original_consumed_states_not_copied':True,'source_PT_opens':0,'SDK_started':False,'canonical_access':False}))
'''%(job,SOURCE)
    result=dict(kind='E0_ATTEMPT2_PREPARE_PURE_METADATA_WAITER',remote_job=job,read_only_source_stage=SOURCE,source_PT_opens=0,SDK_started=False,canonical_access=False)
    client=sf=None
    try:
        client=connect72()
        i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();result.update(stage_stdout=stdout,stage_stderr=stderr,stage_rc=rc)
        assert rc==0,'Attempt2 nonPT stage failed; saved scoped report retains original error'
        sf=client.open_sftp();sf.put(str(waiter),job+'/waiter_e0_attempt2.py')
        start="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);assert not(B/'RESOURCE_WAITER_STARTED.json').exists();log=(B/'RESOURCE_WAITER_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'waiter_e0_attempt2.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();print(json.dumps({'waiter_pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'no_locks_held_by_waiter':True,'waiter_only_dispatched':True}))"%(job,BASE+'/run-python.sh')
        i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(start),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr)
        result.update(status='ATTEMPT2_PURE_METADATA_WAITER_DISPATCHED',waiter=json.loads(stdout),waiter_source_SHA=hashlib.sha256(waiter.read_bytes()).hexdigest())
        with (LOCAL/'ATTEMPT2_CURRENT.json').open('x',encoding='utf-8') as f:json.dump(dict(remote_job=job,waiter=result['waiter']),f,indent=2)
    except BaseException as error:
        result.update(status='ATTEMPT2_STAGE_OR_DISPATCH_ERROR',error_type=type(error).__name__,error=str(error));raise
    finally:
        if sf is not None:sf.close()
        if client is not None:client.close()
        report=ROOT/'reports'/('E0_attempt2_waiter_dispatch_'+stamp+'.json');report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if k not in ('stage_stdout','stage_stderr')},ensure_ascii=False,indent=2));print('REPORT',report)


if __name__=='__main__':main()
