"""Build a new episode-direction scope; every predecessor file remains immutable."""
from pathlib import Path
import ast,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
P=D/'payload';C=P/'isaac/mod4';C.mkdir(parents=True,exist_ok=True)
E=W/'MOD4_E1_WAVE50_ENTRY_PREPARE_20261012/payload_initialization_reviewed'
B=W/'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011/payload/isaac/mod4'
OLD='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_SECOND_BOUNDED_20261012'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_EPISODE_DIRECTION_REVIEWED_20261012'
def put(name,s):
 p=P/name;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True)
 if p.suffix=='.py':ast.parse(s)
 p.write_text(s,encoding='utf8',newline='\n')
def main():
 assert not (R/'BUILD_STARTED.json').exists()
 (R/'BUILD_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),old_sources_not_modified=True)))
 math=(W/'MOD4_E1_WAVE50_ENTRY_SECOND_BOUNDED_20261012/direction_cpu_component/wave50_episode_direction_math.py').read_text()
 put('isaac/mod4/wave50_episode_direction_math.py',math)
 state=(B/'curb20_direction_state.py').read_text().split('\ndef bind_numpy')[0]
 state=state.replace('CURB20_actual_entry_episode_direction_v1','WAVE50_actual_legal_entry_episode_direction_v1').replace('E1_CURB_entry_direction_state','E1_WAVE50_episode_direction_state').replace('curb_mask','wave_mask')
 state=state.replace("('assignment_sha256','entry_map_sha256')","('assignment_sha256','entry_map_sha256','entry_origin_sha256')")
 put('isaac/mod4/wave50_direction_state.py',state)
 runtime=(B/'curb20_direction_runtime.py').read_text().replace('CURB','WAVE50').replace('curb_mask','wave_mask').replace('CurbEntryDirectionCommand','WaveEntryDirectionCommand').replace('curb20_direction_state','wave50_direction_state').replace('curb20_entry_v3_runtime','wave50_entry_runtime_v2').replace('_curb_entry_map_receipt','_wave50_entry_map_receipt')
 runtime=runtime.replace("assert (d[mask].abs()>.7).all()", "receipt=self._env._wave50_entry_map_receipt\n  ex=torch.tensor(receipt['collision_sample_extent_xy'],device=self.device)\n  assert (d[mask].abs()-ex[0]-receipt['ten_wave_span_m']*.5>=.4-1e-6).all()\n  assert ((xy[mask]-ex>=b[mask,0,:2]+.004-1e-6)&(xy[mask]+ex<=b[mask,1,:2]-.004+1e-6)).all()")
 runtime=runtime.replace("selected=ids[self.wave_mask[ids]&~self.is_standing_env[ids]]", "selected=ids[self.wave_mask[ids]&(self.family[ids]==4)&~self.is_standing_env[ids]]")
 runtime=runtime.replace('ids=torch.nonzero(self.wave_mask).flatten()', 'ids=torch.nonzero(self.wave_mask&(self.family==4)).flatten()')
 runtime=runtime.replace("entry_map_sha256=self._env._wave50_entry_map_receipt['map_sha256'],", "entry_map_sha256=self._env._wave50_entry_map_receipt['map_sha256'],entry_origin_sha256=self._env._wave50_entry_map_receipt['actual_origin_sha256'],")
 runtime=runtime.replace("assert s['entry_map_sha256']==self._env._wave50_entry_map_receipt['map_sha256']", "assert s['entry_map_sha256']==self._env._wave50_entry_map_receipt['map_sha256']\n  assert s['entry_origin_sha256']==self._env._wave50_entry_map_receipt['actual_origin_sha256']")
 runtime=runtime.replace('ids=self.wave_mask&~self.is_standing_env', 'ids=self.wave_mask&(self.family==4)&~self.is_standing_env')
 runtime=runtime.replace('c[self.wave_mask,1:]', 'c[self.wave_mask&(self.family==4),1:]')
 put('isaac/mod4/wave50_direction_runtime.py',runtime)
 ck=(B/'curb20_direction_full_checkpoint.py').read_text().replace('curb20_entry_full_checkpoint','wave50_entry_full_checkpoint_v2').replace('curb20_direction_state','wave50_direction_state').replace('E1_CURB_entry_direction_profile','E1_WAVE50_episode_direction_profile').replace('CURB_DIRECTION_ACTUAL','WAVE50_DIRECTION_ACTUAL').replace('E1_CURB_DIRECTION_RESUME_STARTUP_VERIFIED','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED')
 put('isaac/mod4/wave50_direction_full_checkpoint.py',ck)
 cpu=(B/'curb20_direction_fullsave_cpu.py').read_text().replace('curb20_entry_fullsave_cpu','wave50_entry_fullsave_cpu_v2').replace('curb20_direction_state','wave50_direction_state').replace('E1_CURB_entry_direction_profile','E1_WAVE50_episode_direction_profile')
 cpu=cpu.replace("info['direction_state_verified']=True", "assert ck[KEY]['entry_origin_sha256']==ck['E1_terrain_state']['entry_origin_sha256']\n info['direction_state_verified']=True")
 put('isaac/mod4/wave50_direction_fullsave_cpu.py',cpu)
 newmods=['wave50_episode_direction_math.py','wave50_direction_state.py','wave50_direction_runtime.py','wave50_direction_full_checkpoint.py','wave50_direction_fullsave_cpu.py','test_wave50_direction_target_cpu.py']
 names={}
 for old in ('train_wave50_entry_fresh_preflight_ppo_v2.py','train_wave50_entry_resume_ppo_v2.py','probe_wave50_entry_fresh_process_full_resume_v2.py'):
  new=old.replace('wave50_entry','wave50_direction').replace('_v2','');names[old]=new
  s=(E/'isaac/mod4'/old).read_text().replace('from wave50_entry_runtime_v2 import','from wave50_direction_runtime import').replace('from wave50_entry_full_checkpoint_v2 import','from wave50_direction_full_checkpoint import')
  if old.startswith('train_'):
   anchor='    manifest["src_sha256"] = snapshot';assert s.count(anchor)==1
   s=s.replace(anchor,"    env.command_manager.get_term('twist')._write_dynamic(torch.arange(env.num_envs,device=env.device))\n    manifest['actual_episode_direction']=env.command_manager.get_term('twist').audit_direction()\n    manifest['new_episode_direction_axis']=True\n    for name in "+repr(tuple(newmods))+":\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n"+anchor)
  else:
   anchor="    assert int(env._sim_step_counter)==0 and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']"
   assert anchor in s
   s=s.replace(anchor,"    direction=json.loads((log_dir/'E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json').read_text())\n    assert direction['passed'] and direction['predecessor_direction_state_restored_exact'] and not direction['explicit_new_episode_direction_scope']\n    assert direction['actual_CUDA_direction_disk_roundtrip_exact'] and direction['saved_source_episode_plus_one_verified']\n"+anchor)
   s=s.replace('proof=proof,terrain=terrain,','proof=proof,terrain=terrain,direction=direction,')
  put('isaac/mod4/'+new,s)
 s=(E/'native_e1_wave50_entry_scope_probe_v2.py').read_text().replace('from wave50_entry_runtime_v2 import','from wave50_direction_runtime import')
 anchor=" report['command_retention']=env.command_manager.get_term('twist').audit_retention()";assert anchor in s
 s=s.replace(anchor,anchor+"\n report['episode_direction']=env.command_manager.get_term('twist').audit_direction()")
 put('native_e1_wave50_direction_scope_probe.py',s)
 put('wave50_direction_source_guard.py', '''"""005 and the accepted35 initial source remain strict; complete149 pins a new direction axis."""
from wave50_entry_source_guard import verify_original_records as old
def verify_original_records(q,D):
 old(q,D)
 a=q.w.read(D/'reports/COMPLETE149_DIRECTION_AXIS_DECISION.json')
 assert a['all_four_actual_complete_errorfree_fullraw_reviewed'] and a['candidate_forward_complete']==1 and a['candidate_reverse_complete']==25
 assert a['E0_and_accepted_CURB20_WAVE35_SLOPE_frozen_gate_untrained']
''')
 ctrl=(E/'supervise_wave50_entry_scope_once_v2.py').read_text().replace('from wave50_entry_source_guard import','from wave50_direction_source_guard import').replace("OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_REVIEWED_20261012')","OLD=Path("+repr(OLD)+")")
 ctrl=ctrl.replace('len(old)==398','len(old)==412').replace('wave50_entry_fullsave_cpu_v2','wave50_direction_fullsave_cpu')
 for old,new in names.items():ctrl=ctrl.replace(old,new)
 ctrl=ctrl.replace('native_e1_wave50_entry_scope_probe_v2.py','native_e1_wave50_direction_scope_probe.py')
 start=ctrl.index('def wait_existing():');end=ctrl.index('\ndef runtime():',start)
 ctrl=ctrl[:start]+'''def wait_existing():
 st=read(OLD/'reports/E1_STATE.json');passed=read(OLD/'reports/e1_WAVE50_entry_second_bounded_observation_PASSED.json')
 assert st['phase']=='E1_WAVE50_entry_second_bounded_saved_review_ready' and st['child'] is None
 assert passed['checkpoint']['sha256']=='9bfe7655b8a641660548c2a62d2ac3151e25bdf1f0e943d529099c017a2e986e' and len(passed['unique_completed_segment'])==1
 for loc in (st['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=passed['own_PID_bound_receipt']['pid'],start_ticks=91013803)):
  actual=identity(loc['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=loc['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
''' + ctrl[end:]
 anchor="        entryproof=read(run/'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json');"
 assert anchor in ctrl
 ctrl=ctrl.replace(anchor,"        direction=read(run/'E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json');assert direction['passed'] and direction['explicit_new_episode_direction_scope'] and not direction['predecessor_direction_state_restored_exact'] and direction['actual_CUDA_direction_disk_roundtrip_exact'] and direction['saved_source_episode_plus_one_verified']\n"+anchor)
 ctrl=ctrl.replace("            audit_native_trace(outpath,v)","        audit_native_trace(outpath,v)")
 start=ctrl.index('def audit_native_trace(');end=ctrl.index('\ndef fresh_resume(',start)
 ctrl=ctrl[:start]+'''def audit_native_trace(outpath,v):
 import numpy as np
 from wave50_episode_direction_math import bind
 paths=list(outpath.parent.glob(outpath.stem+'_trace/retention_prefix_*.npz'));assert len(paths)==1
 with np.load(paths[0]) as z:rows=z['rows'].copy()
 cmd=rows[:,:,7:10];fam=rows[:,:,10];count=len(v['reset_root_before_physics']);expected=300 if count==10 else 144
 assert len(cmd)==expected and cmd.shape[1:]==(count,3) and np.isfinite(rows).all()
 receipt=v['actual_entry_map_receipt'];xy=np.array(v['reset_root_before_physics'],dtype='<f4')[:,:2]
 mask,sign=bind(xy,v['actual_generated_family_assignments'],receipt['ten_wave_span_m']*.5,receipt['collision_sample_extent_xy'])
 assert mask.sum()==count if count==10 else mask.sum()==2820
 counts=[]
 for side in (-1,1):
  selected=(sign>0) if side<0 else (sign<0);take=(fam==4)&selected[None,:];vx=cmd[:,:,0][take]
  assert len(vx)>0 and np.max(abs(cmd[:,:,1:][take]))==0 and np.max(abs(vx))<=.300001
  assert np.min(vx*(1 if side<0 else -1))>=-1e-7
  row=dict(side=side,negative=int((vx<0).sum()),positive=int((vx>0).sum()),standing=int((vx==0).sum()))
  assert row['positive' if side<0 else 'negative']>0 and row['standing']>0
  counts.append(row)
 audit=v['episode_direction'];assert audit['actual_WAVE50_environments']==int(mask.sum()) and audit['all_episode_identity_exact']
 write(outpath.stem+'_DIRECTION_FULL_TRACE_REVIEW.json',dict(passed=True,path=str(paths[0]),bytes=paths[0].stat().st_size,sha256=s.q.base.sha(paths[0]),two_entry_sides_toward_direction_and_standing=counts,no_new_RNG=True,not_fullroute_contact_or_causal_certificate=True))
''' +ctrl[end:]
 ctrl=ctrl.replace(" assert proof['actual_same_WAVE50_terrain_command_private_CPUCUDA_disk_roundtrip_exact'] and proof['saved_source_episode_plus_one_verified']", " assert proof['actual_same_WAVE50_terrain_command_private_CPUCUDA_disk_roundtrip_exact'] and proof['saved_source_episode_plus_one_verified']\n assert proof['direction']['predecessor_direction_state_restored_exact'] and not proof['direction']['explicit_new_episode_direction_scope'] and proof['direction']['actual_CUDA_direction_disk_roundtrip_exact']")
 ctrl=ctrl.replace('e1-wave50-entry-own-','e1-wave50-direction-own-').replace('e1-wave50-entry-repair','e1-wave50-direction-repair').replace('E1_WAVE50_entry_saved_review_ready','E1_WAVE50_direction_saved_review_ready').replace('e1_WAVE50_entry_observation','e1_WAVE50_direction_observation').replace('bounded_E1_WAVE50_independent_learning','bounded_E1_WAVE50_episode_direction_learning')
 ctrl=ctrl.replace('old398_retained_failed_zero_PPO_actual_exits_two_OS_locks_held_active_empty','old412_ownsave_unique_settled_actual_exits_two_OS_locks_held_active_empty')
 put('supervise_wave50_direction_once.py',ctrl)
 # A fresh CPU test executes the actual runtime class with the original parent
 # write isolated; oldsource/entry/migration validators run separately unchanged.
 put('isaac/mod4/test_wave50_direction_target_cpu.py', '''"""Authentic source+entry tests and direction runtime/storage CPU fixtures, no CUDA."""
from pathlib import Path
import ast,json,io,contextlib,types,torch,numpy as np,copy,tempfile
def verify(D,source):
 from test_wave50_entry_target_cpu_v2 import main as entry_test
 from wave50_entry_runtime_v2 import reset_entry_xy
 from wave50_direction_state import PROFILE,FIELDS,validate
 from wave50_episode_direction_math import bind,apply
 from retention_command_state import same
 capture=io.StringIO()
 with contextlib.redirect_stdout(capture):entry_test(source)
 old=json.loads(capture.getvalue());assert old['passed']
 native=json.loads(Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012/WAVE50_NATIVE20K.json').read_bytes())
 xy=torch.tensor(native['reset_root_before_physics'],dtype=torch.float32)[:,:2];rows=native['actual_generated_family_assignments']
 family=torch.full((40,40),-1,dtype=torch.long);bounds=torch.zeros((40,40,2,3));names=('plane_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','random_uniform_for_rm')
 for a in rows:family[a['row'],a['column']]=names.index(a['family']);bounds[a['row'],a['column']]=torch.tensor(a['bounds'])
 terrain=types.SimpleNamespace(retention_size=(9.,9.),retention_family=family,retention_bounds=bounds,retention_assignment=rows,retention_assignment_sha=native['command_retention']['assignment_sha256'])
 env=types.SimpleNamespace(num_envs=20000,device='cpu',_e1_episode=torch.zeros(20000,dtype=torch.long),scene=types.SimpleNamespace(terrain=terrain,env_origins=xy.clone()))
 reset_entry_xy(env,torch.arange(20000));assert torch.equal(env._wave50_entry_xy,xy)
 receipt=env._wave50_entry_map_receipt;mask,sign=bind(xy.numpy(),rows,receipt['ten_wave_span_m']*.5,receipt['collision_sample_extent_xy'])
 class Parent:
  def _write_dynamic(self,ids):pass
 node=next(x for x in ast.parse((D/'isaac/mod4/wave50_direction_runtime.py').read_text()).body if isinstance(x,ast.ClassDef))
 ns=dict(torch=torch,RetainedFlatNamedOwnedCommand=Parent,reset_entry_xy=reset_entry_xy,PROFILE=PROFILE,FIELDS=FIELDS,validate=validate)
 exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-wave-direction-class>','exec'),ns)
 term=ns['WaveEntryDirectionCommand'].__new__(ns['WaveEntryDirectionCommand']);term._env=env;term.device='cpu';term.num_envs=20000
 term.wave_mask=torch.zeros(20000,dtype=torch.bool);term.entry_sign=torch.zeros(20000);term.bound_episode=torch.full((20000,),-1,dtype=torch.long);term.reset_xy=torch.zeros((20000,2));term.direction_control_histogram=torch.zeros((2,3),dtype=torch.long)
 term._retention_resampling=False;term.manual_evaluation_mode=False;term.family=torch.where(torch.tensor(mask),4,0)
 rng=torch.Generator().manual_seed(20260928);term.is_standing_env=torch.rand(20000,generator=rng)<.2
 command=torch.zeros((20000,3));command[:,0]=torch.rand(20000,generator=rng)*.6-.3;command[term.is_standing_env]=0;term.vel_command_b=command.clone()
 before=torch.get_rng_state().clone();private=rng.get_state().clone();ids=torch.arange(20000);term._write_dynamic(ids)
 assert torch.equal(before,torch.get_rng_state()) and torch.equal(private,rng.get_state())
 assert np.array_equal(term.vel_command_b.numpy(),apply(command.numpy(),mask,sign)) and term.audit_direction()['all_episode_identity_exact']
 # The parent runtime may classify a moved body as nonWave/plane: preserve
 # its current command exactly without changing the episode binding/sign.
 take=torch.nonzero(term.wave_mask).flatten()[:9];bound=term.entry_sign.clone();term.family[take]=0;term.vel_command_b[take]=torch.tensor([1.2,0.,1.4]);unchanged=term.vel_command_b[take].clone();term._write_dynamic(ids)
 assert torch.equal(term.vel_command_b[take],unchanged) and torch.equal(term.entry_sign,bound)
 term.family[take]=4;term.vel_command_b[take]=command[take];term._write_dynamic(ids)
 env._e1_episode[[1,4,7]]+=1;term._write_dynamic(torch.tensor([1,4,7]));assert (term.bound_episode==env._e1_episode).all()
 state=term.state_dict_direction()
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'direction.pt';torch.save(state,p);term.load_state_direction(torch.load(p,map_location='cpu',weights_only=False));assert same(state,term.state_dict_direction())
 rejects=[]
 for key in ('assignment_sha256','entry_map_sha256','entry_origin_sha256'):
  bad=dict(state);bad[key]='0'*64
  try:term.load_state_direction(bad)
  except AssertionError:rejects.append(key)
  else:raise AssertionError('wrong direction identity accepted '+key)
 bad=dict(state,profile='wrong')
 try:validate(bad,20000)
 except AssertionError:rejects.append('profile')
 else:raise AssertionError('wrong direction profile accepted')
 checked=[]
 for name in ('train_wave50_direction_fresh_preflight_ppo.py','train_wave50_direction_resume_ppo.py','probe_wave50_direction_fresh_process_full_resume.py'):
  text=(D/'isaac/mod4'/name).read_text();tree=ast.parse(text);assert 'from wave50_direction_runtime import' in text and 'from wave50_direction_full_checkpoint import' in text
  for node in ast.walk(tree):
   if isinstance(node,ast.For) and isinstance(node.iter,ast.Tuple) and 'shutil.copy2(Path(__file__).parent' in ast.unparse(node):
    for item in node.iter.elts:
     if isinstance(item,ast.Constant) and isinstance(item.value,str):assert (D/'isaac/mod4'/item.value).is_file(),item.value;checked.append(item.value)
  if name.startswith('train_'):assert text.index('_write_dynamic(torch.arange(env.num_envs,device=env.device))')<text.index("manifest['actual_episode_direction']")
 assert not torch.cuda.is_initialized()
 return dict(passed=True,CPU_only=True,old_source_and_entry_unmodified_test=old,actual_20k_Wave2820_and_nonWave17180=True,original_command_abs_standing_rng_exact=True,current_nonWave_parent_command_exact=True,episode_sign_only_changes_on_selected_episode=True,direction_disk_roundtrip_exact=True,strict_rejections=rejects,source_snapshot_required_paths_checked=len(checked),no_CUDA_initialized=True,new_direction_SDK_native_PPO_fresh_formal_pending=True)
''')
 files={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in P.rglob('*') if p.is_file()}
 (R/'PAYLOAD_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),new_files=files,count=len(files),prepared_only_not_targetCPU_or_GPU=True),indent=2))
 print(json.dumps(dict(prepared_files=len(files),root=ROOT,no_targetCPU_or_GPU_yet=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('BUILD_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),original_prepared_sources_retained=True)));raise
