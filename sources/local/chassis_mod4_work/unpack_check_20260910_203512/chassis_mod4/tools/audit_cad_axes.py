"""Independently compare packaged joints to the STEP analytic cylinder axes."""
from pathlib import Path
import json
import numpy as np
import mujoco
ROOT=Path(__file__).resolve().parents[1]
parts=json.loads((ROOT/'reports/cad_parts.json').read_text(encoding='utf8'))
manifest=json.loads((ROOT/'reports/model_manifest.json').read_text(encoding='utf8'))
params=json.loads((ROOT/'model_parameters.json').read_text(encoding='utf8'))
rot=np.array(manifest['cad_to_model_rotation']);origin=np.array(manifest['cad_origin_mm'])
m=mujoco.MjModel.from_xml_path(str(ROOT/'scene.xml'));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
base=d.xpos[m.body('chassis').id];rows=[]
for side,delta in [('right',0),('left',91)]:
    tests=[('hip',144,24.55,'O'),('hip',119,20.,'O'),
      ('knee',144,23.525,'K'),('knee',134,15.075,'K'),
      ('rocker_pin',144,5.5,'P'),('rocker_pin',124,6.05,'P'),
      ('coupler_pin',119,6.05,'A'),('coupler_pin',120,5.025,'A'),
      ('distal_pin',124,6.05,'C'),('distal_pin',129,5.025,'C'),
      ('gas_pin',148,4.,'S'),('gas_pin',144,5.,'S'),
      ('drive_hip_spin',142,41.,None),('drive_input_spin',143,41.,None)]
    for joint,i,r,key in tests:
        i+=delta;p=parts[i];member=manifest['part_membership'][i]
        R=np.array(member['transform_rotation']);t=np.array(member['transform_translation_m'])
        candidates=[c for c in p['cylinders'] if abs(c['r']-r)<1e-4 and abs(c['axis'][0])>.99999]
        if key is not None:
            target=np.array(manifest['source_skeleton_xz_m'][side][key])
            candidates.sort(key=lambda c:np.linalg.norm((rot@(np.array(c['p'])-origin)*.001)[[0,2]]-target))
        assert candidates,(joint,i,r)
        c=candidates[0];axis=R@rot@np.array(c['axis']);point=R@rot@(np.array(c['p'])-origin)*.001+t+base
        anchor=d.xanchor[m.joint(side+'_'+joint).id];actual_axis=d.xaxis[m.joint(side+'_'+joint).id]
        error=np.linalg.norm(np.cross(anchor-point,axis));axis_error=1-abs(actual_axis@axis)
        assert error<1e-8 and axis_error<1e-10,(joint,i,error,axis_error)
        rows.append({'joint':side+'_'+joint,'source_part':i,'source_cylinder_radius_mm':r,'axis_line_distance_m':float(error),'axis_error':float(axis_error)})
    i=183 if side=='right' else 276;p=parts[i];member=manifest['part_membership'][i]
    c=next(c for c in p['cylinders'] if abs(c['r']-62.5)<1e-8 and abs(c['axis'][0])>.99999)
    point=np.array(c['p']);point[0]=.5*(p['bbox_mm'][0]+p['bbox_mm'][3])
    expected=np.array(member['transform_rotation'])@rot@(point-origin)*.001+member['transform_translation_m']+base
    tire=m.geom(side+'_tire').id;error=float(np.linalg.norm(d.geom_xpos[tire]-expected))
    assert error<1e-8,(side,error)
    assert np.allclose(m.geom_size[tire,:2],[.0625,.010],atol=1e-10)
    rows.append({'wheel':side,'source_part':i,'tire_center_error_m':error})
track=abs(d.geom_xpos[m.geom('left_tire').id,1]-d.geom_xpos[m.geom('right_tire').id,1])
assert abs(track-.4376)<1e-10
members=manifest['part_membership'];assert len(members)==277 and {p['id'] for p in members}==set(range(277))
assert all(p['mass_kg']>0 and p['body'] in manifest['body_masses_kg'] for p in members)
result={'status':'PASS','checks':rows,'tire_track_m':float(track),
    'max_axis_line_distance_m':max(r.get('axis_line_distance_m',r.get('tire_center_error_m',0)) for r in rows),
    'source_sha256':manifest['source']['source_sha256'],
    'scope':'STEP analytic axes for major hinges, both wheel contact centres and complete occurrence membership; SI conversion and neutral articulation verified.'}
(ROOT/'reports/cad_axis_audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print({k:v for k,v in result.items() if k!='checks'})
