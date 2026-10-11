from pathlib import Path
import json,hashlib,ast,time

D=Path(__file__).resolve().parent;P=D/'payload';R=D/'reports';R.mkdir(exist_ok=True)
OLD=D.parent/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_FULLSTATE_REVIEWED_20261011'
H=lambda b:hashlib.sha256(b).hexdigest()

def put(name,text):
    p=P/name;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True)
    ast.parse(text);p.write_text(text,encoding='utf8')

def main():
    assert not (R/'COMPONENTS_PREPARED.json').exists()
    prior=json.loads((OLD/'reports/ENTRY_NATIVE_COMPLETE_FAMILY_SCHEMA_ACTUAL_REVIEW.json').read_bytes())
    assert prior['native20k_scope_passed'] and not prior['SDK10_CURB_entry_scope_admission']
    runtime=(OLD/'payload/isaac/mod4/curb20_entry_v2_runtime.py').read_text(encoding='utf8')
    runtime=runtime.replace("if not hasattr(env,'_curb_entry_xy'):","if not hasattr(env,'_curb_entry_xy') or not hasattr(env,'_curb_entry_origin_snapshot') or not torch.equal(env.scene.env_origins[:,:2],env._curb_entry_origin_snapshot):")
    runtime=runtime.replace("env._curb_entry_map_receipt=receipt","env._curb_entry_map_receipt=receipt\n  env._curb_entry_origin_snapshot=env.scene.env_origins[:,:2].clone()")
    runtime=runtime.replace('curb20_entry_v2_full_pose_reset','curb20_entry_v3_full_pose_reset')
    put('isaac/mod4/curb20_entry_v3_runtime.py',runtime)
    fullreset=(OLD/'payload/isaac/mod4/curb20_entry_v2_full_pose_reset.py').read_text(encoding='utf8').replace('curb20_entry_v2_runtime','curb20_entry_v3_runtime')
    put('isaac/mod4/curb20_entry_v3_full_pose_reset.py',fullreset)
    probe=(OLD/'payload/native_curb20_entry_v2_probe.py').read_text(encoding='utf8').replace('curb20_entry_v2_runtime','curb20_entry_v3_runtime')
    marker="report['SDK_forced_resampling_controls']=[50,150,200,250] if args.num_envs==10 else []"
    assert marker in probe
    probe=probe.replace(marker,marker+"\n if args.num_envs==10:\n  assert report['CURB_entry_map']['changed_environments']==10\n  assert hashlib.sha256(__import__('numpy').asarray(initial_root,dtype='<f4')[:,:2].tobytes()).hexdigest()==report['CURB_entry_map']['map_sha256']\n  assert all(x>=126. and x<135. for x in __import__('numpy').asarray(initial_root)[:,1])")
    put('native_curb20_entry_origin_bound_sdk_probe.py',probe)
    state='''"""Original CURB geometry plus deterministic, origin-bound entry identity."""
from pathlib import Path
import hashlib
import curb20_current_state as old
PROFILE='mod4_CURB_derived20mm_strip150_mirrored_entryreset_v2_origin_bound_v1'
def validate(state,n):
 assert state['profile']==PROFILE
 old.validate(dict(state,profile=old.PROFILE),n)
 assert state['entry_reset_profile']=='CURB20_actual_cell_entry_reset_v2'
 assert state['entry_origin_bound_cache'] and state['entry_no_new_rng']
 for k in ('entry_map_sha256','entry_assignment_sha256','entry_runtime_sha256'):assert isinstance(state[k],str) and len(state[k])==64
def current_state(env):
 from curb20_entry_v3_runtime import reset_entry_xy
 import torch
 reset_entry_xy(env,torch.arange(env.num_envs,device=env.device))
 s=old.current_state(env);r=env._curb_entry_map_receipt
 s.update(profile=PROFILE,entry_reset_profile=r['profile'],entry_origin_bound_cache=True,entry_no_new_rng=True,entry_map_sha256=r['map_sha256'],entry_assignment_sha256=env.scene.terrain.retention_assignment_sha,entry_runtime_sha256=hashlib.sha256(Path(__file__).with_name('curb20_entry_v3_runtime.py').read_bytes()).hexdigest())
 validate(s,env.num_envs);return s
def identity(state):return old.identity(state)
'''
    put('isaac/mod4/curb20_entry_current_state.py',state)
    checkpoint=(OLD/'inherited_source/isaac/mod4/curb20_full_checkpoint_environment_view.py').read_text(encoding='utf8')
    checkpoint=checkpoint.replace('from curb20_current_state import','from curb20_entry_current_state import')
    checkpoint=checkpoint.replace("ck['E1_CURB_initial_source_sha256']=SOURCE_SHA","ck['E1_CURB_initial_source_sha256']=SOURCE_SHA\n  ck['E1_CURB_entry_reset_identity']=identity(ck['E1_terrain_state'])\n  assert hashlib.sha256(ck['E1_terrain_state']['spawn_xy'].cpu().numpy().astype('<f4').tobytes()).hexdigest()==ck['E1_terrain_state']['entry_map_sha256']")
    checkpoint=checkpoint.replace("assert ck['independent_terrain_expert']=='E1_CURB' and ck['E1_CURB_initial_source_sha256']==SOURCE_SHA","assert ck['independent_terrain_expert']=='E1_CURB' and ck['E1_CURB_initial_source_sha256']==SOURCE_SHA\n  assert ck['E1_CURB_entry_reset_identity']==identity(state)")
    checkpoint=checkpoint.replace("explicit_G2_to_G3_geometry_transition=False,","explicit_G2_to_G3_geometry_transition=False,entry_reset_state_restored_exact=same_scope,explicit_new_entry_reset_scope=not same_scope,entry_origin_cache_bound_to_actual_origins=True,")
    put('isaac/mod4/curb20_entry_full_checkpoint.py',checkpoint)
    cpu=(OLD/'inherited_source/isaac/mod4/curb20_fullsave_cpu.py').read_text(encoding='utf8')
    cpu=cpu.replace('from curb20_current_state import validate as CURB_validate','from curb20_current_state import validate as CURB_validate\n        from curb20_entry_current_state import validate as ENTRY_validate,PROFILE as ENTRY_PROFILE')
    cpu=cpu.replace("validator=CURB_validate if", "validator=ENTRY_validate if ck['E1_terrain_state']['profile']==ENTRY_PROFILE else CURB_validate if")
    cpu=cpu.replace('    return info',"    if ck.get('E1_terrain_state',{}).get('profile')==ENTRY_PROFILE:\n        import hashlib\n        from curb20_entry_current_state import identity\n        st=ck['E1_terrain_state'];assert ck['E1_CURB_entry_reset_identity']==identity(st)\n        assert hashlib.sha256(st['spawn_xy'].cpu().numpy().astype('<f4').tobytes()).hexdigest()==st['entry_map_sha256']\n    return info")
    put('isaac/mod4/curb20_entry_fullsave_cpu.py',cpu)
    extras=['curb20_entry_v2_math.py','curb20_entry_v3_runtime.py','curb20_entry_v3_full_pose_reset.py','curb20_entry_current_state.py','curb20_entry_full_checkpoint.py','curb20_entry_fullsave_cpu.py']
    for oldname,newname in (('train_curb20_fresh_preflight_ppo.py','train_curb20_entry_fresh_preflight_ppo.py'),('train_curb20_environment_view_resume_ppo.py','train_curb20_entry_resume_ppo.py')):
        worker=(OLD/'inherited_source/isaac/mod4'/oldname).read_text(encoding='utf8')
        worker=worker.replace('from curb20_retention_runtime import','from curb20_entry_v3_runtime import').replace('from curb20_current_state import','from curb20_entry_current_state import').replace('from curb20_full_checkpoint_environment_view import','from curb20_entry_full_checkpoint import').replace('from curb20_full_checkpoint import','from curb20_entry_full_checkpoint import')
        if '    if os.environ.get(\'RM_CURB_PREFLIGHT_SELF_RESUME\')' in worker:
            start=worker.index("    if os.environ.get('RM_CURB_PREFLIGHT_SELF_RESUME')")
            end=worker.index('    info["log_dir"]',start)
            worker=worker[:start]+worker[end:]
        marker='    manifest["src_sha256"] = snapshot'
        addition='    for name in '+repr(tuple(extras))+':\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n    manifest["entry_reset_identity"]=identity(current_state(env))\n'
        assert worker.count(marker)==1;worker=worker.replace(marker,addition+marker)
        put('isaac/mod4/'+newname,worker)
    fresh=(OLD/'inherited_source/isaac/mod4/probe_curb20_fresh_process_full_resume.py').read_text(encoding='utf8')
    fresh=fresh.replace('from curb20_retention_runtime import','from curb20_entry_v3_runtime import').replace('from curb20_full_checkpoint_environment_view import','from curb20_entry_full_checkpoint import')
    line="    install_e1_save_contract(runner,env);saved=log_dir/'fullsave_after_fresh_resume_no_learning.pt';runner.save(str(saved))"
    assert line in fresh;fresh=fresh.replace(line,'    install_e1_save_contract(runner,env) # no optional save on an uninitialized logger')
    line="own_complete_new_episode_save=dict(path=str(saved),bytes=saved.stat().st_size,sha256=hashlib.sha256(saved.read_bytes()).hexdigest()),"
    assert line in fresh;fresh=fresh.replace(line,'own_complete_new_episode_save=None,optional_uninitialized_logger_save_not_called=True,')
    fresh=fresh.replace("    assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G3_to_CURB_geometry_transition']","    assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G3_to_CURB_geometry_transition']\n    assert terrain['entry_reset_state_restored_exact'] and not terrain['explicit_new_entry_reset_scope']")
    put('isaac/mod4/probe_curb20_entry_fresh_process_full_resume.py',fresh)
    target='''"""CPU-only source and snapshot admission; no CUDA or optimizer updates."""
from pathlib import Path
import json,torch,ast,hashlib,os
def verify(D):
 torch.set_num_threads(1)
 from curb20_entry_fullsave_cpu import fullsave
 row=json.loads((D/'reports/SOURCE_SELECTED.json').read_bytes());p=Path(row['path']);v=fullsave(p)
 assert v['finite_tensors']==102 and v['sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
 ck=torch.load(p,map_location='cpu',weights_only=False)
 assert ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1'
 for name,h in json.loads((D/'reports/SOURCE_FREEZE.json').read_bytes())['sha256'].items():
  q=D/name;assert hashlib.sha256(q.read_bytes()).hexdigest()==h
 for name in ('train_curb20_entry_fresh_preflight_ppo.py','train_curb20_entry_resume_ppo.py','probe_curb20_entry_fresh_process_full_resume.py'):
  text=(D/'isaac/mod4'/name).read_text();ast.parse(text)
  assert 'curb20_entry_v3_runtime' in text and 'curb20_entry_full_checkpoint' in text
 assert not torch.cuda.is_initialized()
 return dict(passed=True,source_checkpoint=v,CPU_only=True,old_full_D0_D7_optimizer_global_named_private_schema_retained=True,source_G3_to_new_CURB_entry_disclosed=True,SDK_new_origin_bound_pending=True,PPO_formal_pending=True)
'''
    put('isaac/mod4/curb20_entry_target_cpu.py',target)
    scope=dict(epoch=time.time(),new_root=NEW,prior_native398_root='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_REPAIR_20261011',native20k_exact_SHA_reuse_no_replay=True,SDK10_origin_cache_scope_repair_required=True,new_entry_state_profile='mod4_CURB_derived20mm_strip150_mirrored_entryreset_v2_origin_bound_v1',files={p.relative_to(P).as_posix():H(p.read_bytes()) for p in P.rglob('*') if p.is_file()},source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',no_deployment_yet=True)
    (R/'COMPONENTS_PREPARED.json').write_text(json.dumps(scope,indent=2),encoding='utf8')
    print(json.dumps(dict(prepared=True,files=len(scope['files']),SDK_only_repair=True,new_fullstate_pending=True)))

if __name__=='__main__':main()
