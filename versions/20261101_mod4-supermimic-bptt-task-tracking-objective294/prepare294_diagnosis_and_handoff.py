"""Record source-grounded objective review, without changing frozen training."""
from pathlib import Path
import hashlib,json,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';R.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
    with (R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
S=T/'DEPTH_STUDENT_RETENTION_REPAIR_V292_20261101/source'
files=[S/name for name in ('teacher_student292.py','reference292.py','terrain292.py','literal_original_config.py','literal_original_methods.py')]
teacher=[]
for case in ('fullDR_lqr','fullDR_mpc'):
    p=Path('F:/RMPOLAR-RL/traditional_control_20261101/results/FINAL_EVIDENCE_V2')/case/'trajectory.json'
    raw=p.read_bytes();rows=json.loads(raw);last=rows[-50:]
    teacher.append(dict(case=case,path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),rows=len(rows),
       last_time=rows[-1]['time'],final_root_xyz=rows[-1]['qpos'][:3],final_velocity6=rows[-1]['qvel'][:6],
       final_halfsecond_vx_mean=sum(r['qvel'][0] for r in last)/len(last),
       final_halfsecond_max_abs_vz=max(abs(r['qvel'][2])for r in last),purpose='Necessary terminal-goal audit of saved JSON teacher, no trajectory rerun or PT/NPZ read'))
put('ACTUAL294_OBJECTIVE_SOURCE_AND_TEACHER_REVIEW.json',dict(epoch=time.time(),kind='SOURCE_AND_SAVED_TEACHER_OBJECTIVE_DIAGNOSTIC',
 user_requests=['Training must have a problem; why Fudan rewards when a teacher exists? Think carefully.', 'SuperMimic uses BPTT to replace PPO for task tracking, correct?'],
 source_files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files],teacher_terminal_evidence=teacher,
 actual_current_algorithm='H32 BPTT through frozen-in-policy-update learned WM, actor and critic; no PPO update. Original PPO constructor is used only for preserved optimizer identity migration.',
 current_actor_objective='negative old Fudan imagined reward return + negative old Fudan critic bootstrap + decaying teacher_state_loss/H32 + originalpolicy ground distillation + overflow loss',
 current_critic_objective='Only old Fudan rewards; teacher tracking excluded from targets',
 confirmed_mismatch='Fixed1.4m/s throughout stair episode versus successful teacher terminal near0m/s. Tracking target and command reward disagree during landing stabilization.',
 reference_limitations=['Only two saved5s MuJoCo successful trajectories,250reference states each at50Hz. Not a privileged action teacher callable on arbitrary PhysX student states.', 'Phase is independently chosen from nearest rootxyz eachstart; no explicit per-episode monotonic phase or reference sequence input to actor35+depth9.', 'Pointwise nearest-root phase can be ambiguous near stationary takeoff/landing. This is a design risk, not a newly measured cause.', 'Teacher contact support/manifold tracking is absent from state_supervision; strict outcome only evaluated later.'],
 decision='Reject unchanged286/292mixed-objective continuation. New standalone route: reference-conditioned motion/task tracking, BPTT policy updates, own transition WM, matching tracking critic. Current frozen292 still saves and independent293evaluates; no hotpatch/kill/replay.',
 permitted_this_diagnostic='Read local source/saved teacher JSON, prepare concrete design and update continuing workorder. No new reward-version GPU GO, no budget modifications.',
 papers=[dict(title='SuperMimic',paper='arXiv:2610.28480',project='https://supermimic.github.io/',sections=['3.1goalconditionedpolicy','3.3BPTT/criticEq2','AppendixAtrackingreward and K10reference','AppendixBseparatevelocityinterface'])],
 distinction='BPTT replaces policygradient estimator/optimizer route, not task definition. Reference tracking still needs a scalar trackingreward/loss. Critic is compatible with BPTT and must value that same task.',
 code_bugs_disclosed=[dict(id='local294-git-cwd',result='Exploratory git status ran from workspace root and failed notgitrepo; later explicitpolar workdir succeeded.'),dict(id='local294-rg-cwd',result='Exploratory relative source rg ran frompolar and pathnotfound; subsequent absolute/source reads succeeded.')],
 model_reads=0,SDK_runs=0,optimizer_steps=0,GO=0,account_writes=0))
design='''本次人类质疑后的结论：当前错误在训练目标，不是缺少PPO到BPTT的切换。292已经通过自己的可微WM做H32 BPTT，但旧Fudan速度/腾空回报、仅旧回报的critic、较弱且衰减的教师state辅助项共同驱动同一个actor。固定1.4m/s与老师台阶上近零速停稳直接冲突。恢复平衡、降低LR和限制更新只能缓解退化，不能证明这个目标正确。

下一独立版本的具体目标：让机器人从当前可观测起点接近270mm台阶，跟随已验证教师的起跳/收腿/越沿/落地/停稳参考，在自己的PhysX动力学和原物理保护内完成动作。训练主信号改为参考跟踪：关节姿态/速度、基座相对台阶的位姿/线角速度，以及可从真实证据提供的双轮支撑/落脚目标。动作平滑和限位作为小型正则；不保留无条件1.4m/s和鼓励腾空作为另一主任务。具体尺度和权重在独立配置中声明，不能拿旧19方法不变约束掩盖目标变化。

BPTT链为：student观测和合法目标 -> actor归一化动作 -> ownWM预测下一状态 -> 与该时刻目标比较 -> 沿整段返回actor。物理模拟器只产自己的转移，不反传。每次policy更新冻结WM参数，保持输入/动作Jacobian；继续用自己实际状态动作训练WM。若使用H32末端critic，应重新定义为同一个跟踪目标的后续return，而不是旧Fudan回报；旧critic权重/Adam历史保留归档，不直接称为新目标已合格。BPTT无需PPO，但可以有critic。

参考接口：先做明确的参考条件跟踪器。每个episode固定教师clip与有序phase，使用当前状态与当前深度估计对齐台阶坐标，并提供计划的后续目标窗口；必要的phase必须训练和部署一致。计划参考不是未来实际传感器。不能只在loss用老师、actor不知道要追哪一段；也不能给最终depth学生未来真实深度/环境GT/教师真state。最终自主接口由当前深度/本体观测产生目标或phase，再接已会动作的跟踪器。独立速度接口可后续开发；当前目标不是训练通用速度追踪。

现有teacher能力边界：两个MuJoCo LQR/MPC成功JSON轨迹，不能冒称任意PhysX状态可查询的特权动作teacher。优先状态/运动参考跟踪，无需把100Hz力矩错当50Hznormalizedaction。要做动作蒸馏或DAgger，应先有相同执行接口上可调用且已验证的teacher；这里没有该证据，因此不把动作克隆作为当前计划。

准入与判断：先用一条已成功参考、同一270mm几何做整个动作跟踪；连续phase与真实执行输入明确。看真实轨迹误差与完整动作成功，再拓展台阶位置、DR和视觉目标接口。评测继续使用实际双轮首次越沿、顶面完整脚印支撑和稳定.5s，单纯腾空或loss下降不合格。原2.5msTGS32/4、400N、50Hz控制/100Hz反馈、10mm单envclosure、.01radmimic以及原canonical预算边界不改。

当前292冻结任务不热改；按原完整保存/安全退出/独立评测保留这一轮证据。postround进程本身不会新开训练。即使293地面回到3/8，也不得据旧混合目标原样新开一轮。下一新训练任务需上述独立目标源码/配置/Task，不能重放已消费once。本文件是明确设计结论，尚未实现或启动新奖励版本。
'''
with (R/'TASK_TRACKING_BPTT_REDESIGN294.md').open('x',encoding='utf8')as f:f.write(design)
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
put('AUTOMATION294_PRIOR_REQUEST_CONTEXT.json',dict(epoch=time.time(),name=app['name'],status=app['status'],rrule=app['rrule'],target_thread_id=app['target_thread_id'],prompt=app['prompt']))
override='''【2026-11-01人类最新目标审查，覆盖下文任何“达到3/8就照旧续训/旧Fudan奖励永不变”的接续指令】
人类明确质疑“都有教师模型还搞复旦奖励函数？搞指令追寻还是别的”，并指出SuperMimic用BPTT代替PPO做任务跟踪。先读 C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/SUPERMIMIC_TRACKING_OBJECTIVE_REVIEW_V294_20261101/reports/ACTUAL294_OBJECTIVE_SOURCE_AND_TEACHER_REVIEW.json 和 TASK_TRACKING_BPTT_REDESIGN294.md。
292已是H32BPTT/PPO更新0；问题是旧Fudan速度/腾空reward为主、teacher只是衰减/H32辅助、critic明确排除teacher。固定1.4m/s与LQR/MPC成功落地末段vx约-.011/-.001m/s直接冲突。降低LR/地面蒸馏/动作变化限制不能替代目标纠正。不再原样启动旧混合目标续训，即使地面3/8保留；旧物理/预算保护不变。
当前冻结292继续原完整保存与安全退出并由原postround48920独立评测293/真实回放，不hotpatch/kill/重复once；收尾不会新GO。之后优先完成独立参考条件运动/任务跟踪源码和配置：主跟踪teacherstate/关节/基座/双轮落脚与停稳，连续phase和合法目标序列；BPTT透过ownWM更新actor，若critic则只估计同一跟踪目标。任务跟踪器先学会完整教师动作，当前深度目标生成/phase再接自主接口；不能把未来真实深度/GT教师状态喂最终学生。计划参考和未来实际观测有区别。两个MuJoCo轨迹不冒充任意PhysX状态可调用动作teacher，力矩不当normalizedaction。
本次审查只完成诊断与具体重设计，未启动新奖励版本；不能把问答当作已有完整新Task/准入。按人类持续接续授权准备必要源码，实际开训遵既有scope和新任务准入；若有真正未明确的范围，说明具体变化，不循环索要已经给过的权限。新phase294唯一diagnostictrial，后续报告追加；历史false及292原记录保留。
【以下为292运行/原收尾信息，旧目标的未来续训段已被以上覆盖】
'''
req=dict(mode='update',id='mod4-10',kind='heartbeat',name=app['name'],status=app['status'],rrule=app['rrule'],targetThreadId=app['target_thread_id'],prompt=override+app['prompt'])
put('AUTOMATION294_OBJECTIVE_REVIEW_UPDATE_REQUEST.json',req)
print(json.dumps(dict(passed=True,review=str(R/'ACTUAL294_OBJECTIVE_SOURCE_AND_TEACHER_REVIEW.json'),request=str(R/'AUTOMATION294_OBJECTIVE_REVIEW_UPDATE_REQUEST.json'),teacher_terminals=teacher),ensure_ascii=False))
