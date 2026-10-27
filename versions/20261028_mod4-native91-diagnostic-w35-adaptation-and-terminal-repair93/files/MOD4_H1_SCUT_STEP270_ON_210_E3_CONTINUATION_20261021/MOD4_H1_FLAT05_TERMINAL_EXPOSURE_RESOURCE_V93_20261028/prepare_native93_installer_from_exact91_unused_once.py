"""Prepare only: retain actual installer/CPU, bind new source and closed W3592."""
from pathlib import Path
import ast,hashlib,importlib.util,json
N=Path(__file__).resolve().parent;T=N.parent
O=T/'MOD4_H1_FLAT05_MASK_AWARE_MIXED72_RESOURCE_V91_20261027'
source=(O/'install_native91_actual_source_SDK_CPU_once.py').read_text('utf8')
spec=importlib.util.spec_from_file_location('old91_installer_definitions_only',O/'install_native91_actual_source_SDK_CPU_once.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
pre=m.PRE
changes=[
 ('MOD4_H1_FLAT05_NATIVE_2610v90b/h1','MOD4_H1_FLAT05_MASK_AWARE_2610v91/h1'),
 ("assert c['remaining_training_seconds']==554499.7579419613", "assert c['remaining_training_seconds']==v['closed_W35_remaining']"),
 ('go[\'original_owner_pid\']==549489 and go[\'original_owner_creation\']==1793109075.93',"go['original_owner_pid']==553988 and go['original_owner_creation']==1793115270.2"),
 ("x['owner_parent_pid']==549489", "x['owner_parent_pid']==553988"),
 ('3610.5603725910187','4101.035485744476'),('256228297','256229065'),
 ('H1_native90B_qualified_h1.pt','H1_native91_qualified_h1.pt'),
 ('actual90B_original_fee_allout_terminal_passed','actual91_original_fee_allout_terminal_passed')]
for a,b in changes:
 assert pre.count(a)==1,(a,pre.count(a));pre=pre.replace(a,b,1)
needle="oldrows={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']}"
assert pre.count(needle)==1
proof='''wroot=owned/'MOD4_W35_PPO50_GAS400_RETENTION_2610v92'
wcf=json.loads((wroot/'owner/COHORT_FINAL.json').read_bytes());assert wcf['original_cost_settled'] and (wroot/'owner/OWNER_EXIT_ACTUAL.json').is_file()
assert wcf['go']['w35']['original_owner_pid']==557831 and wcf['go']['w35']['original_owner_creation']==1793119787.14 and wcf['go']['w35']['learning_started_epoch']==1793119790.600079
wt=json.loads((wroot/'node_w35/NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert wt['terminal_all_own_children_waited']
ws=[s for s in c['completed_segments'] if s['owner_parent_pid']==557831 and s['experts']['w35']['started_epoch']==1793119790.600079]
assert len(ws)==1 and ws[0]['charged_expert_seconds']==v['closed_W35_original_fee']
'''
pre=pre.replace(needle,proof+'\n'+needle,1)
tree=ast.parse(source);preassign=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='PRE' for y in x.targets));lines=source.splitlines(keepends=True)
derived=''.join(lines[:preassign.lineno-1])+'PRE='+repr(pre)+'\n'+''.join(lines[preassign.end_lineno:])
derived=derived.replace('MOD4_H1_FLAT05_MASK_AWARE_2610v91/h1','MOD4_H1_FLAT05_TERMINAL_2610v93/h1',1)
derived=derived.replace('NATIVE91_','NATIVE93_')
derived=derived.replace("prep=json.loads((R/'NATIVE93_SOURCE_PREPARED_ACTUAL.json').read_bytes());manifest=", "prep=json.loads((R/'NATIVE93_SOURCE_PREPARED_ACTUAL.json').read_bytes());prep['manifest_SHA']=prep['h1_spec_pending_actual_CPU_and_controller']['payload_manifest_SHA'];wclosed=json.loads((T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_fixed92_correct_normal900_collector_v1_source/reports/W35_FIXED92_COMPLETE_FINAL_OR_PARTIAL_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert wclosed['canonical_None'] and wclosed['actual_finite_returned'];manifest=")
needle="dict(root=REMOTE,manifest=manifest,native_SHA=prep['task']['source_SHA'])"
assert derived.count(needle)==1
derived=derived.replace(needle,"dict(root=REMOTE,manifest=manifest,native_SHA=prep['task']['source_SHA'],closed_W35_remaining=wclosed['closing_remaining_snapshot'],closed_W35_original_fee=wclosed['original_fee_seconds'])")
ast.parse(derived)
out=N/'install_native93_actual_source_SDK_CPU_UNUSED_once.py'
with out.open('x',encoding='utf8') as f:f.write(derived)
with (N/'reports/NATIVE93_INSTALLER_SOURCE_ONLY_DERIVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,prepared_only_no_execution=True,source_original=str(O/'install_native91_actual_source_SDK_CPU_once.py'),selected=str(out),SHA=hashlib.sha256(out.read_bytes()).hexdigest(),retains_original_per_file_copy_loop_and_full_manifest_CPU=True,requires_actual_W35_closed_fee_CNone_before_new_source_CPU=True,no_GO=True),f,indent=2)
print(json.dumps(dict(source_prepared=True,actual_source_SDK_CPU_pending=True)))
