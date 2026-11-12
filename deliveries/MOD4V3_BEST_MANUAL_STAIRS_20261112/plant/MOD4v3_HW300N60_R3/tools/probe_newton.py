"""CPU Newton/SolverMuJoCo importer probe using the actual v3 coordinate defaults."""
from pathlib import Path
import argparse
import json
import inspect
import xml.etree.ElementTree as ET

import numpy as np
import warp as wp
import newton
import mujoco
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
    references={e.get('name'):float(e.get('ref','0'))for e in root.findall('.//body/joint')}
    for i,label in enumerate(one.joint_label):
        n=label.rsplit('/',1)[-1]
        if n in runtime['initial_joint_positions']:
            # Newton stores displacement from authored pose, q_MJCF-ref.
            # SolverMuJoCo adds dof_ref at its own conversion boundary.
            one.joint_q[one.joint_q_start[i]]=runtime['initial_joint_positions'][n]-references[n]
    builder=newton.ModelBuilder();SolverMuJoCo.register_custom_attributes(builder)
    builder.replicate(one,1)
    model=builder.finalize(device='cpu')
    solver=SolverMuJoCo(model,use_mujoco_cpu=True,separate_worlds=True,iterations=32,ls_iterations=15,
        integrator='implicitfast',solver='Newton',cone='elliptic',nconmax=128,njmax=512)
    state,next_state=model.state(),model.state();control=model.control()
    source_model=mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'))
    source_data=mujoco.MjData(source_model);mujoco.mj_forward(source_model,source_data)
    body_index={label.rsplit('/',1)[-1]:i for i,label in enumerate(model.body_label)}
    initial_body_error=0.
    for n,i in body_index.items():
        initial_body_error=max(initial_body_error,float(np.max(np.abs(state.body_q.numpy()[i,:3]-source_data.xpos[source_model.body(n).id]))))
    closure_pairs=[(e.get('site1'),e.get('site2'))for e in root.find('equality').findall('connect')]
    def closure_error(state):
        from scipy.spatial.transform import Rotation
        poses=state.body_q.numpy()
        points={}
        for pair in closure_pairs:
            for name in pair:
                site=source_model.site(name);bname=source_model.body(int(source_model.site_bodyid[site.id])).name
                b=poses[body_index[bname]]
                points[name]=b[:3]+Rotation.from_quat(b[3:]).apply(source_model.site_pos[site.id])
        return max(float(np.linalg.norm(points[x]-points[y]))for x,y in closure_pairs)
    initial_closure=closure_error(state);max_closure=initial_closure
    q0=state.joint_q.numpy().copy()
    for _ in range(20):
        state.clear_forces();solver.step(state,next_state,control,None,.0025);state,next_state=next_state,state
        max_closure=max(max_closure,closure_error(state))
        mujoco.mj_step(source_model,source_data)
    q=state.joint_q.numpy()
    if solver.mj_model.neq!=10:raise AssertionError('Imported equalities were lost')
    final_body_error=0.
    for n,i in body_index.items():
        final_body_error=max(final_body_error,float(np.max(np.abs(state.body_q.numpy()[i,:3]-source_data.xpos[source_model.body(n).id]))))
    report=dict(actual_Newton=True,version=str(getattr(newton,'__version__','unknown')),
        importer_options=options,actual_SolverMuJoCo=True,use_mujoco_cpu=True,GPU_started=False,
        body_count=model.body_count,joint_labels=model.joint_label,
        native_nq=solver.mj_model.nq,native_nv=solver.mj_model.nv,native_equalities=solver.mj_model.neq,
        physics_dt_s=.0025,steps=20,all_state_finite=bool(np.isfinite(q).all()),
        q_max_abs=float(np.max(np.abs(q))),initial_q_max_abs=float(np.max(np.abs(q0))),
        coordinate_default_source='runtime_config.json',policy_or_learning_updates=0,
        Newton_position_basis='MJCF_qpos_minus_authored_ref',
        initial_body_position_error_vs_direct_MJCF_m=initial_body_error,
        final_body_position_error_vs_direct_MJCF_m=final_body_error,
        initial_closure_m=initial_closure,max_closure_m=max_closure,
        source_and_solver_gravity_SI=[source_model.opt.gravity.tolist(),solver.mj_model.opt.gravity.tolist()],
        verified_initial_geometry=initial_body_error<1e-5 and initial_closure<1e-5,
        verified_closure10mm=max_closure<.01)
    print('MOD4V3_RESULT_JSON '+json.dumps(report))
    if not report['verified_initial_geometry']or not report['verified_closure10mm']:
        raise AssertionError('Newton geometry/closure diagnostic did not pass')


if __name__=='__main__':main()
