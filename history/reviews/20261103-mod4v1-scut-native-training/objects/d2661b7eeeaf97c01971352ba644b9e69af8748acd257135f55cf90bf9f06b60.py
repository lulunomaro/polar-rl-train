"""Select a measured GPU and reuse the original owned finite training flow."""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import time
import traceback

N=Path(__file__).resolve().parent
A=N/'env20000_scut_stairs_1h_20261104'
R=A/'reports'
Q=N/'env20000_target_axis_repair_1h_20261104/scut_stairs_eval1'
read=lambda path:json.loads(Path(path).read_bytes())
H=lambda value:hashlib.sha256(value).hexdigest()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def put(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2)


def inventory():
    m=load('scut_stair_human_four_card_read',N/'check_four_gpu.py')
    m.R=R
    m.READ=m.READ.replace('MOD4_STANDING200_SCUT_RECIPE_V20_FLAT_1793718811682640300',
                         'MOD4_STANDING200_SCUT_RECIPE_V25_FLAT_1793750781803008100')
    m.READ=m.READ.replace('1549188','1576385').replace('1793718880.82','1793756526.71')
    m.main()


def freeze():
    assert not(R/'LAUNCH_ONCE.json').exists()
    assert not(A/'INDEX_SOURCE_FROZEN.json').exists()
    review=read(Q/'reports/ACTUAL_SCUT_STAIR_REVIEW.json')
    assert review['native_execution_passed'] and review['current_model_view_image']
    result=read(Q/'reports/FULL_RETURNED.json')['files']
    release=result['RELEASE.json']
    assert release['all_own_waited'] and release['locks_released'] and release['error'] is None
    value=read(R/'FOUR_GPU_HUMAN_REQUEST_ACTUAL.json')
    assert value['all_clients_closed'] and value['SESSION_restored']
    host=value['hosts']['72'];assert host['passed']
    actual=host['actual']
    assert actual['canonical']['active'] is None and all(actual['locks'].values())
    peer=actual['exact_peer']['OWNER_EXIT.json']
    assert peer and peer['all_own_waited'] and peer['original_cost_settled'] and peer['original_leases_released']
    assert actual['ram']['available']>64*1024**3 and actual['disk']['free']>50*1024**3
    assert time.time()-actual['epoch']<300
    apps=actual['compute_apps'];assert apps['rc']==0
    occupied={row.split(',')[0].strip() for row in apps['stdout'].splitlines() if row.strip()}
    gpu=actual['gpu'];assert gpu['rc']==0
    choices=[]
    for line in gpu['stdout'].splitlines():
        fields=[field.strip()for field in line.split(',')]
        index,uuid,name,total,free,used,util=fields
        free,used,util=map(int,(free,used,util))
        if name=='NVIDIA GeForce RTX 4090' and free>15669 and (uuid not in occupied or(used<=4096 and util<=30)):
            choices.append(dict(index=int(index),UUID=uuid,free_MiB=free,used_MiB=used,util_percent=util,
                                has_compute=uuid in occupied,line=line))
    assert choices,'No measured card with capacity on the shared native host'
    choices.sort(key=lambda item:(item['has_compute'],-item['free_MiB']))
    selected=choices[0]
    plan=read(A/'PLAN.json')
    plan['GPU_UUID']=selected['UUID']
    plan.pop('live_GO',None);plan.pop('pending_actual_resource_selection',None)
    plan['native_diagnostic_review']=str(Q/'reports/ACTUAL_SCUT_STAIR_REVIEW.json')
    (A/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
    prepared=read(A/'SOURCE_ONLY_PREPARED.json');files=list(prepared['files'])
    for row in files:
        raw=Path(row['path']).read_bytes();assert len(raw)==row['bytes'] and H(raw)==row['SHA']
    for name in ('PLAN.json','owner.py','entry.py'):
        path=A/name;raw=path.read_bytes()
        if name.endswith('.py'):ast.parse(raw)
        files.append(dict(path=str(path),relative=name,bytes=len(raw),SHA=H(raw)))
    put(R/'ACTUAL_GPU_SELECTION.json',dict(epoch=time.time(),selected=selected,
        all_four_receipt=str(R/'FOUR_GPU_HUMAN_REQUEST_ACTUAL.json'),
        original_canonical_and_peer_released=True,native_owner_rechecks_locks_capacity_and_budget=True))
    put(A/'INDEX_SOURCE_FROZEN.json',dict(files=files,shared_text=prepared['shared_text'],
        overlay_resolution_order=plan['module_overlays'],source_only=True,
        whole_tree_model_asset_copy=False,native_diagnostic_reviewed=True,
        no_output_reinitialization=True,original_canonical_budget_and_reserve=True))
    print(json.dumps(dict(frozen=True,files=len(files),GPU=selected,GO=False)))


def launch():
    m=load('scut_stair_original_launch',N/'repaired_training_control.py')
    m.A=A;m.R=R;m.launch()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['inventory','freeze','launch'])
    args=parser.parse_args()
    try:globals()[args.mode]()
    except BaseException:
        put(R/('CONTROL_ERROR_'+str(time.time_ns())+'.json'),
            dict(epoch=time.time(),PID=os.getpid(),mode=args.mode,error=traceback.format_exc()))
        raise
