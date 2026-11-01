"""Source-only identity contract, NOT a Task instance, Ready, resource lease or GO.

Parent supplies the next actual scope/path/asset installation; this module never
contacts an owner, budget, SDK or model and does not invent a remote PT location.
"""
from pathlib import Path
KIND='H1_NORMAL_TYPED71DB_MOD4V1_WHOLE20K_NATIVE24_NOUPDATE_V1'
SOURCE_SHA='71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4'
SOURCE_BYTES=16879851
ITER=41448
ADAM=832460
LR=.00038443359375000017
MOTHER453_SHA='97cdcde4a891359a5f1209fdad1614bf87629e0c3d3a40ce9018dc1fe9e2426b'
USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'

def validate_future_task_metadata(task):
    expected=dict(kind=KIND,source_SHA=SOURCE_SHA,source_bytes=SOURCE_BYTES,
        source_iteration=ITER,source_Adam17_step=ADAM,source_LR=LR,
        actual_mother453_manifest_SHA=MOTHER453_SHA,asset_USD_SHA=USD_SHA,
        asset_contract_SHA=CONTRACT_SHA,num_envs=20000,actor_obs=35,critic_obs=38,
        action_dim=6,policy_hz=50,feedback_hz=100,public_phase_tick_hz=100,
        physics_dt_s=.0025,decimation=8,TGS=[32,4],closure_episode_m=.01,
        mimic_rad=.01,no_optimizer_or_normalizer_update=True,
        original_H1_true270_scope=True)
    for key,value in expected.items():
        if task[key]!=value:raise ValueError('H1 future Task source identity: '+key)
    for key in ('selected_source_path','asset_dir'):
        if not isinstance(task[key],str) or not Path(task[key]).is_absolute():
            raise ValueError('Parent must supply actual absolute '+key)
    return expected

# Descriptions only. No Task.json / Ready / GO is created by this source package.
SOURCE_ONLY_TASK_CONTRACT=dict(status='DESCRIPTOR_NOT_INSTANTIATED_NOT_ADMITTED',
    kind=KIND,selected_source_remote_path='UNKNOWN_not_explicit_in_saved_report',
    selected_source_path='Parent supplies an actually resolved path in the next admitted scope',
    typed_layer='Inherit existing71db400N50; do NOT retype/modify a model',
    mother453_manifest_SHA=MOTHER453_SHA,
    asset_dir='Parent installs new2c root+bae contract+all USD dependencies before first task import',
    no_new_canonical_writer_or_resource_permission=True,
    no_current_Ready_or_GO_or_SDK_claim=True,
    intended_future_work='Original actual H1 fullrestore -> ONE freshreset -> mean24 controls only',
    future_PPO='Not implemented/admitted by this no-update source-only derivation',
    physics='2.5ms/TGS32/4; 50Hz policy,100Hz feedback and100Hz publicPhase age+2',
    model='20k/35/38/6/rawlearnedSTD6/17Adam832460/iter41448/LR.00038443359375000017',
    history='Whole original20k H1 phase/command/privateRNG/histories/queues; no slicing or reconstruction',
    numerical_scope='No extra FP64/bitwise physics health gate; original state-equality checks retained')
