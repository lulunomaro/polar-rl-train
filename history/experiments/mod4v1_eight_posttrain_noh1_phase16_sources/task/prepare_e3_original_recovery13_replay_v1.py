"""Newsource-only actual-performance replay plan, originalE3 RecoveryPhase credited event, notnewgrade.
160controls3.2s spans original300ageunits3s request; full20k/restoration/newsourcepurpose/noPPO.
"""
from pathlib import Path
import ast,json,hashlib,textwrap
R=Path(__file__).resolve().parent;S=R/'E3_actual_fullrestore_native24';D=R/'E3_original_recovery13_replay_v1';assert not D.exists();D.mkdir();w=(S/'evaluate_e3_1cd_native24_no_update_v1.py').read_text(encoding='utf-8')
w=w.replace('MOD4V1_E3_1CD_N20K_FULLRESTORE_NATIVE34_EVAL_ONLY_V1','MOD4V1_E3_1CD_RECOVERY13_SKILL160_EVAL_ONLY_V1').replace('NEW_E3_1CD_FULLRESTORE_NATIVE34_','NEW_E3_1CD_RECOVERY13_SKILL160_').replace("task['controls']==24","task['controls']==160").replace('E3_1CD_NATIVE34_EVAL_ONLY_NO_UPDATE','E3_1CD_RECOVERY13_SKILL160_NO_UPDATE').replace('E3_N20K_FULLRESTORE_BEFORE_NATIVE34.json','E3_RECOVERY13_FULLRESTORE_BEFORE_REPLAY.json').replace('E3_N20K_FULLRESTORE_NATIVE34_COMPLETE.json','E3_RECOVERY13_SKILL160_COMPLETE.json').replace('E3_N20K_FULLRESTORE_ORIGINAL_ERROR.json','E3_RECOVERY13_SKILL160_ORIGINAL_ERROR.json')
lines=w.splitlines(keepends=True);hits=[i for i,l in enumerate(lines)if l.strip()=='with torch.inference_mode():'];assert len(hits)==1;a=hits[0];pref=lines[a][:len(lines[a])-len(lines[a].lstrip())]
def block(text,p):return ''.join(p+x+'\n'if x else'\n'for x in textwrap.dedent(text).strip('\n').splitlines())
setup=block('''
phase_runtime=env.recovery
initial_episode=env._sensor_mild.episode.clone()
initial_recipe=phase_runtime.recipe.clone()
original_credit_seen=torch.zeros(20000,dtype=torch.bool,device=env.device)
original_peak=phase_runtime.peak.clone()
first_age=torch.zeros(20000,dtype=torch.long,device=env.device)
max_stable=torch.zeros_like(first_age)
first_credit_age=torch.full_like(first_age,-1)
first_terminated=torch.zeros_like(original_credit_seen)
first_timeout=torch.zeros_like(original_credit_seen)
old_phase_update=phase_runtime.update
old_compute_term=env.termination_manager.compute
def observe_original_phase(gravity_z,root_speed,angular_speed):
 old_phase_update(gravity_z,root_speed,angular_speed)
 mask=env._sensor_mild.episode==initial_episode
 event=mask&phase_runtime.credited&~original_credit_seen
 first_credit_age[event]=phase_runtime.age[event]
 original_credit_seen[mask]|=phase_runtime.credited[mask]
 original_peak[mask]=torch.maximum(original_peak[mask],phase_runtime.peak[mask])
 first_age[mask]=phase_runtime.age[mask]
 max_stable[mask]=torch.maximum(max_stable[mask],phase_runtime.stable[mask])
def observe_original_term(*aa,**kk):
 result=old_compute_term(*aa,**kk)
 mask=env._sensor_mild.episode==initial_episode
 first_terminated[mask]|=env.termination_manager.terminated[mask]
 first_timeout[mask]|=env.termination_manager.time_outs[mask]
 return result
phase_runtime.update=observe_original_phase
env.termination_manager.compute=observe_original_term
''',pref)
lines[a]=setup+lines[a];w=''.join(lines);w=w.replace('for _ in range(24):','for control_index in range(160):')
a='assert int(env._integrated_contact.tick)-before==8 and int(env._feedback_100hz_tick)-fb==2';matches=[l for l in w.splitlines()if l.strip()==a];assert len(matches)==1;line=matches[0];pfx=line[:len(line)-len(line.lstrip())];w=w.replace(line,line+'\n'+pfx+"if control_index==23:put('NATIVE24_PART_OF_RECOVERY13_CASE.json',dict(passed=True,controls=24,physics=192,feedback=48,optimizer_updates=0,source_SHA=SHA))")
w=w.replace('int(env._integrated_contact.tick)-tick==192 and int(env._feedback_100hz_tick)-feedback==48','int(env._integrated_contact.tick)-tick==1280 and int(env._feedback_100hz_tick)-feedback==320').replace("{'legs':192,'wheels':192}","{'legs':1280,'wheels':1280}").replace('controls=24,physics_callbacks=192,feedback_samples=48,actor_calls=24','controls=160,physics_callbacks=1280,feedback_samples=320,actor_calls=160').replace('skill_evaluation_or_expert_graduation=False','skill_evaluation=True,expert_graduation=False')
a='counts=cache.receipt();assert counts[\'source_physical_byte_opens\']==counts[\'source_decodes\']==1 and all(v==0 for v in forbidden.values())';matches=[l for l in w.splitlines()if l.strip()==a];assert len(matches)==1;line=matches[0];pfx=line[:len(line)-len(line.lstrip())]
summary=block('''
phase_runtime.update=old_phase_update
env.termination_manager.compute=old_compute_term
recipe_rows=[]
for recipe_id in range(13):
 ids=initial_recipe==recipe_id
 n=int(ids.sum())
 credit=original_credit_seen[ids]
 peaks=original_peak[ids]
 ages=first_credit_age[ids&original_credit_seen]
 recipe_rows.append(dict(recipe=recipe_id,num_envs=n,initial_request_recipe=recipe_id!=12,original_credited_count=int(credit.sum()),original_credited_and_no_first_termination_count=int((ids&original_credit_seen&~first_terminated).sum()),first_terminated_count=int(first_terminated[ids].sum()),first_timeout_count=int(first_timeout[ids].sum()),first_age_max=int(first_age[ids].max()),max_original_stable_age=int(max_stable[ids].max()),original_peak_min=float(peaks.min()),original_peak_mean=float(peaks.mean()),original_peak_max=float(peaks.max()),first_credit_age_min=int(ages.min())if ages.numel()else None,first_credit_age_max=int(ages.max())if ages.numel()else None))
put('ORIGINAL_E3_RECOVERY13_FIRST_EPISODE_FACTS.json',dict(kind='ORIGINAL13RECIPES_PHASE_CREDIT_OBSERVATION_NOT_NEW_GRADUATION_GATE',source_SHA=SHA,num_envs=20000,controls=160,seconds=3.2,policy_hz=50,public_phase_age_hz=100,original_request_age_limit=300,original_good_gravity_z_less_than=-.984807753,original_good_speed_m_s_less_than=.03,original_good_ang_rad_s_less_than=.2,original_credit_stable_age_at_least=50,source_phase_SHA='5883e0461d667ed474c29f1a07f78b88d4a8ee07f9570ae9c9df81a6584319a7',rows=recipe_rows,first_episode_identity_not_reset_stitched=True,no_new_RNG_action_mode_physics_reward_or_grad_threshold=True,does_not_infer_full_expert_graduation=True))
''',pfx)
w=w.replace(line,line+'\n'+summary.rstrip('\n'));ast.parse(w);(D/'evaluate_e3_1cd_recovery13_no_update.py').write_text(w,encoding='utf-8')
p=(S/'supervise_e3_1cd_no_update_v1.py').read_text(encoding='utf-8').replace('MOD4V1_E3_1CD_N20K_NATIVE34_NOUPDATE_','MOD4V1_E3_1CD_RECOVERY13_SKILL160_').replace("plan['controls']==24","plan['controls']==160").replace('MOD4V1_E3_1CD_N20K_FULLRESTORE_NATIVE34_EVAL_ONLY_V1','MOD4V1_E3_1CD_RECOVERY13_SKILL160_EVAL_ONLY_V1').replace('num_envs=20000,controls=24','num_envs=20000,controls=160').replace('evaluate_e3_1cd_no_update.py','evaluate_e3_1cd_recovery13_no_update.py').replace('E3_N20K_FULLRESTORE_NATIVE34_COMPLETE.json','E3_RECOVERY13_SKILL160_COMPLETE.json').replace('E3_N20K_FULLRESTORE_ORIGINAL_ERROR.json','E3_RECOVERY13_SKILL160_ORIGINAL_ERROR.json').replace('E3_1CD_N20K_NATIVE34_NOUPDATE_FINISHED','E3_1CD_RECOVERY13_SKILL160_FINISHED').replace('expert_graduation_or_full_skill_evaluation=False','expert_graduation=False,original_recovery13_skill_observed=True');ast.parse(p);(D/'supervise_e3_1cd_recovery13_no_update.py').write_text(p,encoding='utf-8')
s=(S/'prepare_dispatch_1cd_no_update_once.py').read_text(encoding='utf-8').replace("LOCAL=Path(__file__).resolve().parent","LOCAL=Path(__file__).resolve().parent").replace('MOD4V1_E3_1CD_N20K_NATIVE34_NOUPDATE_','MOD4V1_E3_1CD_RECOVERY13_SKILL160_').replace('NEW_E3_1CD_FULLRESTORE_NATIVE34_','NEW_E3_1CD_RECOVERY13_SKILL160_').replace('E3_1CD_N20K_NATIVE34_EVAL_ONLY_NEW_PURPOSE','E3_1CD_RECOVERY13_SKILL160_NEW_PURPOSE').replace("('evaluate_e3_1cd_no_update.py',LOCAL/'evaluate_e3_1cd_native24_no_update_v1.py')","('evaluate_e3_1cd_recovery13_no_update.py',LOCAL/'evaluate_e3_1cd_recovery13_no_update.py')").replace("('supervise_e3_1cd_no_update.py',LOCAL/'supervise_e3_1cd_no_update_v1.py')","('supervise_e3_1cd_recovery13_no_update.py',LOCAL/'supervise_e3_1cd_recovery13_no_update.py')").replace('num_envs=20000,controls=24','num_envs=20000,controls=160').replace("B/'supervise_e3_1cd_no_update.py'","B/'supervise_e3_1cd_recovery13_no_update.py'").replace('E3_1CD_EVAL_ONLY','E3_1CD_RECOVERY13_SKILL160').replace('E3_1cd_fullrestore_native24_dispatch_','E3_original_recovery13_skill160_dispatch_');ast.parse(s);(D/'prepare_dispatch_recovery13_once.py').write_text(s,encoding='utf-8')
# Cross-check exact full basenames parentreads workerputs, no global role-substring rewrite.
wat=ast.parse(w);pat=ast.parse(p);puts={n.args[0].value for n in ast.walk(wat)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='put'and n.args and isinstance(n.args[0],ast.Constant)};assert 'E3_RECOVERY13_SKILL160_COMPLETE.json'in puts and 'E3_RECOVERY13_SKILL160_ORIGINAL_ERROR.json'in puts and 'NATIVE24_PART_OF_RECOVERY13_CASE.json'in puts
v={'kind':'SOURCE_ONLY_ORIGINAL_E3_RECOVERY13_FIRST_EPISODE_PERFORMANCE_REPLAY','controls':160,'physics':1280,'feedback':320,'seconds':3.2,'original_request_age_100hz_units':300,'source_SHA':'1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8','scope':'Ownoriginal97 RecoveryEnv+phase13/7+owngeometry/privateRNG/full20krestore/ONEnewreset/new2c-bae, originalcreditedeventwithfirst-episodeidentity,noreward/action/physicschanges, noaggregategraduationgate','newpurpose_distinct_from_old_native24':True,'model_reads_SDK_budget_actions_by_preparer':0,'worker_basename': 'evaluate_e3_1cd_recovery13_no_update.py','parent_basename':'supervise_e3_1cd_recovery13_no_update.py','worker_puts':sorted(puts),'files':[{'relative':x.name,'bytes':x.stat().st_size,'SHA':hashlib.sha256(x.read_bytes()).hexdigest()}for x in D.glob('*.py')]};(D/'SOURCE_ONLY_INDEX.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
