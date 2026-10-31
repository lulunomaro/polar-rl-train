"""Closed210 model qualification and current authority binding; JSON only."""
from pathlib import Path,PurePosixPath
import hashlib,json
GENERATION='MOD4_SINGLE_WRITER72_20261026'
E0_PARENT='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'
W35_INPUT='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
E0_JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_JUMP32066_GROUND10_THREE_HOUR_20261031v210/e0_72'
GPUS={'GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}
KIND='NEW220_CLOSED210_E0_MEAN_N1_PLANE_YAW0_FLIGHT_EVIDENCE'


def read_ref(path):
 path=Path(path);assert path.suffix=='.json' and not path.name.endswith(('.partial','.active'))
 raw=path.read_bytes();return json.loads(raw),dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())


def qualified210(closing,cpu,*,synthetic_fixture=False):
 c,cr=read_ref(closing);u,ur=read_ref(cpu)
 assert synthetic_fixture or not (c.get('synthetic_fixture_only') or u.get('synthetic_fixture_only'))
 assert c['passed_collection'] and c['owner_closed']['canonical_None'] and c['owner_closed']['shared_locks_free']
 assert c['owner_closed']['cohort_final']['original_cost_settled'] and c['owner_closed']['owner_exit']['original_cost_settled']
 r=c['roles']['e0_72'];f=c['formals']['e0_72'];q=u['roles']['e0_72']
 assert r['qualified_formal'] and r['errors']==[] and r['private_EX_free']
 assert r['original_node_terminal']['row']['returncode']==0 and r['original_node_exit']['all_own_children_waited'] and r['original_node_exit']['private_EX_released']
 assert r['final']['passed'] and f['transfers']==1 and f['two_host_SHA_equal']
 assert u['passed'] and u['old_model_reads']==0 and q['passed'] and q['actor35_critic38_STD6'] and q['complete_task_and_DR_state_present']
 assert q['save_at_or_after_requested_deadline']
 row=r['final']['final'];updates=r['final']['actual_new_PPO_updates']
 assert type(updates)is int and updates>0 and row['source_SHA']==E0_PARENT
 assert f['SHA']==row['SHA']==q['SHA'] and f['SHA'] not in (E0_PARENT,W35_INPUT)
 assert f['bytes']==row['bytes'] and q['saved_iteration']==row['saved_iteration']==32066+updates
 assert q['Adam17_step']==row['Adam_min']==row['Adam_max']==642840+20*updates
 assert q['new_PPO_updates']==updates
 remote=PurePosixPath(f['source']);assert remote.parent==PurePosixPath(E0_JOB)/'production' and remote.name=='model_final_complete.pt'
 return dict(model_path=str(remote),model_SHA=f['SHA'],model_bytes=f['bytes'],model_iteration=q['saved_iteration'],
  actual_training_new_PPO_updates=updates,actual_17Adam_step=int(q['Adam17_step']),
  qualified197_package_root=E0_JOB,input_source_SHA=E0_PARENT,source_key='source_parent_branch_SHA',task_key='typed_MIX210_task',
  closed_qualification_refs=[cr,ur],source_fullstate_CPU_reused_without_PT_read=True)


def original219_binding(launch,state):
 l,lr=read_ref(launch);s,sr=read_ref(state)
 assert set(l['specs'])=={'w35_72'} and s['current_owner_matched'] and not s['canonical_None']
 owner=l['owner'];g=s['current']['go']['w35_72'];spec=l['specs']['w35_72']
 assert set(s['current']['go'])=={'w35_72'} and owner['pid']==g['original_owner_pid']
 assert owner['creation']==g['original_owner_creation'] and g['run_id']==l['run_id']
 assert g['role_key']=='w35_72' and g['source_model_SHA']==W35_INPUT and g['input_Adam']==648360
 assert g['one_original_writer'] and g['manifest_SHA']==spec['manifest_SHA']
 assert spec['GPU_UUID']==g['GPU_UUID']
 return dict(kind='EXACT_ORIGINAL219_OWNER_GO',authority_generation=GENERATION,run_id=l['run_id'],
  owner=owner,go=g,training_GPU_UUID=spec['GPU_UUID'],local_refs=[lr,sr])


def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert c['authority_generation']==GENERATION and c['authorized_training_seconds']==2268000
 assert c['new_authority_budget_extensions']==[]
 active=c['active_segment']
 if binding['kind']=='FRESH_CNONE':
  assert binding['authority_generation']==GENERATION and active is None
 else:
  assert binding['kind']=='EXACT_ORIGINAL219_OWNER_GO' and active is not None
  assert active['owner_parent_pid']==binding['owner']['pid']
  assert owner_identity['pid']==binding['owner']['pid'] and owner_identity['creation']==binding['owner']['creation']
  assert set(owner_current['go'])=={'w35_72'} and owner_current['go']['w35_72']==binding['go']
  assert binding['go']['run_id']==binding['run_id'] and binding['go']['source_model_SHA']==W35_INPUT
 return True


def validate_task(task):
 assert task['kind']==KIND and task['target_host']=='72' and task['num_envs']==1
 assert task['controls_max']==1000 and task['physics_callbacks_max']==8000 and task['feedback_samples_max']==2000
 assert task['policy_hz']==50 and task['physics_dt']==.0025 and task['TGS']==[32,4] and task['feedback_hz']==100
 assert task['model_iteration']>32066 and task['model_SHA'] not in (E0_PARENT,W35_INPUT)
 assert task['input_source_SHA']==E0_PARENT and task['qualified197_package_root']==E0_JOB
 assert task['GPU_UUID'] in GPUS and task['no_optimizer_or_training_or_budget_write'] is True
 assert task['eval_yaw_range']==[0.,0.] and task['vx_range']==[-2.1,2.1] and task['height_range']==[.12,.15]
 assert task['model_byte_reads']==1 and task['model_decodes']==1 and task['model_copies']==0
 binding=task['current_authority_binding']
 if binding['kind']=='EXACT_ORIGINAL219_OWNER_GO':assert task['GPU_UUID']!=binding['training_GPU_UUID']
 return True
