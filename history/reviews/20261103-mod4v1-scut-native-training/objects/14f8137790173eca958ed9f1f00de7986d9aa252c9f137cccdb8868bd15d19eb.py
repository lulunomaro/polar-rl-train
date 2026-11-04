"""Use measured idle GPU0 after the old pre-model resource refusal."""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import inspect
import json
import time
import traceback

N=Path(__file__).resolve().parent
D=N/'env20000_target_axis_repair_1h_20261104/scut_stairs_eval1'
R=D/'reports_gpu0'
read=lambda path:json.loads(Path(path).read_bytes())
H=lambda value:hashlib.sha256(value).hexdigest()


def put(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2)


def prepare():
    old=read(D/'reports/FULL_RETURNED.json')['files']
    assert old['RELEASE.json']['all_own_waited']and old['RELEASE.json']['locks_released']
    assert 'evaluation/NATIVE_STARTUP.json'not in old
    assert 'insufficient measured capacity'in old['ERROR.json']['error']
    actual=read(N/'env20000_scut_stairs_1h_20261104/reports/FOUR_GPU_HUMAN_REQUEST_ACTUAL.json')
    gpu=actual['hosts']['72']['actual']
    assert gpu['canonical']['active']is None and all(gpu['locks'].values())
    assert 'GPU-16828f91-2b45-b646-8dc0-9481138e2842'not in gpu['compute_apps']['stdout']
    plan=read(D/'PLAN.json');plan['GPU_UUID']='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
    plan['resource_revision']=3;plan['old_failure_before_model_and_physics']=True
    put(D/'PLAN_GPU0.json',plan);R.mkdir()
    text=(D/'owner_eval.py').read_text(encoding='utf8')
    pairs=[("r/'PLAN.json'","r/'PLAN_GPU0.json'"),("r/'INSTALL_MANIFEST.json'","r/'INSTALL_MANIFEST_GPU0.json'"),
        ("r/'evaluation'","r/'evaluation_gpu0'"),("r/'WORKER.log'","r/'WORKER_GPU0.log'"),
        ("r/'WORKER_IDENTITY.json'","r/'WORKER_IDENTITY_GPU0.json'"),
        ("r/'WORKER_WAITED.json'","r/'WORKER_WAITED_GPU0.json'"),
        ("r/'GPU_ADMISSION.json'","r/'GPU_ADMISSION_GPU0.json'"),("r/'SOURCE_REGISTRY.json'","r/'SOURCE_REGISTRY_GPU0.json'"),
        ("r/'RELEASE.json'","r/'RELEASE_GPU0.json'"),("r/'ERROR.json'","r/'ERROR_GPU0.json'"),
        ("r/'evaluation/RESULT.json'","r/'evaluation_gpu0/RESULT.json'"),
        ("r/'evaluation/ERROR.json'","r/'evaluation_gpu0/ERROR.json'")]
    for before,after in pairs:
        assert text.count(before)==1,(before,text.count(before));text=text.replace(before,after)
    ast.parse(text);(D/'owner_gpu0.py').write_text(text,encoding='utf8',newline='\n')
    files=[]
    for name in('PLAN_GPU0.json','owner_gpu0.py'):
        path=D/name;value=path.read_bytes();files.append(dict(path=str(path),relative=name,bytes=len(value),SHA=H(value)))
    shared=read(D/'INDEX_REV2.json')['files']
    put(D/'INDEX_GPU0.json',dict(files=files,existing_remote_files=shared,source_only=True,whole_tree_model_asset_copy=False))
    print(json.dumps(dict(prepared=True,GPU=plan['GPU_UUID'],new_files=2,reused_source_modules=5)))


def run():
    s=importlib.util.spec_from_file_location('scut_stair_original_gpu0',N/'target_limits_control.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.D=D;m.R=R
    source=inspect.getsource(m.run)
    pairs=[("D/'PLAN.json'","D/'PLAN_GPU0.json'"),("D/'INDEX.json'","D/'INDEX_GPU0.json'"),
        ('TARGET_LIMIT_NATIVE01','SCUT_STAIRS_IDLE_GPU0'),
        ("p.mkdir(exist_ok=False);(p/'overlay').mkdir()","assert p.is_dir()"),
        ("'/INSTALL_MANIFEST.json'","'/INSTALL_MANIFEST_GPU0.json'"),
        ("r/'OWNER.log'","r/'OWNER_GPU0.log'"),("r/'owner_eval.py'","r/'owner_gpu0.py'"),
        ("'WORKER.log','OWNER.log'","'WORKER_GPU0.log','OWNER_GPU0.log'"),
        ("D/'evaluation'","D/'evaluation_gpu0'")]
    for before,after in pairs:
        assert before in source,before;source=source.replace(before,after)
    before=" p=r/name\n if p.is_file():files[name]=json.loads(p.read_bytes())"
    after=""" actual=name.replace('evaluation/','evaluation_gpu0/')
 if '/'not in name:actual=name.replace('.json','_GPU0.json')
 p=r/actual
 if p.is_file():files[name]=json.loads(p.read_bytes())"""
    assert source.count(before)==1;source=source.replace(before,after)
    before="with sf.file(plan['remote_root']+'/INSTALL_MANIFEST_GPU0.json','wx')as stream:stream.write(json.dumps(index['files']).encode())"
    after=before.replace("index['files']","index['files']+index['existing_remote_files']")
    assert source.count(before)==1;source=source.replace(before,after)
    needle="ready=c['active_segment']is None and e['all_own_waited']and e['original_cost_settled']and e['original_leases_released']"
    wait=read(D/'RESOURCE_WAIT.json')
    added="""
peer_started=json.loads((Path(%r)/'OWNER_STARTED.json').read_bytes())
assert peer_started['identity']['pid']==%r and peer_started['identity']['creation']==%r
peer_exit_path=Path(%r)/'OWNER_EXIT.json'
peer_exit=json.loads(peer_exit_path.read_bytes())if peer_exit_path.exists()else None
ready=ready and bool(peer_exit and peer_exit['all_own_waited']and peer_exit['original_cost_settled']and peer_exit['original_leases_released'])
"""%(wait['peer_root'],wait['peer_owner']['pid'],wait['peer_owner']['creation'],wait['peer_root'])
    assert source.count(needle)==1;source=source.replace(needle,needle+added)
    scope=dict(vars(m));exec(compile(source,str(Path(__file__)),'exec'),scope);scope['run']()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);args=p.parse_args()
    try:globals()[args.mode]()
    except BaseException:
        if R.exists():put(R/('LOCAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc()))
        raise
