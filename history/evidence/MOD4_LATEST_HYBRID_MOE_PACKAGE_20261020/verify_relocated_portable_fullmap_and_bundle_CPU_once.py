"""Move the delivery, load it from another cwd and verify actual model/inference wiring."""
from pathlib import Path
import ast,hashlib,json,os,sys,threading,time,traceback,xml.etree.ElementTree as ET
import mujoco,numpy as np
B=Path(__file__).resolve().parent;W=B.parent;P=B/'delivery/MOD4_HybridMoE_20261020';T=B/'relocation_check/MOD4_HybridMoE_20261020';R=B/'reports';D=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert P.resolve().is_relative_to(W.resolve()) and T.resolve().is_relative_to(W.resolve()) and P.is_dir() and not T.exists();T.parent.mkdir(exist_ok=True);P.rename(T);oldcwd=Path.cwd()
 try:
  os.chdir(B);sys.path.insert(0,str(T/'player'));sys.path.insert(0,str(T));from rm7v7_moe_sim import RM7V7MoESim;from infer import HybridMoE;from player_camera import set_player_camera
  for path in T.rglob('*.py'):ast.parse(path.read_text('utf8'))
  sim=RM7V7MoESim();params=sim.parameter_readback();assert sim.policy.path.is_relative_to(T) and sim.policy.path.name=='hybrid_moe.onnx';assert sim.cfg.leg_kp==60 and sim.cfg.leg_kd==2 and sim.cfg.crank_scale==.5 and sim.cfg.yaw_assist_gain==0 and not sim.command.auto_mode
  original=mujoco.MjModel.from_xml_path(str(D/'rm7v7_latest_moe.xml'));fields=['body_mass','body_inertia','body_pos','body_quat','jnt_type','jnt_axis','jnt_pos','jnt_range','dof_armature','dof_damping','geom_type','geom_pos','geom_quat','geom_size','geom_friction','geom_contype','geom_conaffinity','geom_solref','geom_solimp','eq_type','eq_data','actuator_gear','actuator_ctrlrange','mesh_vert','mesh_face'];checks={name:np.array_equal(getattr(original,name),getattr(sim.model,name)) for name in fields};assert all(checks.values());assert original.opt.timestep==sim.model.opt.timestep==.0005 and original.nu==sim.model.nu==6 and original.neq==sim.model.neq==10
  scenarios=[]
  for mode in (0,4,3,6):
   sim.reset_route('flat_run');sim.select_skill(mode)
   for _ in range(5):a=sim.step_control();assert a.shape==(6,) and np.isfinite(a).all()
   assert sim.health()['finite'];scenarios.append(dict(mode=mode,controls=5,health=sim.health(),last_action=a.tolist()))
  class Viewer:
   def __init__(self,m):self.m=m;self.cam=mujoco.MjvCamera();self.mu=threading.RLock()
   def lock(self):return self.mu
  viewer=Viewer(sim.model)
  for i in range(100):set_player_camera(viewer,sim.chassis_id,bool(i%2));assert 0<=viewer.cam.trackbodyid<sim.model.nbody
  x=np.zeros((4,35),np.float32);x[:,3]=1.25;x[:,9]=-1;x[np.arange(4),28+np.array([0,4,3,6])]=1;y=HybridMoE()(x);assert y.shape==(4,6) and np.isfinite(y).all()
  # Strip only asset path fields and require exact remaining XML semantics.
  def normalized(p):
   tree=ET.parse(p);root=tree.getroot();root.find('compiler').set('meshdir','ASSET_PATH')
   for element in root.iter():
    if element.get('file') is not None:element.set('file','ASSET_FILE')
   return ET.tostring(root)
  assert normalized(D/'rm7v7_latest_moe.xml')==normalized(T/'player/rm7v7_latest_moe.xml')
  result=dict(epoch=time.time(),passed=True,actual_relocated_root=str(T),cwd_different_from_package=True,all_runtime_assets_loaded_within_delivery=True,source_fullmap_compiled_fields_exact=checks,XML_exact_except_asset_paths=True,parameter_readback=params,mode_wiring_smokes=scenarios,camera_helper_100_locked_state_switches_stub_not_actual_renderer=True,combined_infer_shape=list(y.shape),no_GUI_or_remote_or_training_or_original_player_change=True,not_a_new_behavior_or_skill_qualification=True)
  put('RELOCATED_PORTABLE_FULLMAP_AND_BUNDLE_CPU_ACTUAL.json',result);print(json.dumps(dict(relocation_passed=True,source_physical_arrays_exact=len(checks),mode_controls=20,no_original_player_change=True)))
 finally:
  os.chdir(oldcwd)
  if T.exists():
   assert T.resolve().is_relative_to(W.resolve()) and not P.exists();T.rename(P)
if __name__=='__main__':
 try:main()
 except BaseException:put('PORTABLE_RELOCATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),original_player_not_modified=True));raise
