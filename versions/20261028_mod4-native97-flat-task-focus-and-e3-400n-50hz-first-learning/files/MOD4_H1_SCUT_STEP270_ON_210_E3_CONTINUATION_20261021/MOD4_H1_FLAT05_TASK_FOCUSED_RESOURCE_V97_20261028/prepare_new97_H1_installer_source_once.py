from pathlib import Path
import ast,hashlib,json,runpy
N=Path(__file__).resolve().parent;T=N.parent
old=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V95_20261028/install_native95_qualified93_task_focus_actual_CPU_UNUSED_once.py'
m=runpy.run_path(str(old),run_name='original95_installer_definitions_only');pre=m['PRE']
assert pre.count('539470.7667970657')==1;pre=pre.replace('539470.7667970657','538787.2676227093',1)
needle="gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';"
proof="""closedroot=owned/'MOD4_TWO96A_H1_E3_2610v96a'
closed=json.loads((closedroot/'owner/COHORT_FINAL.json').read_bytes());ending=json.loads((closedroot/'owner/OWNER_EXIT_ACTUAL.json').read_bytes())
assert closed['original_cost_settled'] and ending['original_cost_settled']
assert set(closed['go'])=={'h1','e3'} and all(g['original_owner_pid']==591209 and g['original_owner_creation']==1793174406.88 for g in closed['go'].values())
original=[a for a in c['completed_segments'] if a['owner_parent_pid']==591209 and set(a['experts'])=={'h1','e3'} and all(a['experts'][k]['started_epoch']==closed['go'][k]['learning_started_epoch'] for k in ('h1','e3'))]
assert len(original)==1 and original[0]['charged_expert_seconds']==663.7164537906647 and original[0]['experts']['h1']['charged_seconds']==258.2691116333008 and original[0]['experts']['e3']['charged_seconds']==405.4473421573639
for key in ('h1','e3'):
 row=json.loads((closedroot/('node_'+key)/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert row['terminal_all_own_children_waited'] and row['original_error']
"""
assert pre.count(needle)==1;pre=pre.replace(needle,proof+'\n'+needle,1)
s=old.read_text('utf8');tree=ast.parse(s);a=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PRE' for t in x.targets));lines=s.splitlines(keepends=True)
s=''.join(lines[:a.lineno-1])+'PRE='+repr(pre)+'\n'+''.join(lines[a.end_lineno:])
s=s.replace('MOD4_H1_FLAT05_TASK_FOCUSED_2610v95/h1','MOD4_H1_FLAT05_TASK_FOCUSED_2610v97/h1').replace('NATIVE95_','NATIVE97_')
s=s.replace('NATIVE97_SOURCE_PREPARED_ACTUAL.json','NATIVE97_DIAGNOSTIC_IO_SOURCE_PREPARED_ACTUAL.json').replace("prep['h1_spec_pending_actual_CPU_and_controller']","prep['spec_pending_actual_new_source_CPU']")
ast.parse(s);target=N/'install_native97_unique_diagnostic_actual_source_SDK_CPU_once.py'
with target.open('x',encoding='utf8') as f:f.write(s)
with (N/'reports/NATIVE97_INSTALLER_SOURCE_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(source=str(old),selected=str(target),SHA=hashlib.sha256(target.read_bytes()).hexdigest(),new97_purpose=True,requires_actual96A_original_fee_CNone_and_same_qualified93_model_source=True,original_CPU_child_identity_wait_wrapper_unchanged=True,no_remote_executed=True),f,indent=2)
print(str(target))
