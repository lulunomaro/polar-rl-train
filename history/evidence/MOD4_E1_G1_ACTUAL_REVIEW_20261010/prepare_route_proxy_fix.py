"""Immutable repair of the observed Warp ProxyArray dtype error, no plant changes."""
from pathlib import Path
import ast,ctypes,hashlib,json,time,zipfile
import torch,numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';A=D/'artifacts';H=lambda b:hashlib.sha256(b).hexdigest()
old=A/'e1-g1-complete-wave-route-v3-frozen.zip'
with zipfile.ZipFile(old) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
entry='runtime/isaac/mod4/frozen_history_flat.py';s=payload[entry].decode()
bad="assert torch.allclose(r.data.root_pos_w[:,:2],torch.as_tensor(starts,device=e.device,dtype=r.data.root_pos_w.dtype),atol=1e-6,rtol=0)"
fixed="root_xy=r.data.root_pos_w.torch[:,:2]\n assert isinstance(root_xy,torch.Tensor) and root_xy.dtype==torch.float32\n assert torch.allclose(root_xy,torch.as_tensor(starts,device=e.device,dtype=root_xy.dtype),atol=1e-6,rtol=0)"
assert s.count(bad)==1;s=s.replace(bad,fixed)
s=s.replace('dtype=r.data.root_pos_w.dtype','dtype=root_xy.dtype').replace('approved_E1_G1_complete_wave_route_behavior_v3','approved_E1_G1_complete_wave_route_behavior_v4')
assert 'dtype=r.data.root_pos_w.dtype' not in s
ast.parse(s);payload[entry]=s.encode();m.update(files={n:H(b) for n,b in payload.items()},protocol='approved_E1_G1_complete_wave_route_behavior_v4',retained_v3_failure='119 anchor failed: ProxyArray.dtype is Warp ctypes, not torch.dtype. Candidate119 never ran.')
p=A/'e1-g1-complete-wave-route-v4-proxy-frozen.zip';assert not p.exists()
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(m,indent=2))
(D/'frozen_fullroute_v4.py').write_text(s,encoding='utf8')
# CPU model of the installed .dtype/.torch interface, with real torch conversion.
class Proxy:
 dtype=ctypes.c_float*3
 def __init__(self,t):self.torch=t
xy=np.array([[175.5,130.5],[-175.5,139.5]],dtype=np.float64);q=Proxy(torch.tensor(xy,dtype=torch.float32))
try:torch.as_tensor(xy,dtype=q.dtype)
except TypeError:reproduced=True
else:raise AssertionError('CPU must reproduce original interface error')
root_xy=q.torch[:,:2];expected=torch.as_tensor(xy,dtype=root_xy.dtype);assert torch.equal(root_xy,expected)
xyz=torch.as_tensor(np.zeros((80,35,3)),dtype=root_xy.dtype);assert xyz.shape==(80,35,3) and xyz.dtype==torch.float32
sdk=(R/'installed_sdk/proxy_array.py').read_bytes();assert H(sdk)=='5d20232ff07cb4d333b8f3e9e68b152568b884e935a1f672bf864ce3942937df'
assert b'Warp dtype of the underlying array' in sdk and b'zero-copy' in sdk
with zipfile.ZipFile(old) as z:assert all(payload[n]==z.read(n) for n in m['files'] if n!=entry)
v=dict(epoch=time.time(),trial_id='E1-G1-ROUTE-PROXY-DTYPE-REPAIR-03',actual_cause='Installed IsaacLab3 PhysX root_pos_w is ProxyArray; direct dtype is Warp ctypes; .torch is documented zero-copy torch view. No variable-shadowing claim.',original_job119_failed_and_candidate_never_run=True,original_error_SHA='36430e1c04ec7f71ce2ac0ec66289af52076d0d5c9d93176380509a1222ce86b',installed_proxy_source_SHA=H(sdk),CPU=dict(passed=True,original_type_error_reproduced=True,explicit_torch_view_conversion_passed=True,actual_reset_assertion_tolerance_unchanged_1e6=True,ray_xyz_shape_and_dtype_passed=True,only_dispatcher_changed=True,AST_passed=True,no_CUDA_initialized=not torch.cuda.is_initialized()),package=dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=H(p.read_bytes())),protocol=m['protocol'],actual_route_result_pending=True,no_learning_or_canonical_or_production_write=True,new_budget_seconds=0)
(R/'FULL_ROUTE_PROXY_CPU_PREPARED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
