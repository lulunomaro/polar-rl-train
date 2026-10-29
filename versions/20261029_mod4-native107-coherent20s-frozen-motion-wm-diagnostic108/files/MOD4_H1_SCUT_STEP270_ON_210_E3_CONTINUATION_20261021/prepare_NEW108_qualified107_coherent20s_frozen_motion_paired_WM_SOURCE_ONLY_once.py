from pathlib import Path
import ast,hashlib,json,time,traceback
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';A=T/'H1_NATIVE104_FUDAN270_FROZEN_MOTION_WM_N1_V105_V2_20261029';S=T/'H1_NATIVE107_COHERENT20S_FROZEN_MOTION_WM_N1_V108_20261029';N=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def rep(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
 assert not S.exists();(S/'reports').mkdir(parents=True);(S/'code').mkdir();changes=[]
 closed=json.loads((N/'reports/CURRENT_CLOSED107_TWO_QUALIFIED20S_FORMALS_2025_TAKEOFF_COUNTER_NO_PLATFORM_SUCCESS_ACTUAL.json').read_bytes());assert closed['fully_closed'] and closed['two_NEW_formals_initial_CPU_qualified']
 for p in (A/'code').glob('*.py'):
  old=p.read_text('utf8');s=old.replace('fudan105','fudan108').replace('native105','native108').replace('NEW105','NEW108').replace('qualified104','qualified107').replace('NATIVE104','NATIVE107')
  if p.name=='fudan105_frozen_diag_driver_v1.py':
   s=s.replace('self.count<=2000','self.count<=8000').replace('fixed original5s/2000 callback cap exceeded','fixed coherent20s/8000 callback cap exceeded').replace('e.cfg.episode_length_s==5.','e.cfg.episode_length_s==20.').replace('clock/5s required','clock/20s required').replace('for control in range(500):','for control in range(2000):').replace('fixed5s_cap_censored','fixed20s_cap_censored')
   s=rep(s,'wm_before={k:v.detach().cpu().clone() for k,v in wm.state_dict().items()};paired=[]','wm_before={k:v.detach().cpu().clone() for k,v in wm.state_dict().items()};paired=[];phase_records=[]')
   needle="     paired.append((s.clone(),xi.clone(),last['executed6'][None].clone(),s1.clone(),frames.clone(),history.clone(),previous.clone()))"
   s=rep(s,needle,needle+"\n     phase_records.append(actual_phase_record(last,actual_geometry,age,control+1,list(e.scene['robot'].body_names)))")
   s=rep(s,"terminal_pre_reset=terminal,terminal_packed127_same_point=s1[0],", "task_relative_features7_for_action=bridge.mdp.relative_features(unflatten_state(s),frames)[0],actor_obs86_for_action=obs[0],packed_frame_for_action=frames[0],env_origin3_world=e.scene.env_origins[0].clone(),physics_dt_s=.0025,control_dt_s=.01,actual_phase_record=phase_records[-1],terminal_pre_reset=terminal,terminal_packed127_same_point=s1[0],")
   start=s.index(' rollouts=[]\n');end=s.index(' sensitivity=frozen_first_action_sensitivity',start)
   s=s[:start]+" validate_actual_action_windows(paired,phase_records,bridge,wm,out)\n"+s[end:]
   s=s.replace('for start in (0,160,184,192,200,208,216,240):','for start in (0,160,192,200,240,512,1000,1280,1600,1900):')
   s=rep(s,'expected_native_contract[\'changed_plant700_to_nominal400\'] is True','expected_native_contract[\'changed_plant700_to_nominal400\'] is False')
   s+='\n'+ACTUAL_WINDOWS
  elif p.name=='run_native105_frozen_flat_WM_N1_once.py':
   s=s.replace('764129c1b4c9ec4560d83423856e9f4f5867f8f18c841215f43ed5552415b89c','36059cd11b17097e82feb58fc48b259613bcf378376c4d219e20e2000baa21ef').replace('256232841','256234249')
   s=s.replace("q['max_controls']==500 and q['max_callbacks']==2000","q['max_controls']==2000 and q['max_callbacks']==8000").replace('one fixed5s case','one fixed20s case').replace('cfg.episode_length_s=5.','cfg.episode_length_s=20.')
   s=s.replace('native[\'iteration\']==16063 and publication[\'world_updates\']==160630 and publication[\'policy_updates\']==15487',"native['iteration']==17272 and publication['world_updates']==172720 and publication['policy_updates']==16632")
   s=s.replace('source_qualified104_CPU.json','source_qualified107_CPU.json').replace('exact admitted103 runtime for qualified107 output','exact admitted107 coherent20s runtime for qualified107 output')
   s=s.replace("require(env.num_envs==1 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4 and env._sim_step_counter==0,'fresh original N1 numerical clock')","require(env.num_envs==1 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4 and env._sim_step_counter==0 and env.cfg.episode_length_s==20.,'fresh coherent20s N1 numerical clock')")
   s=rep(s,"  command=install_fudan_step_request_and_command(env)","  command=install_fudan_step_request_and_command(env)\n  from private_phase_frame_v1 import STRIDE,PUBLIC_EPISODE_MAX_TICKS\n  require(STRIDE==4096 and PUBLIC_EPISODE_MAX_TICKS==2000 and command['request_control_interval']==[200,2000],'actual20s phase/frame/source binding')")
  name=p.name.replace('fudan105','fudan108').replace('native105','native108');ast.parse(s);(S/'code'/name).write_text(s,encoding='utf8');changes.append(dict(old_source=str(p),old_SHA=H(p),new_source=str(S/'code'/name),new_SHA=H(S/'code'/name)))
 s=(A/'run_NEW105_qualified104_fixed_Fudan270_motion_WM_case_UNUSED_once.py').read_text('utf8')
 s=s.replace('NEW105','NEW108').replace('FROZEN105','FROZEN108').replace('native105','native108').replace('qualified104','qualified107').replace('actual104','actual107')
 s=s.replace("N=T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028'","N=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029'")
 s=s.replace('MOD4_H1_NATIVE104_FUDAN270_FROZEN_MOTION_WM_DIAG_20261029r2','MOD4_H1_NATIVE107_FUDAN270_FROZEN_MOTION_WM_DIAG_20261029v108')
 s=s.replace('TWO104_FUDAN270_CLOSING_INITIAL_CPU_SCHEMA_REPAIRED_SOURCE_V3','TWO107_FUDAN270_20S_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1').replace('NATIVE103_seed27','NATIVE106_seed27').replace('TWO103_COMPLETE','TWO107_COMPLETE').replace("N/'payloads_v4/seed27/","N/'payloads_v2/seed27/")
 s=s.replace('MOD4_H1_FUDAN270_BANK_READER_2610v103CPUv3/seed27','MOD4_H1_FUDAN270_EPISODE20_2610v107CPUv2/seed27').replace('max_controls=500,max_callbacks=2000','max_controls=2000,max_callbacks=8000').replace('source_qualified104_CPU.json','source_qualified107_CPU.json')
 s=s.replace('p.wait(timeout=300)','p.wait(timeout=780)').replace('RUN,dict(root=ROOT),timeout=330','RUN,dict(root=ROOT),timeout=810')
 ast.parse(s)
 for node in ast.parse(s).body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('PRE','RUN') for t in node.targets):ast.parse(ast.literal_eval(node.value))
 entry=S/'run_NEW108_qualified107_fixed20s_Fudan270_motion_paired_WM_UNUSED_once.py';entry.write_text(s,encoding='utf8')
 put(S/'SOURCE108_DERIVATION_AND_NEW_PURPOSE_AST_ACTUAL.json',dict(epoch=time.time(),status='SOURCE_ONLY_UNUSED',source_model_SHA='36059cd11b17097e82feb58fc48b259613bcf378376c4d219e20e2000baa21ef',source_bytes=256234249,source_global_counters=[17272,172720,16632],new_purpose='qualified107 ownplant fixedseed20260928 frozenmean maximum20s/2000controls/8000callbacks motion+actual-action8/32WM validation and frozen32first-action sensitivity',old105_raw_model_case_not_read_or_replayed=True,source_changes=changes,entry_SHA=H(entry),all_sources_AST_passed=True,model_loads_preparation=0,SDK_GPU_remote_account_action=False,no_guaranteed_airborne_or_skill_result=True,source_runtime_reward_physics_actions_normalizers_unchanged=True))
 (S/'HANDOFF.md').write_text('NEW108 fixed qualified107 native own-plant20s frozen mean diagnostic. SOURCE ONLY until exact unused entry after fresh local exact CIM/global serial lease. Exact107 payload/qualifiedCPU/formal SHA, actual CNone/privateEX, user-light resource and original SDK/RSL/400/reset/TGS32/4/100Hz gates before model read/forward. One NEWpurpose model load, no normal86/old104/105/98 reads, no optimizer/norm/account writer. Physical episode stops on original done, maximum2000controls8000callbacks; full20s not promised when earlytermination. Maximum780s owned helper actualwait,810s remote finite; no automatic retry. Actual execution action/4callback queue/state/context/reset fields recorded. Teacherforced8/32 windows selected from actual terminal contact phase, explicitly report grounded-to-air coverage and missing phase data. Fixedcase validation is not population heldout accuracy or mechanical success. Raw/newPT/media only path/bytes/producerSHA in Git; no rendering/redecode forGit. Allsourceerrors preserved.\n',encoding='utf8')
 put(S/'FROZEN_UNUSED_SOURCE108_MOTION_WM20S_INDEX_V1.json',dict(frozen=True,unused=True,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(S.rglob('*')) if p.is_file()]))
 print(json.dumps(dict(prepared=True,folder=str(S),entry=str(entry),SHA=H(entry),no_model_or_GPU_execution=True)))
ACTUAL_WINDOWS='''def actual_phase_record(last,geometry,age,control,names):
 import torch
 forces=last['body_contact_force31'].norm(dim=-1);ids=[names.index(x) for x in ('left_wheel','right_wheel')];non=[i for i in range(len(names)) if i not in ids]
 bottoms=geometry['low'][0,:,2];loads=forces[ids];nonmax=forces[non].amax()
 air=bool((bottoms>.005).all() and (loads<=1).all() and nonmax<=1)
 return dict(control=control,age_for_action=int(age[0]),public_request_for_action=bool((age[0]>=200)&(age[0]<2000)),airborne_both_above5mm_and_unloaded=air,both_supported=bool((loads>1).all()),wheel_bottom2=json_value(bottoms),wheel_load_norm2=json_value(loads),nonwheel_max_load_N=float(nonmax),root_vz=float(last['root13_sdk_xyzw'][9]),original_counter=last['takeoff_count'],done_boundary_observed_separately=True)

def validate_actual_action_windows(paired,phases,bridge,wm,out):
 import torch
 from supermimic_wheel_leg_v3.geometry import unflatten_state as unpack
 count=len(paired);transitions=[i for i in range(1,count) if phases[i]['airborne_both_above5mm_and_unloaded']!=phases[i-1]['airborne_both_above5mm_and_unloaded']]
 selected=[]
 # Deterministic bounded phase-transition starts first, then uniform temporal
 # coverage. Missing airborne transitions stay explicitly missing.
 for i in transitions[:16]:
  for shift in (31,16,7,4,0):
   j=max(0,i-shift)
   if j not in selected:selected.append(j)
 for i in [0,160,192,200,240,512,1000,1280,1600,1900,*range(0,count,128)]:
  if i<count and i not in selected:selected.append(i)
 selected=selected[:80];rows=[]
 with torch.inference_mode():
  for horizon in (8,32):
   for start in selected:
    if start+horizon>count:continue
    window=paired[start:start+horizon];base=window[0][4]
    if not all(torch.equal(x[4],base+k) for k,x in enumerate(window)):continue
    predicted=unpack(window[0][0]);steps=[]
    for offset,row in enumerate(window,1):
     predicted=wm.step(predicted,row[2],bridge.mdp.normalize_context(row[1]));actual=unpack(row[3]);pg=bridge.mdp.wheel_geometry(predicted);ag=bridge.mdp.wheel_geometry(actual)
     error=(pg['low'][0,:,2]-ag['low'][0,:,2]).abs()
     steps.append(json_value(dict(offset=offset,predicted_root_z=predicted[0][0,2],actual_root_z=actual[0][0,2],predicted_wheel_bottom2=pg['low'][0,:,2],actual_wheel_bottom2=ag['low'][0,:,2],wheel_bottom_abs_error2=error,actual_phase=phases[start+offset-1])))
    labels=phases[start:start+horizon];air=[x['airborne_both_above5mm_and_unloaded'] for x in labels]
    rows.append(dict(start_control=start+1,horizon=horizon,start_age=phases[start]['age_for_action'],starts_grounded_not_air=not air[0],contains_actual_airborne=any(air),grounded_start_then_air=not air[0] and any(air[1:]),contains_air_to_supported=any(air[j-1] and labels[j]['both_supported'] for j in range(1,horizon)),actual_executed_actions_only=True,no_actor_resampling_or_observation_noise_in_validation=True,steps=steps))
 with (out/'NEW108_ACTUAL_ACTION_CONTIGUOUS_8_32_WM_WINDOWS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(rows=rows,actual_controls=count,max_selected_starts=80,phase_transition_count=len(transitions),phase_records=phases,scope='one NEW frozen case, no update; not population heldout accuracy',missing_airborne_windows_not_synthesized=True,no_reset_crossing_imaginary_data=True),f,indent=2,allow_nan=False)
'''
if __name__=='__main__':
 try:main()
 except BaseException:
  (S/'reports').mkdir(parents=True,exist_ok=True);put(S/'reports'/('PREPARE108_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_model_remote_or_GPU=True));raise
