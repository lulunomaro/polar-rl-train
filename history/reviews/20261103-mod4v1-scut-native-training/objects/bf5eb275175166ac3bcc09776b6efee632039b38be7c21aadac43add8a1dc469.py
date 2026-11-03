"""New frozen repair attempt; retain and reference the failed original package."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','launch']);p.add_argument('--attempt',required=True);a=p.parse_args()
A=N/a.attempt
read=lambda p:json.loads(Path(p).read_bytes())
def put(path,value):
    with Path(path).open('x',encoding='utf-8')as f:json.dump(value,f,ensure_ascii=False,indent=2)
if a.mode=='prepare':
    A.mkdir();(A/'reports').mkdir()
    original=read(N/'PLAN.json');j=original['remote_root']+'/'+a.attempt
    plan=dict(original,remote_root=j,run_id=original['run_id']+'_'+a.attempt,
        package_root=original['remote_root']+'/package',module_overlay=j+'/overlay',
        repair='USD GfVec3f points and actual new SDK raycaster cache keyed by mesh path/device')
    files=[]
    def add(path,relative):
        raw=Path(path).read_bytes();files.append(dict(path=str(path),relative=relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    for name in ['sdk.py','train.py','checkpoint.py','evaluate.py']:
        add(G/'project/isaac/mod4v1_scut'/name,'overlay/'+name)
    if a.attempt=='env20000_1h':
        closed=read(N/'reports/HUMAN_CHANGE20000_80_CLOSED_RETURNED.json')['files']
        assert closed['OWNER_EXIT.json']['all_own_waited']and closed['production/FINAL.json']['passed_execution']
        evaluation=read(N/'reports/EVAL80_INFERENCE_FIX01_RETURNED.json')['files']['evaluation/RESULT.json']
        assert evaluation['passed_execution']and evaluation['independent_first_episodes']==80
        plan.update(run_id=original['run_id'].replace('2H','20000ENV_1H')+'_'+a.attempt,
            num_envs=20000,train_seconds=3600,max_parent_seconds=3900,
            source_checkpoint=closed['production/FINAL.json']['checkpoint'],resized_learning_continuation=True,
            initialization='FullPPO actorcriticSTDAdamLRiter26 and globalRNG; fresh20000physicalDRqueues',
            repair='Human explicitly changed80x2hours to20000x1hour; closed80strict0 retained',
            old80_independent_evaluation=evaluation)
    for name in ['owner.py','entry.py','SOURCE_PATHS.json']:add(N/name,name)
    put(A/'PLAN.json',plan);add(A/'PLAN.json','PLAN.json')
    previous=read(N/'INDEX_SOURCE_FROZEN.json')['files']
    shared=[dict(path=original['remote_root']+'/'+r['relative'],bytes=r['bytes'],SHA=r['SHA']) for r in previous]
    put(A/'INDEX_SOURCE_FROZEN.json',dict(files=files,shared_text=shared,no_tree_or_model_copy=True))
    put(A/'FAILURE_FIX.json',dict(actual_failure=N.as_posix()+'/reports/FIRST_ACTUAL_RETURNED.json',
        error='pxr GfVec3f numpy scalar type mismatch',fix=plan['repair'],prior_owner_all_own_waited=True,
        source_PT_reads_before_failure=0,PPO_updates_before_failure=0))
    print(json.dumps(dict(root=str(A),remote=j,overlaybytes=sum(r['bytes']for r in files))))
else:
    spec=importlib.util.spec_from_file_location('scut_serial',N/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.N=A;m.R=A/'reports';m.launch()
