"""Finite25 config-only low-STD branch; preserve original owner/resource/account lifecycle."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent
old_branch='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8';branch=old_branch+'_LOWSTD005'
old_kind='fdn_fresh_mlp_warm_1cd_n20000_timeout8';kind=old_kind+'_lowstd005'
old_sha='386107b02983505518e1dcfb5bbdeb6f243392d390dfd48e16a61d75cb2c51e2'
overlay=D/'source_task_runtime_v4_passive_lowstd/e3_fudan_task_runtime_v1.py';raw=overlay.read_bytes();sha=hashlib.sha256(raw).hexdigest();size=len(raw)
N=D/'source_fudan_native_worker_v7_lowstd005';O=D/'source_original_owner_v7_lowstd005';stager=D/'stage_fudan_nonpt_v7_lowstd005.py'
helper_names=('prepare_stage_fudan_lowstd005_w10_once.py','dispatch_fudan_lowstd005_w10_original_owner_once.py','collect_fudan_lowstd005_w10_window_once.py')
assert not O.exists() and not stager.exists() and all(not(D/n).exists()for n in helper_names)
worker=(N/'worker_fudan_sequence_ppo_native_v1.py').read_bytes();worker_sha=hashlib.sha256(worker).hexdigest();text=worker.decode('utf8')
old_worker=(D/'source_fudan_native_worker_v5_fresh1cd_timeout8/worker_fudan_sequence_ppo_native_v1.py').read_text(encoding='utf8')
normalized=text.replace(branch,old_branch).replace(kind,old_kind).replace(sha,old_sha).replace('version=6','version=4').replace('TASK_RUNTIME_BYTES = '+str(size),'TASK_RUNTIME_BYTES = 8571').replace('core.PPOConfig(seed=int(task["seed"]), initial_std=.05)','core.PPOConfig(seed=int(task["seed"]))')
assert ast.dump(ast.parse(normalized))==ast.dump(ast.parse(old_worker)), 'Only declared branch metadata and initial_std allowed in worker'
def change(s):return s.replace(old_branch,branch).replace(old_kind,kind).replace(old_sha,sha)
files={}
old_owner=(D/'source_original_owner_v5_fresh1cd_timeout8/fudan_original_owner_v1.py').read_text(encoding='utf8');new_owner=change(old_owner)
needle='lowrise_episode_timeout_s=8.0,';assert new_owner.count(needle)==1;new_owner=new_owner.replace(needle,needle+'initial_policy_gaussian_std=.05,tracking_heightgate_enabled=False,')
old_nodes={n.name:n for n in ast.parse(old_owner).body if isinstance(n,ast.FunctionDef)};new_nodes={n.name:n for n in ast.parse(new_owner).body if isinstance(n,ast.FunctionDef)}
for name in('require','gpu','account','environment','main','qualify_waited','admit'):assert ast.dump(old_nodes[name])==ast.dump(new_nodes[name]),name
assert ast.dump(ast.parse(new_owner.replace(kind,old_kind).replace(sha,old_sha).replace('initial_policy_gaussian_std=.05,tracking_heightgate_enabled=False,','')))==ast.dump(ast.parse(old_owner))
files[O/'fudan_original_owner_v1.py']=new_owner
c=change((D/'source_original_owner_v5_fresh1cd_timeout8/fudan_worker_close_contract_v1.py').read_text(encoding='utf8')).replace('fresh_version4=','fresh_version6=')
assert c.count("intent['version']==4")==1;c=c.replace("intent['version']==4","intent['version']==6");assert c.count('==8571')==1;c=c.replace('==8571','=='+str(size))
addition="""   init=json.loads((P/'FDN_SINGLE_SOURCE_NEW_BRANCH_WARM_START.json').read_bytes());summary=f['task_summary'];tracking=summary['tracking_reward_config'];criteria=summary['low_criterion_summary'];peaks=summary['low_rollout_summary'];samples=summary['low_envs']*native['actual_native_policy_steps'];names={'height_ok','upright_ok','speed_ok','angular_ok','wheels_ok','chassis_ok','joint_good'}
   checks.update(actual_initial_std005=init['learner_config']['initial_std']==.05 and init['version']==6 and init['initial_counters']==PINNED_BASE,original_tracking_rewards_not_height_gated=tracking['height_gate_enabled']is False and set(tracking['terms'])=={'track_lin_vel','track_lin_vel_tight','track_ang_vel'} and all(t['height_gate_installed']is False for t in tracking['terms'].values()),passive_sample_clock=criteria['samples']==peaks['samples']==samples,passive_seven_counts_bounded=set(criteria['counts'])==names and all(0<=n<=samples for n in criteria['counts'].values()) and all(criteria['counts']['joint_good']<=n for n in criteria['counts'].values()),passive_not_acceptance=criteria['descriptive_only_not_acceptance']is True)
"""
assert c.count('  except Exception as exc:')==1;c=c.replace('  except Exception as exc:',addition+'  except Exception as exc:');files[O/'fudan_worker_close_contract_v1.py']=c
s=change((D/'stage_fudan_nonpt_v5_fresh1cd_timeout8.py').read_text(encoding='utf8')).replace('e3_fudan_seq_n20000_timeout8_fresh1cd_25','e3_fudan_seq_n20000_timeout8_fresh1cd_lowstd005_25');files[stager]=s
stage=(D/'prepare_stage_fudan_heightgate_w9_once.py').read_text(encoding='utf8');a=stage.index('previous=json.loads(');b=stage.index('source=dict(',a)
guard="""previous=json.loads((D/'reports/FDN_N20000_W9_LOWHEIGHTGATE_20261105_024651/CLOSED_RESULT.json').read_bytes());m=previous['metadata'];f=m['FDN_FINAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];end=m['OWNER_EXIT_ACTUAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json']
assert previous['closed']is True and end['errors']==[] and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released')) and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0 and outer['controller_pid']==1629746 and outer['original_owner_pid']==1629753
assert m['FDN_PARENT_WAIT_QUALIFICATION.json']['qualified']is True and latest==f['latest_complete_save'] and latest['sha256']=='bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2' and latest['bytes']==146247539 and f['counters']==dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000) and f['native_counters']['actual_native_policy_steps']==1200
assessment=json.loads((D/'FDN_HEIGHTGATE_CLOSED25_QUALITY_DECISION_V1.json').read_bytes());assert assessment['decision']=='KEEP_REGISTRY_V12_E3_1CD_NO_HEIGHTGATE_PROMOTION' and assessment['original_N80']['execution_qualified']is True and assessment['original_N80']['actual_original_parent_qualified']is True
"""
stage=stage[:a]+'__CURRENT_CLOSED_GUARD__\n'+stage[b:]
def namespace(s):return s.replace('FDN_N20000_W9_LOWHEIGHTGATE_','FDN_N20000_W10_LOWSTD005_').replace('native_payload_v9_lowheightgate25','native_payload_v10_lowstd00525').replace('FRESH1CD25_HEIGHTGATE_W9_','FRESH1CD25_LOWSTD005_W10_')
stage=namespace(stage).replace('source_fudan_native_worker_v6_lowheightgate',N.name).replace('source_original_owner_v6_lowheightgate',O.name).replace('stage_fudan_nonpt_v6_lowheightgate.py',stager.name).replace('source_task_runtime_v3_lowheightgate','source_task_runtime_v4_passive_lowstd').replace('a89ff5487e76a5d7256b4cf9e60d5c7292047e3d70ca681f02d8c9900f0c4c35',sha).replace('len(overlay_raw)==12723','len(overlay_raw)=='+str(size)).replace('13da06004b93c0c561bbc638e27bbfe0b93556690b91076625b06c600f17dc32',worker_sha).replace('new_window_updates=25,','new_window_updates=25,initial_policy_gaussian_std=.05,')
stage=stage.replace('__CURRENT_CLOSED_GUARD__\n',guard);files[D/helper_names[0]]=stage
files[D/helper_names[1]]=namespace((D/'dispatch_fudan_heightgate_w9_original_owner_once.py').read_text(encoding='utf8'))
files[D/helper_names[2]]=namespace((D/'collect_fudan_heightgate_w9_window_once.py').read_text(encoding='utf8'))
for path,s in files.items():ast.parse(s);compile(s,str(path),'exec')
for path,s in files.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_text(s,encoding='utf8',newline='\n')
print(json.dumps(dict(task_overlay=dict(bytes=size,sha256=sha),worker=dict(bytes=len(worker),sha256=worker_sha),files=[str(x)for x in files],source_only_AST_normalized_single_config_change=True,original_owner_math_resource_lifecycle_unchanged=True,model_SDK_SSH_GPU_C_operations=0),indent=2))
