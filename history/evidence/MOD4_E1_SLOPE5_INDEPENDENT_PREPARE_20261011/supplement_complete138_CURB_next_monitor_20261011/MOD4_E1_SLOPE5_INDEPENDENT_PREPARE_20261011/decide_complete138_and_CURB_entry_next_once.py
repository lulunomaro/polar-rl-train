"""Freeze observed slope scopes and prepare approved isolated CURB correction work."""
from slope_io import *
import traceback

def main():
    path=sorted(R.glob('SLOPE138_ACTUAL_REVIEW_[0-9]*.json'))[-1];review=json.loads(path.read_bytes());assert review['review_complete'] and not review['pending']
    collection=json.loads(Path(review['collection']).read_bytes());assert len(collection['cases'])==1
    case=next(iter(collection['cases'].values()));data=case['probe'];groups=next(iter(review['review'].values()))['groups']
    assert all(groups[k]['complete_envs']==groups[k]['contact_confirmed_envs']==27 for k in ('ascending','descending'))
    assert data['actual_union_ordinary']==0 and data['reason_coverage_exact'] and not data['nonfinite']
    old=json.loads((R/'SLOPE137_COMPLETE_SCOPE_DECISION.json').read_bytes())
    audit=json.loads((R/'CURB20_SAVED_ENTRY_EXPOSURE_CPU_REVIEW.json').read_bytes());assert audit['no_GPU_training_budget_or_runtime_mutation']
    row=dict(epoch=time.time(),trial_id='E1-SLOPE10-138-COMPLETE-SCOPE-DECISION-01',complete_review=str(path),complete_collection=review['collection'],source_checkpoint=old['source_checkpoint'],actual_full_raw=data['full_route_raw'],
      explicit10deg_analytic_normal_actualfloat32_query_contract_passed=True,normal_max_component_error=data['route_scope']['analytic_normal_max_abs_error'],height_tolerance_m=1e-6,normal_component_unit_tolerance=1e-6,
      scoped10deg_mirrored_frozen_behavior_accepted=True,scope_groups=groups,accepted_observed_frozen_slope_angles_deg=[5.,8.,10.],scope_candidate_frozen=True,no_mechanical10deg_PPO_needed=True,
      ordinary=0,max_closure_mm=data['max_closure_m']*1000,declared_truncations=data['actual_union_truncation'],two_reason_coverage_exact=True,physical_process_elapsed_s=case['result']['physics_process_elapsed_s'],new_PPO_or_budget_cost=False,
      source5deg_saved_fullstate_not8or10deg_training=True,no_claimed_causal_learning_gain_or_permanent_anti_forgetting=True,qualified_full_SLOPE_RM_or_MoE=False,gate_trained=False,hardware_calibrated=False,
      old135_negative4pi_decline_original_strictfalse_and_136_failure_kept=True,no_higher_slope_before_actual_RM_CAD_route_review=True,
      next_independent_expert='E1_CURB',next_axis='CURB20 directional route-entry exposure CPU contract first; original geometry/command range fixed',next_CURB_warmstart_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',
      next_entry_audit=str(R/'CURB20_SAVED_ENTRY_EXPOSURE_CPU_REVIEW.json'),entry_membership_from_CPU_grid_mapping_not_fresh_ground_or_wheel_query=True,actual_CURB_command_histogram_and_eligible_fullfootprint_admission_pending=True,
      no_new_CURB_repair_implementation_GPU_PPO_or_learning_executor=True,all_E0_Wave_CURB_and_slope_weights_optimizer_unchanged=True,new_budget_seconds=0)
    save('SLOPE138_COMPLETE_SCOPE_DECISION.json',row)
    work=R/'NEXT_E1_CURB20_DIRECTION_ENTRY_REPAIR_WORK_ORDER.md';assert not work.exists()
    oldwork=(R/'NEXT_E1_CURB20_DIRECTION_ENTRY_REPAIR_WORK_ORDER_DRAFT.md').read_text(encoding='utf8')
    prefix='''# 当前已完成138之后的独立CURB20方向入口修复工作单

138 actualcomplete/errorfree，两hostJSONbyteSHA/full181377338byte NPZ SHAf329491238a7a06632eaf248b0f6624a7ac0faf8573119d0281020941c1a900a、全root30q参数recipesassignment/6000callback/actualground-contact积分COMlinkhardware独立审查；10°镜像上下各27/27且1N支撑，ordinary0/closure.657063094mm/11声明route截断two reasoncoverageexact。actualfloat32解析normal maxerror2.329113868e-8，component/unit1e-6与ground1e-6原合同通过。冻结source40424b已观测5/8/10°范围，不机械10°PPO或整体SLOPE/RM/MoE毕业，旧negative4pi诊断下降保留。

按已批准004转回独立E1_CURB20正向方向问题的合理修复准备，下面旧draft前置“待138”现已满足。本轮对原389已保存20k spawn映射推导CURB列34–39，共2820 root样本：原向1400（下平台680、上平台720、至少.4m前接近600）；镜像1420（下平台700、上平台720、至少.4m前接近620）。这只是保存root与保留grid/geometry的CPU映射，不是freshground/fullwheelcontact确认或真实命令histogram，不能宣称未覆盖跨坎或证明优化目标因果。

下一积极准备新的隔离reset入口单轴CPU组件和完整ownership/state合同：使用原133实际prefix证据、完整1293c97暖启动，先actualassignment下合法fullfootprint/不重叠/两镜像/上下行起点与selectedreset/episode+1/旧所有私有CPUCUDA流身份；保持20mm/150mm几何、命令范围/standing/plane真实条件命令、reward/LR/全部DR/硬件/时钟和五族比例，不混改command轴。未新scope准入前不部署学习或盲叠df0c；源24b冻结5°存储状态只是SLOPE范围证据，不作CURB暖启动。其它专家和gate预算保护保持。

'''
    work.write_text(prefix+oldwork,encoding='utf8')
    print(json.dumps(dict(scoped10deg_complete=True,groups=groups,ordinary=0,closure_mm=row['max_closure_mm'],truncations=row['declared_truncations'],normal_error=row['normal_max_component_error'],next_expert='E1_CURB',next_only_CPU_entry_contract_pending=True,no_new_PPO_or_budget=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('SLOPE138_COMPLETE_DECISION_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only=True));raise
