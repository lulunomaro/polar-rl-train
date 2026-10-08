"""Export the exact downloaded actor and create an isolated MuJoCo playground."""
from pathlib import Path
import hashlib,json,shutil,xml.etree.ElementTree as ET
import numpy as np
import torch
from torch import nn
import onnxruntime as ort

D=Path(__file__).resolve().parent;W=D.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=json.loads((D/'DOWNLOAD_RECEIPT.json').read_text());checkpoint=Path(receipt['local_checkpoint'])
    assert sha(checkpoint)==receipt['checkpoint_sha256']
    saved=torch.load(checkpoint,map_location='cpu',weights_only=False)
    actor=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6)).eval()
    actor.load_state_dict({k.removeprefix('mlp.'):v for k,v in saved['actor_state_dict'].items() if k.startswith('mlp.')})
    torch.set_num_threads(1)
    onnx=D/(checkpoint.stem+'.onnx')
    torch.onnx.export(actor,torch.zeros(1,35),str(onnx),input_names=['observation'],output_names=['action'],opset_version=17,dynamo=False)
    rng=np.random.default_rng(61008);fixture=rng.normal(size=(64,35)).astype('float32')
    session=ort.InferenceSession(str(onnx),providers=['CPUExecutionProvider'])
    errors=[]
    with torch.no_grad():
        for x in fixture:
            ref=actor(torch.from_numpy(x[None])).numpy();out=session.run(None,{'observation':x[None]})[0]
            errors.append(float(np.max(np.abs(ref-out))))
    print('ONNX float32 fixture max absolute action error:',max(errors),flush=True)
    assert max(errors)<1e-3, errors
    for name in ('sim_runtime.py','policy_runtime.py'):
        shutil.copyfile(W/'mod4-onnx-mujoco-launcher-git'/name,D/name)
    c=json.loads((D/'src_snapshot/import_contract.json').read_text())
    source=W/'mod4-onnx-mujoco-launcher/model/source_rolling_model.xml'
    tree=ET.parse(source);root=tree.getroot();root.set('model','MOD4 latest D5 - manual MuJoCo playground')
    root.find('compiler').set('meshdir',(W/'chassis_mod4/assets').as_posix())
    # MuJoCo uses its own 0.5 ms Newton integration; 100 Hz policy matches training.
    # This is a separate sim-to-sim adapter, not a PhysX-equivalent reproduction.
    root.find('option').set('timestep','0.0005')
    world=root.find('worldbody')
    for geom in list(world.findall('geom')):world.remove(geom)
    for body in root.findall('.//body'):
        name=body.get('name')
        if name.startswith('guide_roller_'):body.set('name','guide_roller_'+name.split('_')[-1].zfill(2))
        info=c['bodies'][body.get('name')]
        inertial=body.find('inertial')
        if inertial is not None:
            for key in ('fullinertia','quat','axisangle','xyaxes','zaxis','euler'):inertial.attrib.pop(key,None)
            inertial.set('mass',str(info['mass_kg']));inertial.set('pos',' '.join(map(str,info['com_m'])))
            inertial.set('diaginertia',' '.join(map(str,info['diagonal_inertia_kg_m2'])))
            inertial.set('quat',' '.join(map(str,info['principal_axes_wxyz'])))
    for joint in world.findall('.//joint'):
        name=joint.get('name')
        if name.startswith('guide_roller_'):
            i=int(name.split('_')[-1]);joint.set('name','guide_roller_'+str(i).zfill(2));name=joint.get('name')
        info=c['joints'].get(name) or c['roller_joints'].get(name)
        if not info:continue
        joint.set('armature',str(info['armature']));joint.set('damping',str(info['damping_si']))
        if info['limits_si'] is not None:joint.set('range',' '.join(map(str,info['limits_si'])))
        if name in ('left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin'):
            # Damping is supplied once by the matching PD controller.
            joint.set('damping','0')
        if name in c['gas_springs']:
            gas=c['gas_springs'][name];joint.set('stiffness',str(gas['stiffness_n_m']));joint.set('springref',str(gas['target_position_m']))
    asset=root.find('asset')
    ET.SubElement(asset,'texture',name='playgrid',type='2d',builtin='checker',rgb1='.19 .23 .29',rgb2='.24 .29 .35',width='512',height='512')
    ET.SubElement(asset,'material',name='playground',texture='playgrid',texrepeat='20 16',texuniform='true',reflectance='.05')
    ET.SubElement(asset,'hfield',name='ripples',nrow='41',ncol='241',size='5 .9 .025 .02')
    ET.SubElement(asset,'hfield',name='gentle_ramp',nrow='41',ncol='161',size='3.5 .9 .08 .02')
    ET.SubElement(world,'geom',name='play_floor',type='plane',size='20 15 .1',material='playground',contype='1',conaffinity='2')
    ET.SubElement(world,'geom',name='ripple_lane',type='hfield',hfield='ripples',pos='6 0 0',rgba='.45 .63 .45 1',contype='1',conaffinity='2')
    ET.SubElement(world,'geom',name='ramp_lane',type='hfield',hfield='gentle_ramp',pos='5 2.7 0',rgba='.50 .57 .71 1',contype='1',conaffinity='2')
    ET.SubElement(world,'light',pos='0 -3 6',dir='0 .3 -1',diffuse='.8 .8 .8',directional='true')
    for x in range(-3,13):
        for y in (-1.04,1.04):
            ET.SubElement(world,'geom',type='box',pos=f'{x} {y} .0006',size='.22 .018 .0005',rgba='.76 .80 .60 1',contype='0',conaffinity='0')
    root.find('statistic').set('extent','12');root.find('statistic').set('center','4 0 .3')
    ET.indent(tree,space='  ');tree.write(D/'playground.xml',encoding='utf8',xml_declaration=True)
    x=np.linspace(0,1,241);y=np.linspace(-1,1,41)
    taper=np.minimum(1,np.minimum(x*10,(1-x)*10));side=np.clip((1-np.abs(y))/.15,0,1)
    z=(.15+.85*np.sin(2*np.pi*6*x)**2)*taper
    ripples=side[:,None]*z[None,:]
    x2=np.linspace(0,1,161);ramp=side[:,None]*np.sin(np.pi*x2)[None,:]**2
    np.savez(D/'terrain.npz',ripples=ripples.astype('float32'),gentle_ramp=ramp.astype('float32'))
    delivery=json.loads((D/'contract_rm2025_later.json').read_text())
    runtime=dict(leg_kp=delivery['leg_kp'],leg_kd=delivery['leg_kd'],wheel_kd=delivery['wheel_kd'],crank_scale=delivery['leg_action_scale'],hip_scale=delivery['leg_action_scale'],wheel_scale=delivery['wheel_action_scale'],diff_min=c['training_window']['input_difference_min_rad'],diff_max=.85,leg_effort=delivery['leg_effort'],leg_stall=delivery['leg_voltage_line_intercept'],leg_no_load=delivery['leg_no_load'],wheel_effort=delivery['wheel_effort'],wheel_stall=delivery['wheel_voltage_line_intercept'],wheel_no_load=delivery['wheel_no_load'],policy_hz=100,yaw_assist_gain=0)
    (D/'runtime_config.json').write_text(json.dumps(runtime,indent=2),encoding='utf8')
    report=dict(checkpoint=checkpoint.name,checkpoint_sha256=sha(checkpoint),onnx=onnx.name,onnx_sha256=sha(onnx),actor_fixture_count=64,max_actor_export_error=max(errors),action_permutation='identity: crank,hip,crank,hip,wheel,wheel',original_rolling_MJCF_sha256=sha(source),adapted_MJCF_sha256=sha(D/'playground.xml'),nominal_parameters_source=c['source_mjcf_sha256'],parameter_readback_pending=True,MuJoCo_dt=.0005,policy_hz=100,no_yaw_or_stabilization_assist=True,terrain_ripple_height_m=.025,terrain_ramp_height_m=.08,formal_Isaac_evaluation=False)
    (D/'BUILD_RECEIPT.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
if __name__=='__main__':main()
