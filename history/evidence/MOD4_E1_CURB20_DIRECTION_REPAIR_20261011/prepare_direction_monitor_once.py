from direction_io import *
import tomllib
def main():
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert t['id']=='mod4-10' and t['kind']=='heartbeat' and t['status']=='ACTIVE' and t['rrule']=='FREQ=HOURLY;INTERVAL=1'
 p=D/'MONITOR_PREVIOUS_ENTRY139_COMPLETE_PROMPT.md';assert not p.exists();p.write_bytes(t['prompt'].encode())
 root=json.loads((R/'DIRECTION_ACTIVE_ROOT.json').read_bytes())['root'];dispatch=json.loads((R/'DIRECTION_DISPATCH_ACTUAL_RECEIPT.json').read_bytes())
 intro=f'''最新2026-10-11人类“赶紧修复完启动训练”已实际推进独立CURB20命令方向范围，旧仅CPUprepared/未部署与139partial全历史。当前root={root}，source421=原410逐字+独立新命令组件/状态/保存恢复/2PPOworker/physicalprobe/controller/CPU读者。唯一supervise_curb20_direction_once.py已实际dispatch，原parent{dispatch['owner']['pid']}/start{dispatch['owner']['start_ticks']}只是定位；以actual/proc argv/cwd/start/自己的E1_STATE、PIDreceipt/latest_complete/rollingfreeze/actualsrcsnapshot/PASSED/唯一账段优先。

先读本机MOD4_E1_CURB20_DIRECTION_REPAIR_20261011/reports的DIRECTION_ACTIVE_ROOT、ACTUAL_SCHEMA_TARGET_CPU_PASSED、DISPATCH_ACTUAL_RECEIPT及最新DIRECTION_ACTUAL数字timestamp；read_direction_actual.py仅仅读可复用。未来中央E1_CURB20_DIRECTION_TARGET_CPU_VERIFIED/DISPATCH_ACTUAL_RECEIPT/CURRENT_ACTUAL/METADATA_SYNCED若尚未生成正常pending，不能按旧scope无executor判当前未部署，不能借CPU叫formal。新SDK10已actual300controls/1200callbacks/PASSED/10实际CURB，同newcommand native20k24warm120timed480timed576totalcallbacks正在运行或以自己的后actual优先。独立控制器只有全部newscopePASSED后依序128x2完整6144steps192callbacks、20kx4完整1.92Msteps384callbacks弃预检权重、独立fresh20k新进程0control0PPO strictsameCURBentrydirection全恢复，再唯一300s含load-learn-save-exit/save25/15s本机guardian。旧clock/DR/geometry原SHA复用，无重复45minclock；已执行stage/main/SDK/native/small/big/fresh/dispatch/record/sync/budgettail once绝不重跑。正式启动/保存/自然退出及ownCPU全save审查之后自己的4case再决定；未完整候选决定不更多PPO/升35或50mm，不无限hold/只队列。

唯一新轴：actualCURB合法resetentry与实际生成cellbounds决定每个physicalepisode固定signedgentle方向，abs原随机vx/standing.2与全部旧随机消耗不变，episode中不按liveposition/yaw纠正或翻转，nonCURB/clearplane旧条件命令不变。新增direction状态独立dict键E1_CURB_entry_direction_state、保存完整mask/sign/boundepisode/resetxy/histogram/actualassignment+entrymap身份，无新RNG/真值actor-gate/teacher/奖励LR硬件几何配额改变。完整warmstart仍129 source364 own32063 SHA3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e/CPU102，不用未合格4102fe、389df0c、Wave2b4或discard；源全actorcriticstdoptimizer/D0D7/globalnamed/dictprivateCPUCUDA旧terraincommand先exact，显式G3→CURB+entry+newdirection迁移、CUDA磁盘roundtrip/savedsourceepisode+1。后续sameCURBentrydirection完整exact，旧named集合/assignment严格不松，非PhysXexactresume。新ownfinite tensors须实读，不硬套源102。

CPU读者原错把model_state_dict套源分开的actor_state_dict/critic_state_dict、忽略actor.distribution.std_param导致误猜16；实际严格9actor+8critic=17与source SHA/完整optimizerDR全保留。原两次CPUerrors、wbx拒绝已存在freeze和schema literal全局替换SyntaxError均preGPU/PPO保存，旧source420与421原badCPU读者逐字保留，独立actualschema仅读者完成CPU组件/来源/17独立storage/原snapshot文件存在准入，没有hotpatch活动代码/放宽校验/物理失败重标。source420从未GPU/main运行，当前421实际CPU已admitted及唯一dispatch。

新候选编号140两主机jobs与中央queue/results无占用已在dispatch前实际核，未来原parent自动发布140-e1-curb20-direction-repair-terrain-flat及retention-flat/spin/world；未发布不占号重发、未result合法pending。已有139/132/115/129/135/137/138等validcomplete不重播，136旧failed不重发。新的collector需actualcomplete/errorfree取两host8JSONbyteSHA/fullNPZ原件SHA后按132同20mm竖直150mm条带连续平台/9m镜像/.4approach→两轮全坎→200mm后支撑/80env1500control15s20260928white3精确配对，以及115/129三skill诊断。全root30q/参数recipesassignment/6000callbacks/ground-contact积分COMlinkhardware原容差、有效失败prefix/1N支撑与位置分列/fullsignedcircle alongcross-dedrift/两signed4pi/直线误差原strictfalse保持，standing不要求跨坎，reset teleport不计进度。140自身通行前不能qualifiedCURB/永久抗遗忘/整E1/RM/MoE毕业。

005solecanonical1188000s330h/七扩展第七100h已唯一应用，不重复扩展/复制/clearactive/重tail/重结。PPOloadpreflightlearnsaveexit原parent唯一正常扣，CPU/SDK/native/fresh0PPO/frozen无PPO不扣。两真实OS锁fcntl held/free，persistent exists非持锁不删；native/PPO正在自己的scope持锁正常，不据旧idle自由启动第二20k。父故障trainer活跃先保护保存修监督，不kill/hotpatch/干预其他AI。E0与接受SLOPE5/8/10冻结，Wave/CURB旧未qualified证据保持，gate未训/硬件未标定/S8后续批准/93-94paused/WASD播放器不自动按键reset停止重启。

所有saved源码/CPU错误/未采用/准入/dispatch/物理/PPO/fresh/formal/候选/metadata/monitor/Git回执继续Git，weights/rawNPZ/USD/ZIP只actualpath-size-SHA，凭据不输出不Git。当前newrepair stage尚待record_experiment唯一annotatedtrial及remote main/tag/peeled实核；之后全部later报告普通supplement，不重复record/tag/commit；pushfailed只续原objects。Git非主训练依赖，所有旧trialobjects保持。当前mod4-10同一heartbeatACTIVE每1h及同target，healthy/pendingDONT_NOTIFY静默；只有实质阶段/真实修复/重大退化/完成/人类动作通知，无新驻守5minSSH/ping/Rich/自动预算。reviewready自然退出是单课合法边界非全课程finished，不复活旧入口/删monitor。

以下旧139完整与固定合同提示保留历史追溯，以上source421及之后actual优先：

'''
 prompt=intro+t['prompt']+'\n';p=D/'MONITOR_CURRENT_DIRECTION_PROMPT.md';assert not p.exists();p.write_bytes(prompt.encode())
 request=dict(id=t['id'],mode='update',kind=t['kind'],name=t['name'],prompt=prompt,rrule=t['rrule'],status=t['status'],targetThreadId=t['target_thread_id'])
 save('DIRECTION_MONITOR_REQUEST.json',request);print(json.dumps(dict(prepared=True,rrule=t['rrule'],root=root)))
if __name__=='__main__':main()
