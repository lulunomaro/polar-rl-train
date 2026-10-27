from pathlib import Path
import ast,hashlib,json,time
HERE=Path(__file__).resolve().parent;T=HERE.parents[2]
PAYLOAD=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/payloads/h1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(name,v):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert not (HERE/'INDEX.json').exists()
 sources=[PAYLOAD/'h1_step270_sdk_runtime_candidate.py',PAYLOAD/'step270_goal_and_scut_rates_candidate.py',PAYLOAD/'step270_triangle_geometry_cpu.py',
  PAYLOAD/'job0/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py',PAYLOAD/'job0/runtime/isaac/mod4/h1_authored_full_collider_plane_reference_v1.py']
 for p in list(HERE.glob('*.py'))+sources:ast.parse(p.read_bytes())
 assert json.loads((HERE/'FLAT_REAL_CALLBACK_TINY_CPU_ACTUAL_V1.json').read_bytes())['passed']
 assert json.loads((HERE/'PREVIOUS_GROUND_REQUEST_EDGE_V2_CPU_ACTUAL.json').read_bytes())['passed']
 emit('CURRENT_ORIGINAL_CALLBACK_CACHE_SOURCE_AUDIT_ACTUAL.json',dict(epoch=time.time(),source_only=True,
  original_sources=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sources],
  actual_cached_fields=['wheel_clear_m','wheel_N','all_min_clear_m','nonwheel_max_N','root_vz','root_planar_speed','roll','pitch','yaw',
   'last_measured.step_wheel_min','last_measured.step_wheel_max','last_measured.step_query_height','last_measured.step_query_face','_integrated_contact.history[:,0,:,2]'],
  wheel_clear_m_is_authored_collider_world_lowest_z_relative_plane0=True,signed_Fz_is_existing5ms_mean=True,
  instantaneous_contact_manifold_or_pair_identity_available=False,authored_floor_faces=[0,1],
  original_environment_init_stage_ordered_triangle_identity_reused=True,AABB_is_location_check_not_floor_identity=True,
  original_payload_not_modified=True,new_runtime_SDK_or_native_execution=False,no_PT_remote_GPU_or_ledger=True))
 files=[dict(relative=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(HERE.rglob('*')) if p.is_file()]
 worker=HERE/'flat_real_physics_events_v2.py'
 emit('INDEX.json',dict(epoch=time.time(),schema='mod4.flat.real_callback.source_frozen.v2',files=files,
  selected_source=dict(path=str(worker),bytes=worker.stat().st_size,SHA=H(worker)),source_frozen=True,
  actual_native_integration_and_jump_pending=True,Git_status='ordinary_supplement_pending_root'))
 print(json.dumps(dict(index_SHA=H(HERE/'INDEX.json'),source_V2_SHA=H(worker),files=len(files),source_only=True)))
if __name__=='__main__':main()
