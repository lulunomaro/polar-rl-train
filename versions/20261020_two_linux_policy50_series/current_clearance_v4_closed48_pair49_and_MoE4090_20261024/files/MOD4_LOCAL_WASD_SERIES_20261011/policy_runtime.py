"""Exact deterministic saved actor on CPU. No optimizer, exploration, or export."""
from pathlib import Path
import hashlib, json
import numpy as np
import torch
from torch import nn

D = Path(__file__).resolve().parent
torch.set_num_threads(1)

class TorchPolicy:
    def __init__(self, path):
        self.path=Path(path).resolve()
        registry=json.loads((D/'DOWNLOAD_RECEIPT.json').read_text(encoding='utf8'))['models']
        item=next(m for m in registry if Path(m['local_path']).resolve()==self.path)
        self.sha256=hashlib.sha256(self.path.read_bytes()).hexdigest()
        assert self.sha256==item['sha256']
        saved=torch.load(self.path,map_location='cpu',weights_only=False)
        state=saved['actor_state_dict']
        keys=[k for k in state if k.startswith('mlp.')]
        assert keys and len(keys)==8
        self.actor=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6)).eval()
        self.actor.load_state_dict({k.removeprefix('mlp.'):state[k] for k in keys},strict=True)
        assert all(torch.isfinite(p).all() for p in self.actor.parameters())
        for p in self.actor.parameters(): p.requires_grad_(False)
        self.input_width=35; self.output_width=6; self.iteration=int(saved['iter'])
        self.item=item
        del saved

    def __call__(self, observation):
        x=np.asarray(observation,dtype=np.float32).reshape(1,35)
        if not np.isfinite(x).all(): raise FloatingPointError('nonfinite observation')
        with torch.inference_mode(): y=self.actor(torch.from_numpy(x)).numpy().reshape(6).copy()
        if not np.isfinite(y).all(): raise FloatingPointError('nonfinite action')
        return y
