"""Audit existing saved CURB spawn/grid exposure, not a causal proof or deployment."""
from slope_io import *
import numpy as np,traceback

def main():
    source=PRE/'reports/CURB_TRAINING_RESET_ACTUAL_1791672164574719500.json'
    v=json.loads(source.read_bytes());xy=np.array(v['spawn_xy'],dtype=np.float64);assert xy.shape==(20000,2)
    for file in v['files']:assert H(Path(file['local']).read_bytes())==file['sha256']
    probe=json.loads(next((R/'cases').glob('*137*/probe.json')).read_bytes());recipe=probe['geometry_recipe']
    keys=recipe['families'];weights=np.array([recipe['subset_proportions'][k] for k in keys]);assert weights.sum()==1.
    family=np.array([int(np.min(np.flatnonzero(i/40+.001<np.cumsum(weights)))) for i in range(40)])
    cols=np.flatnonzero(family==keys.index('random_uniform_for_rm'));assert np.array_equal(cols,np.arange(34,40))
    rows=np.floor((xy[:,0]+180.)/9.).astype(int);columns=np.floor((xy[:,1]+180.)/9.).astype(int)
    assert (rows>=0).all() and (rows<40).all() and (columns>=0).all() and (columns<40).all()
    selection=np.isin(columns,cols);ids=np.flatnonzero(selection);orientation=np.where(rows<20,1.,-1.)
    canonical=(xy[:,0]-((rows+.5)*9.-180.))*orientation
    # Only frozen geometric root-side exposure is audited; complete wheel footprint is not in this receipt.
    groups={}
    for label,o in (('original',1.),('mirror',-1.)):
        selected=selection&(orientation==o);u=canonical[selected]
        groups[label]=dict(environments=int(selected.sum()),root_before_riser=int((u<-.075).sum()),root_upper_strip=int(((u>=-.075)&(u<=.075)).sum()),root_on_upper_platform=int((u>.075).sum()),root_before_with_400mm_approach=int((u<=-.475).sum()),root_beyond_200mm_after_strip=int((u>=.275).sum()),canonical_root_offsets_unique_m=np.unique(u).tolist())
    exposure=dict(epoch=time.time(),trial_id='CURB20-SAVED-TRAINING-ENTRY-EXPOSURE-CPU-01',actual_source_report=str(source),actual_source_report_SHA=H(source.read_bytes()),checkpoint=v['checkpoint'],actual_geometry_identity=v['terrain_identity'],source_files_SHA_exact=True,
      ordered_families=keys,source_proportions=recipe['subset_proportions'],geometry_column_assignment_source='Unchanged pinned generator ordered proportions /40; frozen actual random-family cols34and35 and mirror rows confirm geometry convention.',derived_CURB_columns=cols.tolist(),total_saved_environments=len(xy),CURB_actual_saved_roots=len(ids),by_orientation=groups,
      root_only_not_complete_wheel_contact_or_exposure_histogram=True,command_values_not_saved_in_this_spawn_receipt=True,old_random_signed_command_range=v['terrain_identity']['command_vx_range'],no_claim_actual_ascending_command_sample_counts=True,
      source132_ascending26_candidate133_22_incomplete_source_env15_kept=True,candidate_four_source_complete_forward_cases_regressed=True,reset_command_optimizer_cause_unproven=True,
      next_repair_scope='Independent CURB20 route-entry/command exposure contract; first verify complete wheel/front approach and actual command histogram in new isolated scope before bounded learning.',
      no_assignment_or_env_id_truth_actor_gate=True,no_new_CURB_geometry_height_reward_LR_hardware_DR_or_PPO=True,no_GPU_training_budget_or_runtime_mutation=True)
    p=save('CURB20_SAVED_ENTRY_EXPOSURE_CPU_REVIEW.json',exposure)
    work=R/'NEXT_E1_CURB20_DIRECTION_ENTRY_REPAIR_WORK_ORDER_DRAFT.md';assert not work.exists()
    work.write_text('''# CURB20正向入口独立修复准备

待当前138完成独立完整实际审查以后，按已批准004独立CURB职责处理原133正向方向退化，不盲继续df0c或升坎高。原132来源3c97上26/27下27/27，133候选df0c上22/27下27/27，四个来源完整变未完整；env15来源和候选都未完整。原五有效未完成轨迹一轮仍未越坎而heading改变横走、env6/18route截断，无ordinary，不缩接近/延窗重标成功。原因只有轨迹证据，训练命令/入口覆盖是待验证推断，不能断言漏restore/router/optimizer错。

本轮CPU审查已保存的原38920k训练spawn/grid，源码freeze SHAexact，源旧geometry/家族比例/40x40/randomcols34–39保持。报告仅root相对侧壁/上平台起点覆盖计数，不能冒完整轮接触/实际正反命令histogram。原full_reset以env_origins固定xy再fullcolliderfootprint实际射线 placement；需独立新scope验证课程入口与完整轮位置、两镜像、正反命令与standing/route覆盖，不能仅靠root报告说训练从未跨坎或证明覆盖因果。

下一新CURB20修复只选完整1293c97暖启动，df0c审查证据/24b坡面权重/E0/Wave互不覆盖。先新隔离CPU合同：actualassignment身份、合法不重叠fullfootprint入口/下行后支撑起点、随机流owned保存/旧named严格不混新增dictprivateRNG，实际commands/standing与两方向histograms。若改起点先只改reset入口这一轴，原20mm竖直/150mm条带/9m镜像、plane30+20/20/15/15、reward/LR1e-4adaptive/KEEPSTD1/clock/hardware/D0D7不改；命令范围保持，若仍需另命令轴则独立下一范围而非混改。不能把env_id或geometryassignment真值喂actor/gate，不能用教师/真值yaw纠偏/改reward掩盖方向问题。

在新origin/fullpose/selectedreset/完整state保存恢复CPUCUDAepisode1/独立ownership合同及必要SDK/native/small-big完整PPO弃预检权重各一次PASSED之前不formal，旧clock/同scope数据SHA精确复用，不重旧389/380/384/386/388/372once。首真正需要学习时300s含load-learn-save-exit/save25/15s本机guardian，同canonical唯一原父扣账，完整自己的save/PID/PASSED/唯一结清/实际退出后新CURB+flat+spin+world四case完整raw配对132/129；旧132/133不重发。完整通行事实与旧技能诊断分别验收，不伪永久抗遗忘/gate毕业。

这是CPU审计和后续工作单准备，尚无新CURB修复implementation/package/executor/GPU/PPO部署，不是准入通过。新权仍需actualownfullsave/oldlaunchclose/三进程exit/twoOSlocksfree/active-Sactive唯一结清。budget828000s六扩展各一次新增0，保护其它专家/gate/min(18h,.13B)规划；S8后续具体批准/硬件未标定/93-94paused/WASD不干预。全部报告/source/错误/旧false/raw/prefix/cost/Git回执记录，大原件真实path-size-SHA。
''',encoding='utf8')
    print(json.dumps(dict(report=str(p),CURB_roots=len(ids),by_orientation=groups,CPU_audit_not_causal_proof_or_learning_admission=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('CURB_ENTRY_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_only=True));raise
