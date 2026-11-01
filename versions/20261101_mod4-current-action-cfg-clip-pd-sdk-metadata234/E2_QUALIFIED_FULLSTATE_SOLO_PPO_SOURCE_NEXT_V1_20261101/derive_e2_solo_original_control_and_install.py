"""New local one-role control/source map;no model or binary reads."""
from pathlib import Path
import hashlib,json,time,traceback

N=Path(__file__).resolve().parent
T=N.parent
A=T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/A_PPO_SOURCE'
BASE=T/'E2_QUALIFIED_METADATA_TASK_READY_SOURCE_V226_20261101'


def ref(p):
 b=p.read_bytes();return dict(local_path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def write(p,b):
 with p.open('xb') as f:f.write(b)
def put(p,v):write(p,json.dumps(v,indent=2,allow_nan=False).encode())
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)


def main():
 C=N/'control_e2_solo';C.mkdir(exist_ok=False)
 old=A/'control227'
 owner=(old/'solo227_finite_owner_authority72.py').read_text(encoding='utf8')
 for a,b in [('from solo227_protocol import validate_schedule,flat_go_fields','from e2_solo_protocol import validate_schedule,flat_go_fields'),
             ("set(specs)=={'w35_72'}","set(specs)=={'e2'}"),
             ('Linux_W35_QUALIFIED343E_SOLO227_ONE_HOUR_','Linux_E2_B3AE_ORIGINAL_SOLO_ONE_HOUR_'),
             ('human_requested_W35_shared_material_one_hour','human_requested_E2_original_world_mix_one_hour')]:owner=once(owner,a,b)
 write(C/'e2_solo_finite_owner_authority72.py',owner.encode())
 common=(old/'three_slot_common_v1.py').read_text(encoding='utf8')
 common=once(common,'from solo227_protocol import valid_ready','from e2_solo_protocol import valid_ready')
 write(C/'three_slot_common_v1.py',common.encode())
 node=(old/'solo227_fullstate_slot_node.py').read_text(encoding='utf8')
 node=once(node,'ADMISSION227_READY.json','ADMISSION_E2_SOLO_READY.json')
 previous='(go.get("literal_original_fudan_JUMP") if spec["key"]=="e0_72" else go.get("genuine_W35_full_original_RM70_course"))'
 node=once(node,previous,'(spec["key"]=="e2" and go.get("genuine_original_E2_WORLD_MOVING_SIGNED4"))')
 write(C/'e2_solo_fullstate_slot_node.py',node.encode())
 for name in ('single_writer72_authority_V85M_source.py','forwarded_original_owner_control_v1.py'):
  write(C/name,(old/name).read_bytes())
 for name in ('e2_solo_contract.py','e2_solo_protocol.py'):write(C/name,(N/name).read_bytes())
 controls=[dict(relative=p.name,**ref(p)) for p in sorted(C.glob('*.py'))]
 put(N/'reports/CONTROL_E2_SOLO_FROZEN_BINDINGS.json',dict(kind='SOURCE_ONLY_ORIGINAL_ONE_OWNER_E2_ROLE',files=controls,
  exact_role_key='e2',correct_existing_sender_byte_reused=True,
  owner_HMAC_twofcntl_budget_charge_STOP_save_close_wait_terminal_ACK_unchanged=True,
  changes='Protocol import,one-role key,label,Ready filename and typedE2 GO recognition only'))
 old_install=BASE/'source_payload226/INSTALL226_EXACT_SOURCE_BINDINGS.json'
 installation=json.loads(old_install.read_bytes())
 excluded={'evaluate_e2_world213.py','probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py'}
 files={r['relative']:r for r in installation['files'] if r['relative'] not in excluded}
 for name in ('worker_e2_original_fullPPO.py','e2_solo_contract.py'):
  files[name]=dict(relative=name,**ref(N/name))
 put(N/'reports/INSTALL_E2_SOLO_ORIGINAL_SOURCE.json',dict(kind='E2_SOLO_ORIGINAL_FULLSTATE_SOURCE_INSTALL_V1',
  status='SOURCE_MAP_ONLY_NOT_INSTALLED_NO_GO',files=[files[k] for k in sorted(files)],
  base_install_ref=ref(old_install),excluded_unselected_eval_entries=sorted(excluded),
  entry='runtime/isaac/mod4/train_e2_213.py',
  selected_source_metadata=dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_PPO50_GAS400_2610v93/e2/adaptation/final_valid_update92.pt',
   SHA='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1',bytes=14615089,installer_model_stat_hash_copy_open=0,worker_byte_open=1,worker_decode=1),
  actor_reward_command_D0_D7_SDK_physics_sources_reused=True,model_asset_raw_reads=0))
 put(N/'reports/DERIVE_E2_SOLO_SOURCE_BINDINGS.json',dict(epoch=time.time(),status='LOCAL_SOURCE_ONLY',
  original_owner=ref(old/'solo227_finite_owner_authority72.py'),original_node=ref(old/'solo227_fullstate_slot_node.py'),
  control_files=controls,selected_profile='Original world_directional_v1 +.5 /signedyaw/pure/body/transition/stand mix',
  no_new_role_whitelist_or_source210_route=True,no_runtime_or_GO=True))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/DERIVE_E2_SOLO_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
