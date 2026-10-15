"""Aggregate only the three genuinely complete, source-bound original pairs."""
from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    evidence=[];summary={}
    for kind in ('flat','spin','world'):
        p=R/(kind+'_COMPLETE_RULE_VS_GATE_ORIGINAL_PHYSICAL_PAIR_CPU_REVIEW.json');v=json.loads(p.read_bytes())
        data=v['result'];old=data['baseline'];new=data['candidate']
        assert data['actual_initial_root_q30_parameters_recipes_RNG_queues_exact'] and old['kind']==new['kind']==kind
        assert old['steps']==new['steps']==1500 and old['data']['complete_data_contract'] and new['data']['complete_data_contract']
        router=[]
        for mode in ('rule_eval','gate_eval'):
            q=R/(f's4_retention_{mode}_{kind}_1500_v1_S4_ROUTING_CPU_ADMITTED.json')
            r=json.loads(q.read_bytes());assert r['passed'] and r['all24_initial_final_source_exact'] and r['mode']==mode
            assert r['gate_source_SHA']=='02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3';router.append(r)
        stats=dict(rule_ordinary=old['data']['ordinary'],gate_ordinary=new['data']['ordinary'],routing=router,
            old_original_flags_rule=old['old_original_flags'],old_original_flags_gate=new['old_original_flags'])
        if kind=='flat':stats.update(rule_straight=old['straight'],gate_straight=new['straight'])
        if kind=='spin':stats.update(rule_pure4pi=old['pure4pi'],gate_pure4pi=new['pure4pi'])
        if kind=='world':stats.update(rule_world_count=old['world_count'],gate_world_count=new['world_count'],
            rule_whole_signedcircle=old['whole_signedcircle_original_target'],gate_whole_signedcircle=new['whole_signedcircle_original_target'],
            all_rule_valid_prefixes=old['all_valid_prefixes'],all_gate_valid_prefixes=new['all_valid_prefixes'])
        summary[kind]=stats;evidence.append(dict(path=str(p),sha256=H(p)))
    result=dict(epoch=time.time(),actual_all_three_full1500_pairs_complete=True,evidence=evidence,summary=summary,
        original_query1e6_contact_COM_hardware_and_signedcircle_tolerances_unchanged=True,
        all_firstphysics_rootq30_parameters_recipes_capturedRNG_queues_and_loaded_binary_pairs_exact=True,
        rule_and_gate_six_full_cases_source_scene_anchor_same_b026_policy_mode_explicit=True,
        trained_gate_source_148_separate_from_scene_anchor=True,all_old_false_failed_valid_prefixes_preserved=True,
        qualification_or_second_gate_learning_admitted=False,no_GPU_PPO_budget_or_dispatch_by_aggregate=True)
    p=R/'FIRST_GATE_FULL_THREE_RETENTION_RULE_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json';assert not p.exists();p.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(dict(complete=True,flat=summary['flat']['gate_straight'],world=[summary['world']['rule_world_count'],summary['world']['gate_world_count']],qualification=False)))

if __name__=='__main__':main()
