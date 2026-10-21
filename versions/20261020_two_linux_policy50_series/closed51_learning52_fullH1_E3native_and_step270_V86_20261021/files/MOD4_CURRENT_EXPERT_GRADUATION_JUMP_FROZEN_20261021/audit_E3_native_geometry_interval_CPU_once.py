from pathlib import Path
import hashlib,json,time,sys,numpy as np
from original_geometry_fp32_interval_cpu import enclose_original_support
B=Path(__file__).resolve().parent;R=B/'reports';A=B/'E3_native60_actual/out'
report=R/'E3_NATIVE60_ORIGINAL_GEOMETRY_FP32_INTERVAL_CPU_ACTUAL.json'
assert not report.exists()
geo=json.loads((A/'GEOMETRY_ACTUAL.json').read_bytes())
p=np.load(A/'PHYSICAL_CALLBACK_ACTUAL.npz',allow_pickle=False)
lo,hi=enclose_original_support(p['witness_body_pos'],p['witness_body_quat_xyzw'],geo['shapes'])
record=p['witness_clear34'].astype(np.float64)
inside=(record>=lo)&(record<=hi);assert inside.all(),np.argwhere(~inside)[:5]
sys.path.insert(0,str(B.parent/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/payload/h1'))
from h1_reference_geometry_cpu import support
ideal=support(p['witness_body_pos'],p['witness_body_quat_xyzw'],geo['shapes'])
error=abs(record-ideal);idx=tuple(int(x) for x in np.unravel_index(error.argmax(),error.shape))
# Falsification: a stale/perturbed 1 mm witness must be rejected in every row.
rejected_plus=(record+.001>hi);rejected_minus=(record-.001<lo)
assert rejected_plus.all() and rejected_minus.all()
# The original float32 implementation on CPU must also fall inside this enclosure.
import torch,importlib.util
torch.set_num_threads(2)
source=B/'E3_recovery104_native60_payload/job0/runtime/isaac/mod4/h1_authored_full_collider_plane_reference_v1.py'
spec=importlib.util.spec_from_file_location('original_geometry',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cpu=m.evaluate(torch.from_numpy(p['witness_body_pos'].reshape(-1,31,3)),torch.from_numpy(p['witness_body_quat_xyzw'].reshape(-1,31,4)),geo['shapes']).numpy().reshape(record.shape)
assert ((cpu>=lo)&(cpu<=hi)).all()
assert not torch.cuda.is_initialized()
value=dict(epoch=time.time(),passed=True,rows=int(record.size),method='Outward float64 interval enclosure of original float32 operations and dot reductions; eps32 conservative rounding, actual float32 inputs/constants; no simulation',original_source_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),auditor_SHA=hashlib.sha256((B/'original_geometry_fp32_interval_cpu.py').read_bytes()).hexdigest(),all_saved_GPU_geometry_inside_forward_roundoff_interval=True,all_original_CPU_float32_geometry_inside_interval=True,maximum_interval_width_m=float((hi-lo).max()),independent_float64_support_maxabs_difference_m=float(error.max()),worst_index=idx,worst_shape=geo['shapes'][idx[-1]],worst_actual_GPU_m=float(record[idx]),worst_independent_float64_m=float(ideal[idx]),worst_interval_m=[float(lo[idx]),float(hi[idx])],plus_and_minus_1mm_witness_perturbations_rejected_all_rows=True,original_blanket_absolute1um_auditor_failure_preserved=True,reason='Cylinder radial sqrt(norm2-axial^2) is ill conditioned near an axial orientation in float32. This resolves a cross-precision arithmetic auditor, not the physical ground-query tolerance.',physical_ground_query_1um_COM10um_closure2mm_mimic01_guards_unchanged=True,no_new_GPU_or_PPO_or_model_change=True)
report.open('x',encoding='utf8').write(json.dumps(value,indent=2));print(json.dumps({k:v for k,v in value.items() if k!='worst_shape'}))
