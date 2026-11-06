"""CPU Newton/SolverMuJoCo importer probe using the actual v3 coordinate defaults."""
from pathlib import Path
import argparse
import json
import inspect
import xml.etree.ElementTree as ET

import numpy as np
import warp as wp
import newton
from newton.solvers import SolverMuJoCo


def main():
    parser=argparse.ArgumentParser();parser.add_argument('package',type=Path);a=parser.parse_args()
    p=a.package;root=ET.parse(p/'mjcf/scene.xml').getroot()
    for parent in root.iter():
        for child in list(parent):
            if child.tag=='mesh' or child.tag=='geom'and child.get('class')=='visual':parent.remove(child)
    for geom in root.iter('geom'):
        if not geom.get('gap'):geom.set('gap','0')
    runtime=json.loads((p/'runtime_config.json').read_bytes())
    one=newton.ModelBuilder();SolverMuJoCo.register_custom_attributes(one)
    signature=inspect.signature(one.add_mjcf).parameters
    options=dict(parse_meshes=False,parse_visuals=False,collapse_fixed_joints=False,ctrl_direct=False)
    if 'convert_mjc_equality_constraints'in signature:
        options['convert_mjc_equality_constraints']=True
    elif 'skip_equality_constraints'in signature:
        options['skip_equality_constraints']=False
    else:
        raise RuntimeError('Installed Newton importer has no explicit equality support')
    if 'collapse_massless_fixed_root'in signature:options['collapse_massless_fixed_root']=False
    one.add_mjcf(ET.tostring(root,encoding='unicode'),**options)
    for i,label in enumerate(one.joint_label):
        n=label.rsplit('/',1)[-1]
        if n in runtime['initial_joint_positions']:
            one.joint_q[one.joint_q_start[i]]=runtime['initial_joint_positions'][n]
    builder=newton.ModelBuilder();SolverMuJoCo.register_custom_attributes(builder)
    builder.replicate(one,1)
    model=builder.finalize(device='cpu')
    solver=SolverMuJoCo(model,use_mujoco_cpu=True,separate_worlds=True,iterations=32,ls_iterations=15,
        integrator='implicitfast',solver='Newton',cone='elliptic',nconmax=128,njmax=512)
    state,next_state=model.state(),model.state();control=model.control()
    q0=state.joint_q.numpy().copy()
    for _ in range(20):
        state.clear_forces();solver.step(state,next_state,control,None,.0025);state,next_state=next_state,state
    q=state.joint_q.numpy()
    if solver.mj_model.neq!=10:raise AssertionError('Imported equalities were lost')
    report=dict(actual_Newton=True,version=str(getattr(newton,'__version__','unknown')),
        importer_options=options,actual_SolverMuJoCo=True,use_mujoco_cpu=True,GPU_started=False,
        body_count=model.body_count,joint_labels=model.joint_label,
        native_nq=solver.mj_model.nq,native_nv=solver.mj_model.nv,native_equalities=solver.mj_model.neq,
        physics_dt_s=.0025,steps=20,all_state_finite=bool(np.isfinite(q).all()),
        q_max_abs=float(np.max(np.abs(q))),initial_q_max_abs=float(np.max(np.abs(q0))),
        coordinate_default_source='runtime_config.json',policy_or_learning_updates=0)
    print('MOD4V3_RESULT_JSON '+json.dumps(report))


if __name__=='__main__':main()
