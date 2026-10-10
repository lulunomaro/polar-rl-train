"""Bind complete133 physical review, failed direction prefixes and approved next expert."""
from review133_io import *

def main():
 p=sorted((P/'reports').glob('CURB133_SCHEMA_REVIEW_[0-9]*.json'))[-1];v=json.loads(p.read_bytes());assert v['review_complete']
 diag=json.loads((R/'CURB133_PREFIX_DIRECTION_ACTUAL_DIAGNOSIS.json').read_bytes())
 published=json.loads((R/'SLOPE134_PUBLISHED.json').read_bytes())
 actual=json.loads(sorted(R.glob('CURB_TRAINING_RESET_ACTUAL_[0-9]*.json'))[-1].read_bytes())
 decision=dict(epoch=time.time(),trial_id='E1-CURB20-133-COMPLETE-RETENTION-AND-SCOPE-DECISION-01',review=str(p),review_SHA=H(p.read_bytes()),review_complete=True,
  own_final=v['own']['checkpoint'],source_checkpoint_sha256='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',
  summary=v['summary'],source_CURB132_ascending_complete=26,candidate_CURB133_ascending_complete=22,ascending_count=27,
  source_CURB132_descending_complete=27,candidate_CURB133_descending_complete=27,descending_count=27,
  valid_incomplete_ascending_prefixes=[3,6,9,15,18],all_incomplete_original_positive_orientation=True,
  in_scope_forward_curb_behavior_regression=True,ordinary=0,
  selected_as_qualified_CURB=False,candidate_frozen_as_review_evidence_only=True,more_CURB_PPO_or_height_increase_admitted=False,
  old_flat_spin_world_are_diagnostics_not_CURB_graduation_lines=True,E0_frozen_gate_untrained_no_router_failure_proof=True,
  no_permanent_anti_forgetting_or_real_RM002_or_stair_claim=True,original_strict_false_raw_cost_reset_and_prefixes_preserved=True,
  prefix_diagnosis=str(R/'CURB133_PREFIX_DIRECTION_ACTUAL_DIAGNOSIS.json'),actual_saved_training_spawn_state=str(sorted(R.glob('CURB_TRAINING_RESET_ACTUAL_[0-9]*.json'))[-1]),
  reset_and_command_exposure_cause_not_proven=True,
  next_action='Approved004 independent E1_SLOPE derived continuous5degree first scope; source3643c97 warmstart. New134 frozen scope actually published; no new learning executor until complete fullraw review and new contracts.',
  next_expert='E1_SLOPE',next_frozen_job=published['jobs'][0]['job_id'],next_frozen_package=published['package'],
  remaining_seconds_snapshot=published['actual_authority']['remaining_seconds'],new_budget_seconds=0)
 save('CURB133_COMPLETE_SCOPE_DECISION.json',decision)
 save('READONLY_LOCATOR_AND_QUATERNION_CONVENTION_REVIEW.json',dict(epoch=time.time(),trial_id='CURB133-CPU-READER-CONVENTION-01',
  errors=[dict(operation='Get-Content/rg read-only',incorrect='prepare_curb132_frozen_once.py',actual='prepare_curb_frozen_scope_once.py',no_source_or_GPU_mutation=True),
   dict(operation='temporary unsaved CPU trajectory print',incorrect='root quaternion interpreted as wxyz',actual='e1_full_pose_reset Rotation.as_quat() and observed identity[0,0,0,1] prove xyzw; final saved independent diagnosis usesxyzw',no_original_result_relabel=True)],
  neither_a_physical_or_training_failure=True,original_tool_outputs_retained_in_task=True))
 text='''# CURB133完整审查与下一独立坡面范围

133四case实际complete/errorfree；两机8份probe/result字节一致，完整rawSHA、初末root30q/参数/recipes/assignments、6000callbacks、ground-contact积分/COMlink/hardware原容差和全部signedcircle已独立审查。

跨坎上行来源132为26/27，389候选为22/27；下行均27/27，ordinary0。五个有效未完成上行prefix为env3/6/9/15/18，均原向正BODYvx+.3/yaw0。一轮留在坎前，车体随后转向并侧行；env6/18出现声明路线截断。四个来源完整案例在候选未完成，env15两版均未完成。不能用缩短接近/延长窗口重标原结果；训练命令/入口暴露或目标冲突为推断，尚无因果消融。

旧技能诊断：source364负4π7/8→8/8，正仍8/8，world63/64→64/64，maxcross约.048298590m/s；负/正1.5误差.021616556/.058025852m/s，所有原strictfalse保留。旧技能保持不能替代CURB自身完整通行。df0c完整保存只冻结为审查候选，不准900s同scope盲叠、升35/50mm或qualifiedCURB/gate。E0未更新，gate尚未训练。

按人类批准004推进独立E1_SLOPE：新134是真正新连续5°、2m坡段、9m格镜像，0.4m前接近、200mm后支撑，80env/1500controls/15s/seed20260928white3。来源仍完整129的3c97，非389、365或Wave失败候选。只替换原random family，其他四族和30/20/20/15/15/clock/reward/hardware/DR保持。CPU198独立三角射线及法向通过，仅组件合同；134已实际发布，未把包/CPU当物理通过。

134actualcomplete/errorfree后只读收两机JSON字节和完整NPZ SHA，独立审两轮前支撑→全部坡段→200mm后支撑的上下行/镜像/站立/原1N接触支撑/ordinary/声明截断和全部有效prefix。不同坡面与CURB不得伪称同geometry参数配对；D0D7及原部署反馈合同按精确SHA复用。合理后准备真正新SLOPE独立geometry/assignment/ground-contact/reset/fullactorcriticstdoptimizer/allD0D7/globalnamed/privateCPUCUDA+旧状态验证再显式新geometry迁移、实际CUDAroundtrip/sourceepisode+1和独立output。必要新CPU/SDK10×300/native20k24warm120timed/128×2及20k×4完整PPO各一次，旧clock无45min重复。全部PASSED后首300s含load-learn-save-exit，再自己完整保存与新四case。未完整不得更多学习。

CURB方向修复单独保留：先据已保存training reset/sourcefreeze与完整失败prefix检查实际近坎正向入口、命令段覆盖及左右轮过程；若新增reset/命令轴须隔离、新身份/私有RNG/fullresume合同，不能修改活动源码或放宽旧named集合/阈值。不要因本次未合格无限重复同课，也不要把专家分工称永久不退化。

canonical828000s/六扩展各一次/新增0；CPU/frozen无PPO不扣，实际原账与锁边界优先。S3/S7原规划保护其他专家/gate/min(18h,.13B)，无reserve交易；不复活93/94/S8/MuJoCo旧任务、不干预人类本地WASD播放器。所有新结果/错误/工作单/同步/监控/Git回执必须补Git，大原件仅实际path-size-SHA。
'''
 out=R/'NEXT_E1_SLOPE5_FROZEN_AND_INDEPENDENT_WORK_ORDER.md';assert not out.exists();out.write_bytes(text.encode())
 print(json.dumps(dict(review_complete=True,CURB_qualified=False,next_expert='E1_SLOPE',new134_published=True,more_CURB_PPO=False)))

if __name__=='__main__':main()
