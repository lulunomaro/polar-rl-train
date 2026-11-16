"""Capture frozen normal teacher pairs while running unchanged fixed regressions."""
from pathlib import Path
import argparse,sys,runpy,json,time
import numpy as np,torch
p=argparse.ArgumentParser();p.add_argument('--script',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True);p.add_argument('--capture',action='store_true');p.add_argument('--stairs',action='store_true');a=p.parse_args();xs=[];ys=[]
def hook(module,inputs,output):
 if a.capture and type(module).__name__=='ActorMLP'and inputs and isinstance(inputs[0],torch.Tensor)and inputs[0].shape[-1]==35 and isinstance(output,torch.Tensor)and output.shape[-1]==6:
  xs.append(inputs[0].detach().cpu().numpy().reshape(-1,35).copy());ys.append(output.detach().clamp(-6,6).cpu().numpy().reshape(-1,6).copy())
handle=torch.nn.modules.module.register_module_forward_hook(hook)
sys.argv=[a.script,'--model',a.model,'--out',a.out]+(['--highest-command-only']if a.stairs else [])
try:runpy.run_path(a.script,run_name='__main__')
finally:
 handle.remove();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 if xs:np.savez_compressed(out/'normal_teacher_pairs.npz',obs=np.concatenate(xs),actions=np.concatenate(ys))
 (out/'CAPTURE_STATUS.json').write_text(json.dumps(dict(frames=sum(len(x)for x in xs),model=a.model,script=a.script,mode='normal',teacher_assistance=False,closure_note='physics functions in these fixed evaluations use only nonfinite and>1m catastrophic checks; historical protocol text2mm guard is diagnostic only'),indent=2)+'\n')
