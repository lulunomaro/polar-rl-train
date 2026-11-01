"""New caller source derivation from actual227D;never transport or runtime."""
from pathlib import Path
import ast,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
D=T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/D_BEFORE_USE_CWD_REPAIR_SOURCE'

def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def literals(p):
 return {n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.Assign)}

def main():
 purpose=json.loads((R/'DERIVE_E2_CALLERS_PURPOSE_FROZEN.json').read_bytes());assert purpose['executions']==1
 assert ref(D/'INDEX227D_FROZEN.json')['SHA']=='4ed43e0ea67798bd4a1e610a49807bb7a5ce32d16dd2b9e751be19f0ca442e0f'
 put(R/'DERIVE_E2_CALLERS_ONCE_CONSUMED.json',dict(epoch=time.time(),source_only=True))
 payload=literals(D/'remote227D_payloads.py')
 payload={k:v.replace('control227','control_e2_solo') for k,v in payload.items()}
 first=payload['FIRST']
 for a,b in [('ACTUAL_W35_RM70_V3_FULLSTATE_BEFORE_NEW_CONTROL.json','E2_FULLSTATE_BEFORE_NEW_CONTROL_ACTUAL.json'),
  ('NATIVE24_W35_RM70_V3_ACTUAL.json','NATIVE24_E2_ORIGINAL_ACTUAL.json'),('ORIGINAL_W35_RM70_V3_ERROR.json','ORIGINAL_E2_PPO_ERROR.json'),
  ('SOURCE208_V3_FINAL_READ_COUNTS.json','E2_SOURCE_SELECTED_FINAL_READ_COUNTS.json'),('APP_CLOSED.json','APP_CLOSING.json'),
  ('PREDELEGATE227_METADATA_GATE_ACTUAL.json','PRELAUNCH_E2_SOLO_ACTUAL_EVIDENCE.json'),('649720','859300'),('649740','859320'),('32405','42823')]:first=first.replace(a,b)
 first=once(first,"and n and n.get('passed')", "and value['first_complete'].get('all_saved_tensor_and_scalar_numbers_finite') is True and n and n.get('passed')")
 payload['FIRST']=first
 payload['POSTCOPY_NO_MODEL']='''from pathlib import Path
import hashlib,json
B=Path(v['job']);rows=v['files']
for r in rows:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.suffix!='.pt' and p.stat().st_size==r['bytes']
 with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==r['SHA'],str(p)
print(json.dumps(dict(passed=True,source_asset_postcopy_passes=1,files=len(rows),selected_model_stat_hash_copy_open_decode=0,no_GPU_or_account_write=True)))'''
 write(N/'remote_e2_solo_payloads.py','"""ROOT-only remote strings derived from actual227D;import is inert."""\n'+
       '\n\n'.join(k+' = '+repr(v) for k,v in payload.items())+'\n')
 additions=literals(D/'remote227D_additions.py')
 additions['RESOURCE']=once(additions['RESOURCE'],"assert gpu=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'",
  "assert gpu in {'GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}")
 additions['VERIFY_METADATA']=additions['VERIFY_METADATA'].replace('control227','control_e2_solo')
 write(N/'remote_e2_solo_additions.py','"""Original availability probes,explicitly released before owner takeover."""\n'+
       '\n\n'.join(k+' = '+repr(v) for k,v in additions.items())+'\n')

 normal=(D/'collect227D_original_W35_formal_cost_normal900_UNUSED_once.py').read_text(encoding='utf8')
 normal=once(normal,'"""One original normal900 collection of219 soleW35; no extra GO."""','"""ROOT-only original E2 solo normal900;no extra GO or automatic signals."""')
 normal=once(normal,"N=Path(__file__).resolve().parent;T=N.parents[1];W=T.parent;R=N/'reports'",'from caller_common import *')
 normal=normal.replace('ROOT227D','ROOT_E2_SOLO').replace('control227','control_e2_solo').replace('w35_72','e2')
 normal=once(normal,'from launch227D_install_original_solo_W35_FIRST_UNUSED_once import verify_index','from caller_common import verify_index,INDEX,validate_original_go,normal900_eligible')
 normal=normal.replace("verify_index(N/'INDEX227D_FROZEN.json',args.caller_index_SHA)","verify_index(N/INDEX,args.caller_index_SHA)")
 normal=once(normal,"assert go and set(go)<=set(specs)","assert set(go)==set(specs)=={'e2'};validate_original_go(go['e2'],launch['run_id'])")
 normal=once(normal,"assert nominal-time.time()<=900 or already_closed,'Original latest signed local900 gate not yet eligible'",
  "assert normal900_eligible(go['e2'],time.time(),already_closed),'Original signed local900 gate not yet eligible'")
 normal=normal.replace("pattern='collect227D_|launch227D_|review227D_|", "pattern='collect_e2_solo_|launch_e2_solo_|review_e2_solo_|collect227D_|launch227D_|review227D_|")
 normal=normal.replace("startswith('ROOT_E2_SOLO_EXCLUSIVE_NORMAL900_')","startswith('ROOT_E2_SOLO_EXCLUSIVE_NORMAL900_')")
 normal=normal.replace('old_W35_and_E0_source_inputs_read','old_E2_source_inputs_read').replace('normal227D_auth','normal_e2_solo_auth')
 normal=normal.replace('NORMAL900_W35_72','NORMAL900_E2').replace('current_closed227_models/e2/formal','current_closed_e2_models/e2/formal')
 normal=once(normal,"O=Path(v['owner']['root']);go=v['go'];nominal=max(g['nominal_end_epoch'] for g in go.values());assert nominal-time.time()<=900 or v['already_closed']",
  "O=Path(v['owner']['root']);go=v['go'];nominal=max(g['nominal_end_epoch'] for g in go.values())\ncurrent=json.loads((O/'OWNER_CURRENT.json').read_bytes());assert current['go']==go and set(go)=={'e2'}\nclosed=(O/'COHORT_FINAL.json').is_file() and (O/'OWNER_EXIT_ACTUAL.json').is_file()\nassert nominal-time.time()<=900 or closed,'Original signed remote900 gate not eligible'")
 normal=once(normal,"assert json.loads((O/'OWNER_IDENTITY.json').read_bytes())['pid']==v['owner']['pid']",
  "identity=json.loads((O/'OWNER_IDENTITY.json').read_bytes());assert identity['pid']==v['owner']['pid'] and identity['creation']==v['owner']['creation']")
 normal=once(normal,"formal=None\nif qualified:",'''counts=None
if qualified:
 counts=json.loads(next(x['UTF8'] for x in texts if Path(x['path']).name=='E2_SOURCE_SELECTED_FINAL_READ_COUNTS.json'))
 assert counts['source_SHA']==v['spec']['source_SHA'] and counts['source_bytes']==14615089 and counts['source_physical_byte_opens']==counts['source_decodes']==1
 assert final['source_SHA']==v['spec']['source_SHA'] and final['final']['source_SHA']==v['spec']['source_SHA']
 u=final['actual_new_PPO_updates'];assert final['new_environment_transitions']==u*480000
 assert final['final']['saved_iteration']==42822+u and final['final']['Adam_min']==final['final']['Adam_max']==859300+20*u
 assert final['final']['all_saved_tensor_and_scalar_numbers_finite'] and final['final']['original_E2_command_state_and_private_RNG_saved']
formal=None
if qualified:''')
 normal=once(normal,"original_node_terminal=t,original_node_exit=e,", "source_readcounts_before_Appclose=counts,original_node_terminal=t,original_node_exit=e,")
 write(N/'collect_e2_solo_original_formal_cost_normal900_ROOT_ONLY_once.py',normal)

 cpu=(D/'review227D_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py').read_text(encoding='utf8')
 cpu=once(cpu,'"""ROOT future NEW complete W35 output only; one CPU read/decode, old PT0."""','"""ROOT-only NEW E2 complete formal CPU;one byte/decode,old model0."""')
 cpu=once(cpu,"N=Path(__file__).resolve().parent;R=N/'reports'","from caller_common import *\nimport math")
 cpu=cpu.replace('ROOT227D','ROOT_E2_SOLO').replace('w35_72','e2').replace('NEW_W35','NEW_E2')
 cpu=once(cpu,'from launch227D_install_original_solo_W35_FIRST_UNUSED_once import verify_index','from caller_common import verify_index,INDEX,validate_original_go')
 cpu=cpu.replace("verify_index(N/'INDEX227D_FROZEN.json',args.caller_index_SHA)","verify_index(N/INDEX,args.caller_index_SHA)")
 cpu=cpu.replace('current_closed227_models/e2/formal','current_closed_e2_models/e2/formal')
 cpu=cpu.replace('343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd','b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1')
 cpu=cpu.replace('old_E0_W35_main_native_witness_PT_reads','old_E2_or_other_PT_reads').replace('649720','859300').replace('32404','42822')
 start=cpu.index(" t=ck['typed_W35_RM70_task']");end=cpu.index(" assert updates==r['final']",start)
 cpu=cpu[:start]+''' t=ck['typed_E2_original_world_PPO_task'];assert t['source_SHA']==SHA and t['source_bytes']==BYTES
 assert t['kind']==WORKER_KIND and t['source_iteration']==ITER and t['source_Adam_step']==ADAM and t['source_LR']==LR
 assert t['actor_obs']==35 and t['critic_obs']==38 and t['action_dim']==6 and t['num_envs']==20000
 assert t['policy_hz']==50 and t['feedback_hz']==100 and t['nominal_gas_N_each']==400 and t['physics_dt']==.0025 and t['TGS']==[32,4]
 assert t['domain_kind']=='E2_WORLD_MOVING_SIGNED4' and t['sampler_stage']=='world_directional_v1'
 for key in ('source_command_state_and_named_global_RNG_restored_before_one_new_physical_episode',
  'original_world_goal_point5_and_body_pure_transition_stand_mix_retained','source_STD_17Adam_and_LR_retained'):assert t[key] is True,key
 assert t['PhysX_exact_resume_claimed'] is False and t['full_E2_skill'] is False and t['full_SuperMimic'] is False
'''+cpu[end:]
 start=cpu.index("  'E1_terrain_state','E1_retained_flat_command_state')");end=cpu.index(" go=c['owner_closed']",start)
 cpu=cpu[:start]+'''  'E2_moving4_command_state'):assert name in ck,name
 cmd=ck['E2_moving4_command_state'];assert cmd['version']==1 and cmd['kind']=='E2_WORLD_MOVING_SIGNED4' and cmd['moving_yaw_cap']==4.
 fields={'is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin','world_direction','signed_yaw','phase_elapsed','vel_command_b'}
 assert set(cmd['tensors'])==fields and all(torch.is_tensor(v) and v.shape[0]==20000 for v in cmd['tensors'].values())
 assert torch.is_tensor(cmd['private_mode_rng']) and cmd['private_mode_rng'].dtype==torch.uint8 and cmd['private_mode_rng'].numel()>0
 assert r['source_readcounts_before_Appclose']['source_physical_byte_opens']==r['source_readcounts_before_Appclose']['source_decodes']==1
 assert r['original_node_terminal']['row']['returncode']==0 and r['original_node_exit']['all_own_children_waited'] and r['original_node_exit']['private_EX_released']
'''+cpu[end:]
 cpu=once(cpu,"go=c['owner_closed']['cohort_final']['go']['e2'];saved=r['formal']['epoch']",
  "go=c['owner_closed']['cohort_final']['go']['e2'];validate_original_go(go,c['run_id']);saved=r['formal']['epoch'];assert saved>=go['save_deadline']")
 cpu=cpu.replace('source_initial_LR=.00017085937500000009','source_initial_LR=.00022500000000000002')
 cpu=cpu.replace('no_full_RM70_skill_inferred','no_E2_skill_inferred')
 cpu=once(cpu,"  elif isinstance(value,dict):", "  elif isinstance(value,(float,complex)):\n   assert math.isfinite(value.real) and math.isfinite(value.imag),'Nonfinite scalar: '+path\n  elif isinstance(value,dict):")
 cpu=once(cpu," assert ck['iter']==r['formal']['saved_iteration'] and min(steps)==r['formal']['Adam_min']==r['formal']['Adam_max']",
  " assert ck['iter']==r['formal']['saved_iteration'] and min(steps)==r['formal']['Adam_min']==r['formal']['Adam_max']\n assert r['formal']['all_saved_tensor_and_scalar_numbers_finite'] and r['formal']['original_E2_command_state_and_private_RNG_saved']")
 write(N/'review_e2_solo_NEW_formal_initial_whole_CPU_ROOT_ONLY_once.py',cpu)
 names=['launch227D_install_original_solo_W35_FIRST_UNUSED_once.py','collect227D_original_W35_formal_cost_normal900_UNUSED_once.py',
  'review227D_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py','remote227D_payloads.py','remote227D_additions.py']
 put(R/'DERIVED_FROM_ACTUAL227D_SOURCE_BINDINGS.json',dict(epoch=time.time(),inputs=[ref(D/n) for n in names],original_D_INDEX=ref(D/'INDEX227D_FROZEN.json'),
  original_SPWAN_globalcwd_byte_body_reused=True,normal_original850_owner_180_node_and_rawfee_body_reused=True,
  changes='role/source/typed E2 names;actual fresh+scoped generator;V2 finite worker binding;parameterized newJ/O/GPU;new outputs;source counts persisted before close;source metadata only',
  HMAC_twofcntl_charge_writer_control_sources='Frozen E2 control unchanged;original correct sender',
  ROOT_execution_pending=True,model_asset_raw_SDK_network_Git_reads_or_calls=0))

if __name__=='__main__':
 try:main()
 except BaseException:put(R/'DERIVE_E2_CALLERS_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
