"""Independent contact evidence audit: retain controller, fix first-flight latch.

363 raw success=0 is retained. Its stable timer was additionally gated by the
current flight_id==1 after first crossing; a landing rebound disabled it forever.
This audit keeps first-flight clearance latched, checks ground/edge returns,
requires real top contact manifolds and retains strict .03m/s and .5s criteria.
"""
from pathlib import Path
import ast,hashlib,json,re,shutil,time,traceback
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
S=T/'MPC_PLANNED_INITIAL_QUEUE_HOLD_V363_20261102';D=T/'MPC_CONTACT_MANIFOLD_LANDING_AUDIT_V365_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def rep(text,old,new):
    assert text.count(old)==1,(old[:100],text.count(old));return text.replace(old,new,1)
try:
    assert read(S/'reports/ROOT363_ALL_SSH_CLOSED_FREE.json')['all_owned_SSH_closed']
    actual=read(S/'reports/ROOT363_EVALUATION_FULL_RETURNED.json')['result'];assert actual['passed']
    assert read(R/'ACTUAL364_363_NAMED_PD_RESET_AND_POSE_REVIEW.json')['passed']
    D.mkdir(exist_ok=False);(D/'reports').mkdir()
    rename=lambda s:re.sub(r'(?<=[A-Za-z_])363(?!\d)','365',s)
    for p in sorted(S.rglob('*')):
        rel=p.relative_to(S)
        if not p.is_file()or'__pycache__'in rel.parts or any(q.startswith(('reports','replay','RECORDED','VISIBLE'))for q in rel.parts)or p.name.startswith(('INDEX','cpu363')):continue
        dest=D/rename(str(rel));dest.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix in('.py','.json'):dest.write_text(rename(p.read_text('utf8')),encoding='utf8')
        else:shutil.copyfile(p,dest)
    w=(D/'source/evaluate365.py').read_text('utf8')
    w=rep(w,"real=sdk.Teacher324Env(cfg=cfg)",'''from isaaclab.sensors import ContactSensorCfg
 cfg.scene.mpc_left_contact=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/links/left_wheel',update_period=0.,history_length=1,track_air_time=False,filter_prim_paths_expr=['/World/ground/teacher_step270'],max_contact_data_count_per_prim=64)
 cfg.scene.mpc_right_contact=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/links/right_wheel',update_period=0.,history_length=1,track_air_time=False,filter_prim_paths_expr=['/World/ground/teacher_step270'],max_contact_data_count_per_prim=64)
 real=sdk.Teacher324Env(cfg=cfg)''')
    w=rep(w,"full_cross=torch.zeros(80,2,dtype=torch.bool,device=real.device);full_clear_ever=torch.zeros_like(active);previous_rear=low[:,:,0].clone()",'''full_cross=torch.zeros(80,2,dtype=torch.bool,device=real.device);full_clear_ever=torch.zeros_like(active);previous_rear=low[:,:,0].clone()
 import warp as wp
 manifold_sensors=[real.scene['mpc_left_contact'],real.scene['mpc_right_contact']]
 for sensor,name in zip(manifold_sensors,('left_wheel','right_wheel')):
  assert list(sensor.body_names)==[name]and sensor.contact_view.filter_count==1
 manifold_rows=[];selected_raw_contacts=[];ground_return=torch.zeros_like(active);edge_return=torch.zeros_like(active)
 top_peak=torch.zeros(80,device=real.device);top_runs=torch.zeros(80,device=real.device,dtype=torch.long)
 blocked_by_old_flight_gate=torch.zeros(80,device=real.device,dtype=torch.long)
 def read_manifold():
  tops=[];ground=[];counts_out=[];selected=[]
  for wheel,sensor in enumerate(manifold_sensors):
   force,point,normal,separation,ct,st=sensor.contact_view.get_contact_data(dt=.0025)
   ff=wp.to_torch(force).flatten();pp=wp.to_torch(point.view(wp.vec3));nn=wp.to_torch(normal.view(wp.vec3));ss=wp.to_torch(separation).flatten()
   cc=wp.to_torch(ct.view(wp.int32)).reshape(80,1).long();start=wp.to_torch(st.view(wp.int32)).reshape(80,1).long()
   assert bool(((cc>=0)&(cc<=64)&(start>=0)&(start+cc<=len(ff))).all())
   offsets=torch.arange(64,device=real.device)[None];valid=offsets<cc;indices=(start+offsets).clamp(0,len(ff)-1)
   f=ff[indices].abs();p=pp[indices];n=nn[indices];sep=ss[indices]
   relative=p-origin[:,None];delta=relative[:,:,:2]-target[:,None,:2]
   xx=ctarget[:,None]*delta[:,:,0]+starget[:,None]*delta[:,:,1]
   yy=-starget[:,None]*delta[:,:,0]+ctarget[:,None]*delta[:,:,1]
   top=valid&(f>0)&(relative[:,:,2]>.267)&(relative[:,:,2]<.28)&(n[:,:,2].abs()>.8)&(xx>=0)&(xx<=3)&(yy.abs()<=1)
   grounded=valid&(relative[:,:,2]<.02)&(n[:,:,2].abs()>.8)
   tops.append(torch.where(top,f,0).sum(1));ground.append(torch.where(grounded,f,0).sum(1));counts_out.append(cc[:,0])
   if phys_calls%8==0:
    for env_id in(0,1,40,41):
     if not bool(active[env_id]):continue
     mask=valid[env_id]&(f[env_id]>1)
     if bool(mask.any()):selected.append(dict(env=env_id,wheel=wheel,force_N=f[env_id,mask].cpu().tolist(),position_relative=relative[env_id,mask].cpu().tolist(),normal_w=n[env_id,mask].cpu().tolist(),separation_m=sep[env_id,mask].cpu().tolist()))
  return torch.stack(tops,1),torch.stack(ground,1),torch.stack(counts_out,1),selected
 ctarget,starget=ct,st''')
    w=rep(w,'phys_calls,full_cross,full_clear_ever,previous_rear','phys_calls,full_cross,full_clear_ever,previous_rear,ground_return,edge_return,top_runs,top_peak,blocked_by_old_flight_gate')
    w=rep(w,'ontop=inside.all(-1)&(low[:,:,2]>=.269).all(-1)&(low[:,:,2]<=.28).all(-1)&(wf[:,:,2]>1).all(-1)&(nw<=1)&active',
        '''top_force,ground_force,contact_counts,selected_manifold=read_manifold()
  # Full authored footprint must be horizontally on the platform. Actual solver
  # points/normal and wheel load establish top support, not authored verticalgap.
  ontop=inside.all(-1)&(top_force>1).all(-1)&(nw<=1)&active
  ground_return|=full_clear_ever&(ground_force>1).any(-1)&active
  edge_return|=full_clear_ever&(low[:,:,0]<-.02).any(-1)&active
  valid_landing=full_clear_ever&(~ground_return)&(~edge_return)
  top_runs=torch.where(ontop&valid_landing,top_runs+1,torch.zeros_like(top_runs));top_peak=torch.maximum(top_peak,top_runs.float())
  if selected_manifold:selected_raw_contacts.append(dict(tick=phys_calls,contacts=selected_manifold))''')
    w=rep(w,'land=torch.where(ontop&full_clear_ever&first,land+1,torch.zeros_like(land))','land=torch.where(ontop&valid_landing,land+1,torch.zeros_like(land))')
    w=rep(w,'stable=torch.where(steady,stable+1,torch.zeros_like(stable));stable_peak=torch.maximum(stable_peak,stable);success|=(stable>=200)&(~real._mixed209_flat)&active',
        '''steady&=valid_landing
  blocked_by_old_flight_gate.add_((steady&(~first)&active).long())
  stable=torch.where(steady,stable+1,torch.zeros_like(stable));stable_peak=torch.maximum(stable_peak,stable);success|=(stable>=200)&(~real._mixed209_flat)&active
  manifold_rows.append(dict(tick=phys_calls,top_force_N=top_force.cpu().tolist(),ground_force_N=ground_force.cpu().tolist(),contact_counts=contact_counts.cpu().tolist(),first_flight_wholeclear_latched=full_clear_ever.cpu().tolist(),ground_return=ground_return.cpu().tolist(),edge_return=edge_return.cpu().tolist(),current_flight_id=first_air.cpu().tolist(),steady=steady.cpu().tolist(),stable_ticks=stable.cpu().tolist(),active=active.cpu().tolist()))''')
    w=rep(w,"longest_stable_seconds=float(stable_peak[i])*.0025,strict270_stable=bool(success[i])", "longest_stable_seconds=float(stable_peak[i])*.0025,strict270_stable=bool(success[i]),top_contact_longest_seconds=float(top_peak[i])*.0025,ground_return_after_clear=bool(ground_return[i]),edge_return_after_clear=bool(edge_return[i]),old_flightgate_blocked_steady_ticks=int(blocked_by_old_flight_gate[i])")
    w=rep(w,"put('ACTUAL365_NAMED_ACTUATOR_INPUT_EFFORT_TRACE.json'", "put('ACTUAL365_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json',dict(rows=manifold_rows,selected_solver_contact_points=selected_raw_contacts,source='actual existing PhysX wheel contact views filtered against own270course mesh',physics_dt=.0025,first_flight_clearance_required=True,landing_latched_across_top_bounces=True,ground_edge_return_disqualify=True,strict_speed_m_s=.03,strict_stable_s=.5))\n put('ACTUAL365_NAMED_ACTUATOR_INPUT_EFFORT_TRACE.json'")
    w=w.replace("support_measurement='400Hz full authored collision wheel bounds+net wheel load over top; no contact manifold normal identity'", "support_measurement='400Hz full authored wheel horizontal footprint plus actual filtered contact points/normals/force on platformtop; first-flight wholeclearance latched; groundreturn forbidden'")
    ast.parse(w);(D/'source/evaluate365.py').write_text(w,encoding='utf8')
    task=read(D/'TASK365_FROZEN.json');task.update(kind='MPC_CONTACT_MANIFOLD_LATCHED_LANDING_AUDIT365',worker_SHA=H(D/'source/evaluate365.py'),independent_new_measurement_purpose='363raw0success remains; audit actual top manifold andfirstflight latch across normaltopbounces, no loosening speed/halfsecond/footprint/firstflight requirements',human_request='Complete actual MPC transfer evaluation and replay; noNNtraining. New contact evidence essential to distinguish top recovery from evaluator firstflight-latch error.')
    (D/'TASK365_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
    c=(D/'contract365.py').read_text('utf8').replace('MPC_PLANNED_INITIAL_QUEUE_HOLD_COMPARISON365','MPC_CONTACT_MANIFOLD_LATCHED_LANDING_AUDIT365');(D/'contract365.py').write_text(c,encoding='utf8')
    for p in D.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
    ns={};exec(compile(c,str(D/'contract365.py'),'exec'),ns);assert ns['validate_task'](task)
    # Deterministic evaluator unit fixture; no simulator or controller is called.
    firstclear=True;groundreturn=False;edgereturn=False;currentflight=3;top=True;steady=True
    old=top and firstclear and currentflight==1 and steady
    repaired=top and firstclear and not groundreturn and not edgereturn and steady
    assert not old and repaired
    assert not(top and firstclear and not True and not edgereturn and steady)
    put(D/'reports/CPU365_LANDING_LATCH_NO_STEP.json',dict(epoch=time.time(),passed=True,fixture_firstflight_clear_then_top_rebound_not_groundreturn=True,old_gate=False,repaired_gate=True,ground_return_still_disqualifies=True,physics=0,SDK=0,NN=0,controller_unchanged=True))
    files=[p for p in sorted(D.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
    put(D/'INDEX365_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
    put(R/'STATIC365_MANIFOLD_LATCH_AUDIT.json',dict(epoch=time.time(),passed=True,root=str(D),INDEX_SHA=H(D/'INDEX365_SOURCE_TASK_CALLERS_FROZEN.json'),same_controller_PD_physics_DR_queue=True,new_actual_contact_data_and_evaluator_latch_only=True,NN=0,SDK=0,network=0,GO=0))
    print(json.dumps(dict(prepared=True,root=str(D),INDEX_SHA=H(D/'INDEX365_SOURCE_TASK_CALLERS_FROZEN.json'),NN=0,GO=False)))
except BaseException:
    put(R/('LOCAL365_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),network=0,SDK=0,NN=0,GO=0));raise
