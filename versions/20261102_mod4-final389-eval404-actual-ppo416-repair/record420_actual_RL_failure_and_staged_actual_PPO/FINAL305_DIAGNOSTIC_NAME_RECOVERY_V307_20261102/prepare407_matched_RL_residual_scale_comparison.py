"""Finite learnedRL counterfactual: same final389 full vs quarter residual,40 matchedpairs."""
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import time

P=Path(__file__).resolve().parent;T=P.parent
O=T/'RL389_EXACT_FINAL_INDEPENDENT_EVAL_V404_20261102'
E=T/'RL389_MATCHED_RESIDUAL_SCALE_DIAG_V407_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
 with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
assert not E.exists()
prior=json.loads((P/'reports/ANALYSIS405_ACTUAL_FINAL389_EVAL404_FACTS_AND_MANIFOLD.json').read_bytes())
assert prior['strict']==0 and prior['whole_footprint_clear']==0 and prior['terminations']['bad_orientation']==77
assert json.loads((O/'reports/ROOT404_ALL_SSH_CLOSED_FREE.json').read_bytes())['all_owned_SSH_closed']
def rename(text):
 text=text.replace(str(O),str(E)).replace(O.as_posix(),E.as_posix())
 return re.sub(r'(?<=[A-Za-z_])404(?!\d)','407',text)
E.mkdir();(E/'reports').mkdir()
shutil.copytree(O/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__','evaluate404.py'))
for name in('feedforward389.json','reference389.npz'):shutil.copyfile(O/name,E/name)
for old,new in(('contract404.py','contract407.py'),('target404_parent.py','target407_parent.py'),
 ('run404_eval_once.py','run407_eval_once.py'),('view404_actual_RL_replay.py','view407_actual_RL_replay.py'),
 ('render404_recorded_frames.py','render407_recorded_frames.py')):
 (E/new).write_text(rename((O/old).read_text('utf8')),encoding='utf8')
matched=T/'MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377_20261102/source/matched_DR377.py'
shutil.copyfile(matched,E/'source/matched_DR377.py')
text=rename((O/'source/evaluate404.py').read_text('utf8'))
needle=" real.reset()\n put('ACTUAL407_INITIAL_PHYSX_STATE.json'"
replacement=""" real.reset()
 from matched_DR377 import install_matched_pairs377
 pair_audit=install_matched_pairs377(real,TASK['seed'],max_feedback_ticks=1100)
 put('ACTUAL407_MATCHED_D0_D7_INITIAL_NOISE_ADMISSION.json',pair_audit)
 residual_scale=torch.ones((80,1),device=real.device);residual_scale[40:]=.25
 initial_policy=real.observation_manager.compute_group('policy')
 assert float((initial_policy[:40]-initial_policy[40:]).abs().max())<1e-6
 put('ACTUAL407_INITIAL_PHYSX_STATE.json'"""
assert text.count(needle)==1;text=text.replace(needle,replacement)
needle="   action=residual.action(actor(actor_input),origin_actor(actor_input),phase)"
replacement="""   baseline=residual.baseline(phase)
   learned_delta=torch.tanh(actor(actor_input)-origin_actor(actor_input))
   action=(baseline+residual_scale*learned_delta).clamp(-6,6)
   if current_control==1:
    state=goal_state()
    initial=dict(policy_max_pair_delta=float((obs['policy'][:40]-obs['policy'][40:]).abs().max()),depth_max_pair_delta=float((d[:40]-d[40:]).abs().max()),goal_max_pair_delta=float((goal[:40]-goal[40:]).abs().max()),root_relative_max_pair_delta=float((state[0][:40]-state[0][40:]).abs().max()),full_residual=learned_delta.cpu().tolist(),issued_actions=action.cpu().tolist(),paired_DR=True)
    put('ACTUAL407_FIRST_RL_INPUT_AND_SCALE_INTERVENTION.json',initial)
"""
assert text.count(needle)==1;text=text.replace(needle,replacement)
text=text.replace("kind='learned_residual_RL389',controls=controls", "kind='full_residual_RL389'if i<40 else'quarter_residual_RL389',controls=controls")
start=text.index("  comparisons=[dict(group='learned_residual_RL389'")
end=text.index("  checkpoint_identity_is_unused_lineage_only=",start)
text=text[:start]+"""  comparisons=[dict(group=name,cases=40,strict=sum(r['strict270_stable']for r in group),wholeclear=sum(r['first_flight_whole_footprint_clear']for r in group),full8s=sum(r['full_window']for r in group),orientation=sum(bool((r['episode_terminal']or{}).get('flags',{}).get('bad_orientation'))for r in group),mean_seconds=sum(r['seconds']for r in group)/40.)for name,group in(('full_residual_RL389',results[:40]),('quarter_residual_RL389',results[40:]))],
  source_command_hz=100,applied_command_hz=50,source_closedloop_recomputed=False,source_initialstate_matched=True,DR_paired=True,RL_residual=True,online_MPC=False,results=results,replay=replay,optimizer_steps=0,model_byte_reads=1,model_decodes=1,account_writes=0,
"""+text[end:]
text=text.replace("'ACTUAL407_POLICY_FEEDBACK_BINDING.json'", "'ACTUAL407_POLICY_FEEDBACK_BINDING.json'")
text=text.replace('all80_fresh_independent_DR=True','all40_fresh_paired_DR=True')
text=text.replace('independent_fresh_DR_episodes=True','new_matched_DR_episodes=True')
(E/'source/evaluate407.py').write_text(text,encoding='utf8')
task=json.loads((O/'TASK404_FROZEN.json').read_bytes())
task.update(kind='FROZEN389_RESIDUAL_RL_EVAL407',worker_SHA=H(E/'source/evaluate407.py'),
 seed=9217,evaluation_seed=9217,
 distinct_evaluation_purpose='Targeted final389RL full vs quarterresidual40 matchedDRpairs afteractual40477orientation0strict; not anothertrainingwindow',
 residual_scales=[1.,.25],matched_DR_pairs=40,common_sensor_noise=True)
put(E/'TASK407_FROZEN.json',task)
contract=(E/'contract407.py').read_text('utf8').replace("t['seed']==9137","t['seed']==9217")
(E/'contract407.py').write_text(contract,encoding='utf8')
text=(E/'source/evaluate407.py').read_text('utf8').replace("'--seed','9137'","'--seed','9217'").replace('cfg.seed=9137','cfg.seed=9217').replace('seed=9137','seed=9217')
(E/'source/evaluate407.py').write_text(text,encoding='utf8');task['worker_SHA']=H(E/'source/evaluate407.py')
(E/'TASK407_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
assert H(E/'feedforward389.json')==task['fixed_feedforward']['SHA']
assert H(E/'reference389.npz')==task['reference']['SHA']
assert H(E/'source/matched_DR377.py')==H(matched)
for path in E.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
assert 'controls==400' in text and 'physics_hz=400'in text
put(E/'INDEX407_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[
 dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(E.rglob('*'))
 if path.is_file()and'__pycache__'not in path.parts]))
put(P/'reports/STATIC407_TARGETED_RL_RESIDUAL_SCALE_PROTOCOL.json',dict(epoch=time.time(),passed=True,
 root=str(E),indexSHA=H(E/'INDEX407_SOURCE_TASK_CALLERS_FROZEN.json'),
 actual404_basis=dict(strict0=True,orientation77=True,wholeclear0=True),
 intervention='fullsamefinalactorlearnedresidual vs quarterresidual, fixedfeedforward/physics/acceptanceunchanged',
 matched377helper_exact=True,modelreads=0,SDK=0,network=0,physics=0,
 no_newtraining_window=True))
print(json.dumps(dict(passed=True,root=str(E),indexSHA=H(E/'INDEX407_SOURCE_TASK_CALLERS_FROZEN.json'))))
