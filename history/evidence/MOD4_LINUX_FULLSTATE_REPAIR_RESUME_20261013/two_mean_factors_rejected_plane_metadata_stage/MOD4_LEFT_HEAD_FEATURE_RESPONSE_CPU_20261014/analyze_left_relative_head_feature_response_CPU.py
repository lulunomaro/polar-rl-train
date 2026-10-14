"""Strict state/matrix diff and same-stored-vector actor mathematics, CPU only.

No saved policy_obs is declared to be the same-control actor input. It is used
only as an actual saved35-vector common to three numerical MLP evaluations.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,json,time,traceback
import torch,numpy as np
import torch.nn.functional as F
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
OUT=R/'LEFT_RELATIVE_FEATURE_COPY_MATRIX_AND_ACTUAL_VECTOR_CPU_REVIEW.json';assert not OUT.exists()
SRC=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt'
CROOT=W/'MOD4_LEFT_JOINT_CENTER_KEEPSTD_CPU_20261014'
CENTER=CROOT/'candidate_cpu_v1/own20k_left_joint_center_keep_saved_std_CPU_prepared.pt'
NEAR=CROOT/'candidate_near_lower_cpu_v1/own20k_left_joint_lower_margin005_keep_saved_std_CPU_prepared.pt'
SHAS={'parent':'2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971','center':'a88fea3ba0ca637d235b95dc1a16834eb0446e3e90c6945a868846b574bb3dba','near_lower':'6235d44aa144a73e46d8326187c7fdf1e406a2d0b00ee6d21922b18f198f3bce'}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def witness(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def digest(v):
 h=hashlib.sha256()
 def visit(x):
  h.update(type(x).__name__.encode());h.update(b'\0')
  if torch.is_tensor(x):h.update(str(x.dtype).encode());h.update(str(tuple(x.shape)).encode());h.update(x.detach().cpu().contiguous().numpy().tobytes())
  elif isinstance(x,np.ndarray):h.update(str(x.dtype).encode());h.update(str(x.shape).encode());h.update(x.tobytes())
  elif isinstance(x,dict):
   for k in sorted(x,key=str):visit(k);visit(x[k])
  elif isinstance(x,(tuple,list)):
   for y in x:visit(y)
  else:h.update(repr(x).encode())
 visit(v);return h.hexdigest()
def same(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
 if isinstance(a,np.ndarray):return isinstance(b,np.ndarray) and a.dtype==b.dtype and a.shape==b.shape and np.array_equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return type(a)is type(b) and a==b
def stats(x):
 x=np.asarray(x,dtype=np.float64)
 return dict(min=float(x.min()),mean=float(x.mean()),median=float(np.median(x)),std=float(x.std()),max=float(x.max()))
def parse(folder):
 p=W/folder/'reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json';r=json.loads(p.read_bytes());assert r['passed']
 raw=r['raw'];assert sha(raw['local_path'])==raw['sha256']
 with np.load(raw['local_path']) as z:
  d={k:z[k].copy() for k in ['policy_obs','action','processed_action','group_ids','episode','terminated','truncated']}
 assert d['policy_obs'].shape==(1500,80,35) and np.isfinite(d['policy_obs']).all()
 assert np.array_equal(d['processed_action'],np.clip(d['action'],-6,6))
 # A source-defined last_action slice; empirically test only that slice/timing.
 nonreset=~(d['terminated'][:-1]|d['truncated'][:-1])
 prior_exact=np.array_equal(d['policy_obs'][1:,:,22:28][nonreset],d['processed_action'][:-1][nonreset])
 return r,d,witness(p),dict(raw=raw,actual_saved35vector_phase='Copiedafter vec.step in recorder; fullsame-control actorinput identity is not established here.',lastaction_source_defined_columns=[22,23,24,25,26,27],saved_lastaction_nonreset_rows_exact_previous_control_processed_request=bool(prior_exact),all_rows_equal_current_control_processed_request=bool(np.array_equal(d['policy_obs'][:,:,22:28],d['processed_action'])),saved_lastaction_left_column22=stats(d['policy_obs'][:,:,22]))
try:
 rng=torch.get_rng_state().clone();nprng=digest(np.random.get_state())
 states={};index={}
 for name,p in [('parent',SRC),('center',CENTER),('near_lower',NEAR)]:
  assert sha(p)==SHAS[name];index[name]=witness(p);states[name]=torch.load(p,map_location='cpu',weights_only=False)
 fingerprints={k:digest(v) for k,v in states.items()}
 base=states['parent'];ba=base['actor_state_dict'];W0=ba['mlp.6.weight'][0].double();W1=ba['mlp.6.weight'][1].double();b0=ba['mlp.6.bias'][0].double();b1=ba['mlp.6.bias'][1].double()
 assert ba['mlp.6.weight'].shape==(6,64) and len(ba)==9 and base.get('history_architecture',{}).get('variant','A0')=='A0'
 for label in ['center','near_lower']:
  c=states[label];a=c['actor_state_dict']
  for k in base:
   if k not in ['actor_state_dict','optimizer_state_dict']:assert same(base[k],c[k]),(label,k)
  for k in ba:
   if k=='mlp.6.weight':assert torch.equal(a[k][0],ba[k][1]) and torch.equal(a[k][1:],ba[k][1:])
   elif k=='mlp.6.bias':assert torch.equal(a[k][1:],ba[k][1:])
   else:assert same(a[k],ba[k]),(label,k)
  so=base['optimizer_state_dict'];co=c['optimizer_state_dict'];assert same(so['param_groups'],co['param_groups'])
  for pid,s in so['state'].items():
   for field,v in s.items():
    u=co['state'][pid][field]
    if pid in (7,8) and field in ('exp_avg','exp_avg_sq'):assert torch.equal(u[0],torch.zeros_like(v[0])) and torch.equal(u[1:],v[1:])
    else:assert same(u,v)
 assert same(states['center']['optimizer_state_dict'],states['near_lower']['optimizer_state_dict'])
 ca=states['center']['actor_state_dict'];na=states['near_lower']['actor_state_dict']
 assert torch.equal(ca['mlp.6.weight'],na['mlp.6.weight'])
 for k in ca:
  if k=='mlp.6.bias':assert torch.equal(ca[k][1:],na[k][1:])
  else:assert torch.equal(ca[k],na[k])
 rel=W0-W1
 matrix=dict(parent_W0_L2=float(W0.norm()),parent_W1_L2=float(W1.norm()),parent_relative_hidden_response_gradient_L2=float(rel.norm()),parent_W0_W1_cosine=float(torch.dot(W0,W1)/(W0.norm()*W1.norm())),parent_relative_gradient_nonzero_dimensions=int(torch.count_nonzero(rel)),parent_relative_gradient_64_values=rel.tolist(),parent_raw_relative_bias=float(b0-b1),
  center_near_shared_final_Wrow0_Wrow1_exact=True,candidate_relative_hidden_response_gradient_zero_all64=True,
  center_relative_bias_raw=float(ca['mlp.6.bias'][0].double()-b1),near_relative_bias_raw=float(na['mlp.6.bias'][0].double()-b1),near_minus_center_bias_raw=float(na['mlp.6.bias'][0].double()-ca['mlp.6.bias'][0].double()),
  center_minus_parent_bias_raw=float(ca['mlp.6.bias'][0].double()-b0),near_minus_parent_bias_raw=float(na['mlp.6.bias'][0].double()-b0),
  shared_weight_replacement_parent_row0_to_hiprow1_L2=float((W1-W0).norm()),both_candidate_std_all6_parent_exact=ba['distribution.std_param'].tolist(),other5_heads_trunk_critic_DR_RNG_exact=True,all_Adam_step_and_std_moments_exact=True,center_near_Adam_fullstate_exact=True,shared_Adam_meanrow0_moment_clearing_only=True)
 reports={};data={};phases={}
 folders={'parent':'MOD4_3060_LEFT_REPAIR_FULL80_20261014','center':'MOD4_3060_LEFT_CENTER_KEEPSTD_FULL80_FACTOR_20261014','near_lower':'MOD4_3060_LEFT_NEAR_LOWER_FULL80_FACTOR_20261014'}
 for label,folder in folders.items():
  r,d,p,phase=parse(folder);assert r['source_SHA']==SHAS[label];reports[label]=dict(report=p,forward=r['forward_complete'],reverse=r['reverse_complete'],ordinary=r['ordinary'],raw=r['raw']);data[label]=d;phases[label]=phase
 # PureMLP mathematics on one actual saved-vector set, commoninput allthree.
 # ELU architecture taken from frozen_history_policy.py, not invented layers.
 arch=W/folders['parent']/'payload/runtime/isaac/mod4/frozen_history_policy.py'
 text=arch.read_text();assert "'actor',6,[256,128,64],'elu'" in text
 X=torch.from_numpy(data['parent']['policy_obs']).double().reshape(-1,35)
 mathematical_outputs={k:np.empty((len(X),6),dtype=np.float64) for k in states}
 feature_effect=np.empty(len(X),dtype=np.float64)
 for start in range(0,len(X),2048):
  h=X[start:start+2048]
  for level in [0,2,4]:h=F.elu(F.linear(h,ba[f'mlp.{level}.weight'].double(),ba[f'mlp.{level}.bias'].double()))
  for k,c in states.items():mathematical_outputs[k][start:start+len(h)]=F.linear(h,c['actor_state_dict']['mlp.6.weight'].double(),c['actor_state_dict']['mlp.6.bias'].double()).numpy()
  feature_effect[start:start+len(h)]=F.linear(h,rel[None],None).numpy().reshape(-1)
 P=mathematical_outputs['parent'];C=mathematical_outputs['center'];N=mathematical_outputs['near_lower']
 assert np.array_equal(P[:,1:],C[:,1:]) and np.array_equal(P[:,1:],N[:,1:])
 relative={k:v[:,0]-v[:,1] for k,v in mathematical_outputs.items()}
 biasdiff=matrix['near_minus_center_bias_raw']
 assert float(np.max(np.abs((N[:,0]-C[:,0])-biasdiff)))<1e-12
 assert float(np.max(np.abs(relative['center']-matrix['center_relative_bias_raw'])))<1e-12
 assert float(np.max(np.abs(relative['near_lower']-matrix['near_relative_bias_raw'])))<1e-12
 per=[]
 for i in range(80):
  sl=np.arange(i,len(X),80)
  per.append(dict(env=i,group=int(data['parent']['group_ids'][i]),parent_relative_raw_mean=stats(relative['parent'][sl]),parent_relative_hidden_feature_response=stats(feature_effect[sl]),center_relative_raw_mean=stats(relative['center'][sl]),near_relative_raw_mean=stats(relative['near_lower'][sl]),center_minus_parent_raw_left_mean=stats((C-P)[sl,0]),near_minus_parent_raw_left_mean=stats((N-P)[sl,0])))
 # Actual saved actions retain their own known requestphase. Bias-only legal
 # interval is a mathematical necessary/sufficient condition in observed hip
 # range (alllo>-6, allhi<6). Do not generate a bias-only candidate.
 A=data['parent']['action'].astype(np.float64);hip=np.clip(A[:,:,1],-6,6);r=A[:,:,0]-hip
 assert (hip-2.1686>-6).all() and (hip+1.7<6).all()
 moving=data['parent']['group_ids']!=2
 intersect={}
 for label,mask in [('all80',np.ones(80,dtype=bool)),('moving54',moving),('forward27',data['parent']['group_ids']==0),('reverse27',data['parent']['group_ids']==1)]:
  rr=r[:,mask];lower=float((-2.1686-rr).max());upper=float((1.7-rr).min())
  intersect[label]=dict(actual_raw_left_minus_clipped_hip_domain=stats(rr),single_bias_delta_needed_at_least_raw=lower,single_bias_delta_needed_at_most_raw=upper,full_saved_mean_legal_bias_intersection_empty=lower>upper)
 assert intersect['all80']['full_saved_mean_legal_bias_intersection_empty']
 assert all(digest(states[k])==fingerprints[k] for k in states)
 assert all(sha(index[k]['path'])==index[k]['sha256'] for k in index)
 assert torch.equal(torch.get_rng_state(),rng) and digest(np.random.get_state())==nprng and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed=True,scope='Independent matrix/state comparison and same-stored-vector CPU actor mathematics only',sources=index,source_tree_fingerprints_before_after=fingerprints,matrix_actual=matrix,
  complete_original_frozen_behaviors=reports,policy_obs_phase_actual_limits=phases,architecture_reference=witness(arch),same_vector_mathematics=dict(input_set=reports['parent']['raw'],vectors=120000,dimensions=35,CPU_float64_linear_ELU_layers=[35,256,128,64,6],other5_mean_outputs_same_input_exact=True,parent_relative_raw_mean=stats(relative['parent']),parent_relative_hidden_feature_response=stats(feature_effect),center_relative_raw_mean=stats(relative['center']),near_relative_raw_mean=stats(relative['near_lower']),center_near_difference_only_constant_left_bias_max_residual=float(np.max(np.abs((N[:,0]-C[:,0])-biasdiff))),per80=per,
    not_samecontrol_actor_input_replay=True,not_GPU_kernel_numerical_equivalence=True,not_physical_rollout_or_causal_disentanglement=True),
  bias_only_smaller_proposal=dict(no_candidate_created=True,mean_response_gradient_preserved='KeepactualW0; changeonebias scalar preserves learnedrawleft-minus-hip relative hiddengradient W0−W1, versus replacement of64weight entries plusbias.',actual_saved_request_mean_legal_constraints=intersect,no_global_bias_shift_makes_all_actual_saved_means_legal=True,physical_passability_and_skill_preservation_unverified=True),
  conclusions=dict(can_infer=['Bothmeaninitializers removed the original rawleft relativehip64Dhidden response at initialization; exactmatrixresult.', 'Twofactors sharethe sameWreplacement/std/Adamclearing. Theirdifferenttargetbias anddifferent physicalresults prove targetposture also matters, butdonotisolateWcopycausally.', 'FrozennoPPO optimizerstateclearing cannotcausefrozenphysical differences throughoptimizerupdates.', 'Other5headweightsbeingexact doesnotpreservetrajectory, because leftprocessedrequest/lastaction feedback andplantstatechange.', 'Bias-only is a smaller parameterfactor andpreservesrelativefeatures, butallobservedmeanlegalintersectionisempty.'],cannot_infer=['CopiedW1 is the solecause of factorfailure.', 'Originalrawrelativefeatures are useful at execution: parentjointguardalreadyprojects almostallleftrequests.', 'Stored35vectors are samecontrolprephysics actorinputs; alias/mutablephase remains excluded.', 'Mathematicalactoroutputs or legalmeans prove physicalq/pose orcompleteWavepassability.', 'Oneunverifiedbias-only shift should be adopted as production orusedfor blindPPO.']),
  source_read_warning_preserved='Initialbroadrg encounteredAccessDenied in unrelated rmuc2026_work/unpack_verify_4zomhj13; returnedactualnear_lowerreportpath. No mutation orfailedphysicsinference.',
  no_new_weight_or_training_source=True,no_SSH_GPU_RNGdraw_budget_Git=True,all_oldsource_raw_false_retained=True,Git_archive_pending_root_owner=True)
 OUT.write_text(json.dumps(out,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(OUT),relative_gradient_norm=matrix['parent_relative_hidden_response_gradient_L2'],candidate_relative_gradient_zero=True,constant_bias_difference=biasdiff,actual_vector_parent_rel_range=[relative['parent'].min(),relative['parent'].max()],bias_only_constraints=intersect['all80'],no_new_weight=True)))
except Exception:
 p=R/f'FEATURE_CPU_ORIGINAL_ERROR_{time.time_ns()}.json';p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source_script=witness(__file__),no_GPU=True,original_false_retained=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8');raise
