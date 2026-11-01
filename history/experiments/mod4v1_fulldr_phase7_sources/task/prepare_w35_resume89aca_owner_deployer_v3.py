"""Newunused owner/deployer joins real89aca GPUrestore+negativefull32+trace decision.
Original accounting/authority functions and budget/lease/timecaps retained; no execution here.
"""
from pathlib import Path
import ast,json,hashlib,re,difflib
R=Path(__file__).resolve().parent;C=R/'staged_sources/W35_89ACA_SOURCE_CERTIFICATE';cert=json.loads((C/'CERTIFICATE_INDEX.json').read_bytes());meta=cert['source'];oldsha='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b';oldkind='MOD4V1_W35_LATEST32481_FULLD0D7_RM70_V2';kind='MOD4V1_W35_RESUME32561_FULLD0D7_RM70_V3';oldmodel='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_QUALIFIED343E_CONTINUE227D_20261101_0712/w35_72/production/model_final_complete.pt';oldcpu='e55cad0a6d1e70b99ed8b527a8d50241c4b30c59f4cdf449842889d2ee84e5fb';owner=R/'w35_mod4v1_finite_original_owner_v3.py';deploy=R/'deploy_w35_finite_mod4v1_resume89aca_v3_once.py';assert not owner.exists()and not deploy.exists()
s=(R/'w35_mod4v1_finite_original_owner_v2.py').read_text(encoding='utf-8');before=s;s=s.replace(oldsha,meta['SHA']).replace(oldkind,kind).replace(oldmodel,meta['path']).replace(oldcpu,cert['restore_proof_SHA']).replace('17619333','17621509').replace('32481','32561').replace('651260','652860').replace('.0002562890625000001','.00011390625000000006').replace("'source_prior_new_PPO_updates':77","'source_prior_new_PPO_updates':80").replace('saved_source_CPU_proof_SHA','source_GPU_fullrestore_proof_SHA');s=re.sub(r'\bCPU\b','GPU_RESTORE',s).replace('preservedsourceCPU proof','actual89aca GPUfullrestore proof, not oldCPUproof')
a="   for path in b.LOCKS:"
b="""   restore=b.read(B/'evidence/INPUT89ACA_GPU_FULLRESTORE_ACTUAL.json');assert b.H(B/'evidence/INPUT89ACA_GPU_FULLRESTORE_ACTUAL.json')==GPU_RESTORE and restore['passed'] and restore['source_SHA']==SOURCE and restore['iteration']==32561 and restore['Adam17']==652860 and restore['actual_LR']==.00011390625000000006 and restore['actor_critic_STD_optimizer_verified']
   decision=b.read(B/'evidence/ACTUAL_POST80_FULL32_DECISION.json');trace=b.read(B/'evidence/ACTUAL_POST80_TRACE_SIGNED.json');closed=b.read(B/'evidence/ACTUAL_POST80_TRACE_EXIT.json')
   assert decision['after_model_SHA']==SOURCE and decision['new_PPO_updates']==80 and decision['decision']['RM70_full_expert_qualification']is False and trace['no_qualification'] and closed['all_own_children_waited'] and closed['owned_private_validation_locks_released'] and closed['error']is None
   for path in b.LOCKS:"""
assert s.count(a)==1;s=s.replace(a,b);oldast=ast.parse(before);newast=ast.parse(s);account=lambda t:next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='account');assert ast.dump(account(oldast),include_attributes=False)==ast.dump(account(newast),include_attributes=False);owner.write_text(s,encoding='utf-8')
s=(R/'deploy_w35_finite_mod4v1_adaptation_v2_once.py').read_text(encoding='utf-8');s=s.replace('W35_MOD4V1_SOURCE_V2_FINAL','W35_MOD4V1_RESUME89ACA_SOURCE_V3').replace('MOD4V1_W35_FULLDR_ADAPT_V2_','MOD4V1_W35_RESUME89ACA_ADAPT_V3_').replace('w35_mod4v1_finite_original_owner_v2.py','w35_mod4v1_finite_original_owner_v3.py').replace(oldsha,meta['SHA']).replace('17619333','17621509').replace("SRC='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_FULLDR_EVAL_20261102_010506_1793552706521956800'","SRC='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_POSTADAPT_EVAL_20261102_031914_1793560754280025200'").replace('W35_adaptation_dispatch_','W35_resume89aca_adaptation_dispatch_')
s=s.replace("for _,p in files:","files += [('evidence/INPUT89ACA_GPU_FULLRESTORE_ACTUAL.json',R/'staged_sources/W35_89ACA_SOURCE_CERTIFICATE/FULLRESTORE227_BEFORE_CONTROL.json'),('evidence/ACTUAL_POST80_FULL32_DECISION.json',R/'reports/W35_FULL32_BEFORE_AFTER_PPO80_DECISION_V1.json'),('evidence/ACTUAL_POST80_TRACE_SIGNED.json',R/'reports/W35_MOTION_TRACE_SIGNED_CHECK_V2.json'),('evidence/ACTUAL_POST80_TRACE_EXIT.json',R/'staged_sources/W35_89ACA_SOURCE_CERTIFICATE/TRACE_EXIT_ACTUAL.json')]\nfor _,p in files:")
a=" for rel,p in files:"
b=""" for rel,p in files:"""
assert s.count(a)==1
# Bind exactcompletedtraceexitbytes from its own runtime, not parsed watcher serialization.
a="  for rel,p in files:"
b="""  trace_job=json.loads((R/'reports/W35_motion_trace_dispatch_20261102_044043.json').read_bytes())['new_job']
  with sf.open(trace_job+'/PARENT_EXIT_SCOPE.json','rb')as f:traceexit=f.read()
  done=json.loads(traceexit);assert done['all_own_children_waited']and done['owned_private_validation_locks_released']and done['error']is None
  trace_local=R/'staged_sources/W35_89ACA_SOURCE_CERTIFICATE/TRACE_EXIT_ACTUAL.json'
  if trace_local.exists():assert trace_local.read_bytes()==traceexit
  else:trace_local.write_bytes(traceexit)
  for rel,p in files:"""
assert s.count(a)==1;s=s.replace(a,b)
# Evidence files withcompletefixed names must be in the checked installmanifest too.
s=s.replace("for f in sorted(B.glob('*.py')):","for f in sorted((B/'evidence').glob('*.json')):files.append({'relative':f.relative_to(B).as_posix(),'bytes':f.stat().st_size,'SHA':hashlib.sha256(f.read_bytes()).hexdigest()})\nfor f in sorted(B.glob('*.py')):")
s=s.replace("'source':'Humanmod4v1fullDR/RM70goal; actual32s speed deficit, same approvedPPO/physics/rewards'","'source':'HumanfullDR/RM70goal; post80full32 actualmovingdeficit andnewtrace shows command+actualwheel-targetwiring intact, one additionalfinite3900sameoriginalPPO/reward/geometry/STD; savedmodelreplay+indepfull32requiredafterexit'")
ast.parse(s);deploy.write_text(s,encoding='utf-8');v={'kind':'UNUSED_RESUME89ACA_FINITE_ORIGINAL_OWNER_V3_SOURCE_ONLY','owner_SHA':hashlib.sha256(owner.read_bytes()).hexdigest(),'deployer_SHA':hashlib.sha256(deploy.read_bytes()).hexdigest(),'original_account_function_AST_unchanged':True,'original_canonical_generation_and_equations_retained':True,'max_parent_seconds':3900,'save_after_seconds':3600,'exit_headroom_seconds':300,'input_source':meta,'input_actual_LR':cert['source_actual_LR'],'input_GPU_restore_proof_SHA':cert['restore_proof_SHA'],'not_old_CPU_proof':True,'model_SDK_budget_reads_or_writes':0,'source_only_not_GO':True};p=R/'reports/W35_RESUME89ACA_OWNER_DEPLOYER_STATIC_V3.json';assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
