"""UnusedR02sources: averageencoder rates coherently, innovation-gatedattitude,
optionalpose-stifflegs with longitudinalLQRwheels and decoupledyaw. No physics.
"""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent
p=R/'sensor_core_v3.py';assert not p.exists();s=(R/'sensor_core_v2.py').read_text(encoding='utf-8').replace('accel_reference="chassis"):', 'accel_reference="chassis",innovation_limit=1.):',1).replace('self.accel_reference=accel_reference;', 'self.innovation_limit=innovation_limit;self.accel_reference=accel_reference;',1)
s=s.replace('error=np.cross(gravity_candidate/max(norm,1e-9),predicted_up)', 'innovation=float(np.linalg.norm(gravity_candidate-G*predicted_up));confidence*=max(0.,1.-innovation/self.innovation_limit) if self.innovation_limit>0 else 1.;error=np.cross(gravity_candidate/max(norm,1e-9),predicted_up)')
ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
p=R/'ground_controller_v3.py';assert not p.exists();s=(R/'ground_controller_v2.py').read_text(encoding='utf-8').replace('from sensor_core_v2','from sensor_core_v3');s=s.replace('self.old_shaped_w=0.','self.old_shaped_w=0.;self.fixed_legs=bool(c.get("fixed_legs",True));self.leg_kp=float(c.get("leg_kp",120.));self.leg_kd=float(c.get("leg_kd",4.));self.wheel_pitch_scale=float(c.get("wheel_pitch_scale",1.));self.wheel_velocity_scale=float(c.get("wheel_velocity_scale",1.))')
needle='tau=self.tau_eq-self.K@error\n  if self.decouple_yaw:';assert needle in s
repl='''if self.fixed_legs:
   for a,b in((3,5),(4,6),(10,12),(11,13)):error[a]=error[b]=.5*(error[a]+error[b])
  weighted_error=error.copy();weighted_error[2]*=self.wheel_pitch_scale;weighted_error[9]*=self.wheel_pitch_scale;weighted_error[7]*=self.wheel_velocity_scale
  tau=self.tau_eq-self.K@weighted_error
  if self.fixed_legs:
   actual_q=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]]);reference_q=np.array([self.ref[3],self.ref[3]+self.ref[4],self.ref[5],self.ref[5]+self.ref[6]]);actual_dq=np.array([x[10],x[10]+x[11],x[12],x[12]+x[13]]);tau[[0,1,3,4]]=self.tau_eq[[0,1,3,4]]+self.leg_kp*(reference_q-actual_q)-self.leg_kd*actual_dq
  if self.decouple_yaw:'''
s=s.replace(needle,repl);ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
p=R/'physics_bridge_v3.py';assert not p.exists();s=(R/'physics_bridge_v2.py').read_text(encoding='utf-8');s=s.replace('self.exact_support=TireMeshSupport(self.m)','self.exact_support=TireMeshSupport(self.m);self.rate_sum=np.zeros(6)');s=s.replace('self.total_highrate_IMU_samples=0\n def sensor_packet','self.total_highrate_IMU_samples=0;self.rate_sum[:]=0.\n def sensor_packet');s=s.replace("idx=[1,0,4,3];clean=", "idx=[1,0,4,3];rates=self.rate_sum/self.imu_window_count if self.imu_window_count else self.d.qvel[self.vids].copy();clean=");s=s.replace("'legqd4':self.d.qvel[self.vids[idx]].copy(),'wheelqd2':self.d.qvel[self.vids[[2,5]]].copy()", "'legqd4':rates[idx].copy(),'wheelqd2':rates[[2,5]].copy()")
s=s.replace('self.imu_acc_sum[:]=0.;return packet','self.imu_acc_sum[:]=0.;self.rate_sum[:]=0.;return packet');s=s.replace('mujoco.mj_step(self.m,self.d);self.tick_phys+=1;', 'self.rate_sum+=self.d.qvel[self.vids];mujoco.mj_step(self.m,self.d);self.tick_phys+=1;');ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
p=R/'run_ground_case_v3.py';assert not p.exists();s=(R/'run_ground_case_v2.py').read_text(encoding='utf-8').replace('from ground_controller_v2','from ground_controller_v3').replace('from sensor_core_v2','from sensor_core_v3').replace('from physics_bridge_v2','from physics_bridge_v3').replace("ROOT/'sensor_core_v2.py',ROOT/'ground_controller_v2.py',ROOT/'physics_bridge_v2.py'","ROOT/'sensor_core_v3.py',ROOT/'ground_controller_v3.py',ROOT/'physics_bridge_v3.py'")
s=s.replace("accel_reference=cfg.get('accel_reference','wheel_midpoint'))", "accel_reference=cfg.get('accel_reference','wheel_midpoint'),innovation_limit=float(cfg.get('accel_innovation_limit',1.)))");s=s.replace("kind='R01_MOD4V1_SENSORFRONTEND_AND_YAWDECOUPLED_SCREEN'", "kind='R02_MOD4V1_COHERENTRATES_GATEATTITUDE_FIXEDLEG_SCREEN'");s=s.replace("sensor_frontend='2kHzphysicalIMUboxcar_to100Hz_thenD1noise_D3delay; differsR00instantaneoussampling'", "sensor_frontend='2kHzIMUandencoderrateboxcar_to100Hz_thenD1noise_D3delay; explicitnewfrontend'")
ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n');print('R02fourmodulesASTpass, newunusedsources')
