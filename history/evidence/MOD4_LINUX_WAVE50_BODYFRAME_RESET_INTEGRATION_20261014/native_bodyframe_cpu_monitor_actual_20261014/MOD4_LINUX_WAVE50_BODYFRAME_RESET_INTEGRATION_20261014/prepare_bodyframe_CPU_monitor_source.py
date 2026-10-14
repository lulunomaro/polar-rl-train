"""Preserve prior exact prompt and prepare the next same hourly monitor source."""
from pathlib import Path
import hashlib
import json
import tomllib

B = Path(__file__).resolve().parent
app = Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
current = tomllib.loads(app.read_text(encoding='utf8'))
assert current['id'] == 'mod4-10' and current['status'] == 'ACTIVE'
assert current['rrule'] == 'FREQ=HOURLY;INTERVAL=1'
assert current['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
old = B / 'MONITOR_PREVIOUS_LOGICAL_ONLY_BEFORE_RESET_COMPOSITION_CPU_20261014.txt'
new = B / 'MONITOR_BODYFRAME_RESET_CPU_COMPOSITION_ACTUAL_20261014.txt'
assert not old.exists() and not new.exists()
old.write_bytes(current['prompt'].encode('utf8'))
git = json.loads((B / 'reports/BODYFRAME_RESET_RESTORE_CPU_STAGE_GIT_RECORDED.json').read_bytes())
assert git['actual_remote_main_tag_peeled_verified'] is True
prefix = f'''最新actual优先（本轮无SSH/GPU/PPO/预算写）：B=C:/Users/lulu/Desktop/claude/mjcf/MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014。已从仅朝向逻辑推进到实际原20k完整源+原25200点碰撞bank的CPU重置/命令/完整检查点组合适配。先读B/reports/BODYFRAME_WHOLE20K_RESET_COMMAND_SAVE_CHAIN_CPU_ACTUAL.json、BODYFRAME_TWO_STAGE_OLD_RESTORE_FIRST_SAVE_RESUME_COMPOSITION_CPU_ACTUAL.json与B/NEXT_BODYFRAME_ACTUAL_TARGET_CPU_NATIVE_FULLRESTORE_WORK_ORDER.json。当前主线仍S3/E1_WAVE/G1 50mm，S4仍原A的CPU接口准备，没有新门控学习。

实际CPU通过：wholee3 model32825/195tensor107float99perenv/N20k及原bankSHA未变，原actual e1_terrain_training_env源码核实super原重置后才episode+1。新adapter第一迁移在完整原恢复和原唯一新episode之后才安装，不重reset或多取DR。原2820Wave出生1410pi/1410不转，选中15行下一birth交替而所有未选root/command/状态exact；原fullresetreceipt不改，原q30/qd30/XY/速度不改，重新用完整25200点原.002m和1e-5采样间隙查safeZ，无cachedgroundfallback。重复子集_write_dynamic命令不会反复翻符号；新明确BODY×出生coefficient×WORLD-entry审计，旧BODY×WORLD-sign审计仍保留且对合法新轴明确预期拒绝，不旁路其原false。已验证3control12callback CPUfixture直方图使用reset前真正施加命令相位，不冒实际物理曝光。11个错误源方向/episode重复跳号/quat/缺ground/setter读回等CPU负例拒绝。

另完整新checkpoint wrapper的首次迁移及从ownbodyframe保存续接两个独立CPUfixture通过：每次原whole-scope恢复callback在newadapter未安装时执行，再绑定唯一sourceepisode+1，bodyframe旧独立state→磁盘roundtrip→新birth→自身保存/恢复；actorcriticstdAdam及原left初始化metadata exact，无新initializer或额外DR/reset，CPU RNG未推进，无CUDA。续接每env出生方向反转，旧字段保持、新ownedbodyKEY明确。两个CPUfixture检查点均带BODYFRAME_CPU_FIXTURE_NOT_TRAINING_SOURCE=True及GPUownmark false，禁止用于生产源。原13项CUDA真实恢复在本新scope尚未执行，CPUfixture启动文件不能冒actual13/14passed；实际worker路径必须拒绝fixture文件。8个manifest/错误身份负例拒绝。CPUfixture场景和flat ray为明确合成，25200点bank与whole20k源为原实际数据；这不是Linux PhysX放置/ABI/恢复pass或通行证明。

当前新payload_v1有效native worker为bodyframe_native_worker_v2.py，已compile，仅native144_0PPO和fullrestore120_0PPO两个新scope模式，源码没有PPO learn/update/backward；独立BODYFRAME_TARGET_CPU_TEMPLATE_NOT_ADMITTED.json始终approved_GPU=false/targetCPU=false/资源预算lease=false/无真实root-parent-freeze，不直接翻flag假实际准入。尚无新remote ROOT/Task/GPU/native/fullrestore/PPO，也没有本轮远端连接。下一root积极独立materialize新Linux持久root，原522runtime/assets bytesexact+新owned源码+原typed13，真正targetCPU wholee3/sourcefreeze/资源与原twofcntl/原canonical CPU只读准入，再唯一newnative0PPO；actual data/native getter、xyzw heading独立见证、选中setter读回与all25200点/health/query/contactCOMhardware/全ownsave及实际父子退出两锁free独立审后，才新fullrestore120。其完整ownsource实际GPU标记/13strict+body14/磁盘state/episode+1及raw审通过后，才另准备首<=300s有界new-axis PPO/save25/15s guardian，不第三盲同left轴duration/自动70，max2后全四case审。正常训练修复授权保持，不自造每块人类确认、不无限hold或只队列。

active fullcheckpoint文件birth_bodyframe_full_checkpoint_v1.py引用birth_bodyframe_reset_adapter_v2.py。原已执行CPU test的adapter_v1保持原reportSHA cf90950b3d9d9e1d42c5ff19114d02ef42418e20e90d420108eff342f2be12d5；v2独立修正后置setter见证不应在placement前伪claim，要求真实pre-getter/xyzw-heading见证+post-nativegetter。原inline PowerShell SyntaxError、Windows路径分隔schema KeyError与nativeworker_v1 unmatched-parenthesis compile拒绝均保留，后saved独立读者和worker_v2仅续未执行步骤；不重原完成CPU/GPU案例。manifest准备器v1原compile失败保持，v2只编译有效5源码，旧badworker不作为active入口。不删除旧错误或改成原PASS。

本轮CPU integration阶段已actualremote main/tag/peeled核：commit{git['commit']}/tag{git['tag']}/object{git['tagobject']}/原{git['all_oldtags_preserved']}tags/{git['saved_sources']}sources。先前A普通supplement c1b1ea614ad3cc47c84a4ee334a8ee43f26ea5ac也已actualremote核。此后本monitor和stageGitreceipt需ordinarysupplement，以后来实际工具为准不凭prompt假完成。所有新旧源码/false/errors/fixture/报告/workorder/monitor持续Git，大PT等仅actualpathsizeSHA原件保留，credentials不输出，pushfailed只existingobjects不重record/tag/commit，Git非训练依赖。

以上实际覆盖下文“new_linux_reset_worker_not_implemented”旧状态：已有CPU适配和native源码准备，但实际GPU/target准入仍未做；A原S4接口/105h规划/唯一原账与pending本机Windows成本/所有固定物理合同和solemod4-10 ACTIVE每1h同target保持。root唯一210/egde及249顺序owner，本机笔记本GPU暂停、3060评测only，无活跃finitecollector，不恢复旧RPC/poller/mirror/TUI/SCUT/main/resume/once，不重旧native/fullcase/GPU，不kill/delete/hotpatch/他人AI-WASDGUI。健康pending无实质变化DONT_NOTIFY静默，不因heartbeat反复生成相同报告。

上一完整prompt原件 {old} SHA{hashlib.sha256(old.read_bytes()).hexdigest()} 保留，仅下列旧逻辑CPU字段被上述实际接续：
'''
new.write_bytes((prefix + '\n' + current['prompt']).encode('utf8'))
print(json.dumps(dict(source=str(new), bytes=new.stat().st_size, sha256=hashlib.sha256(new.read_bytes()).hexdigest(),
                      previous_prompt_sha=hashlib.sha256(old.read_bytes()).hexdigest())))
