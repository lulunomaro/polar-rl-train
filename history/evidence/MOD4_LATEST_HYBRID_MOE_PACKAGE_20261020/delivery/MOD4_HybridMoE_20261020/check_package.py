"""Verify delivered files and a small inference; no GUI or training."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
def main():
 m=json.loads((ROOT/'PACKAGE_MANIFEST.json').read_text('utf8'))
 for r in m['files']:
  p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve());assert p.is_file() and p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'],r['path']
 from infer import HybridMoE
 import numpy as np
 x=np.zeros((4,35),dtype=np.float32);x[:,3]=1.25;x[:,9]=-1;x[np.arange(4),28+np.array([0,4,3,6])]=1;y=HybridMoE()(x);assert y.shape==(4,6)
 print(json.dumps(dict(files_verified=len(m['files']),inference='PASS',source_hours={'H1':16,'E2':17,'E3':17},not_skill_qualification=True),indent=2))
if __name__=='__main__':main()
