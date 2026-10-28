from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
N=T/'MOD4_H1_FLAT05_STANCE_START_COMPARE_RESOURCE_V99_20261028'
B=L/'TWO99_CORRECT_NORMAL900_TWO_NATIVE_COLLECTOR_SOURCE_V1';B.mkdir();(B/'reports').mkdir()
old=(L/'TWO97_correct_normal900_dual_native_PPO_collector_source_v1/collect_TWO97_native_H1_PPO_E3_correct_normal900_UNUSED_once_v1.py').read_text()
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
tree=ast.parse(old);code=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CODE' for t in x.targets))
code=code.replace('e3','restart').replace("wout=wjob/'adaptation'","wout=wjob/'job0/production'").replace("read(wjob/'GO_PRODUCTION.json')","read(wjob/'job0/GO_PRODUCTION.json')")
line="  if key=='restart':assert formal['source_SHA']==go[key]['source_SHA'] and row['new_updates']>0 and row['Adam_step']==864320+20*row['new_updates'] and not formal['new_branch_skill_qualified']\n"
assert code.count(line)==1;code=code.replace(line,"  w=row['native88_migration_window'];assert w['schema']=='mod4.native99.stance_'+go[key]['input_start_mode']+'.objective_window.v1' and w['reference_SHA']==go[key]['native_reference_SHA']\n  assert w['counters']['new_world_updates']>=640 and w['counters']['new_policy_updates']>0 and w['counters']['completed_fresh_controls']>=64\n")
new=old
node=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CODE' for t in x.targets))
lines=new.splitlines(keepends=True);new=''.join(lines[:node.lineno-1])+f'CODE={code!r}\n'+''.join(lines[node.end_lineno:])
new=new.replace('TWO97_H1_E3_NEW_FULL_CPU_OWNER_SOURCE_V1','TWO99_GENUINE_NATIVE_START_COMPARISON_OWNER_SOURCE_V1').replace('TWO97_H1_E3_COMBINED_FIRST_INLINE_SOURCE_V1','TWO99_TWO_NATIVE_FIRST_POLICY_OBSERVER_SOURCE_V1')
new=new.replace('TWO97_ACTUAL_TWO_GO_OWNER_METADATA_RETURNED.json','TWO99_ACTUAL_TWO_GO_OR_ORIGINAL_ERROR_OWNER_RETURNED.json')
new=new.replace('TWO97','TWO99').replace('closed97','closed99').replace('e3','restart')
new=new.replace('UNUSED97 normal900','UNUSED99 normal900 two-native').replace('PPO_E3','native_restart0')
ast.parse(new);ast.parse(code)
entry=B/'collect_TWO99_two_native_formals_correct_normal900_UNUSED_once_v1.py';entry.write_text(new,encoding='utf8')
reviewdir=L/'TWO99_NEW_TWO_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1';reviewdir.mkdir();(reviewdir/'reports').mkdir()
oldreview=(L/'TWO97_NEW_H1_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1/review_NEW97_H1_formal_initial_whole_CPU_UNUSED_once_v2.py').read_text()
rows=[]
for key,mode in [('h1','continue97'),('restart','restart0')]:
 r=oldreview.replace('TWO97_correct_normal900_dual_native_PPO_collector_source_v1',B.name).replace('MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028',N.name)
 r=r.replace("B=N/'payload'",f"B=N/'payloads/{mode}'")
 r=r.replace("current_closed97_models/h1/",f"current_closed99_models/{key}/").replace("{'h1','e3'}","{'h1','restart'}").replace("go['e3']","go['restart']")
 for field in ['terminals','formals','published']:
  r=r.replace("v['"+field+"']['h1']","v['"+field+"']['"+key+"']")
 r=r.replace('TWO97_COMPLETE','TWO99_COMPLETE')
 r=r.replace('NATIVE97_NEW','NATIVE99_'+mode+'_NEW').replace('Initial NEW97','Initial NEW99 '+mode).replace('NEW97 native','NEW99 '+mode+' native')
 r=r.replace("count['native_iteration']>10692","count['native_iteration']>SOURCE_PINS['source_progress']['updates']")
 r=r.replace("p['world_updates']==106920+count['new_world_updates'] and p['policy_updates']==10372+count['new_policy_updates']","p['world_updates']==SOURCE_PINS['source_progress']['world_updates']+count['new_world_updates'] and p['policy_updates']==SOURCE_PINS['source_progress']['policy_updates']+count['new_policy_updates']")
 needle="producer=p['producer'];assert producer['native_learning_seed']==producer['physical_initial_seed']==27 and producer['task_focused_real_replay']==NATIVE_CONTRACT['task_focused_real_replay']"
 assert r.count(needle)==1
 r=r.replace(needle,needle+f"\n assert producer['input_start_mode']=='{mode}' and producer['stance_reference_revision']==NATIVE_CONTRACT['stance_reference_revision']\n assert window['schema']=='mod4.native99.stance_{mode}.objective_window.v1' and window['reference_SHA']==NATIVE_CONTRACT['stance_reference_revision']['reference_SHA']")
 r=r.replace('input_native93','input_native97_or_native0').replace('full97','full99')
 ast.parse(r);p=reviewdir/f'review_NEW99_{mode}_formal_initial_whole_CPU_UNUSED_once_v1.py';p.write_text(r,encoding='utf8');rows.append(p)
def index(folder,files,name):
 value=dict(epoch=time.time(),unused=True,source_only_preparation=True,normal900_original_gates=True,no_model_GPU_SSH_or_account_action=True,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files])
 (folder/name).write_text(json.dumps(value,indent=2),encoding='utf8')
index(B,[entry],'FROZEN_TWO99_NORMAL_COLLECTOR_INDEX_V1.json');index(reviewdir,rows,'FROZEN_TWO99_INITIAL_CPU_REVIEWERS_INDEX_V1.json')
print(json.dumps(dict(prepared=True,collector=str(entry),two_reviewers=[str(p) for p in rows],not_executed=True)))
