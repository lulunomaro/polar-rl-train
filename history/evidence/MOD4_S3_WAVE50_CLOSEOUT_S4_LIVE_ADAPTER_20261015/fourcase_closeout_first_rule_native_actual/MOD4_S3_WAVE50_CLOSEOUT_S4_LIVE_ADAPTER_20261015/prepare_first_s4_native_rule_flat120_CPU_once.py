"""Prepare only a new pair-router native120 on the unchanged original flat scene."""
from pathlib import Path
import json,ast,shutil,zipfile,time,hashlib,traceback
A=Path(__file__).resolve().parent;W=A.parent;R=A/'reports'
OLD=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015'
NEW=W/'MOD4_S4_E0_WAVE35_ROUTER_NATIVE_20261015'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 proof=R/'S4_SHARED_TICK_ROUTER_JOINT_PROBABILITY_AND_CPU_FULLSAVE_ACTUAL.json';audit=json.loads(proof.read_bytes());assert audit['passed_CPU_runtime_probability_and_disk_contracts'] and audit['optimizer_updates']==0 and not audit['gate_GPU_PPO_admitted']
 assert not NEW.exists();Q=NEW/'payload';T=NEW/'reports';Q.mkdir(parents=True);T.mkdir()
 m=json.loads((OLD/'payload/RETENTION_CPU_MANIFEST_V8.json').read_bytes())
 for row in m['package_files_v8']:
  p=OLD/'payload'/row['relative'];assert h(p)==row['sha256'];target=Q/row['relative'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 shutil.copytree(OLD/'payload/cpu_contracts',Q/'cpu_contracts',ignore=shutil.ignore_patterns('__pycache__'))
 witness=Q/'retention_native_witness_v8.py';s=witness.read_text();tree=ast.parse(s);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build_observed_frozen_policy');before=ast.get_source_segment(s,node)
 replacement="def build_observed_frozen_policy(vec,path,device):\n from s4_native_pair_adapter_v2 import build_native_rule_pair\n return build_native_rule_pair(vec,path,device)"
 witness.write_text(s.replace(before,replacement),encoding='utf8')
 # Every physical capture/reset/finalize function and each original main remains unchanged.
 oldtree=ast.parse(s);newtree=ast.parse(witness.read_text());oldtree.body=[n for n in oldtree.body if not (isinstance(n,ast.FunctionDef) and n.name=='build_observed_frozen_policy')];newtree.body=[n for n in newtree.body if not (isinstance(n,ast.FunctionDef) and n.name=='build_observed_frozen_policy')];assert ast.dump(oldtree,include_attributes=False)==ast.dump(newtree,include_attributes=False)
 worker=Q/'retention_worker_v8.py';worker.write_text(worker.read_text().replace(OLD.name,NEW.name),encoding='utf8')
 for row in m['package_files_v8']:row.update(bytes=(Q/row['relative']).stat().st_size,sha256=h(Q/row['relative']))
 frozen=W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014/hard_top1_frozen_expert_CPU_component_v1.py'
 for p in (A/'s4_shared_feedback_hardtop1_v1.py',A/'s4_native_pair_adapter_v2.py',frozen):
  shutil.copy2(p,Q/p.name);m['package_files_v8'].append(dict(relative=p.name,bytes=p.stat().st_size,sha256=h(p)))
 refs=[];(Q/'source').mkdir()
 for row in audit['sources']:
  assert h(row['local_path'])==row['sha256'];target=Q/'source'/(row['expert']+'_frozen_source.pt');shutil.copy2(row['local_path'],target)
  refs.append(dict(expert=row['expert'],local_path='D:/MOD4_async_eval/'+NEW.name+'/payload/source/'+target.name,sha256=row['sha256'],bytes=target.stat().st_size))
  m['sources']['S4_'+row['expert']]=dict(local_path=str(target),remote_path=refs[-1]['local_path'],sha256=row['sha256'],bytes=target.stat().st_size)
 pair=dict(version=1,mode='rule_eval',sources=refs,no_gate_learning=True,no_new_observation_or_terrain_truth=True,shared_observation35=True,one_whole6action_no_blend=True,original_clip6=True,source_bound_CPU_report_SHA=h(proof),first_stateless_native_flat120_only=True,full35_transition_route_and_gate_PPO_pending=True)
 (Q/'S4_PAIR_SOURCE_MANIFEST.json').write_text(json.dumps(pair,indent=2),encoding='utf8');m['package_files_v8'].append(dict(relative='S4_PAIR_SOURCE_MANIFEST.json',bytes=(Q/'S4_PAIR_SOURCE_MANIFEST.json').stat().st_size,sha256=h(Q/'S4_PAIR_SOURCE_MANIFEST.json')))
 m['S4_native_CPU_scope']=dict(namespace=NEW.name,kind='flat',steps=120,num_envs=80,seed=20261002,immutable_pair=refs,no_new_physics_reset_command_OR_numeric_contract=True,policy_adapter_new_scope=True,gate_trained=False,GPU_admitted=False,actor19_or_single_source_not_claimed=True)
 (Q/'RETENTION_CPU_MANIFEST_V8.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 for p in Q.rglob('*.py'):compile(p.read_text(),str(p),'exec')
 z=NEW/'FIRST_S4_RULE_PAIR_NATIVE120_CPU_PREPARED.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
  for row in m['package_files_v8']:out.write(Q/row['relative'],row['relative'])
  out.write(Q/'RETENTION_CPU_MANIFEST_V8.json','RETENTION_CPU_MANIFEST_V8.json')
  for p in (Q/'source').iterdir():out.write(p,'source/'+p.name)
 result=dict(epoch=time.time(),prepared_CPU_only=True,package=dict(path=str(z),bytes=z.stat().st_size,sha256=h(z)),new_root='D:/MOD4_async_eval/'+NEW.name,case='s4_rule_pair_flat80_native120_v1',task='MOD4_S4_RulePairFlat80_Native120_v1_20261015',manifest_SHA=h(Q/'RETENTION_CPU_MANIFEST_V8.json'),pair_manifest_SHA=h(Q/'S4_PAIR_SOURCE_MANIFEST.json'),worker_SHA=h(worker),policy_adapter_SHA=h(Q/'s4_native_pair_adapter_v2.py'),source_pair=refs,mainloop_all_physical_witness_AST_exact_except_one_policy_builder=True,original_flat_main_and_hardware_contact_COM_query_bytes_exact=True,original_all_native_plane_reference_files_exact=True,not_a_completed35mm_transition_route=True,not_gate_GPU_or_PPO_admitted=True,no_SSH_GPU_PPO_or_budgetwrite=True)
 (T/'FIRST_S4_NATIVE_RULE_PAIR_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(prepared=str(T/'FIRST_S4_NATIVE_RULE_PAIR_CPU_PREPARED_ACTUAL.json'),package=result['package'],new_native_scope='rule_pair_flat80_native120',no_GPU=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('S4_NATIVE_CPU_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_SSH_GPU=True),indent=2),encoding='utf8');raise
