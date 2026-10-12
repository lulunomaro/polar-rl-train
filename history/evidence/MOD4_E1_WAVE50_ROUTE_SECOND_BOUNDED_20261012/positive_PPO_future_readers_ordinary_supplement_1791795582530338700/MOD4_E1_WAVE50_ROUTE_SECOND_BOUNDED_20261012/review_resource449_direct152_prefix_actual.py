"""Read saved complete candidate and complete151 only; no decision from pending."""
from route_second_io import *

def latest(folder,pattern):return max(folder.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))

def main():
    paths=(latest(R,'RESOURCE449_CANDIDATE_COLLECTED_[0-9]*.json'),latest(R,'RESOURCE449_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json'),latest(W/'MOD4_E1_WAVE50_ROUTE_LIFECYCLE_REPAIR_20261012'/'reports','ROUTE443_CANDIDATE_COLLECTED_[0-9]*.json'),latest(W/'MOD4_E1_WAVE50_ROUTE_LIFECYCLE_REPAIR_20261012'/'reports','ROUTE443_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json'))
    c,a,b,source=[json.loads(p.read_bytes()) for p in paths]
    assert a['review_complete'] and source['review_complete'] and not c['pending'] and not b['pending']
    probe=lambda x:next(v['probe'] for v in x['cases'].values() if 'full_route_raw' in v['probe'])
    x,y=probe(b),probe(c)
    for k in ('initial','geometry','geometry_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):
        assert x[k]==y[k],('direct152_actual_initial_parameter_static_recipe_identity',k)
    old={q['env']:q for q in source['terrain']['full_route_rows']};rows=[]
    changes={g:dict(regressed=[],improved=[],unchanged_complete=[],unchanged_incomplete=[]) for g in ('forward','reverse','stand')}
    for q in a['terrain']['full_route_rows']:
        p=old[q['env']];assert p['group']==q['group'];before=bool(p['complete_episodes']);after=bool(q['complete_episodes'])
        kind='unchanged_complete' if before and after else 'regressed' if before else 'improved' if after else 'unchanged_incomplete'
        changes[q['group']][kind].append(q['env']);rows.append(dict(env=q['env'],group=q['group'],source152=p,actual_new_candidate=q))
    report=dict(epoch=time.time(),passed=True,source_collection=str(paths[2]),candidate_collection=str(paths[0]),same50_initial30q_parameters_staticrecipes_assignments_exact=True,changes=changes,all_source_candidate_valid_failed_prefixes=rows,no_GPU_replay_or_causal_ablation_claim=True,no_new_graduation_percentage_or_threshold=True,full_candidate_and_training_exposure_required_for_next_scope=True)
    path=save('RESOURCE449_DIRECT152_PREFIX_ACTUAL_REVIEW_'+str(time.time_ns())+'.json',report)
    print(json.dumps(dict(report=str(path),passed=True,changes=changes)))

if __name__=='__main__':
    try:main()
    except BaseException:save('RESOURCE449_DIRECT152_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_oldonce_replay=True));raise
