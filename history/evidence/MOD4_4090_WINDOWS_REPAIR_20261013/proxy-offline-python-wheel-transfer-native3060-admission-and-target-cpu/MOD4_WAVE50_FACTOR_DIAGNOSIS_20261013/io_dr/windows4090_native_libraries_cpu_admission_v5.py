"""Actual CPU DLL bridge admission; deliberately no Isaac/Kit or CUDA context."""
from pathlib import Path
import time,sys,json,importlib.metadata as md
R=Path(__file__).resolve().parent;out=R/'install_reports/WINDOWS4090_NATIVE_CPU_LIBRARIES_ADMITTED.json';assert not out.exists()
import numpy as np,scipy,torch,torchvision,tensordict
assert torch.__version__=='2.7.0+cu128' and torchvision.__version__=='0.22.0+cu128'
assert not torch.cuda._initialized
x=torch.arange(6,dtype=torch.float32).reshape(2,3);assert float(x.sum())==15
td=tensordict.TensorDict({'x':x},batch_size=[2]);assert torch.equal(td['x'],x)
keep=torchvision.ops.nms(torch.tensor([[0.,0.,1.,1.],[0.,0.,1.,1.]]),torch.tensor([.9,.8]),.5);assert keep.tolist()==[0]
assert np.isfinite(np.fft.fft(np.arange(8))).all()
assert not torch.cuda._initialized
report=dict(epoch=time.time(),python=sys.executable,python_version=sys.version,CPU_native_tensor_TensorDict_NMS_numpy_passed=True,torch_CUDA_initialized=False,Isaac_Kit_GPU_PPO_not_initialized=True,versions={n:md.version(n) for n in ('torch','torchvision','tensordict','numpy','scipy','warp-lang','isaacsim','rsl-rl-lib')})
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
