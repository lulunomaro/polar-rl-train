"""New E3 selected-source eval-only purpose. Stage no weights; supervisor reads none."""
from pathlib import Path
import ast,datetime,hashlib,json,shlex,sys,time
ROOT=Path(__file__).resolve().parent.parent;LOCAL=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'
SOURCE=BASE+'/tasks/MOD4V1_E3_FRESH80_FULLDR_20261102_030504_1793559904510076900'
MODEL=BASE+'/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt'
SHA='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'

def main():
    assert not (LOCAL/'CURRENT_NEW_CASE.json').exists()
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns())
    job=BASE+'/tasks/MOD4V1_E3_1CD_N20K_NATIVE34_NOUPDATE_'+stamp;purpose='NEW_E3_1CD_FULLRESTORE_NATIVE34_'+stamp
    local_files=[('evaluate_e3_1cd_no_update.py',LOCAL/'evaluate_e3_1cd_native24_no_update_v1.py'),('supervise_e3_1cd_no_update.py',LOCAL/'supervise_e3_1cd_no_update_v1.py')]
    for _,p in local_files:ast.parse(p.read_text(encoding='utf-8'))
    code='''import pathlib,shutil,json,hashlib
B=pathlib.Path(%r);S=pathlib.Path(%r);assert not B.exists() and (S/'runtime').is_dir()
fresh=json.loads((S/'FINAL.json').read_bytes());closed=json.loads((S/'PARENT_EXIT_SCOPE.json').read_bytes())
assert fresh['passed'] is True and closed['all_own_children_waited'] is True and closed['original_private_lock_released'] is True and closed['original_shared_lock_released'] is True,'Fresh80 actualPASS and clean original locks exit REQUIRED before any source permission'
SUFFIX={'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc'}
def ignore(path,names):return [n for n in names if n=='__pycache__' or pathlib.Path(n).suffix.lower() in SUFFIX or n.upper().startswith('TRAINING_BUDGET')]
B.mkdir();shutil.copytree(S/'runtime',B/'runtime',ignore=ignore)
if (S/'lib').is_dir():shutil.copytree(S/'lib',B/'lib',ignore=ignore)
old=json.loads((S/'E3_FRESH80_PLAN.json').read_bytes());rows=[]
for row in old['files']:
 rel=pathlib.PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts
 if str(rel) in ('probe_e3_fresh80_no_pt.py','supervise_e3_fresh80.py'):continue
 if not str(rel).startswith('runtime/'):
  dst=B/str(rel);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(S/str(rel),dst)
 p=B/str(rel);assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];rows.append(row)
assert not any(p.suffix.lower() in SUFFIX for p in (B/'runtime').rglob('*') if p.is_file())
(B/'NONMODEL_STAGE_INDEX.json').write_text(json.dumps({'files':rows,'staged_model_files':0,'source_PT_reads_during_stage':0},indent=2))
print(json.dumps({'new_root':str(B),'original_E3_runtime_without_model_files':True,'source_PT_reads':0,'canonical_access':False}))
'''%(job,SOURCE)
    result=dict(kind='E3_1CD_N20K_NATIVE34_EVAL_ONLY_NEW_PURPOSE',remote_root=job,source_read_purpose=purpose,source_PT_reads_by_deployer=0,canonical_access=False)
    client=sf=None
    try:
        client=connect72();i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();result.update(stage_rc=rc,stage_stdout=stdout,stage_stderr=stderr);assert rc==0,'New case stage failed; see saved scoped report'
        sf=client.open_sftp()
        with sf.open(job+'/NONMODEL_STAGE_INDEX.json','r') as f:rows=json.load(f)['files']
        for relative,p in local_files:
            sf.put(str(p),job+'/'+relative);b=p.read_bytes();rows.append(dict(relative=relative,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
        plan=dict(kind='E3_1CD_N20K_NATIVE34_EVAL_ONLY_NEW_PURPOSE',execution_scope='EVAL_ONLY_NO_OPTIMIZER',source_read_purpose=purpose,model_path=MODEL,model_SHA=SHA,model_bytes=14715029,num_envs=20000,controls=24,GPU_index=1,GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',parent_limit_s=1200,worker_limit_s=900,files=rows,no_production_GO=True,canonical_access=False)
        with sf.open(job+'/E3_NOUPDATE_PLAN.json','wx') as f:f.write(json.dumps(plan,indent=2))
        start="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);assert not(B/'PARENT_STARTED.json').exists();log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'supervise_e3_1cd_no_update.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();print(json.dumps({'parent_pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'dispatched_only':True}))"%(job,BASE+'/run-python.sh')
        i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(start),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr)
        result.update(status='PARENT_DISPATCHED_E3_1CD_EVAL_ONLY',parent=json.loads(stdout),plan=plan)
        with (LOCAL/'CURRENT_NEW_CASE.json').open('x',encoding='utf-8') as f:json.dump(dict(remote_root=job,parent=result['parent'],source_read_purpose=purpose),f,indent=2)
    except BaseException as error:result.update(status='STAGE_OR_DISPATCH_ERROR',error_type=type(error).__name__,error=str(error));raise
    finally:
        if sf is not None:sf.close()
        if client is not None:client.close()
        report=ROOT/'reports'/('E3_1cd_fullrestore_native24_dispatch_'+stamp+'.json');report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if k not in ('stage_stdout','stage_stderr','plan')},ensure_ascii=False,indent=2));print('REPORT',report)

if __name__=='__main__':main()
