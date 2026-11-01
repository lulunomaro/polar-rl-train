"""LQR physical full-state reference at 50Hz; no foreign transitions in WM replay."""
from pathlib import Path
import json,hashlib
import numpy as np
import mujoco
B=Path('/home/lc01/Zonglin Li/zonglin2/tasks')
ROOT=B/'MOD4_E0_LQR_SUPERMIMIC_STEP270_20261101'
TRAD=B/'MOD4_MUJOCO_LQR_MPC_STEP270_20261101'
if __name__=='__main__':
    import sys
    sys.path.insert(0,str(TRAD));from control_core import make_model
    m=make_model(True);joint_names=[m.joint(i).name for i in range(1,m.njnt)]
    src=TRAD/'results/FINAL_EVIDENCE_V2/nominal_lqr/trajectory.json';rows=json.load(open(src));rows=rows[::2]
    qpos=np.asarray([r['qpos'] for r in rows]);qvel=np.asarray([r['qvel'] for r in rows]);times=np.asarray([r['time'] for r in rows]);states=[]
    for q,v in zip(qpos,qvel):
        rot=np.empty(9);mujoco.mju_quat2Mat(rot,q[3:7]);omega=rot.reshape(3,3)@v[3:6]
        states.append(np.r_[q[:7],v[:3],omega,q[7:],v[6:]])
    states=np.asarray(states,np.float32);assert states.shape[1]==73 and len(joint_names)==30
    (ROOT/'reference').mkdir(exist_ok=True)
    np.savez_compressed(ROOT/'reference/lqr_step270_50hz.npz',states=states,times=times,joint_names=np.asarray(joint_names))
    receipt={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_engine':'MuJoCo 3.12.0','reference_hz':50,'samples':len(states),'packed_state':'pos3,quat_wxyz4,world_linvel3,world_angvel3,q30,qd30','joint_names':joint_names,'motion':'real LQR first-flight full-footprint 270mm and final stable2.95s','position_offset':'absolute local x remains -0.8 start, step edge0','imitation_reference_only_not_Isaac_world_model_transitions':True,'action_cloning':False,'no_forced_rollout_state':True,'shape':list(states.shape)}
    (ROOT/'reference/REFERENCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
