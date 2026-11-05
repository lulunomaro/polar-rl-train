"""New explicit three-process low80 scope. Preserve pi math, original resource owner and close."""
from pathlib import Path
import ast,copy,hashlib,json
D=Path(__file__).resolve().parent;S=D/'source_fudan_frozen_low80_confirm_v1';P=D/'source_fudan_frozen_low80_parent_v1';old=D/'source_fudan_frozen_native_eval_v7_lrschedule001';op=D/'source_fudan_frozen_parent_v7_lrschedule001';R=D.parent/'mod4v1_supermimic_bptt_20261102'
K='E3_FDN_FROZEN_LOW80_CONFIRM_V1';scope='LOW80_FIVE_POSE16_8S_FULLDR_FIRSTEPISODE_CONFIRM';members=['E3_LOW80_'+str(s)for s in(20260929,20260930,20261001)]
assert not P.exists()and not(S/'fudan_frozen_eval_safe.py').exists()
raw_overlay=(D/'source_task_runtime_v4_passive_lowstd/e3_fudan_task_runtime_v1.py').read_bytes();assert len(raw_overlay)==12745 and hashlib.sha256(raw_overlay).hexdigest()=='a84823a59731f9cd805aa0bf6a91af10e0e26e729652df39b8cbd17dc6def3f9'
phase=(S/'low80_confirmation_phase_v1.py').read_bytes();phase_tree=ast.parse(phase.decode('utf8'));original_tree=ast.parse(raw_overlay.decode('utf8'))
up=next(n for n in ast.walk(phase_tree)if isinstance(n,ast.FunctionDef)and n.name=='update');old_up=next(n for n in ast.walk(original_tree)if isinstance(n,ast.FunctionDef)and n.name=='update')
class StripEndpointCopies(ast.NodeTransformer):
 def visit_Expr(self,n):
  v=n.value
  if isinstance(v,ast.Call)and isinstance(v.func,ast.Attribute)and v.func.attr=='copy_'and isinstance(v.func.value,ast.Attribute)and v.func.value.attr in('low80_last_flags','low80_last_metrics'):return None
  return self.generic_visit(n)
assert ast.dump(StripEndpointCopies().visit(copy.deepcopy(up)))==ast.dump(old_up),'Only two passive endpoint copy expressions allowed in update'
files={S/'low80_confirmation_phase_v1.py':phase,S/'worker_fudan_original_n80.py':(S/'worker_fudan_original_n80.py').read_bytes(),S/'e3_fudan_task_runtime_v1.py':raw_overlay,S/'pose_cache_runtime_adapter_v4.py':(R/'payload_a1_v6_small_source/source/pose_cache_runtime_adapter_v4.py').read_bytes()}
for name in('frozen_sequence_mean.py','n80_gpu_capacity.py','launch_storage_contract.py','app_close_semantics_v6.py','resume_runtime_contracts_v3.py'):files[S/name]=(old/name).read_bytes()
s=(old/'fudan_frozen_eval_safe.py').read_text(encoding='utf8').replace('E3_FDN_SEQUENCE_FROZEN_ORIGINAL_N80_V1',K).replace('ORIGINAL_E3_74_PLUS_6_NORMAL',scope)
s=s.replace('role="E3"','role=task["role"]').replace('final["role"] == "E3"','final["role"] == task["role"]').replace('controls=160','controls=400').replace('controls_expected=160','controls_expected=400').replace('controls_completed == 160','controls_completed == 400').replace('seed=20260928','seed=task["seed"]')
a='    for key, expected in fixed.items():';assert s.count(a)==1;s=s.replace(a,'    need(task["seed"] in (20260929,20260930,20261001) and task["role"] == "E3_LOW80_"+str(task["seed"]), "Explicit independent case/seed binding differs")\n'+a)
a='value["members"] == ["E3"]';assert s.count(a)==1;s=s.replace(a,'value["members"] == task["eval_members"] and len(value["members"]) == 3 and task["role"] in value["members"]');files[S/'fudan_frozen_eval_safe.py']=s.encode('utf8');safe_sha=hashlib.sha256(files[S/'fudan_frozen_eval_safe.py']).hexdigest()
q=(op/'fudan_eval_parent_wait_contract_v1.py').read_text(encoding='utf8').replace('E3_FDN_SEQUENCE_FROZEN_ORIGINAL_N80_V1',K).replace('FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V7_LRSCHEDULE001','FDN_LOW80_3SEED_ACTUAL_WAIT_QUALIFICATION_V1').replace('ORIGINAL_E3_74_PLUS_6_NORMAL',scope)
old_safe_sha=hashlib.sha256((old/'fudan_frozen_eval_safe.py').read_bytes()).hexdigest();assert q.count(old_safe_sha)==2;q=q.replace(old_safe_sha,safe_sha).replace('role="E3"','role=t["role"]').replace('controls=160','controls=400').replace('controls_expected=160','controls_expected=400').replace('seed=20260928','seed=t["seed"]').replace('physics_callbacks=1280','physics_callbacks=3200').replace('feedback_samples=320','feedback_samples=800').replace('seconds=3.2','seconds=8.0').replace('"legs": 1280, "wheels": 1280','"legs": 3200, "wheels": 3200').replace('("final", final, 160)','("final", final, 400)')
a='original_recovery_requests=74, normal_envs_excluded_from_recovery_denominator=6,\n            new_lowrise_8second_task_enabled=False,';assert q.count(a)==1;q=q.replace(a,'low80_request_denominator=80, normal_envs_excluded_from_low_denominator=0,\n            new_lowrise_8second_task_enabled=True, original_74_score_recomputed=False,')
a='original_recovery_request_denominator=74, normal_envs_excluded=6,\n            no_reset_stitched_credit=True, new_lowrise_8second_task_evaluated=False';assert q.count(a)==1;q=q.replace(a,'low80_request_denominator=80, normal_envs_excluded=0,\n            no_reset_stitched_credit=True, new_lowrise_8second_task_evaluated=True, original_74_score_recomputed=False, independent_low80_scope=True')
a='        notes.append("No PT/source file SHA recomputation here:';i=q.index(a);extra='''        rows=skill.get("pose_rows",[])
        audit.check("scope.three_independent_case_seeds", t.get("seed") in (20260929,20260930,20261001) and t.get("role")=="E3_LOW80_"+str(t.get("seed")))
        audit.check("scope.exact_five_pose16_first_episode_denominators", len(rows)==5 and [r.get("pose") for r in rows]==list(range(5)) and all(r.get("first_episode_denominator")==16 for r in rows))
        audit.check("scope.credit_counts_bounded", all(0<=r.get("credited_and_stable_at_end",-1)<=r.get("first_episode_stable_credits",-1)<=16 and 0<=r.get("first_episode_physical_terminated",-1)<=16 for r in rows))
        audit.eq("scope.credit_sum",skill.get("first_episode_stable_credits"),sum(r.get("first_episode_stable_credits",0)for r in rows))
        audit.eq("scope.end_stable_sum",skill.get("credited_and_stable_at_end"),sum(r.get("credited_and_stable_at_end",0)for r in rows))
        audit.fields("scope.original_criterion",skill,dict(stable_policy_controls=25,stable_seconds=.5,request_policy_controls=400,source_training_credit_not_used=True,reference_native_cohort_executed=False,paired_native_difference=None))
''';q=q[:i]+extra+q[i:];files[P/'fudan_eval_parent_wait_contract_v1.py']=q.encode('utf8')
s=(op/'single_gpu_group_supervisor.py').read_text(encoding='utf8');a="assert len(roles)==1 and {r['role']for r in roles}=={'E3'}";assert s.count(a)==1;s=s.replace(a,"assert len(roles)==3 and {r['role']for r in roles}==set("+repr(members)+")").replace('assert len(children)==1','assert len(children)==3').replace('if len(ready)==1:','if len(ready)==3:').replace('ONEGPU_E3_FDN_FRESH80_ORIGINAL_SKILL_EVAL_NO_LEARNING','ONEGPU_E3_LOW80_THREE_SEED_CONFIRM_NO_LEARNING').replace('ACTUAL_SINGLE_GPU_E3_FDN_FRESH80_ORIGINAL_SKILL_SCREEN','ACTUAL_SINGLE_GPU_E3_LOW80_THREE_SEED_CONFIRM');files[P/'single_gpu_group_supervisor.py']=s.encode('utf8')
t='''"""Pure low80 task wrapper; original locks, timeouts, parent and asset bindings retained."""
import os
from worker_sources.parent.task_contract import make_task as _original_make_task

def make_task(role,plan,deadline,fds):
 assert role['role']=='E3_LOW80_'+str(role['seed'])and role['seed']in(20260929,20260930,20261001)and role['controls']==400
 assert role['source_training_execution_qualified']is True and len(fds)==2 and fds[0]!=fds[1]
 t=_original_make_task(role,plan,deadline,fds)
 for name in('source_iteration','source_Adam17','source_LR'):t.pop(name,None)
 kind='E3_FDN_FROZEN_LOW80_CONFIRM_V1'
 t.update(kind=kind,purpose=kind,owner_parent_pid=os.getpid(),policy_interface='fudan_sequence_raw35_history5_latent3_clipped_mean_v1',evaluation_scope='LOW80_FIVE_POSE16_8S_FULLDR_FIRSTEPISODE_CONFIRM',source_training_execution_qualified=True,expert_role='E3',seed=role['seed'],controls=400,physics_callbacks=3200,feedback_samples=800,eval_members=[r['role']for r in plan['roles']])
 return t
''';files[P/'fudan_task_contract_v2.py']=t.encode('utf8')
for p,raw in files.items():ast.parse(raw.decode('utf8'));compile(raw.decode('utf8'),str(p),'exec')
for p,raw in files.items():
 if p.exists():assert p.read_bytes()==raw;continue
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
print(json.dumps(dict(new_scope=scope,cases=members,source_file_manifest=[dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())for p,raw in files.items()],phase_original_update_except_two_endpoint_copies_AST_exact=True,case_constructor_fresh_seed_not_inplace_reseed=True,per_case_source_input_reads_planned=1,group_source_input_reads_planned=3,original_pi_math_and_seven_resource_close_modules_not_rewritten=True,source_AST_compiled_once=True,SDK_model_CPUfixture_SSH_GPU_canonical_Git_operations=0),indent=2))
