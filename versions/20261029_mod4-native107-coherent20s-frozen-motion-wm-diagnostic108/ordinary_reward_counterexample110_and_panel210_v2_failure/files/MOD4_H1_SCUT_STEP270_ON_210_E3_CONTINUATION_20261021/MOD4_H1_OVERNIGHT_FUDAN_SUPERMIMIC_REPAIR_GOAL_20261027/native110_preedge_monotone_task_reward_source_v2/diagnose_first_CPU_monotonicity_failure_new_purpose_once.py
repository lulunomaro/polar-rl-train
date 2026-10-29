from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;original=B/'verify_reward_counterexamples_and_domain_bounds_CPU_UNUSED_once.py'
text=original.read_text(encoding='utf8')
# Reuse only the deterministic setup and the grid-prefix for a new algebraic diagnostic.
prefix=text.split("try:\n rng=",1)[0]
grid=text.split(" # Exhaustive tensor product",1)[1].split(" assert torch.isfinite(grad)",1)[0]
ns={'__file__':str(original)};exec(compile(prefix,str(original),'exec'),ns)
exec("if True:\n"+grid,ns)
torch=ns['torch'];grad=ns['grad'];d=ns['d'];r=ns['r'];x=ns['x'];nx=ns['nx']
idx=int(grad.nan_to_num(nan=-1e9).argmin())
row=int(d.reshape(-1).argmin());state=row//(nx-1);position=row%(nx-1)
report=dict(epoch=time.time(),purpose='Diagnose failed NEW110v2 source CPU monotonicity assertion only; no model/raw/physics',gradient_finite=bool(torch.isfinite(grad).all()),
 min_gradient=float(grad.nan_to_num(nan=-1e9).min()),min_adjacent_delta=float(d.min()),min_grad_index=idx,min_grad_x=float(x[idx]),min_grad_state=ns['states'][idx//nx].tolist(),
 worst_delta=dict(state=ns['states'][state].tolist(),position_index=position,reward_left=float(r['total'].detach().reshape(-1,nx)[state,position]),reward_right=float(r['total'].detach().reshape(-1,nx)[state,position+1])),
 candidate_still_NOT_ADMITTED=True)
with (B/'reports/NEW110_V2_FIRST_MONOTONICITY_FAILURE_DIAGNOSIS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report))

