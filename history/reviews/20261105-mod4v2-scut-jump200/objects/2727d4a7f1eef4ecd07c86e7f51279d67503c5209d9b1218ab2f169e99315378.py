from pathlib import Path
import sys,json,time
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.newton_model import NewtonPlant
from mujoco_warp._src.collision_driver import MJ_COLLISION_TABLE
from mujoco_warp._src.types import CollisionType
import mujoco
p=NewtonPlant('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package',1,'cuda:0')
m=p.solver.mj_model;w=p.solver.mjw_model;d=p.solver.mj_data
collisions=[]
for c in d.contact:
 collisions.append(dict(geoms=[mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,int(i))for i in c.geom],dist=float(c.dist)))
pairs=w.nxn_geom_pair_filtered.numpy();types=w.geom_type.numpy()
convex=[]
for a,b in pairs:
 if a<0 or b<0:continue
 key=tuple(sorted([int(types[a]),int(types[b])]))
 if MJ_COLLISION_TABLE.get(key)==CollisionType.CONVEX:convex.append([int(a),int(b)])
out=dict(epoch=time.time(),ncon=d.ncon,nefc=d.nefc,njmax=p.solver.mjw_data.njmax,
    naccdmax=p.solver.mjw_data.naccdmax,allpair_count=len(pairs),convexpair_count=len(convex),
    q=p.state.joint_q.numpy().tolist(),mjq=d.qpos.tolist(),collisions=collisions,
    productionPT=0,physics_steps=0)
with(N/'reports/NEWTON_COLLISION_MEMORY_DIAGNOSIS.json').open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
print(json.dumps(out))
