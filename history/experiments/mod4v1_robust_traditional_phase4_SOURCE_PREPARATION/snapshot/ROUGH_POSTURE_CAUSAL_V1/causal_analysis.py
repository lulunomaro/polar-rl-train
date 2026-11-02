"""Existing R22 TRAIN analysis + sparse analytic rigid-box geometry,0physics.
Truth offline only; no new2kcontact/force identity reconstructed from100Hz rows.
"""
from pathlib import Path
import hashlib,json,math,sys,xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parent;TASK=R.parent;sys.path.insert(0,str(TASK))
from CONTACT_PROXY_NOMINAL_V1.nominal_model import NominalModel
CASES=[f'r22_height{d}bar{h}' for d in (0,20,40) for h in (40,60)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cv(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {k:cv(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [cv(v) for v in x]
    return x

def rotation(g):
    r,p,y=g['roll_true'],g['pitch_true'],g['yaw_true'];cr,sr=np.cos(r),np.sin(r);cp,sp=np.cos(p),np.sin(p);cy,sy=np.cos(y),np.sin(y)
    return np.array([[cy*cp,cy*sp*sr-sy*cr,cy*sp*cr+sy*sr],[sy*cp,sy*sp*sr+cy*cr,sy*sp*cr-cy*sr],[-sp,cp*sr,cp*cr]])

def sat_box(cA,RA,a,cB,b):
    axes=[RA[:,i] for i in range(3)]+[np.eye(3)[:,i] for i in range(3)]+[np.cross(RA[:,i],np.eye(3)[:,j]) for i in range(3) for j in range(3)]
    gaps=[]
    for ax in axes:
        norm=np.linalg.norm(ax)
        if norm<1e-12:continue
        n=ax/norm;gaps.append(float(abs((cA-cB)@n)-np.sum(a*abs(RA.T@n))-np.sum(b*abs(n))))
    return max(gaps)

def main(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);assert not (out/'RESULT.json').exists();m=NominalModel();xml=TASK/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml';assert sha(xml)=='0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324';tree=ET.fromstring(xml.read_bytes());body=tree.find("worldbody/body[@name='chassis']");rigid=[]
    for e in body.findall('geom'):
        if e.get('type')=='box':rigid.append({'name':e.get('name'),'local_center':np.array(list(map(float,e.get('pos','0 0 0').split()))),'half_size':np.array(list(map(float,e.get('size').split())))})
    corners=np.array([[i,j,k] for i in (-1,1) for j in(-1,1) for k in(-1,1)])
    bank=json.loads((TASK/'TALL_ROUGH_BANK_V1/INDEX.json').read_text(encoding='utf-8'));nominal=[]
    for row in bank['rows']:
        q=np.array([row['q'][3],row['q'][3]+row['q'][4],row['q'][5],row['q'][5]+row['q'][6]]);p=m.fk(q);height=float(np.mean(-p['wheel_B'][:,2])+.06369999796152115)
        nominal.append({'delta':row['delta'],'q4':q.tolist(),'leg_length2_m':np.linalg.norm(p['wheel_B'][:,[0,2]],axis=1).tolist(),'drop2_m':(-p['wheel_B'][:,2]).tolist(),'root_level_height_m':height,'rigid_box_upright_min_z':{box['name']:height+float(box['local_center'][2]-box['half_size'][2]) for box in rigid},'minimum_upright_rigid_box_clearance_above6cm_m':min(height+float(b['local_center'][2]-b['half_size'][2])-.06 for b in rigid)})
    report=[];sources=[]
    for case in CASES:
        base=TASK/'results'/case;cfg=json.loads((base/'config.json').read_text(encoding='utf-8'));result=json.loads((base/'result.json').read_text(encoding='utf-8'));gain=json.loads((TASK/cfg['gain_file']).read_text(encoding='utf-8'))['gain'];nom=next(x for x in nominal if abs(x['delta']-gain['q'][4])<1e-9);target=np.array(nom['q4']);rows=[]
        with (base/'trace.jsonl').open('r',encoding='utf-8') as f:
            for line in f:rows.append(json.loads(line))
        assert len(rows)==result['controls'] and result['physics_callbacks']==20*len(rows)
        for p in (base/'config.json',base/'result.json',base/'SOURCE_MANIFEST.json',TASK/cfg['gain_file']):sources.append({'path':str(p),'bytes':p.stat().st_size,'SHA':sha(p)})
        first=next((i for i,x in enumerate(rows) if x['physics_nonwheel_contact_ticks']>0),None);rail=next((i for i,x in enumerate(rows) if max(abs(np.array(x['actual_tau'])[[2,5]]))>=5.775909774436091-1e-6),None)
        events={'boot':0,'pre_command':min(len(rows)-1,99),'first_wheel_endstep_peak_limit':rail,'quarter_second_before_first_nonwheel':None if first is None else max(0,first-25),'pre_first_nonwheel':None if first is None else max(0,first-1),'first_nonwheel_bin':first,'terminal':len(rows)-1}
        snapshots={};boxes=result['scene']['boxes']
        for label,i in events.items():
            if i is None:continue
            x=rows[i];gt=x['ground_truth'];gb=x['ground_truth_before'];RR=rotation(gt);XYZ=np.array(gt['xyz']);enc=np.array(x['encoder4']);pose=m.fk(enc,check_limits=False);wp=pose['wheel_B'];body_drop=float(np.mean(-wp[:,2]));world_drop=float(np.mean(-(wp@RR.T)[:,2]));qmean=np.array([(enc[0]+enc[2])*.5,(enc[1]+enc[3])*.5]);bodyboxes=[]
            for box in rigid:
                center=XYZ+RR@box['local_center'];verts=(corners*box['half_size'])@RR.T+center;hits=[];xy=[]
                for j,b in enumerate(boxes):
                    bc=np.array(b['position_m']);bh=np.array(b['size_m'])/2;name='ground' if j==0 else f'rm_bar_{j:03d}';gap=sat_box(center,RR,box['half_size'],bc,bh)
                    if gap<=0:hits.append({'terrain_box':name,'geometric_max_separation_m':gap})
                    if np.all(verts[:,:2].max(0)>=bc[:2]-bh[:2]) and np.all(verts[:,:2].min(0)<=bc[:2]+bh[:2]):xy.append({'terrain_box':name,'terrain_top_z_m':float(bc[2]+bh[2]),'min_corner_z_minus_top_m':float(verts[:,2].min()-bc[2]-bh[2])})
                bodyboxes.append({'name':box['name'],'min_world_z_m':float(verts[:,2].min()),'SAT_overlap_candidates_NOT_observed_contact':hits,'horizontal_projection_candidates':xy})
            wt=np.array(x['wheel_rate2']);tau=np.array(x['actual_tau'])[[2,5]];req=np.array(x['raw_requested_tau'])[[2,5]];signed_hi=np.minimum(5.775909774436091,28.18532894736838*(1-wt/55.3557));signed_lo=np.maximum(-5.775909774436091,28.18532894736838*(-1-wt/55.3557))
            snapshots[label]={'row':i,'bin_s':[x['estimate_time'],x['time']],'sensor_time_s':x['sensor_timestamp_s'],'root_xyz_post_m':gt['xyz'],'pitch_roll_post_deg':[math.degrees(gt['pitch_true']),math.degrees(gt['roll_true'])],'estimated_pitch_deg':math.degrees(x['estimated14'][2]),'pitch_est_error_vs_pretruth_deg':math.degrees(x['estimated14'][2]-gb['pitch_true']),'truth_pre_symmetric_hip_delta_rad':gb['state'][2:4],'truth_post_symmetric_hip_delta_rad':gt['state'][2:4],'encoder_mean_hip_delta_rad':[float(qmean[0]),float(qmean[1]-qmean[0])],'max_abs_encoder_target_error_rad':float(max(abs(enc-target))),'encoder_leg_length2_m':np.linalg.norm(wp[:,[0,2]],axis=1).tolist(),'encoder_body_drop_m':body_drop,'nominal_target_body_drop_m':float(np.mean(nom['drop2_m'])),'shape_vertical_drop_loss_m':float(np.mean(nom['drop2_m']))-body_drop,'posture_projection_vertical_loss_m':body_drop-world_drop,'world_projected_leg_drop_m':world_drop,'wheel_hub_cache_z2_m':[v[2] for v in gt['wheel_xyz']],'wheel_hub_cache_time_s':gt['collision_site_cache_time_s'],'root_pose_time_s':gt['root_pose_velocity_time_s'],'nonwheel_pair_point_ticks_in_bin':x['physics_nonwheel_contact_ticks'],'wheel_mean_force_N2':x['physics_wheel_mean_force_N2'],'wheel_mean_rate2_rad_s':wt.tolist(),'wheel_requested_tau2_Nm':req.tolist(),'wheel_endstep_tau2_Nm':tau.tolist(),'signed_DC_interval_at_MEAN_speed_diagnostic_only_Nm':np.stack([signed_lo,signed_hi],axis=1).tolist(),'not_exact_endstep_DC_limit_because_mean_speed_and_endpoint_torque_differ_in_time':True,'body_box_geometry':bodyboxes,'geometric_reconstruction_not_actual_force_or_contact_identity':True}
        pre=rows[:first] if first is not None else rows;preerr=np.array([max(abs(np.array(x['encoder4'])-target)) for x in pre]);wheelrates=np.array([x['wheel_rate2'] for x in rows]);alltau=np.array([x['actual_tau'] for x in rows]);end=rows[-1]['ground_truth']
        report.append({'case':case,'nominal_target':nom,'bar_height_m':result['scene']['actual_bar_height_m'],'producer_trace':result['trace_artifact'],'trace_SHA_not_recomputed':True,'completed':result['complete'],'stop':result['stop_reason'],'progress_m':result['rough_progress_m'],'rough_pass':result['rough_case_pass'],'duration_actual_s':result['duration_actual_s'],'original_health_stop_flags':{'finite_false':not end['finite'],'closure_gt0p01':end['closure']>.01,'mimic_gt0p01':end['mimic']>.01,'upright_lt0p45':end['upright_cos']<.45,'final_upright_cos':end['upright_cos'],'final_closure_m':end['closure'],'final_mimic_rad':end['mimic']},'sparse_snapshots':snapshots,'pre_nonwheel_tracking_max_abs_error_rad':float(preerr.max()),'pre_nonwheel_tracking_abs_error_p95_rad':float(np.percentile(preerr,95)),'max_recorded_wheel_mean_rate_abs_rad_s':float(abs(wheelrates).max()),'max_recorded_leg_encoder_mean_speed_abs_rad_s':float(np.max(abs(np.array([x['encoder_rate4'] for x in rows])))),'max_endstep_leg_tau_abs_Nm':float(abs(alltau[:,[0,1,3,4]]).max()),'max_endstep_wheel_tau_abs_Nm':float(abs(alltau[:,[2,5]]).max()),'physical2k_velocity_torque_peaks':'not_saved_unknown_no_reconstruction','same_height_change_also_resynthesized_gain':'not_a_pure_geometry_only_controlled_intervention'})
    r30p=TASK/'batches/r30_rm_blocker4/BATCH_RESULT.json';r30=json.loads(r30p.read_text(encoding='utf-8'));sources += [{'path':str(r30p),'SHA':sha(r30p),'bytes':r30p.stat().st_size}]
    obj={'status':'OFFLINE_TRAIN_ROUGH_POSTURE_CAUSAL_DIAGNOSIS_NO_NEW_PHYSICS','nominal_geometry':nominal,'cases':report,'R30_independent_existing_small_contact_summary':r30,'sources':sources,'public_XML_SHA':sha(xml),'new_physics_steps':0,'SDK_or_mesh_reconstruction_calls':0,'Git_GPU_newagents_realIO':False,'heldout_H1_H2_H4_read':False,'GT_used_only_offline':True,'time_limits':'sensor and pre-grade t vs post-grade t+.01; collision/sitecache post-.0005; nonwheel onset only20step bin; stored symmetrictruth angles not per-leg truth','geometry_limits':'rigid chassis4box analytic SAT at sparse captured poses only. Not dynamic force,not2kidentity,not all279mesh proof'}
    (out/'RESULT.json').write_text(json.dumps(cv(obj),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    compact=[]
    for c in report:
        f=c['sparse_snapshots'].get('first_nonwheel_bin',{});compact.append({'case':c['case'],'height':c['nominal_target']['root_level_height_m'],'progress':c['progress_m'],'first_contact_rootZ_pitch':None if not f else [f['root_xyz_post_m'][2],f['pitch_roll_post_deg'][0]],'body_drop':f.get('encoder_body_drop_m'),'shape_loss':f.get('shape_vertical_drop_loss_m'),'posture_loss':f.get('posture_projection_vertical_loss_m'),'SAT_at_first':{} if not f else {b['name']:[h['terrain_box'] for h in b['SAT_overlap_candidates_NOT_observed_contact']] for b in f['body_box_geometry']},'health':c['original_health_stop_flags']})
    print(json.dumps(cv({'nominal_geometry':nominal,'case_compact':compact}),ensure_ascii=False,indent=2))
if __name__=='__main__':main(R/'analysis')
