"""Complete learned-vs-rule original35 pair, preserving all failed prefixes."""
from pathlib import Path
import hashlib,json,time
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports'
BASE=D.parent/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    names=['S4_RULE35_FULL1500_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json',
           'S4_FIRST_TRAINED_GATE35_FULL1500_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json']
    paths=[BASE/'reports'/names[0],R/names[1]]
    reviews=[json.loads(p.read_bytes()) for p in paths];assert all(v['passed'] for v in reviews)
    reports=[json.loads(Path(v['original_report']['local_path']).read_bytes()) for v in reviews]
    initials=[json.loads(Path(v['first_physics_initial_snapshot']['local_path']).read_bytes())['values'] for v in reviews]
    assert initials[0]==initials[1], 'Actual firstphysics root/q/params/recipes/RNG/queues pair mismatch'
    for field in ('geometry','geometry_recipe','route_scope','feedback_recipe','action_recipe','spring_recipe','gas_recipe'):
        left=reports[0][field];right=reports[1][field]
        if field=='route_scope':
            left=dict(left);right=dict(right);lq=left.pop('query_worldmesh_evidence');rq=right.pop('query_worldmesh_evidence')
            assert lq['bytes']==rq['bytes'] and lq['sha256']==rq['sha256']
        assert left==right,field
    sensor=[];draws=[]
    for report in reports:
        recipe=dict(report['sensor_recipe']);draws.append(recipe.pop('noise_draw_counts'));sensor.append(recipe)
    assert sensor[0]==sensor[1]
    differences=[]
    for old,new in zip(reviews[0]['rows'],reviews[1]['rows']):
        assert old['env']==new['env'] and old['group']==new['group']
        differences.append(dict(env=old['env'],group=old['group'],standing_no_transit_requirement=old['group']==2,
            rule_complete=old['contact_complete'],trained_gate_complete=new['contact_complete'],
            improved=not old['contact_complete'] and new['contact_complete'],
            regressed=old['contact_complete'] and not new['contact_complete'],
            rule_valid_episodes=old['all_valid_episodes'],trained_valid_episodes=new['all_valid_episodes']))
    standing=[]
    for review in reviews:
        with np.load(review['raw']['local_path'],allow_pickle=False) as z:
            root=z['root'];before=z['before_root'];terminated=z['terminated'];group=z['group_ids'];episodes=z['episode']
        row=[]
        for i in np.flatnonzero(group==2):
            valid=np.flatnonzero(episodes[:,i]==episodes[0,i]);bad=valid[terminated[valid,i]]
            if len(bad):valid=valid[valid<bad[0]]
            assert len(valid)>0
            row.append(dict(env=int(i),valid_controls=len(valid),first_ordinary_control=int(bad[0]) if len(bad) else None,
                mean_horizontal_speed_m_s=float(np.linalg.norm(root[valid,i,7:9],axis=-1).mean()),
                mean_abs_yaw_rate_rad_s=float(abs(root[valid,i,12]).mean()),
                displacement_from_actual_first_root_m=float(np.linalg.norm(root[valid[-1],i,:2]-before[0,i,:2]))))
        standing.append(row)
    routing=json.loads((R/'S4_FIRST_TRAINED_GATE35_SHARED_ROUTING_ADMITTED_s4_first_gate_final35_full1500_v1.json').read_bytes());assert routing['passed']
    result=dict(epoch=time.time(),passed_complete_pair_CPU_review=True,
        baseline_rule_review=dict(path=str(paths[0]),sha256=H(paths[0])),
        own_trained_gate_review=dict(path=str(paths[1]),sha256=H(paths[1])),
        source_SHA=reviews[1]['source_SHA'],same_actual_firstphysics_rootq30_allphysicalparams_assignment_staticrecipes_capturedRNG_queues_exact=True,
        same_original35_tenwaves_040approach_200mmafter_15s_6000callbacks=True,newnamespace_query_paths_separate_actual_query_bytes_SHA_exact=True,
        original_query_contact_COM_hardware_tolerances_unchanged=True,
        baseline_counts=dict(forward=reviews[0]['forward_complete'],reverse=reviews[0]['reverse_complete'],ordinary=reviews[0]['ordinary']),
        trained_counts=dict(forward=reviews[1]['forward_complete'],reverse=reviews[1]['reverse_complete'],ordinary=reviews[1]['ordinary']),
        improved_envs=[v['env'] for v in differences if v['improved']],regressed_envs=[v['env'] for v in differences if v['regressed']],
        all_valid_failed_unfinished_prefixes=differences,standing_rule=standing[0],standing_trained_gate=standing[1],
        standing_no_transit_requirement_not_silently_credited_as_perfect_tracking=True,
        sensor_draw_counts_at_own_final_phase=draws,rule_and_gate_source_separate_not_relabelled=True,
        trained_gate_routing=routing,no_new_PPO_or_budgetwrite=True,
        original35_pair_only_not_flat_spin_world_retention_or_full_S5_fair_MoE=True,
        automatic_second_gate_learning_admitted=False,qualification_claimed=False)
    out=R/'S4_FIRST_TRAINED_GATE35_COMPLETE_DIRECT_RULE_PAIR_CPU_REVIEW.json';assert not out.exists()
    out.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:result[k] for k in ('passed_complete_pair_CPU_review','baseline_counts','trained_counts','improved_envs','regressed_envs')}))

if __name__=='__main__':main()
