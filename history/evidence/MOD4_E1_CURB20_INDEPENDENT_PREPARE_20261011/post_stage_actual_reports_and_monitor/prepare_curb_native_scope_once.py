"""Prepare genuinely new SDK/native contracts after actual complete132 review."""
from curb_io import *
import ast,traceback
def main():
    review=json.loads(sorted(R.glob('CURB132_REVIEW_[0-9]*.json'))[-1].read_bytes())
    assert review['review_complete'] and not review['pending']
    actual=next(iter(review['review'].values()));assert actual['base_review']['ordinary']==0 and actual['base_review']['full_raw_reviewed']
    save('CURB_NATIVE_SCOPE_PREPARE_STARTED.json',dict(epoch=time.time(),trial_id='E1-CURB20-NEW-SDK-NATIVE-CONTRACT-01',once=True,no_PPO=True))
    source=W/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010/assignment_reviewed_payload/native_e1_retention_assignment_reviewed_probe.py'
    old=source.read_text(encoding='utf8')
    new=old.replace('from retention_flat_runtime_sdk_reviewed import configure_retention as configure_intro','from curb20_retention_runtime import configure_retention as configure_intro')
    first=new.index(' if args.num_envs==10:\n')
    last=new.index(' env.reset();obs=',first)
    replacement=''' sdk_curb_placement=None
 if args.num_envs==10:
  from e1_full_pose_reset import query
  import numpy as np
  rows=env.scene.terrain.retention_assignment
  chosen=[]
  for row in range(15,25):
   choices=[x for x in rows if x['row']==row and x['family']=='random_uniform_for_rm' and not x['actual_mesh_flat']]
   assert len(choices)==6
   chosen.append(sorted(choices,key=lambda x:x['column'])[0])
  centers=np.array([[(x['bounds'][0][k]+x['bounds'][1][k])*.5 for k in (0,1)] for x in chosen])
  ray=query(env);ceiling=float(ray.geometry.vertices[:,2].max())+2.
  points=np.repeat(centers[:,None,:],2,axis=1);points[:,0,0]-=1.;points[:,1,0]+=1.
  out=ray.cast(torch.as_tensor(np.concatenate((points,np.full((10,2,1),ceiling)),axis=-1),device=env.device,dtype=torch.float32),10.)
  heights=out['height'].cpu().numpy();orientation=np.where(heights[:,1]>heights[:,0],1.,-1.)
  assert out['hit'].all() and (out['normal'][...,2]>.99).all() and set(orientation)=={-1.,1.}
  assert np.max(abs(np.ptp(heights,axis=1)-.020))<=1e-6
  xy=centers.copy();xy[:,0]+=orientation*np.where(np.arange(10)%2==0,-.475,.475)
  xy=torch.as_tensor(xy,device=env.device,dtype=torch.float32)
  env.scene.env_origins[:,:2]=xy;env.scene.terrain.env_origins[:,:2]=xy
  sdk_curb_placement=dict(chosen_actual_assignments=chosen,centers=centers.tolist(),requested_starts=xy.cpu().tolist(),orientation=orientation.tolist(),actual_sampled_ground=heights.tolist(),lower_upper_front_support_both_mirrors=True,assignment_sha256=env.scene.terrain.retention_assignment_sha)
  Path(args.output+'.assignment.json').write_text(json.dumps(dict(actual_assignments=rows,SDK_curbs=sdk_curb_placement,diagnostic_before_any_probe_control=True),indent=2))
'''
    new=new[:first]+replacement+new[last:]
    new=new.replace('from g3_terrain_checkpoint import current_state,identity','from curb20_current_state import current_state,identity')
    new=new.replace("report['SDK_plane_support_placement_only']=args.num_envs==10", "report['SDK_plane_support_placement_only']=False;report['SDK_CURB_actual_assignment_placement']=sdk_curb_placement")
    # Timed native simulation and original audits are reused byte-for-byte AST.
    a=next(x for x in ast.parse(old).body if isinstance(x,ast.FunctionDef) and x.name=='main')
    b=next(x for x in ast.parse(new).body if isinstance(x,ast.FunctionDef) and x.name=='main')
    one=lambda root:next(x for x in root.body if isinstance(x,ast.FunctionDef) and x.name=='one')
    assert ast.dump(one(a),include_attributes=False)==ast.dump(one(b),include_attributes=False)
    compile(new,'native_e1_curbscope_probe.py','exec')
    p=D/'implementation/native_e1_curbscope_probe.py';assert not p.exists();p.write_bytes(new.encode())
    save('CURB_NATIVE_SCOPE_PREPARED.json',dict(epoch=time.time(),trial_id='E1-CURB20-NEW-SDK-NATIVE-CONTRACT-01',
        complete132_physical_fullraw_review=str(sorted(R.glob('CURB132_REVIEW_[0-9]*.json'))[-1]),
        ordinary=actual['base_review']['ordinary'],closure_mm=actual['base_review']['closure_mm'],full132_groups=actual['groups'],
        original_native_source_SHA=H(source.read_bytes()),new_native_source_SHA=H(p.read_bytes()),
        unchanged_native_step_health_ground_hardware_AST=True,SDK10_real_CURB_lower_upper_both_mirrors=True,
        native20k_original_five_family_assignment=True,existing_command_plane_native_sampling_evidence_exact_reused=True,
        no_PPO_preflight_or_learning_executor_yet=True,full_CURB_CPUCUDA_restore_assignment_migration_pending=True,new_budget_seconds=0))
    print(json.dumps(dict(prepared=True,SDK10_new_Curb_geometry=True,actual132_complete=True,no_PPO=True)))
if __name__=='__main__':
    try:main()
    except Exception:
        save('CURB_NATIVE_SCOPE_PREPARE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),CPU_only=True,no_replay_once=True));raise
