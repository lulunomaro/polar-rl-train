"""Bounded mathematical CUDA replay of retained witness, no simulation or PPO."""
from pathlib import Path
import ast, hashlib, json, time, os, msvcrt, psutil
R=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013')
O=R/'COM_JIT_SAVED_WITNESS_MATH_V11'
assert not O.exists();O.mkdir()
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(O/n).write_text(json.dumps(x,indent=2),encoding='utf8')
lock=(R/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
try:
 import torch
 source=R/'sdk_exact/source/isaaclab/isaaclab/utils/math.py'
 tree=ast.parse(source.read_text(encoding='utf8'));names=('quat_mul','quat_apply','combine_frame_transforms')
 funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 assert len(funcs)==3
 code='import torch\nfrom typing import Optional, Tuple\n'+ '\n\n'.join(ast.unparse(n) for n in funcs)
 f=O/'independently_frozen_SDK_arithmetic.py';f.write_text(code,encoding='utf8')
 import importlib.util
 spec=importlib.util.spec_from_file_location('mod4_COM_repr_v11',f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 rows=[]
 for v in (9,10):
  scope='temporary_scope128_memory20GB_resident_v9_20261013' if v==9 else 'temporary_scope128_memory20GB_COM_repr_v10_20261013'
  p=R/scope/'attempts/temporary2048_native_v1/output/SUBSTEP_READBACK_V6_FAILURE_WITNESS.pt'
  witness=torch.load(p,map_location='cpu',weights_only=False)
  for phase,row in witness.items():
   l=row['link_pose_wxyz'].float().cuda();c=row['local_COM_pose_wxyz'].float().cuda()
   # All input tensors are retained independent native link/local reads. Actual COM is comparison only.
   expected,q=m.combine_frame_transforms(l[...,:3],l[...,3:7],c[...,:3],c[...,3:7])
   for _ in range(8):expected,q=m.combine_frame_transforms(l[...,:3],l[...,3:7],c[...,:3],c[...,3:7])
   error=(expected.cpu().double()-row['world_COM_pos']).abs()
   rows.append(dict(version=v,phase=phase,control=row['control'],callback=row['callback'],witness_sha256=H(p),max_error_m=float(error.max()),original_tol_m=1e-5,passed=bool(float(error.max())<1e-5)))
 proof=dict(epoch=time.time(),passed=all(x['passed'] for x in rows),rows=rows,math_source=dict(path=str(source),sha256=H(source)),frozen_arithmetic=dict(path=str(f),sha256=H(f)),expected_uses_link_local_only=True,no_original_false_relabelled=True,no_physics_steps_no_PPO=True,pid=os.getpid(),created=psutil.Process().create_time())
 save('COM_JIT_MATH_ACTUAL.json',proof);print(json.dumps(proof))
finally:
 lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
