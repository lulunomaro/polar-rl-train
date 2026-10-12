from route_repair_io import *
import ast
old=D/'payload/native_e1_wave50_route_lifecycle_scope_probe.py';raw=old.read_bytes();s=raw.decode()
anchor=' from wave50_route_runtime import audit as audit_route,verify_GPU_boundary_fixture';assert s.count(anchor)==1
s=s.replace(anchor,' from wave50_route_runtime import audit as audit_route\n from wave50_route_fixture_adapter_v2 import verify_GPU_boundary_fixture')
anchor=" report['route_lifecycle_GPU_boundary_fixture']=verify_GPU_boundary_fixture(env)";assert s.count(anchor)==1
s=s.replace(anchor," Path(args.output+'.before_route_fixture.json').write_text(json.dumps(report,indent=2))\n"+anchor)
p=D/'payload_fixture_reviewed/native_e1_wave50_route_fixture_v2_scope_probe.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf8')
save('FIXTURE_ADAPTER_V2_PREPARED.json',dict(epoch=time.time(),passed=True,original_native_path=str(old),original_native_SHA=H(raw),new_native_path=str(p),new_native_SHA=H(p.read_bytes()),only_scene_fixture_attribute_and_mapping_API_and_beforefixture_report_save_changed=True,physical_loop_actor_command_DR_geometry_route_math_thresholds_unchanged=True,old440_failed_SDK_no_PPO_retained=True,target_CPU_and_GPU_pending=True))
print(json.dumps(dict(prepared=True,new_physical_loop_unchanged=True)))
