"""Independent full CURB raw/contact and mirrored signed route review, CPU only."""
from curb_io import *
import ast, traceback
import numpy as np
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'))
import review_actual_schema_checked as common
hashfile=lambda p:H(p.read_bytes())
recipe_manager=common.recipe_manager
node=next(n for n in ast.parse(common.oldterrain.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='terrain')
class ProtocolOnly(ast.NodeTransformer):
    def visit_Constant(self,n):
        if n.value=='approved_E1_gentle_route_behavior_v1':n.value=PROTOCOL
        return n
exec(compile(ast.fix_missing_locations(ast.Module(body=[ProtocolOnly().visit(node)],type_ignores=[])),str(common.oldterrain),'exec'))

def audit(p,folder):
    base=terrain(p,folder);s=p['route_scope']
    assert s['actual_authored_ground_query_passed'] and s['initial_two_wheels_on_requested_side']
    assert s['height_m']==.020 and s['strip_width_m']==.150 and s['required_after_support_m']==.2
    assert s['not_actual_RM002_height'] and s['not_stair_flight'] and s['vertical_riser_unsmoothed']
    centers=np.array(s['tile_centers']);starts=np.array(s['requested_starts']);orient=np.array(s['orientation'])
    assert centers.shape==starts.shape==(80,2) and sum(orient==1)==sum(orient==-1)==40
    assert len(set(zip(s['tile_rows'],s['tile_cols'])))==80
    assert np.all(np.array(s['tile_cols'])>=34) and np.all(np.array(s['tile_cols'])<=39)
    assert np.allclose(np.array(p['initial']['root'])[:,:2],starts.astype(np.float32),atol=1e-6,rtol=0)
    initial=np.array(s['initial_wheel_link_positions']);initial_u=(initial[:,:,0]-centers[:,None,0])*orient[:,None]
    group=np.arange(80)%3
    assert (initial_u[group!=1]<-.075).all() and (initial_u[group==1]>.075).all()
    x=np.array(s['actual_sampled_canonical_x_m']);h=np.array(s['actual_sampled_ground'])
    assert np.max(abs(h-np.where(x<-.075,0.,.020)[None,:]))<=1e-6
    names=p['body_names'];wheelids=[names.index(n) for n in ('left_wheel','right_wheel')]
    rows=[]
    with np.load(folder/p['full_route_raw']['name']) as a:
        assert a['COM_link_pos'].shape==(1500,80,len(names),3)
        assert np.max(abs(np.linalg.norm(a['normal'],axis=-1)-1))<=.01 and a['normal'][...,2].min()>.01
        expected=np.array([.3,-.3,0.])[group]*orient
        assert np.array_equal(a['targets_m_s'],expected.astype(np.float32))
        assert np.allclose(a['command'][:,:,0],expected[None,:]) and (a['command'][:,:,1:]==0).all()
        forces=a['physical_wheel_force_N'].reshape(1500,4,80,2,3)
        supported=(np.maximum(forces[...,2],0).sum(1)*.0025/.01)>1.
        for i in range(80):
            failure=int(np.where(a['terminated'][:,i],np.arange(1500),1500).min())
            u=(a['COM_link_pos'][:,i,wheelids,0]-centers[i,0])*orient[i]
            episodes=a['episode'][:,i];segments=[];full=[];contact=[]
            for ep in np.unique(episodes):
                ids=np.flatnonzero((episodes==ep)&(np.arange(1500)<failure))
                if not len(ids):continue
                wheel=u[ids]
                if group[i]==0:
                    before=np.flatnonzero(wheel.max(1)<-.275);after=np.flatnonzero(wheel.min(1)>.275)
                elif group[i]==1:
                    before=np.flatnonzero(wheel.min(1)>.275);after=np.flatnonzero(wheel.max(1)<-.275)
                else:before=np.array([],dtype=int);after=np.array([],dtype=int)
                complete=group[i]!=2 and len(before)>0 and len(after)>0 and before.min()<after.max()
                # Keep contact-confirmed support separate from position completion.
                bc=[k for k in before if supported[ids[k],i].all()]
                ac=[k for k in after if supported[ids[k],i].all()]
                confirmed=bool(complete and len(bc) and len(ac) and min(bc)<max(ac))
                if complete:full.append(int(ep))
                if confirmed:contact.append(int(ep))
                segments.append(dict(episode=int(ep),first_control=int(ids[0]),last_control=int(ids[-1]),
                    canonical_wheel_x_range_m=[float(wheel.min()),float(wheel.max())],
                    both_wheels_before_support_observed=bool(len(before)),both_wheels_after_support_observed=bool(len(after)),
                    full_riser_strip_and_after_support_before_ordinary_failure=bool(complete),
                    actual_before_and_after_both_wheel_mean_contact_above_original1N=confirmed))
            rows.append(dict(env=i,group=('ascending','descending','stand')[group[i]],orientation=int(orient[i]),
                signed_command_m_s=float(expected[i]),first_ordinary_failure_control=failure,complete_episodes=full,
                contact_confirmed_complete_episodes=contact,segments=segments))
        summaries={name:dict(environments=sum(x['group']==name for x in rows),complete_envs=sum(bool(x['complete_episodes']) for x in rows if x['group']==name),
            contact_confirmed_complete_envs=sum(bool(x['contact_confirmed_complete_episodes']) for x in rows if x['group']==name),
            both_wheels_control_support_fraction=float(supported[:,group==i].all(-1).mean()),
            original_and_mirrored={str(o):dict(environments=sum(x['group']==name and x['orientation']==o for x in rows),complete_envs=sum(bool(x['complete_episodes']) for x in rows if x['group']==name and x['orientation']==o)) for o in (-1,1)}) for i,name in enumerate(('ascending','descending','stand'))}
    return dict(base_review=base,actual_wheel_indices=wheelids,full_route_rows=rows,groups=summaries,
        all_saved_failed_prefixes_retained=True,reset_teleports_not_used_for_crossing=True,standing_not_required_to_cross=True)

def main():
    collection=sorted(R.glob('CURB132_COLLECTED_[0-9]*.json'))[-1]
    v=json.loads(collection.read_bytes());rows={}
    for jid,row in v['cases'].items():
        p,m,r=row['probe'],row['manifest'],row['result']
        assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files']
        assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==p['checkpoint_sha256']==SHA
        assert r['checkpoint']['finite_tensors']==102 and not r['new_learning'] and row['raw_SHA_exact']
        assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']
        g=p['geometry_recipe']['CURB_geometry_change']
        assert g['other_four_families_unchanged'] and g['proportions_unchanged'] and g['not_stair_flight']
        rows[jid]=audit(p,R/'cases'/jid)
    result=dict(epoch=time.time(),trial_id='E1-CURB20-132-FULL-ACTUAL-REVIEW-01',collection=str(collection),review=rows,
        summary={jid:dict(groups=x['groups'],ordinary=x['base_review']['ordinary'],closure_mm=x['base_review']['closure_mm']) for jid,x in rows.items()},
        pending=v['pending'],review_complete=len(rows)==1 and not v['pending'],frozen_source_not_trained_CURB_expert=True,
        SDK_native_CPUCUDA_fullsave_fullresume_PPO_admission_still_required=True,no_MoE_gate_deployment_or_real_RM002_claim=True,
        original_Wave131_false_prefix_cost_preserved=True,no_learning_or_budget_write=True,new_budget_seconds=0)
    p=save('CURB132_REVIEW_'+str(int(time.time()))+'.json',result)
    print(json.dumps(dict(report=str(p),summary=result['summary'],pending=v['pending'],review_complete=result['review_complete'])))
if __name__=='__main__':
    try:main()
    except Exception:
        save('CURB132_REVIEW_ERROR_'+str(int(time.time()))+'.json',dict(epoch=time.time(),error=traceback.format_exc(),reader_only=True,original_results_not_relabelled=True));raise
