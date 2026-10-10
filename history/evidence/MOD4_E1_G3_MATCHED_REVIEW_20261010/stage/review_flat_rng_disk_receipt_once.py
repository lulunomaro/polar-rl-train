"""Independent disk roundtrip of the undeployed CPU sampler, no plant imports."""
from pathlib import Path
import base64,hashlib,json,sys,time
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D/'implementation'))
import torch
from retained_flat_command_math import sample_commands
g=torch.Generator(device='cpu').manual_seed(20261010);n=20000
v=torch.linspace(-3.14,3.14,n);e=torch.arange(n)<6000;s=torch.arange(n)%5==0
before=g.get_state().clone();a=sample_commands(g,e,s,v);after=g.get_state().clone()
p=R/'FLAT_CPU_NAMED_GENERATOR_DISK_STATE.json';assert not p.exists()
p.write_bytes(json.dumps(dict(before=base64.b64encode(bytes(before.tolist())).decode(),after=base64.b64encode(bytes(after.tolist())).decode(),algorithm='Torch CPU generator synthetic sampler only; not full actor/optimizer/CUDA state')).encode())
saved=json.loads(p.read_bytes());g2=torch.Generator(device='cpu');g2.set_state(torch.tensor(list(base64.b64decode(saved['before'])),dtype=torch.uint8))
b=sample_commands(g2,e,s,v);assert all(torch.equal(a[k],b[k]) for k in a)
assert torch.equal(g2.get_state(),torch.tensor(list(base64.b64decode(saved['after'])),dtype=torch.uint8))
q=R/'FLAT_CPU_NAMED_GENERATOR_DISK_VERIFIED.json';assert not q.exists()
q.write_bytes(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-FLAT-CPU-NAMED-RNG-DISK-01',file=str(p.resolve()),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),actual_CPU_disk_roundtrip_exact=True,source_runtime_full_CPU_CUDA_resume_pending=True,new_budget_seconds=0),indent=2).encode())
print(json.dumps(dict(actual_CPU_disk_roundtrip_exact=True,SDK_or_PPO_admitted=False)))
