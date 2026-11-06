"""Render recorded body poses only; no policy inference or physics stepping."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--evaluation',type=Path,required=True)
    p.add_argument('--startup',type=Path,required=True)
    p.add_argument('--usd',type=Path,required=True)
    p.add_argument('--renderer-library',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    import numpy as np
    import mujoco
    from PIL import Image,ImageDraw
    sys.path.insert(0,str(a.renderer_library))
    from render_standing_recorded_v2 import mesh_visuals
    startup=json.loads(a.startup.read_bytes())
    result=json.loads((a.evaluation/'RESULT.json').read_bytes())
    names=startup['native_body_names']
    source=a.evaluation/'actual_replay.npz'
    with np.load(source,allow_pickle=False) as z:
        poses={k:z[k].copy() for k in z.files}
    assert poses['body_pos'].shape[2]==len(names)
    assert np.isfinite(poses['body_pos']).all() and np.isfinite(poses['body_quat']).all()
    elements,vfs=mesh_visuals(a.usd,names)
    root=ET.Element('mujoco',model='saved MOD4v3 PhysX poses only')
    ET.SubElement(root,'compiler',angle='radian')
    visual=ET.SubElement(root,'visual')
    ET.SubElement(visual,'global',offwidth='640',offheight='400')
    ET.SubElement(visual,'headlight',ambient='.6 .6 .6',diffuse='.6 .6 .6')
    assets=ET.SubElement(root,'asset');world=ET.SubElement(root,'worldbody')
    ET.SubElement(world,'light',pos='0 -1 3',dir='0 0 -1')
    for name,file in elements:
        ET.SubElement(assets,'mesh',name=name,file=file)
        body=ET.SubElement(world,'body',name=name,mocap='true',pos='0 0 -10')
        color='.15 .18 .22 1' if 'wheel' in name else '.73 .77 .82 1'
        ET.SubElement(body,'geom',type='mesh',mesh=name,contype='0',conaffinity='0',density='0',rgba=color)
    model=mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'),vfs)
    data=mujoco.MjData(model)
    assert model.nq==0 and model.nmocap==len(names)
    ids=np.array([model.body_mocapid[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,n)] for n in names])
    renderer=mujoco.Renderer(model,height=400,width=640)
    camera=mujoco.MjvCamera();mujoco.mjv_defaultCamera(camera)
    a.output.mkdir(parents=True,exist_ok=False)
    media=[];cases=[]
    try:
        for case in [0,20,40,60]:
            done=poses['terminated'][:,case]|poses['timeout'][:,case]
            ends=np.flatnonzero(done)
            last=int(ends[0]) if len(ends) else len(done)-1
            indices=np.linspace(0,last,6).round().astype(int)
            offset=poses['root_pos'][0,case].copy()
            for top in [False,True]:
                sheet=Image.new('RGB',(1920,800))
                for k,i in enumerate(indices):
                    pos=poses['body_pos'][i,case]-offset
                    data.mocap_pos[ids]=pos
                    data.mocap_quat[ids]=poses['body_quat'][i,case]
                    mujoco.mj_forward(model,data)
                    camera.lookat[:]=pos[names.index('base_link')]
                    camera.distance=1.5;camera.azimuth=90;camera.elevation=-89 if top else -18
                    renderer.update_scene(data,camera)
                    tile=Image.fromarray(renderer.render());draw=ImageDraw.Draw(tile)
                    draw.rectangle((0,0,640,46),fill='black')
                    draw.text((6,6),'Saved PhysX env%d %.2fs vx=%.3f'%(case,(i+1)*.02,poses['velocity'][i,case,0]),fill='white')
                    draw.text((6,24),'Actual body poses; terrain was not recorded',fill='white')
                    sheet.paste(tile,((k%3)*640,(k//3)*400))
                target=a.output/('env%d_%s.png'%(case,'top' if top else 'side'))
                sheet.save(target);media.append(target)
            cases.append(dict(env=case,first_episode_seconds=(last+1)*.02,
                last_vx=float(poses['velocity'][last,case,0]),
                last_L0=poses['length'][last,case].tolist(),last_theta=poses['theta'][last,case].tolist()))
    finally:
        renderer.close()
    def artifact(path):
        return dict(path=str(path),bytes=path.stat().st_size,SHA=hashlib.sha256(path.read_bytes()).hexdigest())
    report=dict(checkpoint=result['restore']['source'],source=artifact(source),USD=artifact(a.usd),
        body_names_source=artifact(a.startup),
        body_names_association='Later native STARTUP, same released USD and SDK; source NPZ omitted names',
        quaternion_order='wxyz from semantic view',terrain='not recorded; no terrain drawn',
        zero_policy_reads=True,zero_physics_steps=True,render_forward_only=True,
        cases=cases,media=[artifact(x) for x in media])
    (a.output/'RENDER_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(output=str(a.output),rendered_cases=len(cases),media=len(media))))


if __name__=='__main__':main()
