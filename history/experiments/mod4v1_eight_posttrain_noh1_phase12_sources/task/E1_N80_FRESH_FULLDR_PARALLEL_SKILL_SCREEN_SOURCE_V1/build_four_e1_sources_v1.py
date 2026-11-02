"""Generate4 childentrypoints/ownfactoryprefixes/rolecontracts fromtextmetadata.
No model/stat/raw/SDK imports/authority operation.
"""
from pathlib import Path
import ast,difflib,hashlib,json
B=Path(__file__).resolve().parent;T=B.parent;W=Path(r'C:\Users\lulu\Desktop\claude\mjcf');P=W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016';S=W/'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011/implementation/frozen_history_flat_SLOPE134.py'
H=lambda x:hashlib.sha256(x).hexdigest()
roles={
 'CURB_PROTECTED878':('worker_curb878_n80.py',T/'E1_three_variants_GPU_actual_v1/CURB_PROTECTED878_ACTUAL_TYPED_SOURCE_V1',T/'E1_three_variants_CPU_actual_v1/CURB_PROTECTED878_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json',P/'eval_payload_v2/full80_runtime_native_v1.py','run_full80'),
 'CURB_INDEPENDENT113':('worker_curb113_n80.py',T/'E1_three_variants_GPU_actual_v1/CURB_INDEPENDENT113_ACTUAL_TYPED_SOURCE_V1',T/'E1_three_variants_CPU_actual_v1/CURB_INDEPENDENT113_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json',P/'curb113_frozen_v2/eval_payload_v2/full80_runtime_native_v1.py','run_full80'),
 'SLOPE135':('worker_slope135_n80.py',T/'E1_actual_qualification_v1/SLOPE135_ACTUAL_TYPED_SOURCE_V1',T/'E1_actual_qualification_v1/SLOPE135_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json',S,'main'),
 'SLOPE_INDEPENDENT50':('worker_slope50_n80.py',T/'E1_three_variants_GPU_actual_v1/SLOPE_INDEPENDENT50_ACTUAL_TYPED_SOURCE_V1',T/'E1_three_variants_CPU_actual_v1/SLOPE_INDEPENDENT50_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json',None,None)}
contracts={};factories=[];proofs=[];refs=[]
for role,(worker,runtime,receipt,source,function) in roles.items():
 j=json.loads(receipt.read_bytes());meta=j['actual_source_metadata'];typed=j['new_typed_source'];canonical=runtime/'E1_CANONICAL_SOURCE_METADATA.json';cm=json.loads(canonical.read_bytes());assert cm['canonical']==role
 primary=[dict(path=str(receipt),SHA=H(receipt.read_bytes()),kind='ACTUAL_TYPED_CPU_METADATA_NO_MODEL_REOPEN'),dict(path=str(canonical),SHA=H(canonical.read_bytes()),kind='OWN_FACTORY_METADATA')]
 contracts[role]=dict(worker_basename=worker,source=typed,core=meta,own_runtime_source_root=str(runtime),controls=1000 if role=='SLOPE_INDEPENDENT50' else 750,num_envs=80,scope='DEFAULT_TRAINING_AXIS_DESCRIPTIVE_SCREEN_NO_ORIGINAL_ACCEPTED_COHORT' if role=='SLOPE_INDEPENDENT50' else 'ORIGINAL_N80_MANUAL_ROUTE_ENDPOINT_CONTACT_SCOPE',primary_references=primary)
 with (B/worker).open('x',encoding='utf-8') as f:f.write('from e1_parallel_worker_safe import main_role\nif __name__=="__main__":main_role('+repr(role)+')\n')
 if source is None:continue
 text=source.read_text(encoding='utf-8-sig');tr=ast.parse(text);n=next(x for x in tr.body if isinstance(x,ast.FunctionDef) and x.name==function);line=text.splitlines(True);first=n.body[0].lineno;last=next(x.end_lineno for x in n.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='targets' for t in x.targets));prefix=''.join(line[first-1:last]);original=prefix;changes=[]
 def rep(old,new):
  global prefix
  assert prefix.count(old)==1,(role,old,prefix.count(old));prefix=prefix.replace(old,new,1);changes.append(dict(old=old,new=new))
 if role.startswith('CURB'):rep('args.steps in (120,1500)','args.steps == 750')
 else:rep('args.steps == 1500','args.steps == 750')
 rep('    cfg.scene.num_envs = args.num_envs','    cfg.scene.num_envs = args.num_envs\n    cfg.terminations.mimic.params={**cfg.terminations.mimic.params,"threshold":.01}\n    configure_new_task(cfg,identity)')
 rep("    r = e.scene['robot']","    r = e.scene['robot']\n    guard=attach_fresh_guard(e,identity,torch,tensor)")
 rep('    e.reset()','    e.reset()\n    audit_before=fresh_full_dr_audit(e,guard,tensor)')
 rep('e.step_dt == 0.01','e.step_dt == 0.02')
 if role.startswith('CURB'):rep('actual_all_physical_parameters=params(e)',"actual_all_physical_parameters=audit_before['actual_parameters']")
 reversed_prefix=prefix
 for c in reversed(changes):reversed_prefix=reversed_prefix.replace(c['new'],c['old'],1)
 assert ast.dump(ast.parse('def original():\n'+reversed_prefix),include_attributes=False)==ast.dump(ast.parse('def original():\n'+original),include_attributes=False)
 name='_factory_'+role.lower();helpers='''    args=SimpleNamespace(steps=750,num_envs=80,seed=20260928,dr_profile='white_v3',device='cuda:0',output=str(case/'ORIGINAL_ROUTE_QUERY.json'))
    import mod4_task as task
    from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv
    from e1_terrain_training_health import declared_truncation_terms
    from e1_full_pose_reset import query
    from mod4v1_fresh_dr_guard import configure_new_task
'''
 helpers+='    from '+('curb20_geometry import configure_curb' if role.startswith('CURB') else 'slope5_geometry import configure_slope')+' as configure_intro\n'
 code='def '+name+'(descriptor,case,identity,torch,np,wp,tensor):\n'+helpers+prefix+'''    return dict(env=e,robot=r,guard=guard,audit_before=audit_before,route_scope=route_scope,command=cmd,manual=True,groups=groups,targets=targets)
'''
 factories.append(code);primary.append(dict(path=str(source),SHA=H(source.read_bytes()),function=function,kind='OWN80_FACTORY_PREFIX_EXTRACTED'))
 proofs.append(dict(role=role,original_path=str(source),original_SHA=H(source.read_bytes()),original_function=function,extracted_firstline=first,extracted_lastline=last,exact_replacements=changes,reverse_original_prefix_AST_exact=True,physical_factory_class='E1ResetEvidenceLearningEnv',core_placement_geometry_manual_commands_preserved=True,old_RSLwrapper_secondreset_omitted='ExplicitONEfreshresetpurpose; originalcarrierCurb110documentsafterwrapperreset. No pairedoldfreshDRclaim.',diff=''.join(difflib.unified_diff(original.splitlines(True),prefix.splitlines(True)))))
aux=P/'eval_payload_v2/curb_worldmesh_query_contract_v1.py';raw=aux.read_bytes();ast.parse(raw)
with (B/'curb_worldmesh_query_contract_v1.py').open('xb') as f:f.write(raw)
refs.append(dict(path=str(aux),SHA=H(raw),kind='OWN_CURB_WORLD_GEOMETRY_QUERY_SOURCE_ONLY'))
module='''"""Exactown80 factoryprefixes, source-onlyderivation;importsSDK onlyinsidecall."""
from types import SimpleNamespace
from pathlib import Path
import hashlib
from e1_fresh_runtime_bridge import attach_fresh_guard,fresh_full_dr_audit

def cpu(x):return x.detach().cpu().numpy().copy() if hasattr(x,'detach') else x.torch.detach().cpu().numpy().copy()
def js(x):return x.detach().cpu().tolist() if hasattr(x,'detach') else x.torch.detach().cpu().tolist()
def assignments(e):
 return dict(action={k:dict(delay_us=js(g['lag_steps']*2500),episode=js(g['episode'])) for k,g in e._physics_action_delay.queue.groups.items()},spring=dict(factor=js(e._spring_pressure.component.factor),episode=js(e._spring_pressure.component.episode)),gas=dict(factor=js(e._gas_damping.component.factor),episode=js(e._gas_damping.component.episode)),COM=dict(delta_m=js(e._chassis_com.component.delta_m),episode=js(e._chassis_com.component.episode)),PD=dict(factors={k:js(v) for k,v in e._explicit_pd.component.factor.items()},episode=js(e._explicit_pd.component.episode)),feedback_delay=js(e._feedback_delay_mild.lag_steps))

'''+ '\n\n'.join(factories)+'''\n
def build_original_route80(role,descriptor,case,identity,torch,np,wp,tensor):
 assert role in ('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135')
 return globals()['_factory_'+role.lower()](descriptor,case,identity,torch,np,wp,tensor)
'''
ast.parse(module)
with (B/'e1_route80_factories.py').open('x',encoding='utf-8') as f:f.write(module)
with (B/'ROLE_CONTRACTS.json').open('x',encoding='utf-8') as f:json.dump(contracts,f,ensure_ascii=False,indent=2)
with (B/'FOUR_E1_ORIGINAL_FACTORY_AST_DIFF_PROOF_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(proofs=proofs,auxiliary_refs=refs,scope='SOURCE_ONLY_no_model_SDK',SLOPE50='Exactoriginalbuild_env AST extractedatruntimewithoutentryApp/main; owntrainingaxis binder,freshN80noPTrestore'),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(workers=4,own_original80_prefixes=3,reverse_AST_exact=True,source_only=True,model_SDK_calls=0),indent=2))
