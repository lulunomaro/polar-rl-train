"""Apply motor/gas numerical settings to all MJCF variants and rebuild USD.

Masses and mechanical limits require a separate CAD/inertia audit and are not
silently changed by this tool. Re-run acceptance after parameter changes.
"""
from pathlib import Path
import sys,json,subprocess,argparse
import numpy as np
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--gas-force',type=float);args=parser.parse_args()
p=json.loads((ROOT/'model_parameters.json').read_text(encoding='utf8'))
if args.gas_force is not None:
    if not 0.<=args.gas_force<=1500.:parser.error('Gas force must be in 0..1500 N; no stability claim above the audited candidate.')
    p['gas_spring']['force_extended_n']=args.gas_force
g=p['gas_spring'];g['stiffness_n_m']=g['force_extended_n']*(g['force_ratio']-1)/g['nominal_stroke_m']
if g['stiffness_n_m']<0:raise ValueError('Invalid spring parameters')
manifest=json.loads((ROOT/'reports/model_manifest.json').read_text(encoding='utf8'))
f=lambda v:' '.join(f'{float(x):.12g}' for x in np.asarray(v).ravel())
for filename in ['scene.xml','scene_training.xml','scene_headless.xml','robot_hifi.xml']:
    tree=ET.parse(ROOT/filename);root=tree.getroot()
    for side in ['left','right']:
        pts=manifest['neutral_skeleton_xz_m'][side];length=np.linalg.norm(np.array(pts['T'])-pts['S'])
        joint=root.find(f".//body/joint[@name='{side}_gas_slide']")
        joint.set('stiffness',f([g['stiffness_n_m']]));joint.set('damping',f([g['damping_n_s_m']]))
        target=0. if g['stiffness_n_m']==0 else g['force_extended_n']/g['stiffness_n_m']+g['extended_eye_length_m']-length
        joint.set('springref',f([target]))
        for name in ['hip','crank','wheel_spin']:
            motor=p['wheel_motor' if name=='wheel_spin' else 'leg_motor']
            joint=root.find(f".//body/joint[@name='{side}_{name}']");joint.set('armature',f([motor['output_armature_kg_m2']]))
            actuator=root.find(f"actuator/motor[@name='{side}_{name}_motor']")
            limit=motor['peak_torque_nm'];assert limit>0
            for field in ['ctrlrange','forcerange']:actuator.set(field,f([-limit,limit]))
    ET.indent(root,space='  ');tree.write(ROOT/filename,encoding='utf8',xml_declaration=True)
(ROOT/'model_parameters.json').write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf8')
subprocess.run([sys.executable,str(ROOT/'tools/export_usd.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'tools/make_usd_scene.py')],check=True)
print('Parameters applied. Re-run tools/validate_model.py and the USD audits before training.')
