"""New purpose binds the original queue clock required by the actual E0 D4 constructor."""
from pathlib import Path
import json,ast
D=Path(__file__).resolve().parent;v=json.loads(Path(json.loads((D/'E0_SINGLE_ADMISSION2_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());m=v['metadata'];e=m['OWNER_EXIT_ACTUAL.json'];o=m['OUTER_OWNER_WAIT_ACTUAL.json'];c=v['cases']['E0'];assert v['closed']is True and all(e[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and o['original_owner_reaped']is True and c['V2_LEARNER_LOADED.json']is c['V2_NATIVE_INITIALIZED.json']is None and "KeyError: 'MOD4_RESUME_QUEUE_CONTROL_US'"in c['V2_MIGRATION_FINAL.json']['error']
outputs={};s=(D/'worker_mod4v2_expert_migration_v3.py').read_text(encoding='utf8');needle="    os.environ['RM_KEEP_STD'] = '1'\n";assert s.count(needle)==1;s=s.replace(needle,needle+"    # Original successful posttrain worker binds the physical queue to 50 Hz.\n    os.environ['MOD4_RESUME_QUEUE_CONTROL_US'] = '20000'\n");outputs[D/'worker_mod4v2_expert_migration_v4.py']=s
s=(D/'stage_e0_single_nonpt_runtime_v1.py').read_text(encoding='utf8').replace('stage_e0_single_nonpt_runtime_v1.py','stage_e0_single_nonpt_runtime_v2.py').replace('worker_mod4v2_expert_migration_v3.py','worker_mod4v2_expert_migration_v4.py');outputs[D/'stage_e0_single_nonpt_runtime_v2.py']=s
for old,new in [('stage_e0_single_admission2_migration_once.py','stage_e0_single_admission3_migration_once.py'),('dispatch_e0_single_admission2_migration_once.py','dispatch_e0_single_admission3_migration_once.py'),('collect_e0_single_admission2_migration_once.py','collect_e0_single_admission3_migration_once.py')]:
 s=(D/old).read_text(encoding='utf8').replace('E0_SINGLE_ADMISSION2','E0_SINGLE_ADMISSION3').replace('e0_single_admission2','e0_single_admission3')
 if old.startswith('stage_'):
  # Existing stronger first zero-start guard remains; append the distinct closed native-constructor failure.
  a='D=Path(__file__).resolve().parent;';assert s.count(a)==1;s=s.replace(a,a+"f2=json.loads((D/'E0_SINGLE_A2_QUEUE_FAILURE_TRUTH.json').read_bytes());assert f2['source_PT_loaded']is False and f2['all_actual_wait_settle_release']is True;")
  s=s.replace('worker_mod4v2_expert_migration_v3.py','worker_mod4v2_expert_migration_v4.py').replace('stage_e0_single_nonpt_runtime_v1.py','stage_e0_single_nonpt_runtime_v2.py')
 outputs[D/new]=s
for p,s in outputs.items():assert not p.exists();ast.parse(s);compile(s,str(p),'exec')
for p,s in outputs.items():p.write_text(s,encoding='utf8',newline='\n')
(D/'E0_SINGLE_A2_QUEUE_FAILURE_TRUTH.json').write_text(json.dumps(dict(root=v['root'],actual_owner_exit=e,actual_outer_wait=o,worker_error=c['V2_MIGRATION_FINAL.json']['error'],source_PT_loaded=False,actual_new_PPO_updates=0,all_actual_wait_settle_release=True,queue_clock_binding_source='Original posttrain_fullstate_common_v1.py:348 control_us20000',no_DR_or_physics_or_PPO_change=True),indent=2),encoding='utf8');print('E0 A3 new source binds original required queue20000us; original clocks/physics/PPO preserved; source-only AST, no old root replay')
