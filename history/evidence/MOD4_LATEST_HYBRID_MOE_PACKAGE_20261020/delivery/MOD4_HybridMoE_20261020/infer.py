"""Minimal combined ONNX inference, without PyTorch or a GUI."""
from pathlib import Path
import hashlib,json
import numpy as np
import onnxruntime as ort
ROOT=Path(__file__).resolve().parent
class HybridMoE:
 def __init__(self):
  path=ROOT/'policy/hybrid_moe.onnx';m=json.loads((ROOT/'policy/manifest.json').read_text('utf8'));assert hashlib.sha256(path.read_bytes()).hexdigest()==m['onnx_SHA'];self.session=ort.InferenceSession(str(path),providers=['CPUExecutionProvider'])
 def __call__(self,obs):
  x=np.asarray(obs,dtype=np.float32)
  if x.ndim==1:x=x[None,:]
  if x.ndim!=2 or x.shape[1]!=35 or not np.isfinite(x).all():raise ValueError('Expected finite float32 [batch,35] observation')
  if not np.all((x[:,28:35]==0)|(x[:,28:35]==1)) or not np.all(x[:,28:35].sum(axis=1)==1):raise ValueError('Mode must be exactly one-hot')
  y=self.session.run(['action'],{'observation':x})[0]
  if y.shape!=(len(x),6) or not np.isfinite(y).all():raise ValueError('Invalid action')
  return y
if __name__=='__main__':
 x=np.zeros(35,dtype=np.float32);x[3]=1.25;x[9]=-1;x[28]=1
 print(json.dumps(dict(action=HybridMoE()(x).tolist(),sample_only=True),indent=2))
