"""Bounded actual TRAIN first-bar identity extraction; no physics/raw rehash.
Accept a case id under this workspace and stop streaming at first positive bar
contact. This is private grade, never controller input or a pass rewrite.
"""
from pathlib import Path
import argparse,bisect,hashlib,json,math
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
assert Path(a.case).name==a.case
D=R/'results'/a.case;rp=D/'result.json';raw=rp.read_bytes();r=json.loads(raw);first_air=r['first_all_world_air_s'];rows=0;event=None
with (D/'physics.jsonl').open(encoding='utf-8')as f:
    for line in f:
        z=json.loads(line);rows+=1
        cc=[c for c in z['environment_contacts']if c['environment_geom']=='rm_bar_011'and c['normal_N']>1.]
        if cc:
            t=z['stage_time_s'];diag=z['private_contact_diagnostic'];A=diag['root_rotation_world_from_body33_pre']
            event=dict(stage_time_s=t,first_fullair_s=first_air,strictly_before_first_fullair=first_air is not None and t<first_air,
                air_qualified_at_event=z['air_qualified'],main_N2=z['main_normal_N2'],all_world_normal_N=z['all_world_normal_N'],
                root_pre_m=z['drivepoint']['root_xyz_pre_m'],pitch_pre_rad=math.asin(max(-1.,min(1.,-A[2][0]))),contacts=cc)
            break
        if first_air is not None and z['stage_time_s']>first_air+1.:break
if event is not None:
    near=None
    with (D/'trace.jsonl').open(encoding='utf-8')as f:
        for line in f:
            x=json.loads(line)
            if x['command_time_s']>event['stage_time_s']+1e-9:break
            near=x
    assert near is not None
    event['bracket_control']=dict(command_time_s=near['command_time_s'],sensor_time_s=near['sensor_time_s'],
        phase=near['phase']['phase'],estimated14=near['estimated14'],landing_position_ref4=near['phase']['landing_position_ref4'],
        capture_weight=near['phase']['landing_transition_weight'])
out=a.out.resolve();assert out.is_relative_to(R);out.parent.mkdir(exist_ok=True)
v=dict(kind='PRIVATE_FIRST_BAR_CONTACT_TRAIN_ONLY',case=a.case,result_SHA=hashlib.sha256(raw).hexdigest(),event=event,
    physics_rows_examined=rows,physical_artifact_producer=r['physical_artifact'],controls_producer=r['trace_artifact'],
    no_new_physics=True,no_raw_archive_rehash=True,no_gate_or_H5_change=True,PH6_pending=True)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
print(json.dumps(dict(case=a.case,physics_rows_examined=rows,event=event),indent=2,allow_nan=False))
