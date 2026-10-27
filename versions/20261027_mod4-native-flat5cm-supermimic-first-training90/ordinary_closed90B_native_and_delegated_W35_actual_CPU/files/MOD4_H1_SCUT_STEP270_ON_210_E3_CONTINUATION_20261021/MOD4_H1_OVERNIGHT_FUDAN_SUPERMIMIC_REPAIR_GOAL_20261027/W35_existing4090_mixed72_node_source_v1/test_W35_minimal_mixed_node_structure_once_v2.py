"""One tiny structural fixture, no model/SDK/GPU/SSH/owner/ledger or real worker."""
from pathlib import Path
import sys,json,time,importlib.util,copy
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
import W35_mixed72_protocol_v1 as q
from W35_mixed72_bound_spec_v1 import bound_W35_spec,bound_Task
import types
sys.modules['fcntl']=types.SimpleNamespace() # IMPORT-ONLY Windows fixture; no lock function invoked or claimed.
import three_slot_common_v1 as b
v=dict(passed=True,kind=q.KIND,source_SHA=q.SOURCE,original_source_SHA=q.ORIGINAL,worker_SHA=q.WORKER,original_run_manifest_SHA=q.ORIGINAL_MANIFEST,
 actor35_critic38_original_STD_17Adam_LR=True,original20k_D1_D7_and_CUDA_rng_codec_retained=True,all_source_cpu_finite=True,W35_G3_saved_terrain_structure_valid=True,W35_retained_flat_command_structure_valid=True,
 queue20ms_fields_CPU_structurally_valid=True,actual_USD_gas400_composition_passed=True,no_GPU_scene_native_or_PPO_or_account_write=True,actual_CUDA_fullrestore_pending=True,
 actual_W35_mesh_GPU_identity_pending=True,actual_command_CUDA_rng_restore_pending=True,constructor_LR_literal_matches_original_optimizer=.00001,W35_nearest250_selected_bank=dict(selected_pose_index=34),
 queue_structure_proof=dict(original_CUDA_rng_bytes_untouched=True,CPU_rng_substitution_used=False,actual_CUDA_generator_restore_passed=False),
 versions={'torch':'2.10.0+cu128','isaaclab':'6.1.14','isaacsim':'6.0.1.0','rsl-rl-lib':'5.0.1'},WM_transition_data_collection_executed=False)
request=dict(node_root=str(Path(q.JOB).parent/'node_w35'),source_CPU_SHA=q.digest(v),CPU_waited_proof_SHA='1'*64,manifest_SHA='2'*64,run_id='SOURCE_FIXTURE_NOT_REAL_GO')
spec=bound_W35_spec(request,'not_a_real_token_'+'x'*48)
row=dict(key=q.KEY,phase='ready',manifest_SHA=spec['manifest_SHA'],original_error=False,actual_validation_fcntl_held=True,closed_source_CPU=dict(value=v,SHA=q.digest(v),actual_CPU_waited_EXIT0=True))
assert b.valid_ready(row,spec) and q.W35_valid_ready(row,spec)
neg=[]
for label,mutate in [('no_lock',lambda r:r.update(actual_validation_fcntl_held=False)),('no_wait',lambda r:r['closed_source_CPU'].update(actual_CPU_waited_EXIT0=False)),('fake_cuda_restore',lambda r:r['closed_source_CPU']['value']['queue_structure_proof'].update(actual_CUDA_generator_restore_passed=True)),('wrong_expert_bank',lambda r:r['closed_source_CPU']['value']['W35_nearest250_selected_bank'].update(selected_pose_index=74)),('wrong_LR',lambda r:r['closed_source_CPU']['value'].update(constructor_LR_literal_matches_original_optimizer=.0001))]:
 n=copy.deepcopy(row);mutate(n);assert not q.W35_valid_ready(n,spec);neg.append(label)
go=q.W35_go_fields(spec);now=time.time();go.update(source_SHA=q.SOURCE,source_CPU_SHA=spec['source_CPU_SHA'],original_owner_pid=1,learning_started_epoch=now,save_deadline=now+3600,nominal_end_epoch=now+3900,max_parent_seconds=3900,exit_headroom_seconds=300,run_id=spec['run_id'])
task=bound_Task(spec,dict(GPU_UUID=q.GPU,GPU_name='NVIDIA GeForce RTX 4090',compute_UUID_only_rows=0))
worker=P.parent/'W35_PPO50_gas400_source_preparation_20261027/W35_PPO50_gas400_finite_worker_v1.py'
sp=importlib.util.spec_from_file_location('original_W35_worker_structural_guard_only',worker);w=importlib.util.module_from_spec(sp);sp.loader.exec_module(w);w.guard_task_go(task,go)
# Inspect real dispatch argv, via fake Popen only; no process or GPU interaction.
case=P/'reports/structural_dispatch_fixture';case.mkdir()
b.J=case;seen={}
class Fake:
 pid=1
 def poll(self):return None
def fake(args,**kw):seen.update(argv=args,cwd=str(kw['cwd']),GPU=kw['env']['CUDA_VISIBLE_DEVICES']);kw['stdout'].close();return Fake()
b.subprocess.Popen=fake;b.ident=lambda pid:{'source_fixture_pid_only':pid}
b.spawn(spec,'production')
assert seen['argv']==[q.PYTHON,'-u','-B',str(case/q.WORKER_NAME),'--job-root',str(case)] and seen['GPU']==q.GPU
assert b.outdir('production')==case/'adaptation'
result=dict(passed=True,source_structure_only=True,fake_CPU_not_an_actual_CPU_receipt=True,no_real_ready_GO_process_model_GPU_SSH_or_ledger=True,negative_cases_rejected_before_any_fee=neg,worker_original_guard_accepts_exact_Task_GO_fields=True,spawn_argv_and_outdir=seen,mixed_H1_and_W35_owner_required=True)
with (P/'reports/W35_MINIMAL_STRUCTURAL_READY_GO_DISPATCH_CPU_ACTUAL_V2.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
