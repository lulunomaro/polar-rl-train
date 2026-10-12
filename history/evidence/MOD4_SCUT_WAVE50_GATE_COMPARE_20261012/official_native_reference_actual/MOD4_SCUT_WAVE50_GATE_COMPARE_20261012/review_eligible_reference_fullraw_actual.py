"""Recompute routes/contact and the actual control-time grace shadow from all saved raw."""
from scut_wave_command_io import *
import numpy as np,zipfile

def main():
    cp=max(R.glob('SCUT_REFERENCE_COLLECTED_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));c=json.loads(cp.read_bytes());eligible=c['latest_eligible_scope'];cases={}
    package=W/'MOD4_E1_WAVE35_SECOND_BOUNDED_20261011/wave50_worldmesh_scope/e1-g4-derived50mm-worldmesh-query-fullroute-frozen-v2.zip'
    with zipfile.ZipFile(package) as z:
        task=z.read('runtime/isaac/mod4/mod4_task.py');env=json.loads(z.read('runtime/isaac/mod4/env.json'))
    assert 'return bad & _past_spawn_grace(env)' in task.decode() or '_past_spawn_grace(env)' in task.decode()
    grace=int(env.get('RM_SPAWN_GRACE_STEPS','10'))*.01
    for key,case in c['completed_cases'].items():
        if not key.startswith(eligible+'/'):continue
        result=case['result'];p=case['probe'];folder=Path(case['local_folder'])
        assert result['phase']=='complete' and not result['exit_code'] and not result['error_files'] and p['actual_actor_command_obs_and_no_special_modes_verified'] and p['original_height_sensor_GPU_ABI_verified']
        assert p['actor_byteexact_unchanged'] and p['no_learning'] and p['optimizer_updates']==0 and p['actual_world_triangles_byteexact'] and p['actual_query_error_m']<=1e-6
        raw=folder/'route_raw.npz';assert H(raw.read_bytes())==p['raw']['sha256'] and raw.stat().st_size==p['raw']['bytes']
        query=folder/'query_actual.npz';assert H(query.read_bytes())==p['query']['sha256']
        data=np.load(raw,allow_pickle=False);assert all(np.isfinite(data[x]).all() for x in data.files)
        assert data['root'].shape==(750,80,13) and data['physical_wheel_force_N'].shape==(3000,80,2,3) and data['obs_policy'].shape==(750,80,35) and (data['special_mode_ids']==-1).all()
        assert np.array_equal(data['command'][:,:,0],np.tile(data['targets_m_s'],(750,1))) and np.max(abs(data['command'][:,:,1:]))==0
        assert np.all(np.sign(data['obs_policy'][:,:,0])==np.sign(data['command'][:,:,0]))
        support=(np.maximum(data['physical_wheel_force_N'].reshape(750,4,80,2,3)[...,2],0).sum(1)*.005/.02)>1.
        last_control_error=data['closure_per_physics_m'].reshape(750,4,80,6)[:,-1].max(-1)
        first_ordinary=np.where(data['terminated'],np.arange(750)[:,None],750).min(0)
        centers=np.array(p['route_scope']['centers']);half=p['route_scope']['halfspan'];wheels=p['initial']['wheel_indices'];rows=[];summary={}
        for group,label in ((0,'forward'),(1,'reverse'),(2,'stand')):
            ids=np.flatnonzero(data['group_ids']==group);counts=dict(position_and_1N_after200mm=0,position_after200mm_only=0,position_and_1N_exit_without200mm=0,control_endpoint_2mm_with_original_100ms_grace=0,ordinary_before_completed=0);forward=[];head=[]
            for i in ids:
                d=1 if group==0 else -1;local=d*(data['body_link_pos'][:,i,wheels,0]-centers[i,0]);complete=[];posonly=[];noafter=[];shadow=[];prefix=[]
                for ep in np.unique(data['episode'][:,i]):
                    ix=np.flatnonzero((data['episode'][:,i]==ep)&(np.arange(750)<first_ordinary[i]))
                    if not len(ix):continue
                    both=support[ix,i].all(-1);frontposition=(local[ix].max(1)<-half-.2);front=frontposition&both
                    def crossed(margin,contact=True,mask=None):
                        active=np.ones(len(ix),dtype=bool) if mask is None else mask;f=np.flatnonzero((front if contact else frontposition)&active);a=np.flatnonzero((local[ix].min(1)>half+margin)&(both if contact else True)&active)
                        return group!=2 and len(f)>0 and len(a)>0 and f.min()<a.max()
                    ok=crossed(.2);pos=crossed(.2,False);end=crossed(0.)
                    # The current MOD4 task reads the control endpoint and uses10*10ms grace.
                    age=(np.arange(len(ix))+1)*.02;bad=(last_control_error[ix,i]>.002)&(age>=grace-1e-9);b=np.flatnonzero(bad);mask=np.arange(len(ix))<(b[0] if len(b) else len(ix));sh=crossed(.2,True,mask)
                    if ok:complete.append(int(ep))
                    if pos:posonly.append(int(ep))
                    if end:noafter.append(int(ep))
                    if sh:shadow.append(int(ep))
                    prefix.append(dict(episode=int(ep),controls=int(len(ix)),seconds=float(len(ix)*.02),last_rear_wheel_past_wave_end_m=float(local[ix[-1]].min()-half),best_rear_wheel_past_wave_end_m=float(local[ix].min(1).max()-half),position_and_1N_complete=bool(ok),position_only_complete=bool(pos),exit_no200mm_complete=bool(end),first_control_closure2mm_after_grace=int(ix[b[0]]) if len(b) else None,control_endpoint_closure_peak_mm=float(last_control_error[ix,i].max()*1000),same_control_prereset_x_m=float((data['root'][ix,i,0]-data['before_root'][ix,i,0]).sum())))
                expected=next(x for x in p['route_rows'] if x['env']==i);assert complete==expected['complete_episodes']
                counts['position_and_1N_after200mm']+=bool(complete);counts['position_after200mm_only']+=bool(posonly);counts['position_and_1N_exit_without200mm']+=bool(noafter);counts['control_endpoint_2mm_with_original_100ms_grace']+=bool(shadow)
                rows.append(dict(env=int(i),group=label,complete_episodes=complete,position_only_complete_episodes=posonly,exit_without200mm_complete_episodes=noafter,control_endpoint_shadow_complete_episodes=shadow,valid_prefixes=prefix))
            assert counts['position_and_1N_after200mm']==p['behavior_completion'][label]['complete']
            summary[label]=dict(count=int(len(ids)),standing_no_cross_required=group==2,**counts)
        cases[p['model']]=dict(passed=True,model_SHA=p['policy_SHA'],raw_index=p['raw'],query_index=p['query'],native_callback_count=3000,seconds=15.,same_actual50mm_mesh_and_04approach_02after=True,actual_original_height_sensor_and_actor_command_ABI_passed=True,summary=summary,rows=rows,ordinary_events=int(data['terminated'].sum()),route_truncations=int(data['route_boundary'].sum()),all_physics_peak_closure_mm=p['max_closure_mm'],control_endpoint_peak_closure_mm=float(last_control_error.max()*1000),original_any_substep_zero_grace_shadow_preserved_as_diagnostic=p['shadow_MOD4_closure2mm_completion'],corrected_shadow_source=dict(package_SHA=H(package.read_bytes()),task_SHA=H(task),grace_seconds=grace,source_query='closure_broken current body pose at control endpoint, then _past_spawn_grace default10 nativeMOD4 controls(.1s)',native_SCUT_5msx4_control20ms_kept=True,no_actual_closure_reset_added=True),original_DR_and_robot_differ_from_MOD4=True,not_author_original_engine_benchmark_or_MOD4_plant_certification=True,all_valid_failed_prefixes_and_old_false_preserved=True)
    assert len(cases)==2,'Both new ABI-admitted actual models must finish; preparation is not a future pass.'
    p=save('ELIGIBLE_SCUT_REFERENCE_FULLRAW_REVIEW.json',dict(epoch=time.time(),passed=True,collection=str(cp),cases=cases,no_new_percentage_graduation_line=True,current_MOD4_physics_health_not_relaxed=True,old_first_scope_ineligible_sources_raw_scores_retained=True,no_GPU_or_budget_replay=True))
    print(json.dumps(dict(passed=True,report=str(p),models={k:dict(summary=v['summary'],closure_peak_mm=v['all_physics_peak_closure_mm']) for k,v in cases.items()})))

if __name__=='__main__':
    try:main()
    except BaseException:save('SCUT_FULLRAW_REVIEW_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_only_no_GPU_replay=True));raise
