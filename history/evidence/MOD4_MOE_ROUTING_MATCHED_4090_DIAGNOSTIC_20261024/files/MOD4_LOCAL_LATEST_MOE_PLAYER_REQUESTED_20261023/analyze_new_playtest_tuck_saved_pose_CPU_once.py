from pathlib import Path
import json,sys,time,traceback
import numpy as np,mujoco
B=Path(__file__).resolve().parent;R=B/'reports';sys.path.insert(0,str(B/'player'))
from rm7v7_moe_sim import RM7V7MoESim
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 report=json.loads((R/'REQUESTED_LOCAL_RUN_JUMP_PLAYTEST_CPU_ACTUAL.json').read_bytes());sim=RM7V7MoESim();out={}
 with np.load(B/'PLAYTEST_SELECTED_LOCAL_TRACES.npz',allow_pickle=False) as raw:
  for case in ('jump_flat','jump_route'):
   rows=raw[case+'_state'];q=raw[case+'_qpos'];peak=int(np.argmax(rows[:,6]));indices=sorted(set([0,99,119,139,159,179,199,239,299,len(rows)-1,peak]));selected=[];source=next(x for x in report['cases'] if x['case']==case)['route_source'];normal=np.asarray(source['spawn_surface_normal']);spawn=np.asarray(source['spawn_ground_m'])
   for i in indices:
    sim.data.qpos[:]=q[i];mujoco.mj_forward(sim.model,sim.data);legs=[];bottom=[];relative=[]
    for side in ('left','right'):
     body=int(sim.model.jnt_bodyid[sim._joint(side+'_wheel_spin')]);legs.append(float(np.linalg.norm(sim.data.xpos[sim.chassis_id]-sim.data.xpos[body])))
     g=mujoco.mj_name2id(sim.model,mujoco.mjtObj.mjOBJ_GEOM,side+'_tire');assert sim.model.geom_type[g]==mujoco.mjtGeom.mjGEOM_CYLINDER
     axis=sim.data.geom_xmat[g].reshape(3,3)[:,2];extent=sim.model.geom_size[g,0]*np.sqrt(max(0.,1.-axis[2]**2))+sim.model.geom_size[g,1]*abs(axis[2]);z=float(sim.data.geom_xpos[g,2]-extent);bottom.append(z)
     xyz=sim.data.geom_xpos[g];planez=spawn[2]-(normal[0]*(xyz[0]-spawn[0])+normal[1]*(xyz[1]-spawn[1]))/normal[2];relative.append(float(z-planez))
    selected.append(dict(control=i+1,sim_time_s=float(rows[i,0]),mode=int(rows[i,1]),chassis_to_wheel_axle_3D_m=legs,tire_cylinder_bottom_world_z_m=bottom,tire_bottom_relative_to_source_spawn_plane_m=relative,recorded_total_MuJoCo_contact_count=int(rows[i,10]),chassis_z_m=float(rows[i,6]),upright_cos=float(rows[i,7])))
   out[case]=dict(base_peak_control=peak+1,selected_saved_poses=selected)
 put('NEW_LOCAL_PLAYTEST_SAVED_POSE_TUCK_DIAGNOSTIC_CPU_ACTUAL.json',dict(epoch=time.time(),source_artifact=report['artifact'],result=out,scope='Kinematic reconstruction of eleven saved MuJoCo poses per jump, actual model wheel joints/cylinder geometry, not a fresh control replay or PhysX callback. Spawn plane reference is not an obstacle/top-contact query. Total contacts include every robot/terrain contact; zero means none at the saved control endpoint.',no_270mm_success_or_unique_cause_claim=True))
 print(json.dumps({k:next(x for x in v['selected_saved_poses'] if x['control']==v['base_peak_control']) for k,v in out.items()}))
except BaseException:put('NEW_PLAYTEST_TUCK_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
