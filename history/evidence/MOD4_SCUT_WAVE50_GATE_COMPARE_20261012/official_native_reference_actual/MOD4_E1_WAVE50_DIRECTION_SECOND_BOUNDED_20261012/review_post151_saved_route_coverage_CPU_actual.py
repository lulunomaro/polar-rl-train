"""Actual contact/position completion and observed displacement versus old2m route."""
from wave_direction_second_io import *
import numpy as np

def main():
    latest=lambda pattern:max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))
    cp=latest('SECOND_DIRECTION_CANDIDATE_COLLECTED_[0-9]*.json');rp=latest('SECOND_DIRECTION_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json');c,a=[json.loads(p.read_bytes()) for p in (cp,rp)];assert a['review_complete']
    jid,row=next((k,v) for k,v in c['cases'].items() if 'full_route_raw' in v['probe']);p=row['probe'];raw=R/'cases'/jid/p['full_route_raw']['name'];assert H(raw.read_bytes())==p['full_route_raw']['sha256']
    z=np.load(raw,allow_pickle=False);cent=np.asarray(p['route_scope']['tile_centers']);half=p['route_scope']['wave_x_halfspan_m'];ids=a['terrain']['actual_wheel_indices'];support=np.maximum(z['physical_wheel_force_N'].reshape(1500,4,80,2,3)[...,2],0).sum(1)*.0025/.01>1.;out=[];travel=[]
    for r in a['terrain']['full_route_rows']:
        i=r['env'];group=r['group'];sign=1 if group=='forward' else -1;expected=r['complete_episodes'];complete=[];segments=[]
        if group=='stand':continue
        local=sign*(z['COM_link_pos'][:,i][:,ids,0]-cent[i,0])
        for seg in r['segments']:
            ep=seg['episode'];ix=np.flatnonzero((z['episode'][:,i]==ep)&(np.arange(1500)<r['first_ordinary_failure_control']));both=support[ix,i].all(-1);before=np.flatnonzero((local[ix].max(1)<-half-.2)&both);after=np.flatnonzero((local[ix].min(1)>half+.2)&both);ok=len(before)>0 and len(after)>0 and before.min()<after.max()
            rec=dict(episode=int(ep),controls=int(len(ix)),two_wheel_before_and_after_position_plus1N_complete=bool(ok))
            if ok:
                complete.append(int(ep));j=int(ix[after[after>before.min()][0]]);distance=float(sign*(z['root'][j,i,0]-z['before_root'][ix[0],i,0]));travel.append(distance);rec.update(first_complete_control=j,actual_root_signed_displacement_at_completion_m=distance)
            segments.append(rec)
        assert complete==expected,('contact_position_completion_match',i)
        out.append(dict(env=i,group=group,complete_episodes=complete,segments=segments))
    assert len(travel)==35
    v=dict(epoch=time.time(),passed=True,collection=str(cp),full_actual_review=str(rp),raw_path=str(raw.resolve()),raw_SHA=H(raw.read_bytes()),all_complete_episode_position_and_actual1N_before_after_support_agree=True,rows=out,observed_completed_frozen_paths_root_signed_displacement_range_m=[min(travel),max(travel)],observed_completed_paths_exceed2m_count=sum(x>2 for x in travel),original_training_route_from_spawn_m=2.,frozen_root_approach_m=.4,training_entry_offsets_m=[.8,.85],training_entry_full10wave_rootproxy_nominal_distance_before_motion_footprint_m=[2*half+.8+.2,2*half+.85+.2],root_or_routeproxy_is_not_full_training_contact_certificate=True,not_global_unreachable_for_all_postures_or_causal_learning_proof=True,original2m_route_not_changed=True,new_route_scope_requires_independent_fullstate_and_actual_admission=True,old_direction_two_duration_blocks_closed_no_third_blind_PPO=True,no_CPU_RNG_GPU_budget_or_validator_write=True)
    save('POST151_SAVED_ROUTE_COVERAGE_CPU_ACTUAL_DIAGNOSIS.json',v)
    print(json.dumps(dict(passed=True,completed_paths=len(travel),root_displacement_range=v['observed_completed_frozen_paths_root_signed_displacement_range_m'],exceed_old2m=v['observed_completed_paths_exceed2m_count'])))

if __name__=='__main__':
    try:main()
    except BaseException:save('POST151_SAVED_ROUTE_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_replay=True));raise
