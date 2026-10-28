from pathlib import Path
import ast,json,hashlib,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';C=L/'TWO101_CORRECT_NORMAL900_TWO_NATIVE20_COLLECTOR_SOURCE_V1';C.mkdir();(C/'reports').mkdir()
old=L/'TWO99_CORRECT_NORMAL900_TWO_NATIVE_COLLECTOR_SOURCE_V1/collect_TWO99_two_native_formals_correct_normal900_UNUSED_once_v2.py';s=old.read_text();tree=ast.parse(s);x=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CODE' for t in x.targets));code=ast.literal_eval(x.value)
code=code.replace("'restart'","'h1_seed28'").replace("'restart_slot'","'seed28_slot'")
a="w['schema']=='mod4.native99.stance_'+go[key]['input_start_mode']+'.objective_window.v1'";assert code.count(a)==1;code=code.replace(a,"w['schema']=='mod4.native99_to_flat20.target100.objective_window.v1'")
a="  w=row['native88_migration_window'];";assert code.count(a)==1;code=code.replace(a,"  assert go[key]['flat_jump_target_m']==row['original_H1_events']['flat_real_physics_events']['height_m']==.20\n"+a)
assert '37e34522213d' in code and '37restart' not in code;ast.parse(code)
lines=s.splitlines(keepends=True);s=''.join(lines[:x.lineno-1])+'CODE='+repr(code)+'\n'+''.join(lines[x.end_lineno:])
s=s.replace('TWO99_GENUINE_NATIVE_START_COMPARISON_OWNER_SOURCE_V1','TWO101_PRODUCER_FIXED_NATIVE20_ORIGINAL_OWNER_SOURCE_V1').replace('TWO99_TWO_NATIVE_FIRST_POLICY_OBSERVER_SOURCE_V1','TWO101_PRODUCER_FIXED_NATIVE20_FIRST_POLICY_OBSERVER_SOURCE_V1').replace('TWO99','TWO101').replace('closed99','closed101').replace("'restart'","'h1_seed28'")
ast.parse(s);entry=C/'collect_TWO101_native20_formals_original_cost_correct_normal900_UNUSED_once.py';entry.write_text(s,encoding='utf8')
B=L/'TWO101_TWO_NATIVE20_FORMAL_INITIAL_CPU_SOURCE_V1';B.mkdir();(B/'reports').mkdir();entries=[]
oldreview=(L/'TWO99_NEW_TWO_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1/review_NEW99_continue97_formal_initial_whole_CPU_UNUSED_once_v2.py').read_text()
for key,mode,seed in [('h1','seed27',27),('h1_seed28','seed28',28)]:
 r=oldreview.replace('MOD4_H1_FLAT05_STANCE_START_COMPARE_RESOURCE_V99_20261028',N.name).replace("B=N/'payloads/continue97'","B=N/'payloads/"+mode+"'").replace('TWO99_CORRECT_NORMAL900_TWO_NATIVE_COLLECTOR_SOURCE_V1',C.name).replace('TWO99_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json','TWO101_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json').replace('current_closed99_models/h1/','current_closed101_models/'+key+'/').replace("{'h1','restart'}","{'h1','h1_seed28'}").replace("go['restart']","go['h1_seed28']")
 for field in ['terminals','formals','published']:r=r.replace("v['"+field+"']['h1']","v['"+field+"']['"+key+"']")
 r=r.replace('NATIVE99_continue97_NEW','NATIVE101_'+mode+'_NEW').replace('Initial NEW99 continue97','Initial NEW101 '+mode).replace('NEW99 continue97 native','NEW101 '+mode+' native')
 r=r.replace("producer['native_learning_seed']==producer['physical_initial_seed']==27","producer['native_learning_seed']==27 and producer['physical_initial_seed']=="+str(seed))
 r=r.replace("producer['input_start_mode']=='continue97'","producer['input_start_mode']=='continue_warm99_height20'").replace("window['schema']=='mod4.native99.stance_continue97.objective_window.v1'","window['schema']=='mod4.native99_to_flat20.target100.objective_window.v1'")
 r=r.replace("assert producer['input_start_mode']", "assert producer['flat_jump_target_m']==.20\n assert producer['input_start_mode']")
 r=r.replace('input_native97_or_native0','input_native99').replace('TWO99_COMPLETE','TWO101_COMPLETE');ast.parse(r);p=B/('review_NEW101_'+mode+'_formal_initial_whole_CPU_UNUSED_once.py');p.write_text(r,encoding='utf8');entries.append(p)
combined='''from pathlib import Path
import importlib.util,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def load(mode):
 name='native101_'+mode;s=importlib.util.spec_from_file_location(name,B/('review_NEW101_'+mode+'_formal_initial_whole_CPU_UNUSED_once.py'));m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 mods=[load(mode) for mode in ['seed27','seed28']]
 for m in mods:m.closure(m.read(m.COLLECTED))
 with (R/'TWO101_INITIAL_TWO_FORMAL_CPU_CONSUMED_ACTUAL.json').open('x') as f:json.dump(dict(epoch=time.time(),both_closures_before_any_model_read=True,NEW_formals_planned2_shared86witness1=True),f,indent=2)
 import torch
 torch.set_num_threads(2);assert not torch.cuda.is_initialized();witness=torch.load(mods[0].B/'job0/source/H1_closed86_policy_only_update138.pt',map_location='cpu',weights_only=False)
 for m in mods:
  for name,other in list(sys.modules.items()):
   path=getattr(other,'__file__',None)
   if path and any(Path(path).is_relative_to(p.B) for p in mods):sys.modules.pop(name,None)
  m.main(witness)
 with (R/'TWO101_INITIAL_TWO_FORMAL_CPU_QUALIFIED_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,NEW_formal_loads=2,shared_normal86_loads=1,input_native99_loads=0,actual20cm_source_and_physical_seeds_bound=True,no_actor_WM_forward_GPU_or_account=True),f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('TWO101_INITIAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),no_repeat_initial_model_load=True),f,indent=2)
  raise
'''
ast.parse(combined);p=B/'review_TWO101_NEW_native20_formals_one_shared_witness_initial_CPU_UNUSED_once.py';p.write_text(combined,encoding='utf8');entries.append(p)
for folder,files,name in [(C,[entry],'FROZEN_UNUSED_TWO101_NORMAL900_COLLECTOR_INDEX_V1.json'),(B,entries,'FROZEN_UNUSED_TWO101_INITIAL_FORMAL_CPU_INDEX_V1.json')]:
 (folder/name).write_text(json.dumps(dict(epoch=time.time(),unused=True,source_AST_passed=True,original850_180_1140_and_normal900_preserved=True,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=True,collector=str(entry),combined_CPU=str(p),no_execution_or_model_read=True)))
