"""Publish exact local attempt08 state without another remote observer."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib
import json
import subprocess
import time

N=Path(__file__).resolve().parent
A=N/'env20000_scut_stairs_1h_20261104/attempt08';R=A/'reports'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261103-mod4v1-scut-native-training'
read=lambda p:json.loads(Path(p).read_bytes())
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
plan=read(A/'PLAN.json')
query="Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|pwsh|powershell|ssh|cmd' -and $_.CommandLine -match 'MOD4_H1|RMPOLAR|watch|run_once_after_resume|E1.*collect|prepare_archive|single_gpu|collect_nine|collect_generic|collect_actual|PAIR|stage_new|dispatch|retention|postround|standing|mod4v1_scut|repaired_training|e0_source_diagnostic|target_limits' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4"
raw=subprocess.check_output(['pwsh','-NoProfile','-Command',query],text=True,encoding='utf8')
rows=json.loads(raw)if raw.strip()else[]
if isinstance(rows,dict):rows=[rows]
launch=[row for row in rows if row['ProcessId']==60636 and str(row['CreationDate'])=='2026-11-04T17:52:18.149113+08:00']
facts=read(R/'FIRST_ACTUAL_RETURNED.json')['files']if(R/'FIRST_ACTUAL_RETURNED.json').exists()else{}
valid=read(R/'FIRST_NATIVE_VALIDATED_AND_COLLECTOR_BOUND.json')if(R/'FIRST_NATIVE_VALIDATED_AND_COLLECTOR_BOUND.json').exists()else None
collector=read(R/'POSTROUND_EXACT_CIM.json')if(R/'POSTROUND_EXACT_CIM.json').exists()else None
source=(A/'INDEX_SOURCE_FROZEN.json').read_bytes()
info=dict(epoch=time.time(),root=str(A),remote_root=plan['remote_root'],
    status='ACTUAL_RIGHTANGLE_VALID_FIRST__SOLE_POSTROUND'if valid else'ACTUAL_RIGHTANGLE_OWNER_LAUNCHED__FIRST_INITIALIZING',
    human_latest='打开MuJoCo后4090续训一小时20000环境；真实直角台阶允许轮子接触；四卡找空闲',
    num_envs=20000,train_seconds=3600,exit_headroom_seconds=300,
    source_checkpoint=plan['source_checkpoint'],full_state_continuation=True,
    geometry='SDK explicit mesh horizontal treads/vertical risers,25-40mmrise/.1mtread/1mplatform',
    geometry_report=str(R/'ACTUAL_SLOPE_CAUSE_AND_RIGHT_ANGLE_GEOMETRY_REPAIR.json'),
    old_attempt07_was_slope_not_stair_or_jump=True,
    owner_launch=read(R/'OWNER_LAUNCH.json'),GPU_UUID=plan['GPU_UUID'],
    resource_admission=read(R/'RESOURCE_READY_ACTUAL.json'),
    frozen_index=dict(path=str(A/'INDEX_SOURCE_FROZEN.json'),bytes=len(source),SHA=hashlib.sha256(source).hexdigest()),
    local_controller=collector if collector else launch[0]if launch else None,
    local_controller_role='sole postround collector'if collector else'sole launch/FIRST reader',
    actual_FIRST=facts.get('production/FIRST_UPDATED.json'),FIRST_verified=bool(valid),
    actual_GO=facts.get('GO_PRODUCTION.json'),actual_startup=facts.get('production/STARTUP.json'),
    actual_full_restore=facts.get('production/FULL_STATE_RESTORE.json'),
    launch_once_consumed=(R/'LAUNCH_ONCE.json').exists(),FIRST_once_consumed=(R/'FIRST_ONCE.json').exists(),
    bind_once_consumed=(R/'POSTROUND_BIND_ONCE.json').exists(),
    all_prior_once_retained=True,no_budget_grant_or_refund=True,trained_skill=False,
    next='Healthy sole localcontroller: no secondSSH/probe/relaunch/hotpatch. FIRST must validate fullstate and completeerrorlog; then solepostround awaits originalsave+45. Originalowner fullsave/exit/independent80 then render/view all actualposes and all80 contact/targets/commands/height review.')
write(R/'CURRENT_LOCAL_STATUS.json',info)
for path in [N.parents[1]/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
    value=read(path)
    value.setdefault('scut_stair_attempt07_closed_summary_before_rightangle08',dict(
        current_training=value.get('current_training'),next=value.get('next'),status=value.get('status')))
    value.update(epoch=info['epoch'],current_training=info['status'],status=info['status'],
        human_latest_request=info['human_latest'],scut_stair_training=info,
        next=info['next'],scut_stair_attempt08=info,
        scut_stair_attempt07_geometry_correction=dict(report=info['geometry_report'],
            actual_saved_mesh_vertical_faces=0,actual_saved_mesh_sloping_faces=9060,
            skill_interpretation='Existing53raiseddual/2stable are slope observations, not true stairs or jumping'))
    if path.name=='WORK_ORDER.json':
        value.update(captured_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
            root=str(A),remote=plan['remote_root'],FIRST=info['actual_FIRST'],GO=info['actual_GO'],
            owner_exit=None,final=None,training_completed=False,evaluation_completed=False,
            native_pose_visual_review=None,local_controller=info['local_controller'],
            local_controller_role=info['local_controller_role'],
            independent_evaluation=None,trained_skill=False,
            success_current_scope='Actual right-angle stairs, wheels may maintaincontact; no fixed270mm or flight requirement')
    write(path,value)
print(json.dumps(dict(status=info['status'],local_controller=info['local_controller'],FIRST=info['actual_FIRST'],GO=info['actual_GO'])))
