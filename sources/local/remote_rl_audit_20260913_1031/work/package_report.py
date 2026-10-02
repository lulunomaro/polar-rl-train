import ast, difflib, hashlib, json, pathlib, re, statistics
ROOT=pathlib.Path(__file__).resolve().parents[1]
PKG=ROOT/'MOD4_RL_FIX_20260913_1500'
SNAP=ROOT/'snapshot'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
status=read(SNAP/'status_final.json');runtime=read(SNAP/'verified_runtime.json')
sources={v['path']:v['sha256'] for v in status['source_files'] if v['path'].startswith('isaac/mod4/')}
bound={};(PKG/'patches').mkdir(exist_ok=True)
for path in sorted((PKG/'overlay/isaac/mod4').glob('*.py')):
 rel='isaac/mod4/'+path.name
 original=SNAP/rel
 if original.exists():
  if sha(original)!=sources[rel]:raise ValueError('audited source changed: '+rel)
  old=original.read_text(encoding='utf8');bound[rel]=sha(original)
 else: old=''
 diff=''.join(difflib.unified_diff(old.splitlines(True),path.read_text(encoding='utf8').splitlines(True),
                                 fromfile='a/'+rel if old else '/dev/null',tofile='b/'+rel))
 (PKG/'patches'/(path.name+'.patch')).write_text(diff,encoding='utf8')
# Bind every task source (including untouched dependencies) while allowing unrelated play tooling updates.
for rel in ('isaac/mod4/mod4_task.py','isaac/mod4/eval_terrain_mod4.py'):
 bound[rel]=sources[rel]
runtime_files={}
for rel,d in runtime['files'].items():
 if not d.get('stable_during_read'):raise ValueError('unstable/missing runtime: '+rel)
 runtime_files['/home/egde/fangzhen_linux/'+rel]=d['sha256']
contract={'schema':'mod4_repair_overlay_v1','status':'CANDIDATE_CPU_TESTED_RUNTIME_PENDING',
 'snapshot_time':status['time'],'source_root':'/home/egde/fangzhen_linux',
 'source_files':bound,'runtime_files':runtime_files,
 'overlay_files':{str(p.relative_to(PKG/'overlay')).replace('\\','/'):sha(p)
                  for p in (PKG/'overlay').rglob('*.py')},
 'notes':['No active training changed','No GPU smoke test performed for this patch',
          'No CAD/USD modifications in this package','Stop on hash drift; rebase explicitly']}
write(PKG/'baseline_manifest.json',contract)
write(PKG/'evidence/status_snapshot.json',status)
write(PKG/'evidence/runtime_hashes.json',{'time':runtime['time'],'files':runtime['files']})
log=re.sub(r'\x1b\[[0-9;]*m','',runtime['log_tail'])
(PKG/'evidence/latest_training_tail.log').write_text(log,encoding='utf8')
(PKG/'evidence/observation_history_excerpt.txt').write_text(
 '\n'.join((SNAP/'runtime/observation_manager.py').read_text(encoding='utf8').splitlines()[407:434]),encoding='utf8')
blocks=re.split(r'Learning iteration\s+(\d+)/(\d+)',log)
rows=[]
for i in range(1,len(blocks),3):
 if i+2>=len(blocks):continue
 row={'iteration':int(blocks[i]),'target':int(blocks[i+1])}
 for line in blocks[i+2].splitlines():
  m=re.match(r'\s*([^:]+):\s*([-+]?[0-9]+(?:\.[0-9]+)?(?:[eE][-+]?\d+)?)\s*s?\s*$',line)
  if m:row[m[1].strip()]=float(m[2])
 if 'Mean reward' in row and 'Iteration time' in row:rows.append(row)
if not rows:raise ValueError('no complete training block')
last=rows[-1];recent=rows[-20:]
keys=['Mean reward','Mean episode length','Steps per second','Episode_Termination/base_contact',
      'Episode_Termination/bad_orientation','Metrics/tunnel_underpass_rate','Metrics/route_complete_rate',
      'Metrics/plant/closure_err_session_max_m','Metrics/plant/mimic_err_session_max_rad']
summary={'snapshot_time':status['time'],'latest_complete_block':last,
 'tail_window_iteration_range':[recent[0]['iteration'],recent[-1]['iteration']],
 'tail_window_medians':{k:statistics.median([r[k] for r in recent if k in r]) for k in keys},
 'warning':'Logged snapshot/rolling metrics are not corrected per-episode acceptance rates.'}
write(PKG/'evidence/log_summary.json',summary)
process=status['processes'][0] if status['processes'] else {}
gpu=status['gpu']['stdout']
report=f'''# 4090 RL 现状与问题

采样时间：{status['time']}（主机本地时间）。依据：进程 `/proc`、正在写入的训练日志、源码及运行库；不是旧交接文档。

## 当前运行情况

| 项目 | 结果 |
|---|---|
| 主机 | `egde@10.24.4.210`，RTX 4090 |
| 工作目录 | `/home/egde/fangzhen_linux` |
| 当前 PID | `{process.get('pid')}` |
| 并行环境 | **512**，狗洞加权混合训练 |
| 已完成到的日志迭代 | **{last['iteration']}/{last['target']}**（日志从 0 编号） |
| 初始化检查点 | `2026-09-13_01-17-30_mod4_fixed_mixed/model_16295.pt` |
| 当前开关 | `RM_DR_OFF=1`；序列编码器默认关；路线课程默认关；45 s 回合 |
| GPU 现场读数 | {gpu} |
| 最近一轮吞吐 | {last.get('Steps per second'):.0f} env-steps/s；20 个物理子步/控制步 |
| 平均回合长度 | {last.get('Mean episode length'):.2f} 控制步，约 {last.get('Mean episode length')*.01:.2f} s |
| 平均 reward | {last.get('Mean reward'):.2f}；上升不能代替技能验收 |
| 闭链/传动会话最大残差 | {last.get('Metrics/plant/closure_err_session_max_m'):.4f} m / {last.get('Metrics/plant/mimic_err_session_max_rad'):.4f} rad |
| 狗洞进入日志项 | {last.get('Metrics/tunnel_underpass_rate'):.4f}，尚无当前策略过洞证据 |
| 底盘碰撞日志项 | {last.get('Episode_Termination/base_contact'):.4f}；统计口径待修，不能直接说成真实失败率 |

日志：`{runtime['log_path']}`。最后 20 个完整块的中位数见 `evidence/log_summary.json`；原始尾部保留在包内。

当前闭链/传动约束未见报警，GPU 使用率高但显存约 7.9/24.6 GB，未见这段日志有 OOM。1024 环境吞吐和总场地技能均未被本次审计验证。上午 64 环境、mild-DR/encoder/curriculum 开启的记录是旧一轮，不能拿来描述现在。

## 已定位的问题与补丁

| 优先级 | 问题与影响 | 当前是否生效 / 处理 |
|---|---|---|
| P0 | `Mod4Env.step` 在 physics 前运行所有 step event；奖励读到滞后的路线/离地状态，terminal step 的成功还可能被 reset 清掉。landing_state 又先于 air_state。 | 当前生效。新增分阶段步进和 reset 前终态证据。 |
| P0 | 旧 evaluator 在整个 rollout 用 `done_route |= success`，下回合失败被上回合成功掩盖；分母用 env 个数。 | 评测时生效。新 evaluator 按完整回合、按种子输出证据，失败优先。 |
| P0 | 独立导轮刚体的力被从底盘 contact 的模长中相减。100 N 底盘撞击可被 200 N 导轮载荷抹成 0。 | 当前生效。移除错误相减和深蹲载荷折扣。仍须验证地形接触/自碰撞的区分。 |
| P0 | 路线课程把每步当尝试；还把 15 条路线的索引当 10 种地形索引，并截断越界值。 | 当前关闭；开启后会触发。改为终止回合计数和显式路线→地形映射。 |
| P0 | 历史按项拼接，`x[-35:]` 不是当前帧；输出层和新增 actor 列同时清零导致 latent 分支不能开始学习。 | 当前 encoder 关闭。修复 gather 与初始化，附动作一致性/梯度测试。 |
| P1 | 热启动 strict=False 未拒绝缺失的旧 actor/critic 权重，形状匹配也不保证 observation 语义匹配。 | 存在于加载路径；当前日志 missing=0，没有证据说当前检查点已丢权重。加严格校验和序列语义版本。 |
| P1 | 旧链脚本吞评测失败、缺指标仍放行；retention 自动建立基线且可缺地形。 | 下一次评测/晋级会用到。提供退出码严格的新评测驱动和 gate；接管清单要求替换旧接线。 |
| P1 | `RM_TUNNEL_LEAD_M` 同时控制蹲下提前量和出生点前移。 | 当前环境未设这一变量，但之后调参会影响路线长度。拆成两个变量。 |
| P1 | 蹲姿驱动门使用速度绝对值，倒退也拿到“移动”奖励。 | 当前生效。改为身体前向正速度门；仍需逐项比较站立/倒退/通过的完整回报。 |

路线索引例证：`0=run,1=jump_in_place,4=slope_spin,9=step_up,13/14=tunnel_cross`，与旧课程的种类列表顺序完全不同。这不是仅有样本不足。

## 尚不能下结论的地方

1. 本次没有运行额外 GPU 探针，不能根据聚合日志断言堵在洞口的唯一机械原因。当前是独立转动导轮资产，不能套用旧“8 个刚性导轮全部锁死”结论。
2. 用户 CAD 的 223 mm 腿高和两个已讨论低姿态仍是有效参考；完整带装甲底盘在当前 PhysX 地面、关节误差和受载状态下的包络、牵引与整机出洞仍需实测。root 加常量不构成整机净空证据。
3. jump 奖励多项为 0，而 jump target/reach 指标仍变化，可能使用了不同任务的聚合统计；需要分 route_id 的终态/轨迹核对，暂不归因为跳跃能力已经学会。
4. 这些代码修复尚未经过目标 Isaac 新运行期验收。关闭 encoder/课程的当前训练只避开对应问题，不能修复碰撞统计、事件顺序和旧评测器。

## 本次操作边界

只读采集进程、日志和源码；在本地制作和测试候选；仅向远端独立 `rl_repair_packages` 目录上传本包。没有覆盖训练文件、修改 USD、重启进程或执行新 GPU 仿真。
'''
(PKG/'CURRENT_STATUS.md').write_text(report,encoding='utf8')
print('package manifest and status written; latest iteration',last['iteration'])
