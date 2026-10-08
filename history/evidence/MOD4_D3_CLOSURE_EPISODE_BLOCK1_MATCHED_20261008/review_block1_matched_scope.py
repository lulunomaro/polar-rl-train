"""Review already completed same-clock D3 cases, preserving all original verdicts."""
from pathlib import Path
import json,time,math,statistics,sys,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sys.path.insert(0,str(D.parent/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target

def facts(p,k):
    e=evidence(p,'spin' if k=='world' else k,15);assert e['pass_'],e
    a=p['frozen_architecture_audit'];s=p['sensor_actual_manager_audit'];d=p['feedback_delay_recipe']
    assert a['variant']=='A0' and a['actual_command_error']==0 and a['optimizer_updates']==0 and not a['actor_receives_teacher'] and not a['actor_receives_critic']
    assert s['actor35'] and s['critic38_clean'] and s['command_lastaction_mode_wheel_slots_exact'] and s['same_tick_draws_unchanged'] and s['formula_max_error']<=2e-6
    assert d['profile']=='control_0_10ms_v1' and d['control_period_us']==10000 and d['requested_delay_us']==[0,10000] and d['action_delay_us']==0
    ages={}
    for channel,row in s['actual_feedback_sample_apply'].items():
        assert row['control_period_us']==10000 and row['apply_tick']==1500
        assert all(age in (0,10000) for age in row['actual_age_us'])
        assert row['actual_age_us']==[(row['apply_tick']-t)*10000 for t in row['actual_sample_tick']]
        assert row['actual_age_us']==row['requested_delay_us'] and all(row['warmup_valid'])
        ages[channel]={str(t):row['actual_age_us'].count(t) for t in (0,10000)}
    out=dict(v4=e,closure_mm=1000*p['max_closure_after_grace_m' if k=='flat' else 'max_closure_m'],actual_delay_age_counts_at_final_tick=ages,original_flags={n:p.get(n) for n in ('strict_pass','strict_pass_window','strict_pass_window_5ms','physical_smoke_pass','spin_skill_pass','spin_skill_pass_legacy_reference')})
    if k=='flat':
        out['straight']=[dict(command=g['command_vx'],error=g['vel_error'],steady_error=g['steady_vel_error']) for g in p['groups'] if g['profile']=='constant' and abs(g['command_vx'])==1.5]
    if k=='spin':
        out['pure4pi']=[]
        for g in p['groups']:
            if g['profile']=='spin' and abs(abs(g['wz'])-4*math.pi)<1e-6:
                values=[p['per_environment']['yaw_rate'][i] for i,gid in enumerate(p['group_ids']) if gid==g['group_id']]
                out['pure4pi'].append(dict(command=g['wz'],passed=sum(abs(v-g['wz'])<=.2 for v in values),count=len(values),mean=statistics.mean(values),values=values))
    if k=='world':
        w=target(p,.5);rows=w['rows'];assert len(rows)==64
        out.update(world_target=w,passed=sum(row['pass_'] for row in rows),count=64,max_abs_cross=max(abs(row['cross_m_s']) for row in rows),along_range=[min(row['along_m_s'] for row in rows),max(row['along_m_s'] for row in rows)],directions=[dict(yaw=y,passed=sum(row['pass_'] for row in rows if row['command_yaw_rad_s']==y),count=sum(row['command_yaw_rad_s']==y for row in rows)) for y in (-2.,-1.,1.,2.)])
    return out

block=read(R/'BLOCK1_EXISTING_RECEIPT_VERIFIED.json');ev=read(R/'BLOCK1_EVALUATOR_SCOPE_EVIDENCE.json')
assert not block['attention'] and not ev['attention']
assert block['own_fullsave']['sha256']=='ac20b24fc75f3b22c340303a85b0936c450ce9854f0419fbcc363c4ccbdc0e31'
assert block['block1']['health']['version']==3 and block['block1']['health']['integrity_task_reset_events']==0 and block['block1']['health']['closure_episode_reset_events']==1 and not block['block1']['health']['legacy_single_peak_2mm_pass']
jobs={j['id']:j for j in ev['jobs']}
report=dict(epoch=time.time(),scope='3060 same-platform2.5ms/TGS32-4/A0/white_v3/seed20261002/actor-noise+bias/0-10ms feedback/flat80-spin88-world88/1500control15s',block1=block['block1'],charged_once_seconds=block['charged_once_seconds'],source_count=block['source_count'],snapshot_count=block['snapshot_count'],anchor25425={},candidate26500={},pairs=[],returned_files=[],new_probe_or_PPO=0,budget_operations=0,cross_host_dynamic_bitexact_claimed=False,full_D3_20_40ms_or_dualseed_allprofile_graduation_claimed=False)
for k in ('flat','spin','world'):
    cases={}
    for role,prefix,sha in [('anchor25425','10-anchor-','b88b66e974e6f4a5e17fa6bcc7f2311224d09c9b63ef0ff8c7c5e69ea2402e1b'),('candidate26500','20-b1-',block['own_fullsave']['sha256'])]:
        job='clk2500-closure-episode-d3-'+prefix+k;j=jobs[job];folder=R/'windows'/job
        assert j['complete'] and j['result']['exit_code']==0 and not j['result']['errors'] and not j['result']['error_files']
        p=read(folder/'probe.json');m=read(folder/'manifest.json');res=read(folder/'result.json')
        assert p==j['probe'] and m==j['manifest'] and res==j['result']
        assert res['checkpoint']['sha256']==sha and res['checkpoint']['finite_tensors']==84 and m['artifacts']['checkpoint']['sha256']==sha
        assert m['steps']==p['steps']==res['steps']==1500 and p['seed']==m['seed']==res['seed']==20261002 and m['profile']==res['profile']=='white_v3'
        assert m['physics_dt_s']==res['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
        assert m['artifacts']['runtime']['sha256']==res['runtime_archive_sha256']=='56f6ac8fe847b27e4a59e679b6dba99912652efe6b077d255f85754963fd359d'
        assert m['no_learning'] and not m['canonical_write_authority']
        for name,h in j['sha256'].items():
            raw=(folder/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==h
            report['returned_files'].append(dict(job=job,name=name,sha256=h,bytes=len(raw),Windows_download_exact=True))
        cases[role]=(p,m,res);report[role][k]=facts(p,k)
    b,bm,_=cases['anchor25425'];n,nm,_=cases['candidate26500']
    params=lambda p:p.get('initial_parameter_audit') or p.get('mild_initial_parameters')
    pair=dict(kind=k,root_exact=b['reset_root_before_physics']==n['reset_root_before_physics'],q_exact=b['reset_joint_pos_before_physics']==n['reset_joint_pos_before_physics'],parameters_exact=params(b)==params(n),probe_exact=b.get('probe_sha256')==n.get('probe_sha256'),runtime_exact=bm['artifacts']['runtime']==nm['artifacts']['runtime'],sensor_recipe_exact=b['sensor_recipe']==n['sensor_recipe'],feedback_delay_recipe_exact=b['feedback_delay_recipe']==n['feedback_delay_recipe'],delay_final_age_assignment_exact=b['sensor_actual_manager_audit']['actual_feedback_sample_apply']==n['sensor_actual_manager_audit']['actual_feedback_sample_apply'])
    assert all(v for key,v in pair.items() if key!='kind'),pair;report['pairs'].append(pair)
def summary(role):
    a=report[role]
    return dict(world={k:v for k,v in a['world'].items() if k in ('passed','count','max_abs_cross','along_range','directions')},straight=a['flat']['straight'],pure4pi=[{k:v for k,v in row.items() if k!='values'} for row in a['spin']['pure4pi']],closure_mm={k:a[k]['closure_mm'] for k in ('flat','spin','world')})
report['summary']={role:summary(role) for role in ('anchor25425','candidate26500')}
report['cost']={role:dict(process_wall_seconds=sum(jobs['clk2500-closure-episode-d3-'+prefix+k]['result']['physics_process_wall_seconds'] for k in ('flat','spin','world')),transfer_seconds=sum(jobs['clk2500-closure-episode-d3-'+prefix+k]['result']['transfer_seconds'] for k in ('flat','spin','world'))) for role,prefix in [('anchor25425','10-anchor-'),('candidate26500','20-b1-')]}
report['decision']=dict(current_0_10ms_same_platform_behavior_scope_accepted=True,remaining_2h_blocks_continue_without_evaluator_wait=True,one_closure_local_reset_did_not_abort_entire_learning=True,peak_mm=1000*block['block1']['health']['max_closure_error_m'],original_legacy_closure_flag_preserved=True,no_additional45min_clock_trial=True,not_a_new_global_numerical_threshold=True,no_skill_graduation_from_checkpoint_alone=True)
(R/'BLOCK1_MATCHED_D3_SCOPE_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(summary=report['summary'],cost=report['cost'],decision=report['decision']),ensure_ascii=False))
