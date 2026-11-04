"""Prepare only the measured final376 reward repair and shared source refs."""
from pathlib import Path
import ast
import hashlib
import json
import time
import numpy as np

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE=G/'project/isaac/mod4v1_scut'
P=N/'env20000_jump200_retry_ascent_1h_20261105'
A=N/'env20000_jump200_target_projection_1h_20261105'
read=lambda p:json.loads(Path(p).read_bytes())
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2)

assert not A.exists()
review=read(P/'reports/ACTUAL_JUMP200_FINAL_LEARNING_AND_ALL80_REVIEW.json')
assert review['all4_actual_images_reviewed'] and review['full_save_diagnosis']['Adam_min']==7520
assert review['all80']['upward_flight_envs']==0 and review['all80']['takeoff_requests_total']==300
assert read(P/'reports/TARGET_PROJECTION_REPAIR_CPU_ORDER02.json')['passed']
assert read(P/'reports/TARGET_PROJECTION_OLDSTAIRS_CPU.json')['passed']
for p in (N/'jump200_training_control.py',N/'review_jump200_final.py'):
    ast.parse(p.read_bytes())
prior=read(P/'reports/POSTROUND_FULL_RETURNED.json')['files']
plan=read(P/'PLAN.json');oldremote=plan['remote_root'];remote=oldremote.rsplit('/',1)[0]+'/'+A.name
A.mkdir();R=A/'reports';R.mkdir()
for key in ('GPU_UUID','original_save_deadline','original_nominal_end_epoch'):
    plan.pop(key,None)
plan.update(run_id='MOD4V1_JUMP200_TARGET_PROJECTION_20000ENV_1H_'+str(time.time_ns()),
    remote_root=remote,module_overlay=remote+'/overlay',module_overlays=[remote+'/overlay']+plan['module_overlays'],
    source_checkpoint=prior['production/FINAL.json']['checkpoint'],source_optimizer_step=7520,
    initialization='Complete same20k fullfinal376 actorcriticSTD/17Adam7520/LR/RNG/components/queues/globalcounter, protect constructor nominal then one freshphysicalreset',
    previous_training_root=str(P),previous_final_review=str(P/'reports/ACTUAL_JUMP200_FINAL_LEARNING_AND_ALL80_REVIEW.json'),
    previous_final_qualification='FULLV4final376/17Adam7520/actorcriticAdamfinite/7components/RNGqueues; independent80actual0flight0wholeclear0landing',
    previous_failed_skill_result=dict(request_envs=69,total_requests=300,upward_flight=0,wholeclear=0,landed_top=0,success=0,
        push_mean_world_vz=review['all80']['push_world_vz_mean'],hip_upper_hit_fraction=[1.,.99993734]),
    repair='Reward-only leg request projection cost: mean squared(request minus originalCAD->contractlimitCADprojection)/actualscale, weight-2; read real constructor offset/scale, preserve D4 and all action limits',
    continuation_reason='Repeated pushes now occur, but both hip targets remain at their upper bound and0actualflight; charge non-executable leg target requests instead of resetting learned outputs or widening limits',
    task_differences=['Adds jump200_target_projection=-2 reward only; existing retries/ascent/approach/landing rewards retained'],
    required_FIRST='iteration377/1newPPO/24controls480000samples192physics20newAdam/restore37617entries7520/nonzeroactorcriticgrad/FULLV4/completefirstlog0errors',
    pending_actual_resource_selection=True,previous_complete_log_required_before_launch=True,
    pending_human_additional_hour=False,source_profile='jump200',target_profile='jump200',task_changed=False,
    repair_first_axis=False,full_state_continuation=True,source_optimizer_loaded=True)
segments=list(plan['authorization_previous_segments'])
segments.append(dict(root=str(P),GO=prior['GO_PRODUCTION.json'],authorized_training_seconds=3600,owner_exit=prior['OWNER_EXIT.json']))
assert sum(x['authorized_training_seconds']for x in segments)+3600<=plan['human_authorization']['max_training_seconds']
plan['authorization_previous_segments']=segments
plan['cumulative_authorized_seconds_before_this_segment']=sum(x['authorized_training_seconds']for x in segments)
plan['newly_authorized_window']=False
plan['new_window_under_existing_100h_authorization']=True
put(A/'PLAN.json',plan)
for name in ('owner.py','entry.py'):(A/name).write_bytes((P/name).read_bytes())
previous=read(P/'INDEX_SOURCE_FROZEN.json');shared=list(previous['shared_text'])
for row in previous['files']:
    if row['relative'].startswith('overlay/'):
        shared.append(dict(path=oldremote+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
files=[]
for name in ('config.py','rewards.py','target_limits.py','sdk.py'):
    path=CODE/name;raw=path.read_bytes();ast.parse(raw)
    files.append(dict(path=str(path),relative='overlay/'+name,bytes=len(raw),SHA=sha(raw)))
put(A/'SOURCE_ONLY_PREPARED.json',dict(epoch=time.time(),files=files,shared_text=shared,source_only=True,
    whole_tree_model_asset_copy=False,human_authorization=plan['human_authorization']))
peerfile=Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/reports/STATUS_SCUT32_FIRST.json')
raw=peerfile.read_bytes();peer=json.loads(raw);go=peer['files']['GO_PRODUCTION.json'];identity=peer['files']['OWNER_STARTED.json']['identity']
assert go['run_id']=='MOD4_STANDING200_SUPPORTED_V32_1793822795305806500'
assert identity['pid']==1633096 and identity['creation']==1793823091.1
put(R/'CONTINUATION_PEER_CONTEXT.json',dict(epoch=time.time(),peer_kind='scut',peer_root=peer['job'],
    peer_identity=identity,peer_GO=go,source=dict(path=str(peerfile),bytes=len(raw),SHA=sha(raw)),
    foreign_local_reader39496='E3W10 metadata; local latest still PREGO_RESOURCE_WAIT, noactualGO at preparation',
    no_remote_read_at_preparation=True))
put(R/'TARGET_PROJECTION_REPAIR_PREPARED.json',dict(epoch=time.time(),previous_review=plan['previous_final_review'],
    measured_hip_upper_hit_fraction=review['all80']['target_upper_hit_fraction'],
    implementation='Current clip6 leg request * actual term scale + actual default offset; originalCAD then contract clamp/CAD; square residual in action units, mean4, weight-2, dt once',
    observation_action_physics_limits_or_optimizer_changed=False,CPU_tests=19,oldstairs_CPU_tests=8,
    previous_complete_log_pending=review['complete_log_review_pending'],
    native_model_reads_for_preparation=0,physics=0,source=plan['source_checkpoint'],
    selected_default_offset_source='Pinned mod4_task.py robot init_state joint_pos all0; production reads actual term._offset, never assumes zero',
    modules=files,sharedrefs=len(shared),existing_authorization=plan['human_authorization']))
print(json.dumps(dict(prepared=str(A),changed_modules=len(files),sharedrefs=len(shared),
    source_iteration=376,source_Adam=7520,complete_log_pending=review['complete_log_review_pending'],peer=go['run_id'])))
