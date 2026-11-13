"""Freeze the explicitly selected five-minute parent and isolated native inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import sys
import tarfile
import time

T = Path(__file__).resolve().parent
R = T.parents[2]
REMOTE = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FORWARD_JUMP_RL_2H_20261114_R1'
parser = argparse.ArgumentParser()
parser.add_argument('--access-dir',required=True)
parser.add_argument('--archive',required=True)
args = parser.parse_args()
sys.path.insert(0,args.access_dir)
from ssh72 import connect, execute
import torch

parent = T/'weights/frozen_best_parent.pt'
digest = hashlib.sha256(parent.read_bytes()).hexdigest()
assert digest == '03884d680c0fcb4c5216f8aeaa42c319473ea1cbc7261df089f42c1136b07edd'
state = torch.load(parent,map_location='cpu',weights_only=False)
source = R/'sources/local/MOD4V3_STAIRS_PHASE_HEIGHT_REPAIR_2H_20261113'
evaluation = json.loads((source/'evidence/checkpoint_evals/model_005m/EVALUATION.json').read_bytes())
selection = dict(epoch=time.time(),selected='model_005m.pt',sha256=digest,bytes=parent.stat().st_size,
    source=str(source/'weights/model_005m.pt'),frozen_copy=str(parent),iteration=state['iter'],
    selection_authority='Human explicitly corrected selection to five-minute checkpoint on 2026-11-14',
    measured=evaluation,full_PPO=dict(actor=True,critic=True,STD=True,Adam_entries=len(state['optimizer_state_dict']['state']),
        RNG_keys=[k for k in state if 'rng' in k.lower()]),
    limitations=['New parent native fullDR/rough acceptance pending upstream; not a production promotion',
                 'No claim that latest timestamp or highest reward establishes global superiority'])
(T/'PARENT_SELECTION.json').write_text(json.dumps(selection,indent=2)+'\n')
old = json.loads((T/'SOURCE_PLAN_parent.json').read_bytes())
plan = dict(schema='MOD4V3_FORWARD_JUMP_RL_V1',root=REMOTE,
    python='/home/lc01/Zonglin Li/zonglin2/run-python.sh',runtime=REMOTE+'/dependencies/launcher',
    shared_package=REMOTE+'/dependencies/package',package=REMOTE+'/native_package',support=REMOTE+'/support',
    source_paths=REMOTE+'/dependencies/SOURCE_PATHS.72.json',reset_bank=REMOTE+'/dependencies/reset_bank.json',
    parent=REMOTE+'/weights/frozen_best_parent.pt',parent_sha256=digest,parent_iteration=state['iter'],
    asset_identity=old['asset_identity'],seed=66,cumulative_training_seconds_before=0,
    budget_total_training_seconds=7200,optimizer_owners=1,training_GPU=0,evaluation_GPU=1,
    training_round=dict(seconds=7200,num_envs=2048,full_checkpoint_every_seconds=300,
        learning_rate=1.e-4,schedule='fixed',clip_param=.2,num_learning_epochs=5,
        value_loss_coef=4.,rollout=24,automatic_extension=False),
    jump_bc=dict(initial=.5,final=.15,decay_seconds=5400.,
        type='Training-only frozen parent plus staged action labels inside the native PPO backward',
        execution='Only sampled learned actor output; no teacher execution overlay'),
    jump=dict(sequence=['forward','crouch','extend_push','airborne_retract','land_and_roll'],
        flat_terrain=True,command_vx_m_s=[.4,.8],jump_cue_s=[1.9,2.5],crouch_seconds=.32,
        episode_seconds=6.,min_air_seconds=.16,min_wheel_lower_rim_peak_m=.12,
        crouch_measured_delta_max_rad=.8,push_measured_delta_min_rad=1.25,retract_measured_delta_max_rad=.9,
        air_pitch_max_deg=10.,air_roll_max_deg=5.,landing_stable_seconds=.5,landing_support_duty_min=.8,
        landing_pitch_roll_max_deg=15.,landing_vx_min_m_s=.1,closure_reset_m=.01,mimic_reset_rad=.01,
        physics_dt_s=.0025,leg_feedback_hz=100,wheel_feedback_hz=400,policy_hz=50,
        solver='Unmodified TGS32/4',original_motor_envelopes=True,full_DR_ranges_unchanged=True,
        nominal_fraction=.2,reset_distribution='Upright feasible pose, yaw +/-0.04 rad, zero velocity',
        policy_slots_28_35=['base_mode','jump_request','measured_air','landed',0,0,0],
        critic_slots_32_39='Privileged task phase one-hot; dimensions unchanged',
        deployment_input_producer_update_required=True,
        selection='Independent deterministic actor-only fixed cases; balanced complete sequence first, nominal/fullDR separate'))
(T/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
paths = json.loads((T/'dependencies/SOURCE_PATHS.relative.json').read_bytes())
(T/'dependencies/SOURCE_PATHS.72.json').write_text(json.dumps({k:REMOTE+'/dependencies/'+v for k,v in paths.items()},indent=2)+'\n')
manifest = []
with tarfile.open(args.archive,'w:gz') as archive:
    for name in ('support','dependencies','native_package','weights','PLAN.json','PARENT_SELECTION.json'):
        source_path = T/name
        for path in sorted(source_path.rglob('*')) if source_path.is_dir() else [source_path]:
            if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            rel = path.relative_to(T).as_posix()
            archive.add(path,arcname=rel,recursive=False)
            manifest.append(dict(path=rel,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(T/'evidence/REMOTE_INPUTS.json').write_text(json.dumps(dict(epoch=time.time(),root=REMOTE,files=manifest),indent=2)+'\n')
client = connect()
try:
    status,out,err = execute(client,'mkdir '+shlex.quote(REMOTE),20)
    if status:
        raise RuntimeError('Independent target must be new: '+out+err)
    sftp = client.open_sftp()
    sftp.put(args.archive,REMOTE+'/inputs.tar.gz')
    sftp.close()
    status,out,err = execute(client,'cd '+shlex.quote(REMOTE)+' && tar -xzf inputs.tar.gz && sha256sum weights/frozen_best_parent.pt native_package/assets/robot.usd',60)
    print(out,err)
    assert status == 0
finally:
    client.close()
print(json.dumps(dict(root=REMOTE,files=len(manifest),archive_bytes=Path(args.archive).stat().st_size)),flush=True)
