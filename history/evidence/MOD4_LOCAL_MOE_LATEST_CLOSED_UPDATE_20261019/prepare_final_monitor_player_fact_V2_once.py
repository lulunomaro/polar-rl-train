from pathlib import Path
import hashlib,json,shutil,tomllib,time
B=Path(__file__).resolve().parent;W=B.parent;D=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
out=B/'AUTOMATION_EXISTING_MONITOR_FIXED_PLAYER_FACT_V2_ARGS.json';assert not out.exists()
launch=json.loads((B/'reports/REQUESTED_PLAYER_V3_LAUNCH_AND_CURRENT_ACTUAL.json').read_text('utf-8-sig'))
observation=json.loads((B/'reports/FIXED_PLAYER_V3_BOUNDED_STATUS_OBSERVATION_ACTUAL.json').read_text('utf8'))
camera=json.loads((B/'reports/FULLMAP_CAMERA_SWITCH_RENDER_ACTUAL.json').read_text('utf8'))
assert observation['status']=='PASS' and camera['status']=='PASS' and camera['consecutive_camera_switches']==100
assert launch['run_path']==observation['run_path']
current=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
prior=json.loads((W/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/AUTOMATION_ACTUAL_SAME_RECIPE_EIGHTH_HOUR_V30_ARGS.json').read_text('utf8'))
assert current['prompt']==prior['prompt'] and current['status']=='ACTIVE'
pid=launch['actual_identity']['ProcessId'];creation=launch['actual_identity']['CreationDate'];run=launch['run_path']
prefix=(f'最新本地播放器actual（2026-10-19人类直接要求“最新的moe策略拉到本地播放器启动”，随后反馈状态写入错误和点跟随闪退）：现已用本机已有第七SCUT+Fudan小时完整wholeCPU通过的H1/E2/E3导出原October8 RM7v7 MoE并完成两处本地修复后重新启动。'
 '新bundle=MOD4_LOCAL_MUJOCO_DRIVE_20261008/latest_moe_scut_fudan_hour7_20261019.onnx；H1 a21a82639c332456a7f89c985c838616ab5f8e5771cc71f32894485658ca866a、E2 dd76c55798ab0f059f168a67cb23b68f90d95fb2b09fab0d119d0ea6d5600c2c、E3 6b5215aedd8ef51e8fa4b09fb85b967f0e21203289b025e182e872841c9d79cf。原gate148 E0/W35普通硬选保持；700行ONNX动作parity最大.00005054474<.0001、完整六维路由及原全场加载/接线通过。'
 '第一本机conda缺onnxruntime在export前失败，改播放器既有.venv后成功，无安装环境。首次player初始成功后真实WinError5 replace状态文件使sim线程退出，原报告/error/source/run1792370000596194400保留；状态写入现对5/32/33短重试，仍占用则保留旧完整JSON、记原warn、下次刷新重试。真实Windows deny-delete handle三次复现与解除后恢复CPU过，其他异常不吞。'
 'V2 run1792370158161191700用户点跟随后原生退出，stderr明确mjv_updateCamera track body id outside valid range；首次45秒观察因stale实际失败，原件保留，不能冒通过。camera新helper在viewer.lock内先合法trackbodyid再启用TRACKING；真实全场passive renderer连续100次follow/overview切换通过，不改physics/policy。'
 f'最终V3实际run={run}，pid{pid}/create{creation}仅当时快照，45秒已有状态文件连续fresh/finite且无INTERACTIVE_ERROR核过；不当永久alive。'
 '详细证据C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_MOE_LATEST_CLOSED_UPDATE_20261019/reports/REQUESTED_PLAYER_V3_LAUNCH_AND_CURRENT_ACTUAL.json、FIXED_PLAYER_V3_BOUNDED_STATUS_OBSERVATION_ACTUAL.json、WINDOWS_STATUS_CONTENTION_REPRODUCTION_AND_FIX_CPU_ACTUAL.json及FULLMAP_CAMERA_SWITCH_RENDER_ACTUAL.json。'
 '两个START入口仍原RM7v7面板、初始暂停P开始，旧hour4原件保留；原runtime/PD/物理/CAD/动作/键不动。不是PhysX/新冻结/技能毕业，也不把本机MoE普通gate行等同H1直出normal诊断。'
 '下文V30“新a21a未替换旧hour4 bundle”已历史覆盖；人类此次直接要求授权的更新/重启已执行完，后续heartbeat不得自动重开/打断/热改用户玩家，除非新明确要求。'
 '未连训练host/下载中途PT/重GPU或Task/native/改账预算，不取消第八小时owner281824原训练与安全接续合同。'
 '新本地stage latest-closed-scut-fudan-hour7-moe-rm7v7-player-update只record一次，后续Git以later实际回执为准，未用首次monitor草稿保留但未发送。\n\n')
args=dict(mode='update',id=current['id'],kind=current['kind'],name=current['name'],prompt=prefix+current['prompt'],rrule=current['rrule'],status=current['status'],targetThreadId=current['target_thread_id'])
out.write_text(json.dumps(args,ensure_ascii=False,indent=2),'utf8')
snapshot=B/'installed_player_fixed_snapshot';snapshot.mkdir()
for name in ('rm7v7_moe_sim.py','drive_rm7v7_moe.py','player_status_io.py','player_camera.py','START_WASD.bat','START_RM7V7_MOE.bat','runtime_config.json','current_moe_sim.py','latest_moe_scut_fudan_hour7_20261019.json'):
    shutil.copy2(D/name,snapshot/name)
large=B/'large_originals';large.mkdir()
image=Path('C:/Users/lulu/AppData/Local/Temp/codex-clipboard-71519255-cab1-458f-8f6b-1e0e58a51763.png')
if image.exists():
    copy=large/'USER_STATUS_WRITE_FAILURE_SCREENSHOT.png';shutil.copy2(image,copy)
    (B/'reports/USER_SCREENSHOT_ARTIFACT_INDEX.json').write_text(json.dumps(dict(source_path=str(image),retained_path=str(copy),bytes=copy.stat().st_size,SHA=hashlib.sha256(copy.read_bytes()).hexdigest()),indent=2),'utf8')
(B/'reports/USER_FOLLOW_CAMERA_EXIT_AND_NATIVE_ERROR_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),user_confirmation=['没有，是它自己退出的','我点了一下跟随机器人，然后就闪退了'],native_error=(B/'reports/PLAYER_V2_STDERR.txt').read_text('utf8'),original_run='1792370158161191700',classification='Original unlocked camera mode publication exposed invalid tracking body to renderer; original native error retained',not_a_training_GPU_failure=True),ensure_ascii=False,indent=2),'utf8')
print(json.dumps(args,ensure_ascii=False))
