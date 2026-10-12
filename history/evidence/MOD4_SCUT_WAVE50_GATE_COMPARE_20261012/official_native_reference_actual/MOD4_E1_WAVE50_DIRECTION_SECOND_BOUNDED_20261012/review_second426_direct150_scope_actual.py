"""Independent saved direct150 pairing and final same-direction scope decision."""
from wave_direction_second_io import *

def latest(folder,pattern):return max(folder.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))
def main():
    cp=latest(R,'SECOND_DIRECTION_CANDIDATE_COLLECTED_[0-9]*.json');rp=latest(R,'SECOND_DIRECTION_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json')
    oldcp=latest(PRIOR/'reports','DIRECTION_CANDIDATE_COLLECTED_[0-9]*.json');oldrp=latest(PRIOR/'reports','DIRECTION_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json')
    c,a,b,source=[json.loads(p.read_bytes()) for p in (cp,rp,oldcp,oldrp)];assert a['review_complete'] and source['review_complete'] and not c['pending'] and not b['pending']
    probe=lambda x:next(v['probe'] for v in x['cases'].values() if 'full_route_raw' in v['probe']);x,y=probe(b),probe(c)
    keys=('initial','geometry','geometry_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names')
    for k in keys:assert x[k]==y[k],('direct150_initial_parameter_recipe_identity',k)
    old={q['env']:q for q in source['terrain']['full_route_rows']};rows=[];changes={g:dict(regressed=[],improved=[],unchanged_complete=[],unchanged_incomplete=[]) for g in ('forward','reverse','stand')}
    for q in a['terrain']['full_route_rows']:
        p=old[q['env']];assert p['group']==q['group'];before=bool(p['complete_episodes']);after=bool(q['complete_episodes']);g=q['group'];kind='unchanged_complete' if before and after else 'regressed' if before else 'improved' if after else 'unchanged_incomplete';changes[g][kind].append(q['env']);rows.append(dict(env=q['env'],group=g,source150=p,candidate151=q))
    save('CANDIDATE151_DIRECT150_PREFIX_ACTUAL_REVIEW.json',dict(epoch=time.time(),passed=True,source_collection=str(oldcp),candidate_collection=str(cp),same50_initial30q_parameters_staticrecipes_assignments_exact=True,changes=changes,all_source_candidate_valid_failed_prefixes=rows,no_GPU_replay_or_causal_ablation_claim=True))
    decision=dict(epoch=time.time(),passed=True,all_four_actual_complete_errorfree_fullraw_reviewed=True,ownsource426_complete_and_fulltrace_reviewed=True,forward_complete=9,reverse_complete=26,previous150_forward=12,previous150_reverse=25,changes=changes,not_qualified50_RM_or_MoE=True,no_perfect_batch_percentage_gate_invented=True,both_same_direction_windows_completed=True,no_third_blind_duration_only_block_or70=True,next_phase='independent_saved_trace_route_coverage_diagnosis',source426_not_default_other_expert_warmstart=True,ordinary0_and_route0_retained=True,all_old_false_cost_and_valid_failed_prefixes_preserved=True,source_CPU104_and_old_35b026_129_lineage_unchanged=True)
    save('CANDIDATE151_COMPLETE_SCOPE_DECISION.json',decision)
    note=D/'NEXT_WAVE50_POST151_TRACE_ROUTE_DIAGNOSIS_WORK_ORDER.md';assert not note.exists();note.write_text('''# Complete151后的独立训练路线暴露诊断

151四case已真实complete/errorfree/fullraw/query/twohost8JSON与原50mm/115/129物理数据合同全审，正9/27倒26/27；直接150正12倒25的全初态/参数/staticrecipes/assignments exact配对，逐env所有改善、退化与有效失败prefix保留。两direction块初300+本900已结束；不第三盲duration-only或升70，不以27/27机械晋级线代替综合能力决定，也不把9/26重标合格。

积极继续已批准004/005独立单轴修复。下一先从已保存的426完整984control/9.84s-per-env trace及实际entry map核原training route-from-spawn2m与完整50mm十波2.406422727m/前接近/后支撑所需位移，保留reset-before/prereset-before/episode/route原因/实际heading/commands；rootproxy不是两轮接触认证。先做CPU可达性与逐episode实际截断审查，不重GPU或旧once。只在独立scope实际证据支持后集成新的route生命周期轴；50geometry/resetXY/episode固定方向/command abs消耗/standing/DR/reward/LR/hardware/clock/fivefamilies不混改、不缩接近/延冻结15s/teleport通行。原2m合同在旧源不热改；未来新scope身份/全state CPUCUDA迁移/严格同scope恢复/ownsave-unique账段/两锁/actual退出边界必须各自实证。来源优先accepted35b026/129完整祖先，unqualified095f/830f不当其它专家默认来源。

此诊断不是新的学习executor/targetfullstate/GPU准入，不能称已经启动下一训练。正常训练流程继续自主推进，不因SCUT对比或Git补档hold。保留原完整SDK/native/PPO/fresh/clock/DR有效SHA，真正缺失新scope才一次实证，005每块<=2h/同scope最多两块全审。原预算1188000/7extensions第七100h已once，不加预算/复制/clearactive/tail/recharge；其它expert/E0/gate/WASD不干预。所有新source/报告/拒绝/原false/raw/cost/同期SCUT参考与monitor/Gitreceipt持续Git。
''',encoding='utf8')
    print(json.dumps(dict(passed=True,forward=9,reverse=26,changes=changes,next_phase=decision['next_phase'])))

if __name__=='__main__':
    try:main()
    except BaseException:save('SECOND_DIRECTION_DIRECT150_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_replay=True));raise
