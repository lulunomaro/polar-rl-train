from pathlib import Path
import ast,hashlib,json,shutil,time,numpy as np,torch
T=Path(__file__).resolve().parent;R=T/'reports';O=T/'production_candidate_V1_UNINSTALLED';D=T/'production_candidate_V2_ARENA_EXIT_UNINSTALLED'
assert not D.exists();D.mkdir();H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p in O.iterdir():
 if p.is_file():shutil.copy2(p,D/p.name)
p=D/'h1_step270_sdk_runtime_candidate.py';old=p.read_text('utf8')
functions='''def out_of_authored_floor(env):
    # The finite global floor is part of the existing authored mesh, not a new distance limit.
    root=tensor(env.scene['robot'].data.root_pos_w)
    if not torch.isfinite(root).all():raise RuntimeError('Nonfinite root position at terrain boundary guard')
    origins=env.scene.env_origins
    lower=origins[:,:2].amin(0)-2.5;upper=origins[:,:2].amax(0)+2.5
    return ((root[:,:2]<lower)|(root[:,:2]>upper)).any(-1)

def save_bad_terrain_query(env,points,q,kind):
    from pathlib import Path
    finite=torch.isfinite(q['height'])&torch.isfinite(q['normal']).all(-1)
    valid=q['hit']&finite
    if kind=='root_ground':valid&=q['normal'][...,2]>0
    bad=torch.nonzero(~valid,as_tuple=False)
    def finite_list(value):
        def clean(x):
            if isinstance(x,list):return [clean(v) for v in x]
            return x if not isinstance(x,float) or np.isfinite(x) else None
        return clean(value.detach().cpu().tolist())
    rows=[]
    for env_id,ray_id in bad.detach().cpu().tolist():
        rows.append(dict(env=env_id,ray=ray_id,actual_start=finite_list(points[env_id,ray_id]),hit=bool(q['hit'][env_id,ray_id]),height=finite_list(q['height'][env_id,ray_id]),normal=finite_list(q['normal'][env_id,ray_id]),distance=finite_list(q['distance'][env_id,ray_id]),face_id=int(q['face_id'][env_id,ray_id])))
    bounds=[finite_list(env.scene.env_origins[:,:2].amin(0)-2.5),finite_list(env.scene.env_origins[:,:2].amax(0)+2.5)]
    out=Path(__file__).resolve().parent/'job0/production';out.mkdir(parents=True,exist_ok=True)
    import time
    path=out/('ACTUAL_BAD_TERRAIN_QUERY_'+str(time.time_ns())+'.json')
    with path.open('x',encoding='utf8') as f:json.dump(dict(kind=kind,actual_bad_rows=rows,actual_floor_xy_bounds=bounds,no_fallback_or_tolerance_change=True),f,indent=2,allow_nan=False)

'''
new=old.replace('def ground_height(env):',functions+'def ground_height(env):')
needle="    if not q['hit'].all() or not torch.isfinite(q['height']).all() or not (q['normal'][...,2]>0).all():raise RuntimeError('Step270 actual terrain query missing/invalid; no flat fallback')"
assert new.count(needle)==1
new=new.replace(needle,"    if not q['hit'].all() or not torch.isfinite(q['height']).all() or not (q['normal'][...,2]>0).all():\n        save_bad_terrain_query(env,points,q,'root_ground')\n        raise RuntimeError('Step270 actual terrain query missing/invalid; no flat fallback')")
needle="        if not q['hit'].all() or not torch.isfinite(q['height']).all():raise RuntimeError('Missing actual wheel terrain query')"
assert new.count(needle)==1
new=new.replace(needle,"        if not q['hit'].all() or not torch.isfinite(q['height']).all():\n            save_bad_terrain_query(env,starts,q,'wheel_ground')\n            raise RuntimeError('Missing actual wheel terrain query')")
needle='    cfg.sim.enable_scene_query_support=True;cfg.sim.physics.enable_scene_query_support=True'
assert new.count(needle)==1
new=new.replace(needle,needle+"\n    from isaaclab.managers import TerminationTermCfg\n    cfg.terminations.h1_step270_arena_exit=TerminationTermCfg(func=out_of_authored_floor,time_out=False)")
ast.parse(new);p.write_text(new,encoding='utf8',newline='\n')
# Execute just the pure guard function on recorded data, with no Isaac scene or policy call.
tree=ast.parse(new);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='out_of_authored_floor')
ns=dict(torch=torch,tensor=lambda x:x);exec(compile(ast.Module(body=[fn],type_ignores=[]),'recorded_boundary_guard','exec'),ns)
v=json.loads((T/'cooked_query_full20k_V9_actual/out/ACTUAL_COOKED_VS_AUTHORED_STEP270_QUERY_RESULT.json').read_bytes())
origins=torch.tensor([[r['actual_Float3_origin'][0]-.25,r['actual_Float3_origin'][1],0.] for r in v['front_rows']],dtype=torch.float32)
from types import SimpleNamespace
last=np.load(T/'relocated_forensic_originals/H1step270_pairV1_closed_control318/control_prefix_13.npz')
root=torch.from_numpy(last['root13']);done=last['done'].astype(bool);selected=[]
for i in range(len(root)):
 env=SimpleNamespace(scene={'robot':SimpleNamespace(data=SimpleNamespace(root_pos_w=root[i,:,:3]))})
 class Scene(dict):pass
 scene=Scene(env.scene);scene.env_origins=origins;env.scene=scene
 mask=ns['out_of_authored_floor'](env);independent=((root[i,:,:2].numpy()<(origins[:,:2].amin(0).numpy()-2.5))|(root[i,:,:2].numpy()>(origins[:,:2].amax(0).numpy()+2.5))).any(-1)
 assert np.array_equal(mask.numpy(),independent)
 selected.append(torch.nonzero(mask).flatten().tolist())
assert selected==[[],[],[],[],[],[19965]] and not done[-1,19965]
# The new condition does not reset healthy environments or declare skill success.
safe=origins.clone();scene['robot'].data.root_pos_w=safe;assert not ns['out_of_authored_floor'](env).any()
bad=safe.clone();bad[0,0]=float('nan');scene['robot'].data.root_pos_w=bad
try:ns['out_of_authored_floor'](env);raise AssertionError('nonfinite guard did not reject')
except RuntimeError:pass
before={x.name:ast.dump(x,include_attributes=False) for x in ast.parse(old).body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
after={x.name:ast.dump(x,include_attributes=False) for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
changed=[k for k in before if before[k]!=after[k]];assert set(changed)=={'configure_scene','ground_height','Step270Phase'}
v=dict(epoch=time.time(),candidate_not_installed=True,passed_recorded_CPU_regression=True,original_failure_preserved=True,recorded_completed_controls318=True,new_selected_termination_envs_by_last6_control=selected,finite_root_guard_retained=True,actual_authored_floor_bounds_not_new_numeric_distance=True,old_160k_query_and_native3_proofs_reused_not_rerun=True,query1um_COM10um_closure2mm_mimic01_unchanged=True,no_mesh_physics_reward_actor_STD_optimizer_source_changed=True,no_airborne_assist_or_success_credit=True,ordinary_failed_episode_selected_reset_via_existing_SDK=True,unexpected_query_misses_still_global_reject_with_saved_bad_rows=True,changed_old_functions=changed,new_functions=['out_of_authored_floor','save_bad_terrain_query'],source=dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)),remaining_required='whole production manifest/SDK termination registration and original resource admission in a NEW unused root; no new H1 GO in this report')
with (R/'H1_STEP270_RECORDED_ARENA_EXIT_AND_QUERY_DIAGNOSTIC_REPAIR_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
