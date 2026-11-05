"""Prepare explicit three-case low80 CLI variants, with original complete materializer and owners."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;members=['E3_LOW80_'+str(x)for x in(20260929,20260930,20261001)];prefix='FDNLOW80_CONFIRM_';kind='E3_FDN_FROZEN_LOW80_CONFIRM_V1';scope='LOW80_FIVE_POSE16_8S_FULLDR_FIRSTEPISODE_CONFIRM';files={}
s=(D/'stage_fudan_lrschedule001_frozen_original_once.py').read_text(encoding='utf8').replace('FDNLR001_FROZEN_',prefix).replace('E3_FDN_SEQUENCE_FROZEN_ORIGINAL_N80_V1',kind).replace('ORIGINAL_E3_74_PLUS_6_NORMAL',scope).replace('source_fudan_frozen_native_eval_v7_lrschedule001','source_fudan_frozen_low80_confirm_v1').replace('source_fudan_frozen_parent_v7_lrschedule001','source_fudan_frozen_low80_parent_v1').replace('gid = PREFIX + "ORIGINAL_N80_"','gid = PREFIX + "THREE_SEED_N80_"')
a=s.index('    plan = copy.deepcopy(old)');b=s.index('    workers = D / ',a)
block='''    plan=copy.deepcopy(old);template=copy.deepcopy(next(r for r in old["roles"]if r["role"]=="E3"));roles=[]
    for seed in (20260929,20260930,20261001):
        role=copy.deepcopy(template);member="E3_LOW80_"+str(seed)
        for key in ("source_iteration","source_Adam17","source_LR"):role.pop(key,None)
        role.update(role=member,expert_role="E3",seed=seed,controls=400,num_envs=80,physics_callbacks=3200,feedback_samples=800,
            worker="worker_sources/parent/worker_fudan_original_n80.py",runtime_origin=template["runtime_root"],
            runtime_root=root+"/runtimes/"+member,asset_dir=root+"/runtimes/"+member+"/runtime/assets",
            source_path=selected["path"],source_bytes=selected["bytes"],source_SHA=selected["sha256"],source_run=run,
            source_training_execution_qualified=True,expected_learner_counters=dict(counters),expected_native_counters=copy.deepcopy(native),
            kind=EVAL_KIND,purpose=EVAL_KIND,policy_input_interface="fudan_sequence_raw35_history5_latent3_clipped_mean_v1",
            evaluation_scope="LOW80_FIVE_POSE16_8S_FULLDR_FIRSTEPISODE_CONFIRM")
        roles.append(role)
    need(selected["sha256"]=="55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7"and selected["bytes"]==146247985,"Actual retained candidate55afa required")
    pose_raw=(D/"CONTRACT_PARITY_AND_POSE_V2.json").read_bytes();pose=json.loads(pose_raw)
    need(pose["body_count"]==31 and pose["coordinates"]==30 and len(pose["best_candidates"])==5 and pose["same_end_poses"]==0,"Original legal five poses only")
    plan.update(kind="SINGLE_GPU_THREE_INDEPENDENT_LOW80_FROZEN_CONFIRM_PLAN",group_id=gid,roles=roles,
        original_74_score_recomputed=False,reference_native_cohort_executed=False,source_reads_per_independent_case=1,group_source_reads_planned=3,
        low80_pose_spec=dict(bytes=len(pose_raw),sha256=hashlib.sha256(pose_raw).hexdigest()))
'''
s=s[:a]+block+s[b:]
a='"resume_runtime_contracts_v3.py"):';assert s.count(a)==1;s=s.replace(a,'"resume_runtime_contracts_v3.py", "e3_fudan_task_runtime_v1.py", "pose_cache_runtime_adapter_v4.py", "low80_confirmation_phase_v1.py"):')
s=s.replace('len(source_override) == 10','len(source_override) == 13').replace('Exactly the frozen seven worker and three parent sources required','Frozen low80 worker/phase and original parent closure sources required')
a='    ast.parse(materializer)';assert s.count(a)==1
post='''    materializer += "\\nfrom pathlib import Path\\nimport hashlib,json\\ngroup=Path("+repr(root)+")\\npose=(group/'LOW80_POSE_SPEC.json').read_bytes()\\nplan=json.loads((group/'GROUP_PLAN.json').read_bytes())\\nassert len(pose)==plan['low80_pose_spec']['bytes']and hashlib.sha256(pose).hexdigest()==plan['low80_pose_spec']['sha256']\\nfor r in plan['roles']:\\n p=Path(r['runtime_root'])/'fudan_task_pose.json';assert not p.exists();p.write_bytes(pose)\\n"
'''
s=s.replace(a,post+a)
s=s.replace('roles=["E3"], num_envs=80,','roles=[r["role"]for r in roles], num_envs=80,').replace('controls=160, seed=20260928, source_training_num_envs=20000,','controls=400, seeds=[20260929,20260930,20261001], source_training_num_envs=20000,')
a='("GROUP_PLAN.json", json.dumps(plan, indent=2, allow_nan=False).encode()),';assert s.count(a)==1;s=s.replace(a,a+'\n                           ("LOW80_POSE_SPEC.json",pose_raw),');files[D/'stage_fudan_low80_confirm_once.py']=s
s=(D/'dispatch_fudan_lrschedule001_frozen_original_once.py').read_text(encoding='utf8').replace('FDNLR001_FROZEN_',prefix).replace('E3_FDN_SEQUENCE_FROZEN_ORIGINAL_N80_V1',kind).replace('ORIGINAL_E3_74_PLUS_6_NORMAL',scope).replace('fdn_lrschedule001_frozen_outer_wait.py','fdn_low80_confirm_outer_wait.py').replace('PREFIX + "ORIGINAL_N80_"','PREFIX + "THREE_SEED_N80_"').replace('FDNLOW80_CONFIRM_ORIGINAL_N80_','FDNLOW80_CONFIRM_THREE_SEED_N80_')
s=s.replace('stage["roles"] == ["E3"]','stage["roles"] == '+repr(members)).replace('stage["controls"] == 160 and stage["seed"] == 20260928','stage["controls"] == 400 and stage["seeds"] == [20260929,20260930,20261001]').replace('len(plan["roles"]) == 1 and plan["roles"][0]["role"] == "E3"','len(plan["roles"]) == 3 and [r["role"]for r in plan["roles"]] == '+repr(members))
a=s.index('    role = plan["roles"][0]');b=s.index('    out = D / ',a);s=s[:a]+'''    for role in plan["roles"]:
        need(role["controls"]==400 and role["seed"]in(20260929,20260930,20261001)and role["role"]=="E3_LOW80_"+str(role["seed"])and role["runtime_root"]==root+"/runtimes/"+role["role"]and role["kind"]==role["purpose"]==EVAL_KIND and role["evaluation_scope"]=="LOW80_FIVE_POSE16_8S_FULLDR_FIRSTEPISODE_CONFIRM"and role["source_training_execution_qualified"]is True and dict(path=role["source_path"],bytes=role["source_bytes"],sha256=role["source_SHA"],run=role["source_run"])==stage["source"],"Each independent low80 case must bind the retained candidate and original closure")
'''+s[b:]
a="len(plan['roles'])==1 and plan['roles'][0]['role']=='E3'and plan['roles'][0]['controls']==160 and plan['roles'][0]['worker']=='worker_sources/parent/worker_fudan_original_n80.py'";assert s.count(a)==1;s=s.replace(a,"len(plan['roles'])==3 and all(r['role']=='E3_LOW80_'+str(r['seed'])and r['controls']==400 and r['worker']=='worker_sources/parent/worker_fudan_original_n80.py'for r in plan['roles'])")
s=s.replace("roles=['E3']","roles=[r['role']for r in plan['roles']]").replace('roles=["E3"]','roles=stage["roles"]').replace('planned_controls=160, planned_seed=20260928','planned_controls=400, planned_seeds=[20260929,20260930,20261001]').replace('single_E3_cardinality_variant=True','three_independent_case_cardinality_variant=True');files[D/'dispatch_fudan_low80_confirm_once.py']=s
for p,s in files.items():
 assert not p.exists();ast.parse(s);compile(s,str(p),'exec')
 for n in ast.walk(ast.parse(s)):
  if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in('controller','start')for t in n.targets)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Attribute)and n.value.func.attr=='replace'and isinstance(n.value.func.value,ast.Constant):ast.parse(n.value.func.value.value.replace('ROOT',repr('/unused/source_only')))
for p,s in files.items():p.write_text(s,encoding='utf8',newline='\n')
print('Prepared unused low80 stage/dispatch; full original runtime/static assets and exact canonical/private/finite/outerwait retained; three independent cases/3 actual future source IO; no models/SDK/SSH/GPU/C/Git')
