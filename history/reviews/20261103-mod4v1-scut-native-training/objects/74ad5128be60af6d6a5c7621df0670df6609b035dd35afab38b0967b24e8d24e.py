"""Retry the measured command-schema gap within the same approved deadline."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import time
import traceback

N=Path(__file__).resolve().parent
B=N/'env20000_jump200_1h_20261104'
A=B/'attempt02';R=A/'reports'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/project/isaac/mod4v1_scut')
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda b:hashlib.sha256(b).hexdigest()


def put(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2)


def main():
    prior=read(B/'reports/FIRST_ACTUAL_RETURNED.json')['files']
    assert prior['TRAIN_CLOSED.json']['passed_execution']is False
    assert '_mode_enabled'in prior['production/ERROR.json']['error']
    assert all(prior['OWNER_EXIT.json'][k]for k in('all_own_waited','original_cost_settled','original_leases_released'))
    cpu=read(B/'reports/COMMAND_PROFILE_RESTORE_FIX_CPU.json');assert cpu['passed']
    go=prior['GO_PRODUCTION.json'];assert time.time()<go['save_deadline']-600
    A.mkdir();R.mkdir()
    plan=read(B/'PLAN.json');oldremote=plan['remote_root'];remote=oldremote+'/attempt02'
    remaining=int(go['save_deadline']-time.time())
    plan.update(remote_root=remote,run_id='MOD4V1_JUMP200_COMMAND_PROFILE_REPAIR_SAMEWINDOW_'+str(time.time_ns()),
        train_seconds=remaining,max_parent_seconds=remaining+300,
        original_window_run_id=go['run_id'],original_save_deadline=go['save_deadline'],
        original_nominal_end_epoch=go['nominal_end_epoch'],original_window_extended=False,
        original_hour_GO=go,remaining_same_human_hour=True,newly_authorized_window=False,
        module_overlay=remote+'/overlay',module_overlays=[remote+'/overlay']+plan['module_overlays'],
        repair='Only explicit scut_stairs->jump200 _mode_enabled constructorflags schema migration; learning/Adam/LR and all compatible tensors retained',
        initialization='Same full f6b6 source; preserve actorcriticSTDAdamLRiter/componentsRNGqueues; target no-special commandflags from constructor; one freshphysicalreset',
        pending_actual_resource_selection=True)
    put(A/'PLAN.json',plan)
    (A/'owner.py').write_bytes((N/'env20000_scut_stairs_1h_20261104/attempt07/owner.py').read_bytes())
    (A/'entry.py').write_bytes((B/'entry.py').read_bytes())
    previous=read(B/'INDEX_SOURCE_FROZEN.json');shared=list(previous['shared_text'])
    for row in previous['files']:
        if row['relative'].startswith('overlay/'):
            shared.append(dict(path=oldremote+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
    files=[]
    for name in('checkpoint.py','train.py'):
        path=G/name;raw=path.read_bytes();ast.parse(raw)
        files.append(dict(path=str(path),relative='overlay/'+name,bytes=len(raw),SHA=H(raw)))
    put(A/'SOURCE_ONLY_PREPARED.json',dict(epoch=time.time(),files=files,shared_text=shared,
        source_only=True,whole_tree_model_asset_copy=False,CPU_report=str(B/'reports/COMMAND_PROFILE_RESTORE_FIX_CPU.json'),
        previous_error=str(B/'reports/FIRST_ACTUAL_RETURNED.json'),original_deadline=go['save_deadline'],
        same_hour_no_extension_or_refund=True))
    put(R/'SAME_ORIGINAL_WINDOW_REPAIR_PREPARED.json',dict(epoch=time.time(),original_GO=go,
        remaining_seconds=remaining,source_checkpoint=plan['source_checkpoint'],source_only_modules=2,
        sharedrefs=len(shared),same_human_authorization=True,no_new_hour=True))
    spec=importlib.util.spec_from_file_location('jump200_command_repair_original_launch',N/'jump200_training_control.py')
    controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)
    controller.A=A;controller.R=R;controller.launch()


if __name__=='__main__':
    try:main()
    except BaseException:
        target=R if R.is_dir()else B/'reports'
        put(target/('COMMAND_RETRY_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),PID=os.getpid(),error=traceback.format_exc()))
        raise
