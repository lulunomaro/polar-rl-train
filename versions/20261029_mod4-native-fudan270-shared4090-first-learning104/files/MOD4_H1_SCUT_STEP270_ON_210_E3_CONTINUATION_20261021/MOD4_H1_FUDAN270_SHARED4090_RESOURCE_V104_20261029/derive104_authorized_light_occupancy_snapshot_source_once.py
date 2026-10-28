from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
old=L/'TWO103_FUDAN270_FIRST_CLOSING_AND_INITIAL_CPU_SOURCE_V1/read_TWO103_new_scheduling_boundary_resource_CPU_only_UNUSED_once.py'
s=old.read_text('utf8');a=s.index("B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;W=T.parent;R=B/'reports'");s=s[:a]+s[a:].replace("B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;W=T.parent;R=B/'reports'","B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=B/'reports'",1)
s=s.replace("x['selected_compute_empty'] and x['free_MiB']>15669", "x['utilization_percent']<=30 and x['free_MiB']>15669")
s=s.replace('FUDAN103_NEW_FINITE_RESOURCE_SNAPSHOT_ENTRY_CONSUMED_ACTUAL.json','SHARED104_USER_AUTHORIZED_RESOURCE_ENTRY_CONSUMED_ACTUAL.json').replace('FUDAN103_NEW_SCHEDULING_BOUNDARY_RESOURCE_RETURNED_ACTUAL.json','SHARED104_USER_AUTHORIZED_RESOURCE_RETURNED_ACTUAL.json').replace('RESOURCE103_NEW_SNAPSHOT_ORIGINAL_ERROR_','SHARED104_RESOURCE_ORIGINAL_ERROR_')
ast.parse(s)
with (N/'read104_fresh_user_authorized_light_compute_resource_UNUSED_once.py').open('x',encoding='utf8') as f:f.write(s)
with (N/'reports/USER_AUTHORIZED_LIGHT_COMPUTE_POLICY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),explicit_user='两张有占用，如果占用不大直接启动，如果占用大不启用，还有不是还有两张卡吗',interpretation=dict(selected_GPU_free_MiB_strictly_above=15669,selected_GPU_utilization_percent_max=30,compute_UUID_rows_may_be_present=True),original_VRAM_floor_not_lowered=True,other_processes_retained_no_unknown_PID_identity=True,not_budget_or_physics_change=True,no_training_GO_yet=True),f,indent=2)
