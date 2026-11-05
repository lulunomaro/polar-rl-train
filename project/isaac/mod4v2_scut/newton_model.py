"""MOD4v2's released MJCF on Newton's actual MuJoCo/Warp solver.

Only visual meshes are omitted from the training model. Authored inertials,
collision geometry, loop equalities, mimic coordinates and gas springs remain.
The simulation solver changes explicitly from PhysX TGS to MuJoCo Newton.
"""
from pathlib import Path
import hashlib
import json
import os
import xml.etree.ElementTree as ET

import newton
import numpy as np
import warp as wp
from newton.solvers import SolverMuJoCo


def training_xml(package):
    path = Path(os.environ.get('MOD4V2_NEWTON_MJCF',str(Path(package) / 'mjcf/scene.xml')))
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    for parent in root.iter():
        for child in list(parent):
            if child.tag == 'mesh' or (child.tag == 'geom' and child.get('class') == 'visual'):
                parent.remove(child)
    # MuJoCo's omitted gap means0. Newton's generic .1m broad-phase gap is
    # unsuitable here: the importer otherwise inflates hundreds of inactive
    # contact records per world and the20k EPA workspace exceeds24GiB.
    for geom in root.iter('geom'):
        if 'gap'not in geom.attrib:geom.set('gap','0')
    world = root.find('worldbody')
    for geom in world.findall('geom'):
        # Independent world copies use a finite ground patch, as the old course.
        if geom.get('name') == 'ground':
            geom.set('type', 'box')
            geom.set('pos', '0 0 -.05')
            geom.set('size', '3.6 3.6 .05')
            geom.set('conaffinity', '3')
    ET.SubElement(world, 'geom', name='jump200_platform', type='box',
                  pos='2.15 0 .1', size='1.35 3.5 .1',
                  contype='1', conaffinity='3', friction='.9 .003 .0001',
                  margin='0', condim='3')
    world.find("geom[@name='jump200_platform']").set('gap','0')
    return ET.tostring(root, encoding='unicode'), dict(
        source_path=str(path), source_SHA=hashlib.sha256(raw).hexdigest(),
        source_bytes=len(raw), visual_meshes_omitted=True,
        equality_count=len(root.find('equality')), source_inertials_retained=True,
        step_height_m=.2, edge_x_m=.8, top_end_x_m=3.5,
        physics_dt=.0025, solver='Newton/SolverMuJoCo',
        solver_is_PhysX_TGS=False, physical_assists=False)


class NewtonPlant:
    """Batched independent worlds, with no Omniverse or PhysX dependency."""
    def __init__(self, package, num_envs=1, device='cuda:0', cpu=False):
        self.package, self.num_envs, self.device = Path(package), num_envs, device
        source, self.receipt = training_xml(package)
        one = newton.ModelBuilder()
        SolverMuJoCo.register_custom_attributes(one)
        one.add_mjcf(source, parse_meshes=False, parse_visuals=False,
                     collapse_fixed_joints=False, collapse_massless_fixed_root=False,
                     convert_mjc_equality_constraints=True, ctrl_direct=False)
        # Allocate solver buffers from one valid authored reset pose. Zero
        # coordinates fold the closed chains into hundreds of initial overlaps.
        from . import BINDINGS
        poses=json.loads(Path(BINDINGS['reset_bank']).read_bytes())['poses']
        pose=next(p for p in poses if .24 <= p['root_height_m'] <= .272)
        one.joint_q[:7]=[0.,0.,.38,0.,0.,0.,1.]
        for i,label in enumerate(one.joint_label[1:31],1):
            name=label.rsplit('/',1)[-1]
            one.joint_q[one.joint_q_start[i]]=pose['joint_pos'].get(name,0.)
        builder = newton.ModelBuilder()
        SolverMuJoCo.register_custom_attributes(builder)
        builder.replicate(one, num_envs)
        self.model = builder.finalize(device=device)
        self.solver = SolverMuJoCo(self.model, use_mujoco_cpu=cpu,
            separate_worlds=True, iterations=32, ls_iterations=15,
            integrator='implicitfast', solver='Newton', cone='elliptic',
            nconmax=128, njmax=512, enable_multiccd=True)
        if not cpu and wp.get_cuda_driver_version() < (12,4):
            self.solver.mjw_model.opt.graph_conditional=False
        self.state, self.next_state = self.model.state(), self.model.state()
        self.control = self.model.control()
        self.initial_q = self.state.joint_q.numpy().copy()
        self.body_names = [s.rsplit('/', 1)[-1] for s in self.model.body_label[:31]]
        self.joint_names = [s.rsplit('/', 1)[-1] for s in self.model.joint_label[:31]]
        self.receipt.update(body_count=self.model.body_count,
                            world_count=self.model.world_count,
                            body_labels=self.model.body_label[:31],
                            joint_labels=self.model.joint_label[:37],
                            source_equalities=10,
                            native_equality_count=self.solver.mj_model.neq,
                            native_nq=self.solver.mj_model.nq,
                            native_nv=self.solver.mj_model.nv,
                            actual_CPU_backend=cpu,
                            actual_Warp_backend=not cpu)

    def step(self):
        self.state.clear_forces()
        self.solver.step(self.state, self.next_state, self.control, None, .0025)
        self.state, self.next_state = self.next_state, self.state
