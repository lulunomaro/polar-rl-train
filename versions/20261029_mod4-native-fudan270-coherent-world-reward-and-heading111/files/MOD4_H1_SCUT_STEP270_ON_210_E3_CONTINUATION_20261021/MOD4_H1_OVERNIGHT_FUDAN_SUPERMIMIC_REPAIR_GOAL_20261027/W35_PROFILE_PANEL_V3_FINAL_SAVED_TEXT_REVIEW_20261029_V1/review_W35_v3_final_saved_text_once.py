"""Saved JSON and three pinned Python TEXT definitions only; never import them.

No model/PT/NPZ/gz/raw/SDK/GPU/remote IO. No new evaluation or promotion.
"""
import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import time
import traceback

D=Path(__file__).resolve().parent;L=D.parent
FINAL=L/'W35_PROFILE_PANEL_V3_NORMAL_TERMINAL_READONLY_UNUSED_SOURCE_20261029_V1/reports/W35_PANEL210_V3_NORMAL_TERMINAL_FULLTEXT_RETURNED_ACTUAL.json'
COMP=L/'W35_PROFILE_PANEL210_TENSORDICT_SNAPSHOT_REPAIR_UNUSED_SOURCE_20261029_V3/w35_profile_env_domain_panel_v1.py'
WORKER=COMP.parent/'evaluate_W35_adapted92_profile_env_domain_panel_UNUSED_once_v2_queue_receipt.py'
MATH=L/'W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/retained_flat_command_math.py'
EXPECTED_COMP='75d683ad48cf8d3981f5490e93db31eb68fb4dd067945113e89f7c414bf2e99e'
EXPECTED_WORKER='e736e61b87898af1db002ea5a1f8b9a1954b89998dda2c8a4b97ba5244478104'
MODE_GROUPS=dict(gentle=(0,),standing=(1,),straight=(2,3),moving_world_yaw=(4,5),eligible_other=(6,))


def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
    with (D/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def input_text(path):
    raw=path.read_bytes();return raw,dict(path=str(path),bytes=len(raw),SHA=H(raw),scope='saved JSON or semantic Python text only; no referenced binary followed')
def fraction(n,d):return n/d if d else None


def main():
    raw,receipt=input_text(FINAL);v=json.loads(raw);t=v['original_terminal'];r=t['result']
    records={x['relative']:x for x in v['complete_original_own_UTF8']}
    panel_row=records['frozen_regression/W35_PROFILE_ENV_DOMAIN_PANEL_ACTUAL.json']
    assert H(panel_row['UTF8'].encode('utf-8'))==panel_row['SHA']
    p=json.loads(panel_row['UTF8']);profiles=p['profile_phase_metrics'];conditions=p['condition_phase_metrics']
    cr,comp_receipt=input_text(COMP);wr,worker_receipt=input_text(WORKER);mr,math_receipt=input_text(MATH)
    assert H(cr)==EXPECTED_COMP and H(wr)==EXPECTED_WORKER
    source=cr.decode();tree=ast.parse(source);math_source=mr.decode()
    fragments={n.name:ast.get_source_segment(source,n) for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name in ('condition_summary','observe','terminal')}
    mode_line=next(x.strip() for x in wr.decode().splitlines() if 'mode=torch.zeros' in x)
    assert 'standing=(1,)' in fragments['condition_summary'] and 'moving_world_yaw=(4, 5)' in fragments['condition_summary']
    assert "command[moving,0]=torch.cos" in math_source and 'command[standing]=0.' in math_source
    checks={}
    def check(name,value):checks[name]=bool(value);assert value,name
    check('own_final_wait_out_release_integrity',v['actual_terminal_allownout_private_release'] and v['integrity_errors']==[] and t['actual_worker_waited'] and t['returncode']==0 and not t['deadline_terminated'] and t['private_EX_released'])
    check('frozen_execution_complete600_100_500',v['passed_original_frozen_execution'] and v['requested600_controls_complete'] and r['controls']==r['requested_controls']==600 and r['warmup_controls']==100 and r['steady_controls']==500 and not r['wall_time_limited'])
    check('mean_core_norm_STD_17Adam_unchanged',r['actual_mean_policy'] and r['core_actor_critic_STD_norm_optimizer_literal_unchanged'] and r['all17_Adam_steps']==648360 and r['no_optimizer_step_no_norm_update'])
    check('no_original_worker_errors',t['original_error'] is None and t['original_worker_errors']==[])
    check('actual_source_same',p['source_SHA']==r['source_SHA']=='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f')
    rr=json.loads(records['frozen_regression/ACTUAL_ORIGINAL_N20K_W35_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json']['UTF8'])
    nn=json.loads(records['frozen_regression/ACTUAL_NATIVE24_W35_40050_MEAN.json']['UTF8'])
    qq=json.loads(records['frozen_regression/ACTUAL_NATIVE24_W35_PROFILE_PANEL_CLOCK_QUEUE_ACTUAL.json']['UTF8'])
    check('actual_fullrestore_original_native24',rr['passed'] and rr['source_SHA']==r['source_SHA'] and rr['Adam_step']==648360 and nn['passed'] and [nn[k] for k in ('controls','physics_callbacks','feedback_samples')]==[24,192,48])
    check('actual_panel_native24_queue_trace_source',qq['passed'] and [qq[k] for k in ('controls','physics_callbacks','feedback_samples')]==[24,192,48] and qq['queue_apply_calls_per_group']=={'legs':192,'wheels':192} and qq['actual_first24_trace_controls']==list(range(1,25)) and qq['panel_component_SHA']==EXPECTED_COMP and qq['panel_worker_SHA']==EXPECTED_WORKER)
    check('actual_each_group_counter_difference',all(qq['queue_calls_after24'][k]-qq['queue_calls_at_start'][k]==192 for k in ('legs','wheels')))
    by={(x['phase'],x['condition']):x for x in conditions};pr={(x['phase'],x['profile']):x for x in profiles}
    check('all126_profile_and18_condition_rows',len(pr)==126 and len(by)==18)
    for phase,total in (('whole',12000000),('warmup',2000000),('steady',10000000)):
        check(phase+'_population_control_total',by[phase,'all']['population_control_denominator']==total and sum(pr[phase,i]['population_control_denominator'] for i in range(42))==total)
        check(phase+'_condition_partition',sum(by[phase,k]['population_control_denominator'] for k in MODE_GROUPS)==total)
        for group,modes in MODE_GROUPS.items():
            check(phase+'_'+group+'_profile_denominator',sum(pr[phase,i]['population_control_denominator'] for i in range(42) if i%7 in modes)==by[phase,group]['population_control_denominator'])
    check('whole_counts_equal_warmup_plus_steady',all(pr['whole',i]['population_control_denominator']==pr['warmup',i]['population_control_denominator']+pr['steady',i]['population_control_denominator'] for i in range(42)))
    criteria=json.loads(records['frozen_regression/ORIGINAL_W35_TASK_COMMAND_AND_TERMINATION_CRITERIA.json']['UTF8'])
    timeout_flags={x['name']:x['time_out'] for x in criteria['criterion_terms']}
    reviewed=[]
    for row in conditions:
        x=dict(row);phase=row['phase'];all_den=by[phase,'all']['population_control_denominator'];u=row['unique_exposed_env_denominator']
        x['share_of_actual_population_controls']=fraction(row['population_control_denominator'],all_den)
        x['observed_unique_terminated_env_fraction']=fraction(row['unique_env_with_terminated_mask'],u)
        x['observed_unique_counter_turn_env_fraction']=fraction(row['unique_env_with_complete_signed_cycle'],u)
        x['fraction_scope']='descriptive ever-observed IDs within actual exposed IDs, not independent episode/command success rate or graduation'
        reviewed.append(x)
    family=[]
    for phase in ('whole','steady'):
        for f in range(6):
            rows=[pr[phase,i] for i in range(f*7,(f+1)*7)]
            family.append(dict(phase=phase,family=rows[0]['family'],population_controls=sum(x['population_control_denominator'] for x in rows),actual_modes=[x['mode'] for x in rows if x['population_control_denominator']],unique_env_union=None,union_not_reconstructable_by_summing_profile_unique_counts=True))
    reason=[]
    for phase in ('whole','warmup','steady'):
        for name,timeout in timeout_flags.items():
            rows=[pr[phase,i] for i in range(42)]
            reason.append(dict(phase=phase,name=name,original_timeout=timeout,events=sum(x['reason_events'][name] for x in rows),per_profile_unique_counts=[dict(profile=x['profile'],family=x['family'],mode=x['mode'],unique_env=x['reason_unique_env'][name]) for x in rows if x['reason_unique_env'][name]],global_unique_not_obtained_by_summing_profiles=True))
    sign=[]
    for phase in ('whole','steady'):
        moving_rows=[pr[phase,i] for i in range(42) if i%7 in (4,5) and pr[phase,i]['population_control_denominator']]
        check(phase+'_moving_only_two_plane_profiles',len(moving_rows)==2 and {x['profile'] for x in moving_rows}=={11,12})
        a,b=moving_rows;g=by[phase,'moving_world_yaw']
        sign.append(dict(phase=phase,negative=a,positive=b,any_moving_unique_env=g['unique_exposed_env_denominator'],any_counter_turn_unique_env=g['unique_env_with_complete_signed_cycle'],both_sign_exposure_unique_env=a['unique_exposed_env_denominator']+b['unique_exposed_env_denominator']-g['unique_exposed_env_denominator'],both_sign_counted_turn_unique_env=a['unique_env_with_complete_signed_cycle']+b['unique_env_with_complete_signed_cycle']-g['unique_env_with_complete_signed_cycle'],intersection_definition='two-set inclusion/exclusion only; recorded heading-turn bins, not per-command world-progress success'))
    uid=p['actual_local_episode_uid_final'];check('run_local_uid_shape',len(uid)==20000 and all(type(n)is int and n>=0 for n in uid))
    uid_stats=dict(total_successful_reset_id_counter_increments=sum(uid),unique_env_with_reset_counter_positive=sum(n>0 for n in uid),zero_reset_counter_env=sum(n==0 for n in uid),max_local_uid=max(uid),histogram=dict(sorted(Counter(uid).items())),not_failure_rate_or_unique_episode_denominator=True)
    all_whole=by['whole','all'];standing=by['whole','standing'];moving=by['whole','moving_world_yaw']
    standing_semantics=dict(source_label='standing',exact_component_group='profile % 7 == 1',classifier_source=mode_line,source_command_intention='sample_commands sets command[standing]=0, but independent measured true-zero command metrics are not stored in allowed summary',complement_of_moving=False,standing_population_controls=standing['population_control_denominator'],nonmoving_complement_population_controls=all_whole['population_control_denominator']-moving['population_control_denominator'],true_zero_command_filter_metrics_pending=True)
    check('standing_not_nonmoving_complement',standing_semantics['standing_population_controls']!=standing_semantics['nonmoving_complement_population_controls'])
    limitations=[
      'No saved actual per-env/profile error distribution/quantiles or required numerical graduation thresholds; scalar means and exposure counts do not certify skill.',
      'Per-condition unique ID sets overlap when an environment changes profile; never sum unique counts over profiles/conditions/phases. Actual population-control exposures partition controls.',
      'Recorded signed-turn counter requires measured net yaw>=2pi, live, same profile/phase/episode. It does not track command-instance/resample UID or fixed world-direction continuity, so it may span same-profile command resampling. Keep original complete_signed_cycle_events label; do not promote it to original per-command/cycle world-progress success.',
      'No cycle endpoint world displacement/duration summary is saved. Instantaneous moving_world_progress_abs_error is |actual projected velocity-.5|, not complete-cycle progress error.',
      'Original command vx=cos(theta-alpha),vy=0 yields ideal projected world velocity cos²(theta-alpha), so instantaneous target-.5 deviation can be nonzero even with exact command tracking. Uniform-angle analytic mean 1/pi is an ideal reference only, not actual sampling/policy evidence.',
      'Standing is the source mode1 bin, not all nonmoving. Gentle and other nonmoving commands may be nonzero. No independently filtered actual zero-command metrics can be obtained without prohibited trace reads.',
      'Only plane has retained straight/moving exposure. Other four G3 families have gentle/standing only in this window; no pure high-rate spin or unobserved command/family acceptance is claimed.',
      'Largest live duration is a maximum over IDs, not an every-ID sustained criterion. No survival/duration distribution or complete same-command duration is available from aggregate text.',
      'Reset/termination/truncation observations are events or scoped unique IDs, not independent trials. rough_route_boundary remains an original timeout; no reclassification as non-timeout skill failure.',
      'Trace is selected profile/IDs and sampled controls. No NPZ/gzip payload was opened or validated; trace completeness, pack127/xi/contact/actual torque and full WM dataset qualification remain unproved.',
    ]
    out=dict(epoch=time.time(),kind='W35_v3_final_saved_text_profile_denominator_review_v1',input_receipts=[receipt,comp_receipt,worker_receipt,math_receipt],panel_embedded_text_receipt={k:x for k,x in panel_row.items() if k!='UTF8'},
      source_semantic_fragments=fragments,source_retained_command_math_UTF8=math_source,standing_semantics=standing_semantics,
      actual_runtime_and_integrity_checks=checks,execution_summary={k:x for k,x in r.items() if not isinstance(x,(list,dict))},original_terminal_without_result={k:x for k,x in t.items() if k!='result'},
      condition_reviews=reviewed,original_profile_phase_metrics=profiles,family_exposure=family,original_reason_event_review=reason,signed_bin_unique_intersections=sign,run_local_reset_uid_statistics=uid_stats,
      original_native24=nn,original_fullrestore=rr,actual_panel_native24=qq,original_termination_criteria=criteria,
      trace_summary=dict(controls=p['trace_controls'],uncompressed_bytes=p['trace_uncompressed_bytes'],retention_limited=p['trace_retention_limited'],payloads_not_read=True),
      original_panel_static_pending_note=p['pending'],static_note_reconciliation='Original source-generated pending string retained verbatim; actual returned fullrestore/native24/queue/final checks above now pass. Skill/WM qualification remains pending.',
      evidence_limits=limitations,skill_graduation=False,complete_WM_dataset=False,no_new_GPU_model_SDK_or_remote=True,ordinary_Git_pending_root=True,no_trial_tag_created=True)
    put('W35_V3_FINAL_PROFILE_ENV_TEXT_REVIEW_COMPLETE_ACTUAL.json',out)
    md=['# W35 v3：最终冻结评测文本审查','',
      '实际600 controls/12s（100 warmup/2s、500 steady/10s）完整收尾；mean模型、actor/critic/STD/norm及17Adam648360不变。原fullrestore、24/192/48和legs/wheels各192/trace1..24正证明、wait/out/private release与integrity[]全部成立。技能毕业与完整WM数据资格仍pending。','',
      '仅保存JSON和3份已冻结语义Python文本被读取；Python只AST解析，未import/执行。NPZ/gz/PT/raw、SDK/GPU/remote均未访问。','',
      '## 条件分组与实际分母','',
      '|phase / source condition|人口control|独立暴露env|forward MAE|yaw MAE|height MAE|瞬时world-progress MAE|turn事件 / 有turn的独立env|','|---|---:|---:|---:|---:|---:|---:|---:|']
    def fmt(x):return '未定义' if x is None else f'{x:.6f}'
    for x in reviewed:
      if x['phase']=='warmup':continue
      means=x['means'];md.append(f"|{x['phase']} / {x['condition']}|{x['population_control_denominator']}|{x['unique_exposed_env_denominator']}|{fmt(means['forward_abs_error'])}|{fmt(means['yaw_abs_error'])}|{fmt(means['height_abs_error'])}|{fmt(means['moving_world_progress_abs_error'])}|{x['complete_signed_cycle_events']} / {x['unique_env_with_complete_signed_cycle']}|")
    md += ['',f"moving占全窗{moving['population_control_denominator']/12000000:.4%}，steady占{by['steady','moving_world_yaw']['population_control_denominator']/10000000:.4%}。全人口MAE不能代替moving/straight表现。每行unique env是该条件实际暴露过的ID集合，条件间有交叉，不能相加当20000个独立人。",'',
      f"standing标签在实际75d source明确是mode1（%7==1），分母{standing['population_control_denominator']}；moving补集是{standing_semantics['nonmoving_complement_population_controls']}，两者不同。gentle/straight/eligible_other也在补集中。源码意图standing时command置0；但本允许文本没有逐控制真实zero-command筛选指标，报告不把source-label自动升级成实测纯零命令验收。",'',
      '## world-progress与turn计数的限制','',
      'source command：moving BODY vx=cos(theta-alpha)、vy=0，目标V=.5；yaw magnitude按1+u生成1–2 rad/s（profile literal yaw12不能擅读为固定1.2）。理想跟踪时world投影速度=cos²(theta-alpha)，瞬时|projection-.5|本来也非零；uniform-angle理想均值1/pi仅是解析参考。实测.305882/.303850不是完整周期进度误差，既不能据此判moving失败，也不能据此判理想跟踪。', '',
      '532是源码记录的signed-turn事件，491是至少一次此计数的独立env，二者不是成功episode数量。counter在同profile/phase/episode且live时净角达到2pi计数；没有command-instance UID，因此同profile resampling可能跨不同world_direction/target。也未保存周期投影位移/实际时长汇总，不能声称完整原world-progress技能已验收。','']
    for x in sign:
      md.append(f"{x['phase']}: 负/正sign暴露env={x['negative']['unique_exposed_env_denominator']}/{x['positive']['unique_exposed_env_denominator']}，两sign都暴露{x['both_sign_exposure_unique_env']}；有负/正turn计数env={x['negative']['unique_env_with_complete_signed_cycle']}/{x['positive']['unique_env_with_complete_signed_cycle']}，两sign都有计数{x['both_sign_counted_turn_unique_env']}。以上用两个实际集合的inclusion/exclusion推导，仍不是per-command world-progress成功率。")
    md += ['','## 每profile覆盖（0曝光不当通过）','','|phase / index / family / mode|人口control|unique env|forward / yaw / height MAE|turn事件 / unique env|最长live秒|','|---|---:|---:|---|---:|---:|']
    for x in profiles:
      if x['phase']=='warmup' or not x['population_control_denominator']:continue
      means=x['means'];md.append(f"|{x['phase']} / {x['profile']} / {x['family']} / {x['mode']}|{x['population_control_denominator']}|{x['unique_exposed_env_denominator']}|{fmt(means['forward_abs_error'])} / {fmt(means['yaw_abs_error'])} / {fmt(means['height_abs_error'])}|{x['complete_signed_cycle_events']} / {x['unique_env_with_complete_signed_cycle']}|{x['maximum_live_continuous_seconds']:.6f}|")
    md += ['','五种G3均有gentle/standing；retained signed straight/world-yaw只在plane。所有126 profile行（含warmup和0曝光）、family人口曝光及每profile reason events/unique在完整JSON保留。family unique无法从profile unique直接相加重建，未补造。','',
      '## 原终止/timeout及域覆盖','',
      f"全窗terminated mask={all_whole['terminated_mask_events']}，独立发生terminated的env={all_whole['unique_env_with_terminated_mask']}；truncated mask事件={all_whole['truncated_mask_events']}，没有group层global unique-truncation指标。原reason flags与phase事件逐项保留；timeout不等于技能失败。",'',
      f"run-local episode UID最终值来源是保存JSON：reset-ID counter增量总计{uid_stats['total_successful_reset_id_counter_increments']}、有reset增量独立env={uid_stats['unique_env_with_reset_counter_positive']}、最大UID={uid_stats['max_local_uid']}。这是评测内reset hook计数，非原训练episode总数或失败率。",'',
      f"有界trace控制点{len(p['trace_controls'])}个、未压缩记录{p['trace_uncompressed_bytes']}B，retention_limited={p['trace_retention_limited']}；数据payload未读。本报告不能验证未打开转移中的全部action/queue/DR/pack127/force/torque，也不称可训完整WM数据。",'',
      '原panel静态pending字符串保持原文，但不能抵消已返回真实runtime正证明；最终仍缺技能阈值与完整coverage/domain验收。','', '## 尚缺条件','']
    md += ['- '+x for x in limitations]
    md += ['','本次只做文本审查，未重跑评测/模型；旧false/原标签未覆盖。新scope待root普通Git补档，不新建trial/tag。','']
    with (D/'W35_V3_FINAL_PROFILE_ENV_TEXT_REVIEW_COMPLETE.md').open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(md))
    print(json.dumps(dict(passed_text_checks=len(checks),moving_whole=moving,moving_steady=by['steady','moving_world_yaw'],standing_not_complement=standing_semantics,sign_intersections=[{k:z for k,z in x.items() if k not in ('negative','positive')} for x in sign],reset_uid=uid_stats,skill_graduation=False),ensure_ascii=False))


if __name__=='__main__':
    try:main()
    except BaseException:
        put('ORIGINAL_TEXT_REVIEW_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),passed=False,error=traceback.format_exc(),no_model_or_remote=True));raise
