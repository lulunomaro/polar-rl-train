"""CPU preparation review against actual completed first-scope files, not future passes."""
from pathlib import Path
import sys,json,os,time,copy,traceback,ast
os.environ['CUDA_VISIBLE_DEVICES']=''
import second_root_owned_transport_common_v1 as t
from left_second_saved_positive_CPU_math_v1 import verify_positive_state,verify_latest_health
sys.path.insert(0,str(t.P))
from second_target_CPU_pure_guard_v2 import tree_sha,KEY
def main():
    import torch,numpy as np
    assert not torch.cuda.is_initialized();rng=torch.get_rng_state().clone();np_rng=tree_sha(np.random.get_state())
    base=t.W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013'
    ownpath=base/'left_formal_final_actual/0_model_32635.pt';parentpath=base/'left_fresh_retained_postexit_actual/4_model_own_repaired0PPO.pt'
    assert t.sha(ownpath)==t.SOURCE_SHA and t.sha(parentpath)=='06a1ea73a943a7bd6fbb3626077f55b9ac06521f814f956cfb1d546074bbf5c2'
    own=torch.load(ownpath,map_location='cpu',weights_only=False);parent=torch.load(parentpath,map_location='cpu',weights_only=False)
    before=tree_sha(own);positive=verify_positive_state(own,parent);assert positive['saved_updates']==189 and positive['optimizer_step_delta']==3780 and positive['saved_controls']==4536
    health=json.loads((base/'left_formal_final_actual/5_CLOCK_TRAINING_HEALTH.json').read_bytes());verify_latest_health(health)
    negatives=[]
    cases=[('zero_update_is_not_saved_PPO',copy.deepcopy(parent)),('left_metadata_reinitialized',copy.deepcopy(own)),('one_Adam_step_wrong',copy.deepcopy(own)),('actor_unchanged',copy.deepcopy(own)),('wrong_perenv_N',copy.deepcopy(own))]
    cases[1][1][KEY]['profile']='wrong'
    cases[2][1]['optimizer_state_dict']['state'][0]['step']-=1
    cases[3][1]['actor_state_dict']=copy.deepcopy(parent['actor_state_dict'])
    cases[4][1]['sensor_DR_state']['n']=512
    for name,c in cases:
        try:verify_positive_state(c,parent)
        except AssertionError:negatives.append(dict(case=name,strict_rejected=True))
        else:raise AssertionError(('Badpositivefixtureaccepted',name))
    for field in ('nonfinite_observed','termination_reason_coverage_exact','truncation_reason_coverage_exact'):
        bad=copy.deepcopy(health);bad[field]=not bad[field]
        try:verify_latest_health(bad)
        except AssertionError:negatives.append(dict(case='wrong_health_'+field,strict_rejected=True))
        else:raise AssertionError(('Badhealthaccepted',field))
    names=('left_second_saved_positive_CPU_math_v1.py','read_left_second_formal_compact_actual.py','collect_left_second_positive_saved_bounded_actual.py','review_left_second_positive_saved_local_CPU_actual.py','collect_left_second_startup_typed13_bounded_actual.py')
    compiled=[];remote=[]
    for name in names:
        p=t.D/name;source=p.read_text();compile(source,str(p),'exec');compiled.append(dict(path=str(p),bytes=p.stat().st_size,sha256=t.sha(p)))
        tree=ast.parse(source)
        assert not any(isinstance(n,ast.ImportFrom) and n.module and 'once' in n.module for n in ast.walk(tree))
    import read_left_second_formal_compact_actual as reader
    import collect_left_second_positive_saved_bounded_actual as collector
    import collect_left_second_startup_typed13_bounded_actual as startup
    for label,module in [('compact',reader),('positive',collector),('startup13',startup)]:
        code='CONTEXT={}\n'+module.CODE;compile(code,label,'exec');remote.append(dict(label=label,compiled_remote_stdin=True,code_bytes=len(code.encode()),uses_original_full_isaaclab_python=t.PY))
    assert tree_sha(own)==before and t.sha(ownpath)==t.SOURCE_SHA
    assert torch.equal(torch.get_rng_state(),rng) and tree_sha(np.random.get_state())==np_rng and not torch.cuda.is_initialized()
    out=dict(epoch=time.time(),passed=True,actual_completed_first_scope_positive_math_fixture=positive,fixture_own_source=dict(path=str(ownpath),sha256=t.SOURCE_SHA),fixture_parent_source=dict(path=str(parentpath),sha256=t.sha(parentpath)),negative_cases=negatives,compiled_sources=compiled,compiled_remote_stdin=remote,source_tree_SHA_unchanged=True,no_CPU_numpy_RNG_draw=True,no_CUDA_initialized=True,no_SSH_or_remote_source_write_or_budget_transaction=True,new_second_actual_save_not_yet_collected_or_CPU_verified=True,first_actual_fixture_not_relabelled_as_future_second_pass=True,all_future_collectors_readonly_and_actual_complete_only=True,pending_Git_by_root=True)
    path=t.REPORTS/'LEFT_SECOND_COMPACT_READERS_POSITIVE_MATH_CPU_PREPARED_ACTUAL.json';t.write_once(path,out)
    print(json.dumps(dict(report=str(path),negative_count=len(negatives),compiled_count=len(compiled),future_second_proof_not_claimed=True)))
if __name__=='__main__':
    try:main()
    except BaseException:t.original_error('LEFT_SECOND_READERS_PREPARATION_ORIGINAL_CPU_ERROR');raise
