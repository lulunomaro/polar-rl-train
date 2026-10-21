from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';N=B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021';sys.path.insert(0,str(N));import deploy_two50_reconciled_original_writer_once as d
s=importlib.util.spec_from_file_location('memory',B/'run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory)
READ=r'''
from pathlib import Path
import fcntl,hashlib,json,os,subprocess,time
root=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1shared_eval50_baseline32_full13_2110v6');assert json.loads((root/'PARENT_EXIT_ACTUAL.json').read_bytes())['all_own_children_waited'];lease=Path('/home/lc01/Zonglin Li/zonglin2/state/MOD4_H1_SHARED_FROZEN_EVAL_20261021.lock').open('a+b');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB);os.environ['CUDA_VISIBLE_DEVICES']='GPU-16828f91-2b45-b646-8dc0-9481138e2842';os.environ['CUDA_DEVICE_ORDER']='PCI_BUS_ID'
try:
 import numpy as np,torch
 torch.set_num_threads(1);source=root/'job0/source.pt';assert hashlib.sha256(source.read_bytes()).hexdigest()==v['source_SHA'];state=torch.load(source,map_location='cpu',weights_only=False);ns={};exec(v['original_reference'],ns);model=ns['FrozenMean35'](state['actor_state_dict']).to('cuda:0').eval();c=np.load(root/'out/CONTROL_ACTUAL.npz',allow_pickle=False);obs=torch.from_numpy(c['policy'].copy()).to('cuda:0');raw=torch.from_numpy(c['raw_action'].copy()).to('cuda:0');before={k:x.clone() for k,x in model.snapshot().items()};rng=torch.cuda.get_rng_state().clone();rows=[]
 with torch.inference_mode():
  for precision in ('highest','high','medium'):
   torch.set_float32_matmul_precision(precision);out=torch.stack([model(x.clone()) for x in obs]);diff=(out-raw).abs();clip=(out.clamp(-6,6)-raw.clamp(-6,6)).abs();rows.append(dict(precision=precision,raw_bitwise_exact=bool(torch.equal(out,raw)),clipped_bitwise_exact=bool(torch.equal(out.clamp(-6,6),raw.clamp(-6,6))),max_raw_abs=float(diff.max()),max_clipped_abs=float(clip.max()),allow_tf32=torch.backends.cuda.matmul.allow_tf32))
 assert all(torch.equal(x,before[k]) for k,x in model.snapshot().items()) and torch.equal(rng,torch.cuda.get_rng_state());gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);own=[x for x in gpu.splitlines() if x.split(',')[1].strip()==str(os.getpid())];assert own and all('GPU-16828f91-2b45-b646-8dc0-9481138e2842' in x for x in own);print(json.dumps(dict(epoch=time.time(),source_SHA=v['source_SHA'],original_reference_SHA=hashlib.sha256(v['original_reference'].encode()).hexdigest(),rows=rows,source9_STD_unchanged=True,CUDA_RNG_unchanged=True,zero_optimizer=True,no_physics_rollout_or_GPU_training_or_account_write=True,own_GPU=own,any_raw_exact=any(x['raw_bitwise_exact'] for x in rows),any_clipped_exact=any(x['clipped_bitwise_exact'] for x in rows))))
finally:fcntl.flock(lease,fcntl.LOCK_UN);lease.close()
'''
try:
 original=B.parent/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017/e3_closed85_frozen_prepared_v1/payload/hard_top1_frozen_expert_CPU_component_v1.py';reference=original.read_text('utf8');(B/'original_frozen_mean35_baseline32_reference_SOURCE_RETAINED.py').open('x',encoding='utf8').write(reference);source=json.loads((R/'SHARED_H1_BASELINE32_FULL13_V6_EXISTING_FINITE_RETURNED_ACTUAL.json').read_bytes())['parent_complete']['final']['source_SHA'];secret=memory.recover();c=d.connect72(secret);secret=None
 try:v=d.code(c,d.PY72,READ,dict(source_SHA=source,original_reference=reference),timeout=120)
 finally:c.close()
 with (R/'SHARED_H1_BASELINE32_FULL13_V6_ORIGINAL_MEAN_SAVED_INPUT_GPU_AUDIT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 print(json.dumps(v))
except BaseException:
 with (R/'SHARED_H1_BASELINE32_FULL13_V6_KERNEL_AUDIT_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_physics_replay=True),f,indent=2)
 raise
