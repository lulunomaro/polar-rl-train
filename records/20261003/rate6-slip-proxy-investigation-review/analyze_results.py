"""Compare frozen shadows with archived failing runs, without changing gates."""
import hashlib, json
from pathlib import Path
import numpy as np

D=Path(__file__).resolve().parent
REPO=D.parent/'polar-rl-train'
results=[]
for model in (16929,17834):
    p=D/f'model{model}_seed20261002_shadow15s.json'
    retry=D/f'model{model}_seed20261002_shadow15s_retry1.json'
    if not p.exists() and retry.exists() and retry.stat().st_size:p=retry
    if not p.exists(): continue
    old_path=next((REPO/f'records/20261003/rate6-model{model}-regression').glob('*_rate.json'))
    old=json.loads(old_path.read_text());new=json.loads(p.read_text());shadow=new['slip_shadow']
    diffs={k:float(np.max(np.abs(np.asarray(v)-np.asarray(new['per_environment'][k])))) for k,v in old['per_environment'].items()}
    same_initial={k:old[k]==new[k] for k in ['checkpoint','seed','steps','profile','group_ids','reset_joint_pos_before_physics','reset_root_before_physics']}
    gids=np.asarray(new['group_ids']);groups=[]
    for gid in (7,8):
        ids=np.flatnonzero(gids==gid);r=dict(group_id=gid,environment_ids=ids.tolist(),original_group=new['groups'][gid],mean={},range={},loaded_mean_range={},per_environment={})
        for key,rows in shadow['per_environment_mean'].items():
            a=np.asarray(rows)[ids];r['mean'][key]=a.mean(0).tolist();r['range'][key]=[a.min(0).tolist(),a.max(0).tolist()];r['per_environment'][key]=a.tolist()
            loaded=np.asarray(shadow['per_environment_loaded_mean'][key])[ids]
            r['loaded_mean_range'][key]=[loaded.min(0).tolist(),loaded.max(0).tolist()]
        r['loaded_fraction_range']=[np.asarray(shadow['loaded_fraction'])[ids].min(0).tolist(),np.asarray(shadow['loaded_fraction'])[ids].max(0).tolist()]
        r['original_numeric_slip_limit_m_s']=.15
        r['correct_reference_both_wheels_within_original_numeric_limit_count']=int(np.sum(np.all(np.asarray(shadow['per_environment_mean']['link_reference_slip'])[ids]<=.15,axis=1)))
        r['diagnostic_not_a_new_skill_pass']=True
        groups.append(r)
    result=dict(model=model,original_report_sha256=hashlib.sha256(old_path.read_bytes()).hexdigest(),diagnostic_report_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),same_initial=same_initial,original_per_environment_max_abs_diff=diffs,original_fields_bit_exact=all(v==0 for v in diffs.values()),old_skill_pass=old['spin_skill_pass'],replay_original_skill_pass=new['spin_skill_pass'],metadata=shadow['metadata'],wheel_com_body_range_m=[np.asarray(shadow['wheel_com_body_m']).min(0).tolist(),np.asarray(shadow['wheel_com_body_m']).max(0).tolist()],frame_error_max_m_s={k:float(np.max(shadow['per_environment_max'][k])) for k in ['velocity_reference_error','link_vs_com_local_error','link_vs_com_world_error']},groups=groups,trace_file=shadow['trace_file'],trace_sha256=shadow['trace_sha256'])
    results.append(result)
    print(json.dumps({k:result[k] for k in ['model','same_initial','original_fields_bit_exact','frame_error_max_m_s','wheel_com_body_range_m']},ensure_ascii=False))
    for g in groups: print(json.dumps(dict(model=model,group=g['group_id'],ranges=g['range'],loaded_fraction_range=g['loaded_fraction_range']),ensure_ascii=False))
(D/'REVIEW.json').write_text(json.dumps(dict(original_reports_and_gates_retained=True,production_or_PPO_modified=False,results=results),ensure_ascii=False,indent=2),encoding='utf8')
