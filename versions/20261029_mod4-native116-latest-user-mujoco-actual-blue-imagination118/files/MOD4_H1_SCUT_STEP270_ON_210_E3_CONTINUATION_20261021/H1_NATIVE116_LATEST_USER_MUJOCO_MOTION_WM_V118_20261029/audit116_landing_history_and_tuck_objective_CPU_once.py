"""Source-only analytical endpoint counterexample, not a feasible trajectory proof."""
from pathlib import Path
import ast,hashlib,json,os,sys,time
import torch
S=Path(__file__).resolve().parent;T=S.parent;B=T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/payloads/seed27/source'
assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not torch.cuda.is_initialized();torch.set_num_threads(2)
sys.path.insert(0,str(B));import direct_wheel_height_command_reward_v1 as reward
source=(B/'direct_wheel_height_command_reward_v1.py').read_text(encoding='utf8');adapter=(B/'mod4_fudan_contact_phase_reward_candidate_v2.py').read_text(encoding='utf8')
assert 'original_leg_length_flight_height_bonuses_not_selected=True' in adapter
low=torch.tensor([[[.65,-.24,.27],[.65,.18,.27]]]*2);high=low+torch.tensor([.14,.06,.13]);forces=torch.full((2,2),1000.)
mode=reward.modes(low,high,forces,torch.full((2,),.75))
m=dict(wheel_bottom2=low[...,2],world_velocity3=torch.zeros(2,3),world_angular_velocity3=torch.zeros(2,3),request_active=torch.ones(2),heading_cos=torch.ones(2),upright_cos=torch.ones(2),root_y=torch.zeros(2),history_valid_takeoff=torch.tensor([False,True]),history_valid_airborne_cross=torch.tensor([False,True]))
out=reward.evaluate(m,mode,torch.zeros(2),torch.ones(2));assert out['total'][0].item()==out['total'][1].item()
node=next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef) and x.name=='evaluate');keys=sorted({x.slice.value for x in ast.walk(node) if isinstance(x,ast.Subscript) and isinstance(x.value,ast.Name) and x.value.id=='m' and isinstance(x.slice,ast.Constant)})
report=dict(epoch=time.time(),source_SHA=hashlib.sha256(source.encode()).hexdigest(),adapter_SHA=hashlib.sha256(adapter.encode()).hexdigest(),analytical_same_supported_top_endpoint=True,
    history_labels=['no qualified takeoff/cross established','qualified takeoff/cross in past'],same_current_reward_inputs=True,total=[float(x) for x in out['total']],selected_terms={k:[float(x) for x in v] for k,v in out['selected_terms'].items()},
    evaluated_measurement_keys=keys,qualified_takeoff_or_cross_history_not_consumed=True,current116_tuck_extension_terms_diagnostic_only=True,
    proves_reward_endpoint_does_not_distinguish_path=True,does_not_prove_quasistatic_270mm_climb_is_physically_possible=True,not_a_saved_physical_trajectory=True,not_unique_failure_cause=True,
    no_checkpoint_raw_SDK_GPU_physics_network_or_optimizer=True,currently_no_new_H1_learning_started=True,
    new_before_use_acceptance_gap='Need verify valid jump/clearance/cross/landing process alignment, not just endpoint reward bounds and approach monotonicity. No scripted joint/force trajectory is authorized by this source audit.')
with (S/'reports/USER_JUMP_VS_STANDING_ENDPOINT_HISTORY_COUNTEREXAMPLE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(total=report['total'],same_despite_history=True,consumed_keys=keys)))
