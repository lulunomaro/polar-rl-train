"""Prepare and run one finite single200mm inference diagnostic, no new hour."""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json
import time
import traceback

N=Path(__file__).resolve().parent
A=N/'env20000_scut_stairs_1h_20261104/attempt08'
D=N/'jump200_step_eval1_20261104';R=D/'reports'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
read=lambda p:json.loads(Path(p).read_bytes())
sha=lambda b:hashlib.sha256(b).hexdigest()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def put(p,v):
    with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2)


def prepare():
    facts=read(A/'reports/POSTROUND_FULL_RETURNED.json')['files']
    assert facts['TRAIN_CLOSED.json']['passed_execution']
    assert facts['OWNER_EXIT.json']['original_leases_released']
    D.mkdir();R.mkdir()
    plan=read(A/'PLAN.json')
    registry=next(row for row in read(N/'env20000_1h/INDEX_SOURCE_FROZEN.json')['files']
                  if row['relative']=='SOURCE_PATHS.json')
    source_registry=dict(path=plan['remote_root'].split('/env20000_scut_stairs_')[0]+
        '/env20000_1h/SOURCE_PATHS.json',bytes=registry['bytes'],SHA=registry['SHA'])
    value=dict(kind='SINGLE200MM_VERTICAL_STEP_ACTUAL_JUMP_DIAGNOSTIC',
        human_quote='我说的是跳台阶，机器人跳上去200mm的台阶不是这个碎台阶',
        closed_root=plan['remote_root'],remote_root=plan['remote_root']+'/jump200_eval1',
        checkpoint=facts['production/FINAL.json']['checkpoint'],GPU_UUID=None,
        profile='jump200',num_envs=80,controls_max=400,seed=9137,
        source_registry=source_registry,optimizer_operations=0,ledger_writes=0,
        source_is_small_stair_locomotion_not_jump_expert=True,
        original_model_unchanged=True,new_training_window=False,
        strict_reserve=plan['original_strictreserve'])
    put(D/'PLAN_PREPARED.json',value)
    base=load('jump200_original_finite',N/'target_limits_control.py')
    wrapper=base.OWNER
    wrapper=wrapper.replace("'--profile',task['profile']","'--profile',plan['profile']")
    wrapper=wrapper.replace("'--repair-target-limits']","'--jump200-source']")
    ast.parse(wrapper);(D/'owner_eval.py').write_text(wrapper,encoding='utf8',newline='\n')
    put(D/'PREPARED.json',dict(epoch=time.time(),profile='jump200',CPU_report=
        str(A/'reports/JUMP200_INTEGRATION_ATTEMPT1.json'),new_training=False))
    print(json.dumps(dict(prepared=str(D),new_training=False)))


def inventory():
    target=R/('FOUR_GPU_'+str(time.time_ns()));target.mkdir()
    m=load('jump200_original_four_gpu',N/'check_four_gpu.py');m.R=target
    # This request concerns available cards/current canonical, not an obsolete peer.
    m.READ=m.READ.replace('MOD4_STANDING200_SCUT_RECIPE_V20_FLAT_1793718811682640300',
                         Path(read(A/'PLAN.json')['remote_root']).name)
    m.main()


def freeze():
    assert not(D/'INDEX.json').exists()
    inv=read(sorted(R.glob('FOUR_GPU_*/FOUR_GPU_HUMAN_REQUEST_ACTUAL.json'))[-1])
    host=inv['hosts']['72']['actual'];assert time.time()-host['epoch']<180
    candidates=[]
    for line in host['gpu']['stdout'].splitlines():
        v=[x.strip()for x in line.split(',')]
        if v[2]!='NVIDIA GeForce RTX 4090':continue
        free,used,util=map(int,v[4:7]);busy=v[1]in host['compute_apps']['stdout']
        if free>15669 and(not busy or(used<=4096 and util<=30)):candidates.append((not busy,free,v[1]))
    assert candidates,'Original host has no currently admissible4090'
    plan=read(D/'PLAN_PREPARED.json');plan['GPU_UUID']=max(candidates)[2]
    put(D/'PLAN.json',plan)
    files=[]
    for name in ('config.py','jump200.py','rewards.py','sdk.py','train.py','evaluate.py'):
        path=G/'project/isaac/mod4v1_scut'/name;raw=path.read_bytes();ast.parse(raw)
        files.append(dict(path=str(path),relative='overlay/'+name,bytes=len(raw),SHA=sha(raw)))
    for name in ('PLAN.json','owner_eval.py'):
        path=D/name;raw=path.read_bytes()
        files.append(dict(path=str(path),relative=name,bytes=len(raw),SHA=sha(raw)))
    put(D/'INDEX.json',dict(epoch=time.time(),files=files,
        shared_index=str(A/'INDEX_SOURCE_FROZEN.json'),
        shared_index_SHA=sha((A/'INDEX_SOURCE_FROZEN.json').read_bytes()),
        source_only=True,whole_tree_model_asset_copy=False))
    print(json.dumps(dict(files=len(files),GPU_UUID=plan['GPU_UUID'],native=False)))


def run():
    m=load('jump200_original_finite_run',N/'target_limits_control.py');m.D=D;m.R=R
    m.run(False)


def logs():
    m=load('jump200_closed_log_transport',N/'run.py');m.R=R
    plan=read(D/'PLAN.json');identity=read(R/'OWNER_LAUNCH.json')
    assert read(R/'COMPLETED.json')['release']['locks_released']
    assert not(R/'FINAL_COMPLETE_LOG_ACTUAL.json').exists()
    code='''from pathlib import Path
import json,time,hashlib,psutil
j=Path(v['root']);release=json.loads((j/'RELEASE.json').read_bytes())
assert release['all_own_waited'] and release['locks_released'] and release['error'] is None
alive=False
try:
 p=psutil.Process(v['pid']);alive=p.create_time()==v['creation'] and p.status()!=psutil.STATUS_ZOMBIE
except psutil.Error:pass
assert not alive
logs={};errors={}
for name in ['WORKER.log','OWNER.log']:
 p=j/name;raw=p.read_bytes();text=raw.decode('utf8','replace')
 logs[name]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=text)
 errors[name]=[line for line in text.splitlines()if any(t in line.lower()for t in ['[error]','traceback (most recent call last)','cooking failure','failed to cook','patch buffer overflow','foundlostaggregatepairscapacity','outofmemoryerror','dropped pair'])]
print(json.dumps(dict(epoch=time.time(),logs=logs,errors=errors,release=release,owner_alive=alive,PT_reads=0,physics=0,ledger_writes=0)))'''
    with m.connection('JUMP200_BASELINE_FINAL_LOG')as(client,t):
        m.put('FINAL_LOG_ONCE.json',dict(epoch=time.time(),read_only=True))
        value=t.code(client,t.PY72,code,dict(root=plan['remote_root'],**identity),timeout=45)
        m.put('FINAL_COMPLETE_LOG_ACTUAL.json',value)
    print(json.dumps(dict(errors=value['errors'],logs={k:{f:v[f]for f in('path','bytes','SHA')}for k,v in value['logs'].items()})))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','inventory','freeze','run','logs']);a=p.parse_args()
    try:globals()[a.mode]()
    except BaseException:
        if R.exists():put(R/('LOCAL_ERROR_'+str(time.time_ns())+'.json'),
            dict(epoch=time.time(),error=traceback.format_exc()))
        raise
