"""Read-only real donor / existing128 selection fixture and source blockers."""
from pathlib import Path
import ast,copy,hashlib,json,sys,time,traceback
import torch
from reduced_projection_reference_cpu import project_complete_original,W,V
from windows20k_fullstate_binding import same,floating_count,perenv_inventory,DONOR_SHA

D=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):p=Path(p);return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
def main():
 source_ref=json.loads((W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/reports/SOURCE_FULL_STATE_CPU_ACTUAL.json').read_bytes());path=Path(source_ref['path']);assert H(path)==source_ref['sha256']==DONOR_SHA
 original=torch.load(path,map_location='cpu',weights_only=False);assert not torch.cuda.is_initialized()
 actual_report=W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/attempts/temporary_train128_v8/output/LOCAL_PROJECTED_STATE_CPU_ADMISSION.json'
 prior=json.loads(actual_report.read_bytes());ids=torch.tensor(prior['projection']['ids'],dtype=torch.long);assert len(ids)==128 and prior['projection']['family_counts']==[38,26,26,19,19]
 rng=torch.get_rng_state().clone();projected,proof=project_complete_original(original,DONOR_SHA,ids);assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 # Independently compare every saved-source environment tensor to index_select;
 # no shape/dtype coercion is accepted by the old module's looser same().
 def get(tree,path):
  for k in path.split('/')[1:]:tree=tree[int(k)] if isinstance(tree,(list,tuple)) else tree[k]
  return tree
 for row in proof['exact99_selected_paths']:
  a=get(original,row['path']);b=get(projected,row['path']);assert b.dtype==a.dtype and same(b,a.index_select(row['axis'],ids)) and b.data_ptr()!=a.data_ptr()
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):
  assert same(original[key],projected[key])
 negatives=[]
 for label,sha,x in [('wrong_source','0'*64,ids),('duplicate_id',DONOR_SHA,torch.cat((ids[:127],ids[:1]))),('out_of_range',DONOR_SHA,torch.tensor([20000])),('wrong_id_dtype',DONOR_SHA,ids.to(torch.float32))]:
  try:project_complete_original(original,sha,x)
  except AssertionError:negatives.append(label)
  else:raise AssertionError('Negative accepted '+label)
 source_files=[V/n for n in ('windows20k_fullstate_binding.py','windows4090_repair_worker.py','windows4090_training_runtime.py','windows4090_substep_readback_v6.py','left_head_offset_aware_migration_v3.py')]
 local=W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/local_state_projection.py';compile(local.read_text(),str(local),'exec')
 capacity_path=W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/attempts/temporary_train128_v10_sameidentity_saved_source/output/LOCAL_SMALL_BATCH_CAPACITY_ADMISSION.json';capacity=json.loads(capacity_path.read_bytes())
 # Exact source blockers, with honest limits. No replacement payload is deployed.
 blockers=[
 {'file':'windows20k_fullstate_binding.py','function':'validate/materialize/perenv_inventory','finding':'N20000 hard assertion and LOCAL_TEMPORARY_BRANCH rejection; new reduced validator required after original donor validation'},
 {'file':'windows4090_repair_worker.py','function':'manifest assertions/cfg.scene.num_envs','finding':'SDK10 else20000 and all11 default capacity equality; not usable by only editing CLI N'},
 {'file':'windows4090_training_runtime.py','function':'make_runner/restore_and_run/actual offset checks/ownsave','finding':'N in10,20000; offsets20kx4; environmentsteps hardcoded20000; new reduced branch must bind actualN everywhere'},
 {'file':'windows4090_substep_readback_v6.py','function':'BoundedSubstepReadback.__init__','finding':'N in10,20000; bounded arrays math reusable, source profile and actualN admission need new module'},
 {'file':'left_head_offset_aware_migration_v3.py','function':'migrate_tree','finding':'expected_num_envs==20000 and full20k validate; do not repair donor before exact projected GPU fullrestore; use new reviewed N-aware initializer after12 own restore markers'},
 {'file':str(local),'function':'global SOURCE/materialize same_local','finding':'Hard binds lulu D/source report and retained v8 proof; cannot use onWin10 remote temporarybranch'},
 {'file':str(local),'function':'materialize metadata loop','finding':'Broad update of all nonTensor direction/route/lifetime fields and only terrain+lifetime same-local equality; must use explicit metadata allowlist and same-reduced command/entry/direction/route/lifetime exact'},
 {'file':str(local),'function':'same','finding':'Torch.equal alone does not prove dtype/schema identity; retain stricter dtype+shape+container/schema checks'},
 ]
 report=dict(epoch=time.time(),passed_CPU_projection_fixture=True,actual_source=ref(path),actual_existing128_selection_receipt=ref(actual_report),CPU_reference_module=ref(D/'reduced_projection_reference_cpu.py'),proof=proof,source107_and99_exact=True,no_model_written_or_source_modified=True,negative_rejections=negatives,source_v6a_files=[ref(p) for p in source_files],local_projection_source=ref(local),existing128_capacity_receipt=ref(capacity_path),existing128_smallbatch_capacity_values=capacity['local'],capacity_scope_only_old5070Ti128_Windows51_not_new4090_admission=True,blockers=blockers,recommendation={'first_temp_N':128,'reason':'Existing exact selected-source entry and complete128 API/DR/PPO evidence provides the narrowest reusable branch; real4090 admission still required','N512_or2048_not_resource_passed':True,'native_original_smallbatch_capacity_not_scaled_from20k':True,'fixed1600cell_10306304triangle_geometry_and_Sim_baseline_memory_not_linear_in_N':True,'retention_trace_max256_updates_bytes_atN128':256*24*128*16*4,'retention_trace_max256_updates_bytes_atN512':256*24*512*16*4,'initial_checkpoint_source_d05c_not_91d_actor_DR_splice':True,'same_reduced_resume_must_not_reproject_or_reinitialize_left_head':True,'original_DR_clock_reward_LR_geometry_commands_otherexperts_not_changed':True},actual4090_reduced_SDK_native_CPUCUDA_restore_PPO_not_run=True,no_SSH_SCP_GPU_agents_canonicalwrite_or_oldsource_change=True,all_new_reports_Git_ordinary_supplement_pending_root=True)
 out=D/'REDUCED20GB_PROJECTION_AND_V6A_CPU_ACTUAL_REVIEW.json';assert not out.exists();out.write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(out),CPU_passed=True,fields=len(proof['exact99_selected_paths']),negative_rejections=negatives,first_temp_N=128,newGPU_admission=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/('REDUCED_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_source_change=True),indent=2));raise
