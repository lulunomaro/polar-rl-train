from pathlib import Path
import json,time,numpy as np,torch
from frozen_actor_exact_cpu import FrozenActor
B=Path(__file__).resolve().parent
q=json.loads((B/'reports/SHARED_H1_NATIVE13_V3_FINITE_RETURNED_ACTUAL.json').read_bytes())
f=q['final']
c=np.load(B/'shared_H1_native13_V3_actual/out/CONTROL_ACTUAL.npz')
torch.set_num_threads(2)
src=B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_48_20261021/current_two50_closed_models/recovery/final_valid_update77.pt'
a=FrozenActor(src,f['source_SHA'],f['source_Adam'])
batch=np.stack([a.mean(torch.from_numpy(x.copy())).numpy() for x in c['policy']])
err=abs(batch-c['raw_action'])
i=np.unravel_index(np.argmax(err),err.shape)
v=dict(epoch=time.time(),max_abs_error=float(err.max()),max_action=float(abs(c['raw_action']).max()),index=[int(x) for x in i],CPU=float(batch[i]),GPU=float(c['raw_action'][i]),mean_error=float(err.mean()),max_relative_error=float((err/(abs(c['raw_action'])+1e-6)).max()),source_weights_literal_exact=a.exact(),original_review_error='AssertionError at review_shared_H1_native13_V3_all_rows_CPU_once.py:10 combined1e-5 mean-action guard',original_anonymous_measure_attempt_error='SyntaxError at truncated long pipeline input line4, no file/GPU/remote mutation',original_GPU_not_replayed=True,not_admitted_yet=True)
with (B/'reports/NATIVE_ACTION_ROUNDOFF_AND_ORIGINAL_CPU_REVIEW_ERRORS_ACTUAL.json').open('x',encoding='utf8') as file:
 json.dump(v,file,indent=2)
print(json.dumps(v))
