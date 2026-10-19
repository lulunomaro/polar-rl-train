from pathlib import Path
import json,tomllib,time,shutil,hashlib
B=Path(__file__).resolve().parent;W=B.parent;D=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
out=B/'AUTOMATION_EXISTING_MONITOR_PLAYER_FACT_ARGS.json';assert not out.exists()
actual=json.loads((B/'reports/REQUESTED_PLAYER_LAUNCH_AND_CURRENT_ACTUAL.json').read_text('utf-8-sig'))
assert actual['status']=='STARTED_AND_ACTUAL_CURRENT_VERIFIED'
current=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert current['status']=='ACTIVE' and current['rrule']=='FREQ=HOURLY;INTERVAL=1'
prefix=('最新本地播放器actual（2026-10-19人类直接要求“最新的moe策略拉到本地播放器启动”）：已用本机已有第七SCUT+Fudan小时完整wholeCPU通过的H1/E2/E3导出并实际启动原October8 RM7v7 MoE驾驶面板。'
 '新bundle=MOD4_LOCAL_MUJOCO_DRIVE_20261008/latest_moe_scut_fudan_hour7_20261019.onnx，H1 a21a82639c332456a7f89c985c838616ab5f8e5771cc71f32894485658ca866a、E2 dd76c55798ab0f059f168a67cb23b68f90d95fb2b09fab0d119d0ea6d5600c2c、E3 6b5215aedd8ef51e8fa4b09fb85b967f0e21203289b025e182e872841c9d79cf，原gate148 E0/W35普通硬选保持。'
 '700行CPU导出动作parity<=1e-4、五路完整六维路由及原全场map加载/五步接线检查实际通过；仅播放器导出与接线，不是新冻结或PhysX资格，不重训练/remote transport/Task/native/PT下载/预算。'
 '原runtime/PD/物理/CAD/动作/控制键和START两个入口保持，仅bundle绑定和界面小时文字更新；旧hour4原件保留。'
 '真实启动run=rm7v7_moe_runs/1792370000596194400，actualpid57968/create2026-10-19T08:33:20.202718+08:00只是本次快照，不当永久alive。初始暂停且viewer_running/finite实际核。'
 '记录见C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_MOE_LATEST_CLOSED_UPDATE_20261019/reports/REQUESTED_PLAYER_LAUNCH_AND_CURRENT_ACTUAL.json及LATEST_CLOSED_MOE_EXPORT_AND_BIND_ACTUAL.json。'
 '最初选错本机导出interpreter缺onnxruntime在导出前失败，原error保留；改用播放器既有.venv完成，未安装或改训练环境。'
 '下文V30“新a21a未替换旧hour4 bundle”字段已经被本actual覆盖。后续heartbeat仍不得自动重开/打断/热改用户窗口，除非人类又明确要求。'
 '本地用户请求不取消原三卡训练，下面V30的第八小时owner281824与全部source/once/cost/安全交接合同继续。新本地阶段latest-closed-scut-fudan-hour7-moe-rm7v7-player-update仅record一次，以laterGit实际回执为准。\n\n')
args=dict(mode='update',id=current['id'],kind=current['kind'],name=current['name'],prompt=prefix+current['prompt'],rrule=current['rrule'],status=current['status'],targetThreadId=current['target_thread_id'])
out.write_text(json.dumps(args,ensure_ascii=False,indent=2),'utf8')
snapshot=B/'installed_player_snapshot';snapshot.mkdir()
for name in ('rm7v7_moe_sim.py','drive_rm7v7_moe.py','START_WASD.bat','START_RM7V7_MOE.bat','runtime_config.json','current_moe_sim.py','latest_moe_scut_fudan_hour7_20261019.json'):
    shutil.copy2(D/name,snapshot/name)
print(json.dumps(args,ensure_ascii=False))
