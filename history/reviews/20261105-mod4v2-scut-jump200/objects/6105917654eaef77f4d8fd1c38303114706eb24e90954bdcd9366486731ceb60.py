from pathlib import Path
import json
import numpy as np
import datetime
ROOT=Path(__file__).resolve().parent
summary={'time':datetime.datetime.now().astimezone().isoformat(),'source':json.loads((ROOT/'SOURCE_BINDING.json').read_text()),'policy_parity':json.loads((ROOT/'POLICY_PARITY.json').read_text()),'tests':{}}
for name in ['matrix01','extended01','extended_saved02','standing_gate01','standing_saved02','native_rough02','native_saved03']:
    p=ROOT/name
    meta=json.loads((p/'CASES.json').read_text()); d=np.load(p/'PHYSICAL.npz'); origin=np.array(meta['origins']); result=[]
    w=[meta['body_names'].index(s+'_wheel_link') for s in ['left','right']]
    cw=[meta['contact_names'].index(s+'_wheel_link') for s in ['left','right']]
    for i,case in enumerate(meta['cases']):
        active=d['active'][:,i].astype(bool)
        t=np.arange(len(active))*.005
        age=d['episode_step'][:,i]*.02
        root=d['root'][:,i];pos=root[:,:3]-origin[i]
        wp=d['body_pos'][:,i,w]-origin[i]
        force=np.linalg.norm(d['force'][:,i,cw],axis=-1)
        rel=wp-pos[:,None,:]
        leg_length=np.sqrt(rel[:,:,0]**2+rel[:,:,2]**2)
        standing=(t>=1.5)&(t<=2.4)&active
        whole=(wp[:,:,0]-.06>1.6).all(-1)&(wp[:,:,2]-.06>.202).all(-1)&active
        iend=np.flatnonzero(active)[-1]
        result.append({'case':i,**case,'first_episode_seconds':float(active.sum()*.005),'first_episode_root_x_max':float(pos[active,0].max()),'first_episode_root_z_gain_from_t1p5':float(pos[active,2].max()-pos[min(299,iend),2]),'first_episode_min_pair_wheel_bottom_max':float((wp[active,:,2]-.06).min(-1).max()),'stand_window_root_height_mean':float(pos[standing,2].mean()),'stand_window_projected_leg_length_mean':float(leg_length[standing].mean()),'stand_window_vertical_axis_ratio_mean':float((np.abs(rel[:,:,2])/np.maximum(leg_length,1.e-6))[standing].mean()),'whole_clear200_any':bool(whole.any()) if case['kind']=='single200' else None,'nonzero_vx_command_issued':bool((np.abs(d['command'][active,i,0])>0).any()),'final_root_x':float(pos[iend,0])})
    summary['tests'][name]={'envs':len(result),'source_compatibility':'Saved gimbal semantics; extra current defaults disabled' if 'saved' in name else 'Current public source has extra gimbal heading defaults absent from checkpoint YAML; exploratory, superseded by saved-semantics tests','cases':result,'standing_gate':json.loads((p/'STANDING_GATE.json').read_text()) if (p/'STANDING_GATE.json').exists() else None}

# Inspect the actual saved terrain, rather than equating the terrain name with vertical stairs.
p=ROOT/'native_saved03';terrain=np.load(p/'ACTUAL_TERRAIN.npz');assert np.all(terrain['counts']==3)
tri=terrain['vertices'][terrain['indices'].reshape(-1,3)]
normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=-1)
ok=length>1e-9;cosz=np.abs(normal[ok,2])/length[ok];slope=np.sqrt(np.maximum(0.,1-cosz*cosz))/np.maximum(cosz,1e-12)
interior=np.max(np.abs(tri[:,:,:2]),axis=(1,2))<3.3
interior_normal=normal[interior];il=np.linalg.norm(interior_normal,axis=-1);keep=il>1e-9
angles=np.rad2deg(np.arccos(np.clip(abs(interior_normal[keep,2])/il[keep],0,1)))
summary['actual_native_terrain']={'path':str(p/'ACTUAL_TERRAIN.npz'),'interior_surface_tilt_degrees_unique':np.unique(np.round(angles,3)).tolist(),'interior_vertical_triangle_count':int((angles>89.).sum()),'scope':'Actual saved native generated terrain mesh interior, excluding external border; not a vertical200mm face'}
summary['verdict']={'public_weights_actual_native_execution':True,'extended_saved_semantics_single200_wholeclear_successes':sum(r['whole_clear200_any'] for r in summary['tests']['extended_saved02']['cases'] if r['kind']=='single200'),'extended_saved_semantics_single200_attempts':8,'standing_saved_semantics_approach_started':sum(summary['tests']['standing_saved02']['standing_gate']['approach_started']),'standing_saved_semantics_envs':24,'native_generated_ascent_is_not_proof_of_vertical_step_jump':True,'MOD4_distillation_started':False,'training_or_optimizers_in_this_teacher_verification':0,'limitations':['Fixed one public checkpoint1000, finite commands/heights and seed66, one first episode per case; not impossibility proof','Old training environment revision is not fully recoverable from saved YAML/current source; extra known gimbal defaults were disabled explicitly','Initial tests under mixed public defaults retained and labelled exploratory','Standing test commands extension via original trained height input, not locking joints or external physical assistance','Original high command is not proof of completely straight linkage or standing stability']}
(ROOT/'VERIFICATION_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'verdict':summary['verdict'],'terrain':summary['actual_native_terrain'],'native_saved03_root_x_max':[r['first_episode_root_x_max'] for r in summary['tests']['native_saved03']['cases']],'extended_leg_lengths':[r['stand_window_projected_leg_length_mean'] for r in summary['tests']['extended_saved02']['cases']],'summary':str(ROOT/'VERIFICATION_SUMMARY.json')},ensure_ascii=False))
