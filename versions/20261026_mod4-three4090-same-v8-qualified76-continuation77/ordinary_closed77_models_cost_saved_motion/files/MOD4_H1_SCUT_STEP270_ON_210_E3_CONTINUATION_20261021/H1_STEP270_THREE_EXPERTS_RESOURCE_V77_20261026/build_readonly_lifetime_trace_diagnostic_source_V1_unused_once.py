"""Prepare exact three-hook lifetime accounting without touching current77 or creating a Task."""
from pathlib import Path
import ast,base64,hashlib,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;P=N/'payloads/h1';R=N/'reports'
M=T/'H1_STEP270_LIFETIME_GOAL_ACCOUNTING_DIAGNOSTIC_PREPARATION_20261026';C=M/'candidate_v1'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def patch(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b,1)
def write(p,s):
    ast.parse(s)
    with Path(p).open('x',encoding='utf8') as f:f.write(s)
try:
    assert not C.exists();C.mkdir();(M/'reports').mkdir(exist_ok=True);refs=M/'reference_sources';refs.mkdir()
    before={}
    for name in ('h1_production_control_prefix_trace_v1.py','sampling_acceleration_installed_CPU_v2.py','h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py'):
        before[name]=H(P/name);shutil.copy2(P/name,refs/(name+'.original_bytes.txt'))
    assert before['h1_production_control_prefix_trace_v1.py']=='84e31ea3a0e49003a8ee2671659411dfd528a9d70ef44c4ac75282fc271a59f7'
    helper=(M/'counter_runtime_source_v1.py').read_text('utf8')+'\nORIGINAL_V8_TRACE_BASE64='+repr(base64.b64encode((P/'h1_production_control_prefix_trace_v1.py').read_bytes()).decode())+'\nORIGINAL_V8_TRACE_SHA='+repr(before['h1_production_control_prefix_trace_v1.py'])+'\n\n'+(M/'trace_validation_fixture_source_v1.py').read_text('utf8')
    write(C/'h1_lifetime_goal_counter_v1.py',helper)
    s=(P/'h1_production_control_prefix_trace_v1.py').read_text('utf8')
    s=patch(s,'from sampling_trace_npz_lossless_v1 import write_trace_rows_npz,sha256_file','from sampling_trace_npz_lossless_v1 import write_trace_rows_npz,sha256_file\nfrom h1_lifetime_goal_counter_v1 import LifetimeGoalCounter, EVENTS')
    old='  old_act=self.runner.alg.act;old_step=self.vec.step;old_term=self.env.termination_manager.compute;old_reward=self.env.reward_manager.compute'
    new=old+"\n  self.lifetime_goal_counter=LifetimeGoalCounter({k:getattr(self.env.h1_phase,k).detach().cpu().numpy().copy() for k in EVENTS},self.env.h1_phase.crossed.detach().cpu().numpy().copy())"
    s=patch(s,old,new);s=patch(s,'self.total+=1','self.total+=1;self.lifetime_goal_counter.complete(self.rows[-1])')
    s=patch(s,'all_success_and_failed_control_prefixes_retained=True))','all_success_and_failed_control_prefixes_retained=True))\n  self.lifetime_goal_counter.save(self.folder)')
    write(C/'h1_production_control_prefix_trace_v1.py',s)
    s=(P/'sampling_acceleration_installed_CPU_v2.py').read_text('utf8')
    s=patch(s,"    tree=ast.parse(Path(path).read_text('utf8'))","    from h1_lifetime_goal_counter_v1 import canonical_V8_trace_tree\n    tree=canonical_V8_trace_tree(path)")
    s=patch(s,"'h1_production_control_prefix_trace_v1.py':'84e31ea3a0e49003a8ee2671659411dfd528a9d70ef44c4ac75282fc271a59f7'","'h1_production_control_prefix_trace_v1.py':"+repr(H(C/'h1_production_control_prefix_trace_v1.py'))+",\n  'h1_lifetime_goal_counter_v1.py':"+repr(H(C/'h1_lifetime_goal_counter_v1.py')))
    old="        result['V8_reward_publication_AST']=validate_V8_trace_reward_publication_only(B/'h1_production_control_prefix_trace_v1.py')"
    s=patch(s,old,old+"\n        from h1_lifetime_goal_counter_v1 import installed_counter_CPU_checks\n        result['lifetime_goal_diagnostic_CPU']=installed_counter_CPU_checks(B)")
    write(C/'sampling_acceleration_installed_CPU_v2.py',s);shutil.copy2(P/'sampling_trace_npz_lossless_v1.py',C/'sampling_trace_npz_lossless_v1.py')
    with (M/'reports/READONLY_LIFETIME_TRACE_SOURCE_V1_PREPARED_NOT_INSTALLED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump({'epoch':time.time(),'source_only':True,'prior_exact_sources':before,'candidate_files':{p.name:H(p) for p in C.glob('*.py')},'hooks':['one initial CPU snapshot before installing closures','complete existing copied row after original step success','optional counter JSON only after original index persist'],'no_new_GPU_per_control_or_actor_physics_reward_RNG_actions':True,'original_V8_step_persistence_retention_and_error_AST_still_required':True,'no_Task_payload_GO_or_current77_change':True,'next_fresh_installed_target_SDK_CPU_admission_required':True},f,indent=2)
    print(json.dumps({'source_only_candidate_ready':True,'files':len(list(C.glob('*.py'))),'not_installed':True}))
except BaseException:
    with (R/('LIFETIME_TRACE_SOURCE_V1_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump({'epoch':time.time(),'error':traceback.format_exc(),'no_same_once_retry_or_current_training_change':True},f,indent=2)
    raise
