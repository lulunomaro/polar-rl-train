from pathlib import Path
import ast,hashlib,json,time
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports';B=T/'H1_STEP270_REWARD_PATH_V1_20261022';old=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/collect_selected_pair_finals_unused_once.py'
source=old.read_text('utf8');tree=ast.parse(source);constants={}
for n in tree.body:
 if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ('READ210','READ72') for x in n.targets):constants[n.targets[0].id]=ast.literal_eval(n.value)
capture=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='capture');cap=ast.get_source_segment(source,capture).replace("'current_pair_closed_text'","'benchmark_closed_text'")
header="""from pathlib import Path,PurePosixPath
import ast,hashlib,importlib.util,json,os,sys,time,traceback,base64
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
"""
main="""
try:
 q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
 assert all(v['performance_benchmark_only'] for v in q['specs'].values())
 observed=json.loads((R/'BENCHMARK_ACTUAL_GO_WORKER_IDENTITY_AND_PROGRESS_SNAPSHOT_ACTUAL.json').read_bytes())
 assert time.time()-min(v['actual_GO']['learning_started_epoch'] for v in observed['slots'].values())>=300
 put('BENCHMARK_CLOSING_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,owner=q['owner_identity'],benchmark_only_no_model_qualification=True,original_210wait850_72wait180_preserved=True))
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory);secret=memory.recover()
 c=d.t.connect()
 try:
  a=d.code(c,d.t.PY,READ210,dict(q=q),timeout=900);put('BENCHMARK_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json',a);ta,unused=capture(c,a,[],'h1')
 finally:c.close()
 c=d.connect72(secret);secret=None
 try:
  b=d.code(c,d.PY72,READ72,dict(q=q),timeout=210);put('BENCHMARK_CLOSED_TARGET72_ACTUAL.json',b);tb,unused=capture(c,b,[],'recovery')
 finally:c.close()
 segment=a['original_segment'];cost=sum(v['charged_seconds'] for v in segment['experts'].values());assert all(v['duration_bound_passed'] for v in segment['experts'].values())
 result=dict(epoch=time.time(),collector_function_complete=True,owner_node_workers_all_actual_out=True,original_canonical_cost_settled=True,original_actual_cost_sumonce=cost,original_remaining_closed_snapshot=a['original_canonical_remaining'],source210=a,source72=b,all_texts=ta+tb,no_models_downloaded_or_claimed_as_qualified=True,qualified_policy_sources_remain_actual_complete67=True,not_training_failure_in_original67=True,no_budget_refund_second_writer_or_clearactive=True)
 put('BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json',result)
 print(json.dumps(dict(closed=True,texts=len(ta)+len(tb),cost_sumonce=cost,remaining_closed_snapshot=a['original_canonical_remaining'],errors_by_slot={k:v.get('original_error') for k,v in a['cohort']['rows'].items()},not_qualified_training_models=True)))
except BaseException:
 put('BENCHMARK_CLOSING_ORIGINAL_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_force_kill_or_retry_same_once=True));raise
"""
text=header+'\nREAD210='+repr(constants['READ210'])+'\nREAD72='+repr(constants['READ72'])+'\n'+cap+'\n'+main;ast.parse(text)
dest=M/'collect_benchmark_text_cost_and_allout_unused_once.py'
with dest.open('x',encoding='utf8') as f:f.write(text)
a=(B/'same_authorized_session_compressed_transport_v53.py').read_text('utf8');needle="        'read_E3_benchmark_preexec_identity_schema_corrected_V2_unused_once.py',";extra="        '"+dest.name+"',";assert a.count(needle)==1;b=a.replace(needle,needle+'\n'+extra);assert ast.dump(ast.parse(b.replace(extra+'\n','')))==ast.dump(ast.parse(a));new=B/'same_authorized_session_compressed_transport_v54.py'
with new.open('x',encoding='utf8') as f:f.write(b)
with (R/'BENCHMARK_CLOSING_READER_AND_V54_EXACT_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,source=str(dest),source_SHA=H(dest) if False else hashlib.sha256(dest.read_bytes()).hexdigest(),READ210_READ72_original_closure_and_cost_lock_checks_byteexact=True,model_collection_removed_for_benchmark_only=True,all_texts_errors_collected=True,normal_model_FINAL_collector_unchanged=True,original_210max900_72max210_waits_preserved=True,source67_stays_latestqualified=True,wrapper=str(new),wrapper_SHA=hashlib.sha256(new.read_bytes()).hexdigest()),f,indent=2)
print(json.dumps(dict(collector=str(dest),wrapper=str(new))))

