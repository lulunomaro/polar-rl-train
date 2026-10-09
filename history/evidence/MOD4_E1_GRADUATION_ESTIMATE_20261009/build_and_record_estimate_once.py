"""Write and Git-record an explicitly conditional ETA; no training mutation."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,shutil,subprocess,sys
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';P=REPO/'history/plans'
assert not (R/'E1_GRADUATION_ESTIMATE.json').exists(),'ETA report exists; do not overwrite'
load=lambda p:json.loads(p.read_text(encoding='utf8'))
v=load(R/'E1_ETA_ACTUAL.json');plan=load(P/'MOD4_RM_TERRAIN_TRAINING_REVISION.json');tz=timezone(timedelta(hours=8))
fmt=lambda epoch:datetime.fromtimestamp(epoch,tz).strftime('%Y-%m-%d %H:%M:%S +08:00')
now=v['epoch'];deadline=v['state']['deadline_epoch'];b=v['budget'];speed=v['recent_log']['mean_iteration_seconds']
assert v['actual_child'] and 'e1_gentle_stable_block2_' in v['actual_child']['argv'][v['actual_child']['argv'].index('--run_name')+1]
assert speed>0 and b['authorized_seconds']==828000 and plan['new_budget_seconds']==0
prediction=dict(report_kind='conditional_working_estimate_not_skill_admission',basis_epoch=now,basis_local_time=fmt(now),
 scope='S3 E1 traversal progression through real70mm rough roads, admitted connecting slopes and selected outer-curb complete routes; not S7 terrain4pi/tunnel/airborne/all-RM certification',
 observed=dict(current_phase=v['phase'],current_course='gentle_stable_block2',own_checkpoint=v['own_run']['latest_complete'],source_count=len(v['own_run']['manifest']['source_map']),snapshot_count=v['own_run']['snapshot_count'],
  current_block_deadline_local=fmt(deadline),current_block_remaining_seconds=max(0,deadline-now),E1_used_accounted_and_active_hours=b['E1_total_used_seconds']/3600,
  existing_S3_cap_remaining_hours=b['S3_planning_cap_remaining_seconds']/3600,all_project_budget_remaining_hours=b['remaining_tail_adjusted_seconds']/3600,
  recent_mean_iteration_seconds=speed,updates_per_hour=3600/speed,env_policy_steps_per_second=v['recent_log']['env_policy_steps_per_second_estimate'],attention=v['attention']),
 estimate=dict(wall_clock_hours_from_observation=[24,48],earliest_local=fmt(now+24*3600),later_local=fmt(now+48*3600),not_statistical_confidence_interval=True,
  assumed_remaining_learning_hours=[16,26],assumed_geometry_preparation_and_review_wall_hours=[8,22],parallel_3060_review_can_overlap=True,
  sufficient_tests_can_skip_redundant_notches=True,no_evidence_for_policy_convergence_time_on_real_RM_yet=True),
 major_uncertainties=['real70mm continuous rough and source-ground/contact admission have not begun','selected149.929/200.069mm outside-curb routes with vertical walls have not begun; mechanical/control feasibility and adaptation not demonstrated','independent E1 must retain old flat-spin-world skills; earlier finite reverse-spin residuals require actual later paired review','new route reset/ground/contact/fullresume preparations or failures can delay wall clock even while no learning budget is consumed'],
 limits=['Tonight shallow-block save is not E1 graduation','30h S3 planning cap includes used preflight/failed observer/formal learning; cap expiry is not a pass','If outer curb needs substantive repair, ETA extends or accepted sub-scope must be honestly reported; no automatic budget extension','23/43degree slopes, unmeasured other stairs and S7 all-terrain spin are later conditional scopes'],
 actual_final_admission='actual complete route/ground/contact/root30q/direction and old-skill matched behavior; integrity/hardware/source/RNG contract; retain raw/flags; no90/95/100 line',
 master_sha256=plan['master_sha256'],new_budget_seconds=0,production_runtime_GPU_PPO_canonical_writes=0)
f=R/'E1_GRADUATION_ESTIMATE.json';f.write_text(json.dumps(prediction,ensure_ascii=False,indent=2),encoding='utf8')
obs=prediction['observed'];est=prediction['estimate']
report=f'''# E1专家毕业时间工作估计

观察时刻：{prediction['basis_local_time']}。来源是实际4090进程argv/start、自己run/manifest/latest_complete、训练日志以及只读canonical账段。此报告是估算，不是技能准入或新训练授权。

预计当前浅地形第二块在 **{obs['current_block_deadline_local']}** 触发完整保存，之后还有自然退出/唯一结账与行为审查。这个时刻只是gentle收尾，不是整个E1毕业。

## 工作区间

按刚修订的S3 E1地形通行范围，把真实70mm连续RM起伏、连接坡和选定外缘坎完整路线列入，**顺利推进的工作估计为观察后24–48小时，即{est['earliest_local']}至{est['later_local']}**。这不是统计置信区间，也没有新RM训练收敛证据支持精确时刻。

当前E1累计约 **{obs['E1_used_accounted_and_active_hours']:.2f}小时**（包含预检、失败observer段、正式学习和当前active时间），原S3含已用时间30h规划上限下还约 **{obs['existing_S3_cap_remaining_hours']:.2f}小时**。整个项目tail-adjusted余额约{obs['all_project_budget_remaining_hours']:.2f}h，预算新增0。最近13个iteration平均{speed:.2f}s，即约{obs['updates_per_hour']:.0f}次PPO更新/小时、{obs['env_policy_steps_per_second']:.0f}环境策略步/秒；这种吞吐只能估计算力供给，不能推断多少update就学会外缘坎。

区间采用约16–26h必要后续学习、约8–22h几何/接触/reset准备与行为审查的规划假设；3060回放可并行，已有精确同范围证据和足够的逐档评测可以减少重复训练。不是每个档位固定2h，也不把尚未部署的路线当已经在训。

## 最大不确定项

- 真实70mm连续起伏、10.5°连接坡与约150/200mm外侧上岛路线尚未开始；尤其外缘坎有竖直边壁，真实两轮跨越/支持能力还没有证据，可能需要专项修复。
- 现有训练健康不等于新课程收敛。完整旧flat/spin/world保持必须跟新的整路线方向、contact/ground/root30q证据一起审查，保留早期reverse-spin有限残差和所有raw。
- 新几何/接触/reset/fullresume合同、缺失依赖或observer错误会增加墙钟时间；同范围有效测试复用，不为估算重复SDK/PPO或45min钟试验。

若外缘坎发生明显困难，该区间会延后或只能报告已接受的子范围；不能到30h规划上限就宣布毕业，也不自动加预算。23°/43°等未准入大坡、其他未核台阶、狗洞/腾空以及S7全地形4π小陀螺不包括在本次E1通行初步毕业时间内。

当前训练继续，整个估算只读主机数据，无GPU/PPO/进程/生产runtime/canonical变更。主计划SHA保持{plan['master_sha256']}。
'''
(R/'E1_GRADUATION_ESTIMATE.md').write_text(report,encoding='utf8')
folder=REPO/'history/evidence/MOD4_E1_GRADUATION_ESTIMATE_20261009';assert not folder.exists();folder.mkdir(parents=True)
files=[]
for src in [D/'read_estimate_actual.py',D/'build_and_record_estimate_once.py',*sorted(R.glob('*.json')),*sorted(R.glob('*.md'))]:
 dst=folder/src.name;shutil.copyfile(src,dst);assert dst.read_bytes()==src.read_bytes();files.append(dst.relative_to(REPO).as_posix())
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id','e1-graduation-working-eta-from-actual-stage-and-throughput',
 '--title','Record conditional E1 graduation ETA from actual stage, throughput and remaining terrain scope','--kind','diagnostic',
 '--note-file',str(folder/'E1_GRADUATION_ESTIMATE.md'),'--files',*files,'--validation','Actual argv/start and own manifest/checkpoint SHA; tail-adjusted budget and recent13-iteration throughput; explicit untrained RM scope and planning assumptions; all saved ETA reports included; no training mutation','--push']
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
 (R/'ETA_RECORD_FAILED.json').write_text(json.dumps(dict(stdout=p.stdout,stderr=p.stderr,exit_code=p.returncode,do_not_repeat_record=True),ensure_ascii=False,indent=2),encoding='utf8')
 raise RuntimeError('Record failed; inspect existing objects before retry')
def git(*a):return subprocess.check_output(['git','-C',str(REPO),*a],text=True,encoding='utf8').strip()
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
print(json.dumps(dict(conditional_ETA_hours=[24,48],current_shallow_end_local=obs['current_block_deadline_local'],earliest_local=est['earliest_local'],later_local=est['later_local'],report_Git=tag,commit=head,remote_verified=True,push_pending=False,new_budget_seconds=0),ensure_ascii=True))
