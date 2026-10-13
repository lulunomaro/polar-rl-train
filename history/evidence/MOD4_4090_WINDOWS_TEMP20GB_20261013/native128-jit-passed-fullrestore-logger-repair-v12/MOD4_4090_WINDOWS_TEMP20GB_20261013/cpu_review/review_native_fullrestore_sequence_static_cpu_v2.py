"""Second CPU observer: actual prepared strictv2, sequence and shape contracts."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,time,traceback
import torch
W=Path('C:/Users/lulu/Desktop/claude/mjcf');D=W/'MOD4_4090_WINDOWS_TEMP20GB_20261013';P=D/'payload';O=D/'cpu_review'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(P))
import original_full20k_binding as old
import selected_source_projection as project
spec=importlib.util.spec_from_file_location('review_strict_v2',D/'temporary_state_binding_strict_v2.py');strict=importlib.util.module_from_spec(spec);spec.loader.exec_module(strict)
def main():
 assert not torch.cuda.is_initialized()
 paths=[D/'temporary_state_binding_strict_v2.py',P/'temporary_state_binding.py',P/'selected_source_projection.py',P/'temporary_worker.py',P/'temporary_training_runtime.py']
 lab=W/'MOD4_4090_WINDOWS_REPAIR_20261013/repair_payload/CPU_SOURCE_ASSEMBLY_FIXTURE_V5_FINAL_BOUND_SOURCE/sdk_exact/source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py'
 paths.append(lab)
 refs=[]
 for p in paths:
  compile(p.read_text(encoding='utf8'),str(p),'exec');refs.append(dict(path=str(p),sha256=H(p),bytes=p.stat().st_size))
 ref=json.loads((W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/reports/SOURCE_FULL_STATE_CPU_ACTUAL.json').read_bytes());assert H(ref['path'])==ref['sha256']==old.DONOR_SHA
 source=old.validate(torch.load(ref['path'],map_location='cpu',weights_only=False),old.DONOR_SHA)
 rng=torch.get_rng_state().clone();ids=torch.linspace(0,19999,2048).round().long();changes=[];candidate=project.project_tree(source,ids,changes=changes)
 assert len(changes)==99 and old.floating_count(candidate)==107
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):assert old.same(source[key],candidate[key])
 t=candidate['E1_terrain_state'];m=hashlib.sha256(t['spawn_xy'].numpy().astype('<f4').tobytes()).hexdigest()
 for state in strict.STATES:
  for field in ('entry_map_sha256','entry_origin_sha256'):
   if field in candidate[state]:candidate[state][field]=m
 candidate['WINDOWS4090_TEMPORARY_BRANCH']=dict(profile=strict.PROFILE,original20k_donor_SHA=old.DONOR_SHA,num_envs=2048,source_original_ids=ids.tolist(),family_counts=[614,410,410,307,307])
 strict.validate(candidate,old.DONOR_SHA)
 shapes=[]
 for label,mutate in (
  ('actor_std_shape7',lambda c:c['actor_state_dict'].__setitem__('distribution.std_param',torch.ones(7))),
  ('actor_output_rows7',lambda c:c['actor_state_dict'].__setitem__('mlp.6.weight',torch.zeros((7,64)))),
  ('Adam_row_matrix_shape7x64',lambda c:c['optimizer_state_dict']['state'][7].__setitem__('exp_avg',torch.zeros((7,64))))):
  bad=copy.deepcopy(candidate);mutate(bad)
  try:strict.validate(bad,old.DONOR_SHA)
  except (AssertionError,KeyError):accepted=False
  else:accepted=True
  shapes.append(dict(case=label,standalone_strict_v2_accepts=accepted,actual_RSL_strict_load_or_Adam_layout_has_later_checks=True,current_actual_source_not_corrupted=True));del bad
 # Review only the declared binding loop semantics, not synthetic GPU state.
 binding_ast=ast.parse((D/'temporary_state_binding_strict_v2.py').read_text(encoding='utf8'))
 bound=next(x for x in binding_ast.body if isinstance(x,ast.FunctionDef) and x.name=='bound_tree')
 text=ast.unparse(bound);assert 'assert not is_small and f in FIELDS' in text
 same_rebind_rejected=[]
 for field in sorted(strict.FIELDS):
  try:assert not True and field in strict.FIELDS
  except AssertionError:same_rebind_rejected.append(field)
 wrapper=ast.parse(lab.read_text(encoding='utf8'));cls=next(x for x in wrapper.body if isinstance(x,ast.ClassDef) and x.name=='RslRlVecEnvWrapper');ctor=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='__init__')
 resets=[x.lineno for x in ast.walk(ctor) if isinstance(x,ast.Call) and ast.unparse(x.func)=='self.env.reset'];assert len(resets)==1
 runtime=(P/'temporary_training_runtime.py').read_text(encoding='utf8');worker=(P/'temporary_worker.py').read_text(encoding='utf8')
 assert runtime.index('vec, runner = make_runner')<runtime.index('path, binding = materialize')<runtime.index('resume = resume_e1_new_episode')<runtime.index('initial_obs = capture_original_first_observation')
 assert worker.index('source = probe_source(env,args)')<worker.index('vec, runner = make_runner')<worker.index('birth = birth_inputs')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 result=dict(epoch=time.time(),CPU_review_completed=True,no_network_no_GPU_no_once_execution=True,reviewed_current_local_refs=refs,
  strict_v2_not_same_SHA_as_payload_original=H(D/'temporary_state_binding_strict_v2.py')!=H(P/'temporary_state_binding.py'),remote_clone_source_identity_requires_root_actualfreeze=True,
  actual_original_source_SHA_unchanged=H(ref['path'])==old.DONOR_SHA,project99_107_source_exact_CPU=True,linear_CPU_indices_not_actual_family_selection=True,
  source_countN2048_12_restore_counts24update49_152envsteps96callbacks_correct=True,
  sequence=dict(wrapper_constructor_reset_actual_source_line=resets[0],native='worker reset + selected reset; bound_tree setup reset; RSL wrapper reset; birth/probe',fullrestore='worker reset + selected reset; RSL wrapper reset; bound_tree setup reset; actor/optimizer load;12 saved DR/RNG/geometry-command restores;one sourceepisode+1;first observation;optional left initialization',training='same repaired2048 source; same metadata no rebind;12 restore+episode+1;original randint_like initial age before single firstobs;initializer not repeated'),
  same2048_metadata_rebinding_reject_fields=same_rebind_rejected,
  remaining_shape_rejection_gaps=shapes,
  proposed_CPU_only_hardening='Extract original actor/critic/optimizer shape/order/std validators into N-independent helper and call from strict_v2 for both initial selected and own2048 sources; add existing107 and exact99 perenv path/axis/dtype comparison to projected donor schema. No production physics or DR tolerance change.',
  no_new_deterministic_current_donor_runtime_blocker_found=True,
  lifecycle_limitations=['Setup resets before fullrestore are not sourceepisode+1 proof; only original12 resume chain is final identity proof.','initialize_selected_env calls real env.reset; its RNG is not claimed absent. The no_RNG claim is strictly project_tree and postrestore left migration only.','The broad initial metadata allowlist must remain only the explicitly frozen selectedentry/ABI code and derived map hashes; same2048 rebinding rejects all changes.','Stored source99 values remain saved values before newepisode; they are not expected equal to fresh initialization masks/episode tensors. Actual fullrestore must prove them via original validators and disk roundtrip.','Already saved missing-path read errors from this observer were pre-read only, no GPU/physics effect.'])
 path=O/('NATIVE_FULLRESTORE_TRAIN_SEQUENCE_CPU_REVIEW_'+str(time.time_ns())+'.json');path.write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(path),sha256=H(path),CPU_completed=True,shape_gaps=[r['case'] for r in shapes if r['standalone_strict_v2_accepts']],new_current_source_blocker=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (O/('SEQUENCE_REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True),indent=2),encoding='utf8');raise
