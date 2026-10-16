"""New nonlearning diagnostic scope, preserve old native; actual full34-shape flight evidence next."""
from pathlib import Path
import ast,json,shutil,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'h1_calibration_payload_v1';Q=D/'payload/job1';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not P.exists();P.mkdir();(P/'job1/runtime/isaac/mod4').mkdir(parents=True)
 names=('h1_fullphysics_calibration_worker_v1.py','h1_calibration_finite_parent_v1.py','h1_authored_full_collider_plane_reference_v1.py','h1_flat_jump_evidence_reward_cpu_v1.py')
 for name in names:compile((D/name).read_text(encoding='utf8'),name,'exec');shutil.copyfile(D/name,P/name)
 rt=P/'job1/runtime/isaac/mod4';shutil.copyfile(D/'h1_external_operator_command_v1.py',rt/'h1_external_operator_command_v1.py');shutil.copyfile(Q/'runtime/isaac/mod4/directional_spin_runtime.py',rt/'h1_original_directional_runtime.py')
 text=(Q/'runtime/isaac/mod4/train_E2_H1_fresh_v1.py').read_text(encoding='utf8');needle='import mod4_task  # noqa: E402';assert text.count(needle)==1;text=text.replace(needle,"import h1_external_operator_command_v1\nsys.modules['directional_spin_runtime']=h1_external_operator_command_v1\n"+needle);compile(text,'H1_owned_calib_fresh','exec');(rt/'train_E2_H1_fresh_v1.py').write_text(text,encoding='utf8')
 # All original D0-D7, hardware, reset, reward/termination remain exact. This is calibration only.
 v=dict(epoch=time.time(),new_scope='H1_fullbody_collider_force_and_motor_takeoff_calibration80_v1',source_SHA='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8',H1_original_native80_scope_not_replayed=True,new_axes=['Actual34authoredcollider support using physical31body poses at every2.5ms callback','Actualall31body contact forces and independent two-wheel-view agreement','Caller-scripted bounded motor inputs solely for dynamics/reward calibration,never PPO/teacher/replay','External zero-twist command maintained through selected reset'],N=80,controls=424,callbacks=1696,DR='Fresh80 allD0D7 engineering pressure,not full20k restore',all_policy_critic_STD_optimizer_original_and_zero_updates=True,scripted_calibration_not_learned_jumping=True,new_gravity_force_hardware_or_airborne_reset=False,actual_cookedShapeLocal_not_directread=True,template_approved_GPU=False,files=[dict(relative=p.relative_to(P).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in P.rglob('*') if p.is_file()])
 with (P/'H1_CALIBRATION_OVERLAY_MANIFEST.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 with (R/'H1_FULL_COLLIDER_CALIBRATION_NEW_SOURCE_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 print(json.dumps(dict(new_calibration_CPU_prepared=True,files=len(v['files']),no_native_or_airborne_credit=True)),flush=True)
if __name__=='__main__':main()
