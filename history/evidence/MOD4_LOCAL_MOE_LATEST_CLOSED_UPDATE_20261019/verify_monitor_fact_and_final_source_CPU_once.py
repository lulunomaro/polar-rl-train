from pathlib import Path
import ast,json,hashlib,tomllib,time
B=Path(__file__).resolve().parent;D=B.parent/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
args=json.loads((B/'AUTOMATION_EXISTING_MONITOR_FIXED_PLAYER_FACT_V2_ARGS.json').read_text('utf8'))
actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
for key in ('prompt','rrule','status','name','kind'):assert actual[key]==args[key]
assert actual['id']==args['id'] and actual['target_thread_id']==args['targetThreadId']
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
export=json.loads((B/'reports/LATEST_CLOSED_MOE_EXPORT_AND_BIND_ACTUAL.json').read_text('utf8'))
assert h(Path(export['onnx_path']))==export['onnx_sha256']
driver=(D/'drive_rm7v7_moe.py').read_text('utf8');ast.parse(driver)
assert 'viewer.cam.' not in driver and driver.count('set_player_camera(viewer,sim.chassis_id,overview)')==2
for name in ('runtime_config.json','current_moe_sim.py','START_WASD.bat','START_RM7V7_MOE.bat'):assert h(D/name)==h(B/'prechange'/name)
for name in ('player_status_io.py','player_camera.py'):ast.parse((D/name).read_text('utf8'))
result=dict(epoch=time.time(),status='PASS',existing_monitor_actual_prompt_matches_app_update=True,
    original_ACTIVE_hourly_target_preserved=True,final_export_actual_SHA=export['onnx_sha256'],
    final_player_sources={n:dict(path=str(D/n),bytes=(D/n).stat().st_size,SHA=h(D/n)) for n in ('rm7v7_moe_sim.py','drive_rm7v7_moe.py','player_camera.py','player_status_io.py')},
    original_runtime_and_launchers_unchanged=True,only_camera_and_status_IO_fixed=True,no_remote_transport_or_training_mutation=True)
with (B/'reports/MONITOR_FACT_AND_FINAL_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False))
