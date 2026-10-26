"""New source/first-proof review and tiny replay interface checks only.

Contains no candidate sampler implementation or model/physics forward. Does not
rerun the old first-Pi/starvation/qualification fixtures.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,sys,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;T=D.parent.parent
N=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 import torch
 torch.set_num_threads(1)
 torch.load=lambda *a,**k:(_ for _ in ()).throw(AssertionError('No PT load permitted'))
 prepared=json.loads((N/'reports/THREE_GPU86B_SOURCE_ADMITTED_PREPARED_ACTUAL.json').read_bytes())
 B=Path(prepared['payloads']['e2'])
 paths=dict(replay=B/'source/supermimic_vendor_v2/replay.py',learner=B/'source/supermimic_vendor_v2/learner.py',
  bridge=B/'source/h1_supermimic_bridge_v1.py',phase=B/'h1_step270_sdk_runtime_candidate.py',
  ordering=B/'job0/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py',
  continuation=B/'source/native_continuation_v1.py',diagnostic=B/'source/native_policy_phase_coverage_v1.py')
 manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());rows={r['relative']:r for r in manifest['files']}
 for path in paths.values():
  rel=path.relative_to(B).as_posix();assert path.stat().st_size==rows[rel]['bytes'] and H(path)==rows[rel]['SHA']
 proof_path=N/'reports/THREE_GPU86B_FIRST_GO_PPO_NATIVE_POLICY_PHASE_ACTUAL.json'
 work_path=N/'reports/CURRENT_ACTUAL86B_NATIVE85_RESUMED_PHASE72_THREE_GO_WORK_ORDER.json'
 proof=json.loads(proof_path.read_bytes());work=json.loads(work_path.read_bytes())
 assert proof['passed'] and proof['actual_finite_returned'] and proof['native_restored_and_new_policy_updates_verified']
 assert work['first_new_native']['before_control']==72
 observed=work['cached_phase_snapshot'];assert observed['sampled_starts']==1536 and observed['bands']['100to135']==80 and observed['bands']['136to179']==0
 spec=importlib.util.spec_from_file_location('retention_review_exact_current_replay',paths['replay'])
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 tree=ast.parse(paths['bridge'].read_text('utf8'));run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
 cfg=next(n.value for n in run.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cfg' for t in n.targets))
 values={k.arg:ast.literal_eval(k.value) for k in cfg.keywords if k.arg in ('buffer_steps','hist','wm_window','pi_batch','horizon','warmup_steps')}
 assert values==dict(buffer_steps=64,hist=10,horizon=16,wm_window=8,pi_batch=512,warmup_steps=48)
 fields=mod._make_fields(30,49,6);field_rows=[]
 for key,(shape,dtype) in fields.items():
  count=shape if isinstance(shape,int) else 1
  element=torch.empty((),dtype=dtype).element_size()
  field_rows.append(dict(key=key,shape=shape if isinstance(shape,int) else [],dtype=str(dtype),elements=count,element_bytes=element,bytes=count*element))
 per_transition=sum(r['bytes'] for r in field_rows)
 start_bytes=sum(r['bytes'] for r in field_rows if r['key'] in ('s','a_prev','xi','f'))
 ring_bytes=64*20000*per_transition
 K=8192;provenance=4*8;record_bytes=(1+10)*start_bytes+provenance
 archive_bytes=K*record_bytes;scratch_bytes=2*512*record_bytes;logical_extra=archive_bytes+scratch_bytes
 cases=[]
 def case(name,fn):
  try:fn();cases.append(dict(name=name,passed=True))
  except Exception as error:cases.append(dict(name=name,passed=False,error=str(error),traceback=traceback.format_exc()))
 def memory_formula():
  assert per_transition==845 and start_bytes==520 and ring_bytes==1081600000
  assert record_bytes==5752 and archive_bytes==47120384 and logical_extra<64*1024**2
 case('actual_make_fields_memory_formula_and_candidate_logical64MiB_limit',memory_formula)
 def tiny_alloc():
  buf=mod.ReplayBuffer(6,2,'cpu',num_joints=30,context_dim=49,action_dim=6)
  assert sum(v.numel()*v.element_size() for v in buf.data.values())==6*2*per_transition
 case('tiny_actual_ReplayBuffer_allocations_match_formula',tiny_alloc)
 def reset_padded_history():
  buf=mod.ReplayBuffer(6,2,'cpu',num_joints=30,context_dim=49,action_dim=6)
  for i in range(6):
   transition={key:torch.zeros_like(value[0]) for key,value in buf.data.items()}
   ep=i if i<3 else i-3
   transition['s'][:,0]=torch.tensor([(0 if i<3 else 100)+ep,200+i],dtype=torch.float32)
   transition['f']=torch.tensor([ep,i],dtype=torch.long)
   transition['ep_step']=torch.tensor([ep,i],dtype=torch.int32)
   transition['done']=torch.tensor([i==2,False])
   buf.add(transition)
  rng=torch.random.get_rng_state().clone()
  with torch.random.fork_rng(devices=[]):
   torch.manual_seed(261026)
   start,history=buf.sample_starts(32,10)
  assert torch.equal(rng,torch.random.get_rng_state())
  assert set(start)==set(history)=={'s','a_prev','xi','f'}
  for key in start:assert torch.equal(start[key],history[key][:,-1]),key
  generation=(start['s'][:,0]//100).long();history_generation=(history['s'][:,:,0]//100).long()
  assert torch.equal(history_generation,generation[:,None].expand_as(history_generation))
 case('new_tiny_raw_history_padding_interface_and_last_equals_start',reset_padded_history)
 def source_order():
  replay=paths['replay'].read_text('utf8');bridge=paths['bridge'].read_text('utf8');ordering=paths['ordering'].read_text('utf8')
  assert 'back = torch.minimum(back.unsqueeze(0), ep_step.unsqueeze(-1))' in replay
  assert 'back = torch.minimum(back, age.unsqueeze(-1))' in replay
  assert "f=info['f'], ep_step=info['ep_step'], done=done.bool()" in bridge
  assert "self.ep_step = torch.where(done.bool(), 0, self.ep_step + 1)" in bridge
  assert "self.h1_phase.finish_control_before_selected_reset()" in ordering and 'self.h1_phase.reset(env_ids)' in ordering
 case('current_source_reset_and_transition_ordering_checked_without_environment_execution',source_order)
 assert not torch.cuda.is_initialized()
 result=dict(schema='mod4.native.phase_retention.next_candidate.source_CPU.v1',epoch=time.time(),passed=all(c['passed'] for c in cases),
  cases=cases,count=len(cases),passed_count=sum(c['passed'] for c in cases),source_scope='current86B installed-source copies; no runtime mutation',
  source_files=[dict(role=k,path=str(v),bytes=v.stat().st_size,SHA=H(v)) for k,v in paths.items()],
  first_actual_proof=dict(path=str(proof_path),bytes=proof_path.stat().st_size,SHA=H(proof_path),run_id=proof['run_id']),
  work_order=dict(path=str(work_path),bytes=work_path.stat().st_size,SHA=H(work_path)),
  actual_evidence_scope='first positive snapshot only; not completed86B exposure or skill',
  first_new_control=72,first_phase_snapshot=observed,configuration=values,replay_fields=field_rows,
  replay_logical_bytes=ring_bytes,replay_logical_GiB=ring_bytes/1024**3,
  existing_obs_hist_logical_bytes=20000*10*128*4,
  candidate=dict(status='DESIGN_REVIEW_ONLY_NOT_IMPLEMENTED_OR_AUTHORIZED',pool_records=K,
   start_plus_history_raw_bytes=record_bytes-provenance,provenance_bytes=provenance,
   record_logical_bytes=record_bytes,pool_logical_bytes=archive_bytes,
   two_max512_record_scratch_logical_bytes=scratch_bytes,logical_extra_bytes=logical_extra,
   logical_extra_MiB=logical_extra/1024**2,declared_extra_tensor_ceiling_bytes=64*1024**2,
   allocator_workspace_runtime_peak_not_measured=True,
   fill='only already-valid original fresh-ring sampled starts with100<=f<180; deterministic bounded FIFO',
   semantics='future explicit25percent archive mixture; not unchanged original uniform recent distribution',
   archive_is_ephemeral_fresh_each_new_window=True,source_weights_and_three_optimizers_retained=True,
   no_current_runtime_sampling_code_written=True),
  alternatives=dict(T128_logical_bytes=128*20000*per_transition,T256_logical_bytes=256*20000*per_transition,
   larger_ring_is_finite_retention_not_permanent_coverage=True,current_restore_config_exactly_rejects_buffer_steps_change=True),
  no_real_PT_raw_NPZ_read_hash_copy=True,no_SSH_GPU_actor_physics_rollout_Git_ledger=True,
  no_old_consumed_fixture_rerun=True,actual_runtime_candidate_verified=False,archive_status='pending root ordinary supplement')
 output=D/'reports'/('NATIVE_PHASE_RETENTION_SOURCE_METADATA_CPU_'+str(time.time_ns())+'.json')
 with output.open('x',encoding='utf8') as stream:json.dump(result,stream,indent=2,allow_nan=False)
 print(json.dumps(dict(passed=result['passed'],count=result['count'],passed_count=result['passed_count'],report=str(output),logical_extra_MiB=result['candidate']['logical_extra_MiB'])))
 if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
