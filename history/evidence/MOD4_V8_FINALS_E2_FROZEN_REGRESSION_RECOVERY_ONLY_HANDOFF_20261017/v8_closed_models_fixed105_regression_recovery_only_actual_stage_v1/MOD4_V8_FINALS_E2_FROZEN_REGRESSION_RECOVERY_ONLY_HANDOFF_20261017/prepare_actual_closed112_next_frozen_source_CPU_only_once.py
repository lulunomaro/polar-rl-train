"""Prepare the actual latest closed112 source for independent frozen comparison; no target access."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,sys,time,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;G=D.parent/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017';Q=G/'e2_closed109_frozen_prepared_v6/payload';R=D/'reports';E=D/'e2_latest_closed112_frozen_source_CPU_v1';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert not E.exists();E.mkdir()
proof=json.loads((R/'TWO_CLOSED_FINALS_FULL_CPU_NEW_HEALTHY72_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());row=proof['source_models']['e2']['final_model'];assert row['updates']==112 and row['Adam_step']==666780 and row['SHA']=='ca6fc2662d5bfe4d33ad63b370389504961a3c2500b4b476c1c527b17b12b2be';source=Path(row['local_path']);assert H(source)==row['SHA'];dst=E/'E2_actual_latest_closed112.pt';shutil.copy2(source,dst);assert H(dst)==row['SHA'];ck=torch.load(dst,map_location='cpu',weights_only=False)
guard=(Q/'e2_closed109_source_guard_v1.py').read_text('utf8').replace('653820','666780').replace("==109","==112").replace('E2_closed109','E2_closed112').replace('bccaf44227c286fee70518b61e3e3ead154c47caf2d5865d80b29b69716fdb33',row['SHA']);p=E/'e2_closed112_source_guard_CPU_v1.py';ast.parse(guard);p.write_text(guard,encoding='utf8',newline='\n')
single=(Q/'e2_closed109_single35_v2.py').read_text('utf8').replace('e2_closed109_source_guard_v1','e2_closed112_source_guard_CPU_v1').replace('bccaf44227c286fee70518b61e3e3ead154c47caf2d5865d80b29b69716fdb33',row['SHA']);p=E/'e2_closed112_single35_CPU_v1.py';ast.parse(single);p.write_text(single,encoding='utf8',newline='\n');sys.path[:0]=[str(E),str(Q)]
from e2_closed112_source_guard_CPU_v1 import validate_E2_source
from e2_closed112_single35_CPU_v1 import Single35
rng=torch.get_rng_state().clone();validate_E2_source(ck);controller=Single35(dst,88,'cpu');assert controller.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();bad=[]
for name in ('wrong_Adam_step','wrong_update_scope','wrong_phase','wrong_kind','wrong_yaw_cap','wrong_35input','wrong_38critic','nonfinite_STD','negative_STD'):
 x=copy.deepcopy(ck)
 if name=='wrong_Adam_step':next(iter(x['optimizer_state_dict']['state'].values()))['step']+=1
 elif name=='wrong_update_scope':x['owned_phase_complete_updates']=109
 elif name=='wrong_phase':x['owned_phase']='native'
 elif name=='wrong_kind':x['E2_moving4_command_state']['kind']='E1'
 elif name=='wrong_yaw_cap':x['E2_moving4_command_state']['moving_yaw_cap']=2.
 elif name=='wrong_35input':x['actor_state_dict']['mlp.0.weight']=x['actor_state_dict']['mlp.0.weight'][:,:34]
 elif name=='wrong_38critic':x['critic_state_dict']['mlp.0.weight']=x['critic_state_dict']['mlp.0.weight'][:,:37]
 elif name=='nonfinite_STD':x['actor_state_dict']['distribution.std_param'][0]=float('nan')
 else:x['actor_state_dict']['distribution.std_param'][0]=-1.
 try:validate_E2_source(x)
 except AssertionError:bad.append(name)
 else:raise AssertionError(name)
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
recipe=json.loads((Q/'E2_CLOSED109_SIGNED4_RECIPE_EXACT_CPU_V1.json').read_bytes());recipe['source']=dict(path=str(dst),bytes=dst.stat().st_size,SHA=H(dst),all17Adam666780=True,updates112=True);recipe['source_scope']='Actual latest closed112, separate guard/namespace from archived closed109 baseline';(E/'E2_CLOSED112_EXACT_SAME_SIGNED4_RECIPE_CPU_PREPARED.json').write_text(json.dumps(recipe,indent=2),encoding='utf8')
out=dict(epoch=time.time(),passed_source_controller_CPU_only=True,source=recipe['source'],source9STD_CPU_exact_RNG_unchanged_no_CUDA=True,negative_cases=bad,baseline_closed109_full1500_3of64_not_promoted=True,same_signed4_worldVpoint5_88env_white_v3_seed60928_recipe=True,source_guard_and_declared_exact_Adam_only_changed_no_reward_physics_DR_command_change=True,static_runtime_reference=dict(path=str(Q),manifest_SHA=H(Q/'E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V6.json')),no_complete_target_package_upload_Task_native120_full1500_or_skill_result_yet=True,next_requires_fresh_exact249resource_targetCPU_unused_native120_and_full1500_with_all_original_guards=True,matched_initial_states_not_assumed_must_actual_compare=True)
with (R/'E2_LATEST_CLOSED112_SAME_RECIPE_FROZEN_SOURCE_CONTROLLER_CPU_PREPARED.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(CPU_source112=True,SHA=row['SHA'],Adam=666780,negative_cases=len(bad),GPU_not_dispatched=True)))
