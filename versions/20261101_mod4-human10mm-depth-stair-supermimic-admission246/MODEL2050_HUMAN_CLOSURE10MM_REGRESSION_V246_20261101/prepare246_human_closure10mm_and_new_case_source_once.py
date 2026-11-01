"""New independent eval revision: user changes only closure reset2->10mm."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True);S=N/'source';S.mkdir(exist_ok=True)
B=T/'MODEL2050_NEW240_CLOSED_MEAN_REGRESSION_SOURCE_V242_20261101'
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
assert not(N/'INDEX246_NEW240_MEAN_REGRESSION_FROZEN.json').exists()
contract=(B/'source/contract242.py').read_text('utf8').replace('NEW242_QUALIFIED240_MEAN_STAND_FORWARD_REVERSE_LITERAL_JUMP_REGRESSION','NEW246_HUMAN_CLOSURE10MM_QUALIFIED240_MEAN_GROUND_JUMP_REGRESSION')
contract=replace(contract,"assert t['kind']==KIND and t['num_envs']==10", "assert t['closure_threshold_m']==.01 and t['mimic_threshold_rad']==.01 and t['human_requested_closure_change']\n assert t['kind']==KIND and t['num_envs']==10")
(S/'contract246.py').write_text(contract,encoding='utf8')
worker=(B/'source/evaluate242_NEW240_mean_regression_UNUSED_once.py').read_text('utf8').replace('242','246')
worker=replace(worker,'sdk.configure(cfg)','sdk.configure(cfg);cfg.terminations.closure.params[\'threshold\']=TASK[\'closure_threshold_m\']')
worker=replace(worker,"real.cfg.terminations.closure.params['threshold']==.002","real.cfg.terminations.closure.params['threshold']==.01")
needle=" put('ACTUAL246_ORIGINAL_MIXED_REWARD_AND_PLANT.json',dict(passed=True,binding=real.binding_receipt(),spring=real.spring_pressure_recipe(),ground_mask=real._mixed209_flat.cpu().tolist(),fresh10env_DR_not_checkpoint_slice=True,controlled_cues_only_no_state_or_force_injection=True,original_guards_unchanged=True))"
new=""" base_binding=real.binding_receipt()
 base_binding['all_physical_guards_unchanged']=False
 base_binding['original_jump_binding']['physical_guard_terminations_are_MOD4_not_Fudan_original_and_unchanged']=False
 base_binding['human_selected_closure_reset_threshold_m']=.01
 put('ACTUAL246_ORIGINAL_MIXED_REWARD_AND_PLANT.json',dict(passed=True,binding=base_binding,spring=real.spring_pressure_recipe(),ground_mask=real._mixed209_flat.cpu().tolist(),fresh10env_DR_not_checkpoint_slice=True,controlled_cues_only_no_state_or_force_injection=True,only_human_closure_reset_threshold_changed=True,actual_closure_threshold_m=real.cfg.terminations.closure.params['threshold'],actual_mimic_threshold_rad=real.cfg.terminations.mimic.params['threshold'],reward_unchanged=True,mechanical_closed_loop_constraints_unchanged=True))"""
worker=replace(worker,needle,new)
worker=replace(worker,"  pending['flags']={n:bool(real.termination_manager.get_term(n)[i])for n in names};return value", "  pending['closure_error_m']=float(real._mod4_closure_now[i])\n  pending['flags']={n:bool(real.termination_manager.get_term(n)[i])for n in names};return value")
worker=replace(worker,"result=dict(name=cue['name'],command=cue,controls=count", "result=dict(actual_closure_reset_threshold_m=.01,actual_terminal_closure_error_m=frames[-1]['closure_error_m'],sampled_max_closure_error_m=max(f['closure_error_m']for f in frames),sampled_closure_error_m=[f['closure_error_m']for f in frames],name=cue['name'],command=cue,controls=count")
(S/'evaluate246_NEW240_mean_regression_UNUSED_once.py').write_text(worker,encoding='utf8')
parent=(B/'source/target242_single_N1_parent_UNUSED.py').read_text('utf8').replace('242','246')
(S/'target246_single_N1_parent_UNUSED.py').write_text(parent,encoding='utf8')
for file in('wheel_geometry220.py','flight_evidence220.py'):(S/file).write_bytes((B/'source'/file).read_bytes())
caller=(B/'run_ROOT242_NEW240_mean_regression_once.py').read_text('utf8').replace('242','246')
caller=replace(caller,"pattern='run_ROOT246_|", "pattern='run_ROOT246_|run_ROOT242_|collect243_|")
caller=replace(caller,"  actual_closed240_qualification=q,source240_formal_CPU_actual_passed=True,", "  closure_threshold_m=.01,mimic_threshold_rad=.01,human_requested_closure_change=True,actual_closed240_qualification=q,source240_formal_CPU_actual_passed=True,")
(N/'run_ROOT246_NEW240_mean_regression_once.py').write_text(caller,encoding='utf8')
files=sorted(S.glob('*.py'))+[N/'run_ROOT246_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:ast.parse(p.read_text('utf8'),filename=str(p))
p=S/'contract246.py';sp=importlib.util.spec_from_file_location('new246_contract',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
C=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/reports';q=m.qualified240(json.loads((C/'ROOT240V2_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes()),json.loads((C/'ROOT240V2_NEW_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes()))
t=dict(kind=m.KIND,closure_threshold_m=.01,mimic_threshold_rad=.01,human_requested_closure_change=True,num_envs=10,controls_per_case_max=500,controls_max=2000,actual_closed240_qualification=q,model_SHA=q['SHA'],model_bytes=q['bytes'],model_path=q['path'],model_iteration=q['iteration'],actual_17Adam_step=q['Adam17'],source_parent_SHA=m.PARENT_SHA,source240_formal_CPU_actual_passed=True,policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',current_authority_binding={'kind':'FRESH_CNONE'},model_byte_reads=1,model_decodes=1,model_copies=0,no_optimizer_or_training_or_budget_write=True,training_reward_changed=False,cases=[dict(name=n,env=e)for n,e in[('standing',0),('forward',0),('reverse',0),('literal_jump',1)]])
assert m.validate_task(t);rejects=0
for k,v in[('closure_threshold_m',.002),('mimic_threshold_rad',.05),('human_requested_closure_change',False),('training_reward_changed',True)]:
 bad=dict(t);bad[k]=v
 try:m.validate_task(bad)
 except AssertionError:rejects+=1
 else:raise AssertionError(k)
report=R/'ROOT246_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json'
put(report,dict(passed=True,epoch=time.time(),AST_files=len(files),new_Task_rejects=rejects,old_fixture_replays=0,model_raw_SDK_remote_GPU=0,qualified_model_metadata=q,human_exact='还有闭链误差调整到10mm终止，因为华南虎和复旦都没有对这个进行约束',scope='Only runtime per-environment closure reset threshold .002->.01. Original reward/actor/physical closed joints/solver/PD/DR/mimic .01 unchanged. SDK readback and real eval pending.'))
idx=N/'INDEX246_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(epoch=time.time(),kind='FROZEN_HUMAN_CLOSURE10MM_NEW_REGRESSION_SOURCE',qualified_model=q,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files+[report]],no_learning_or_GO=True,model_read_decode_admission_max=1,old244_raw_replay=0,actual_SDK_pending=True))
print(json.dumps(dict(passed=True,INDEX_SHA=H(idx),AST=len(files),rejects=rejects,old_models_or_SDK_reads=0)))
