"""Pure matrix condensation from frozen JSON; never imports the parent module."""
from pathlib import Path
import hashlib,json,sys,numpy as np
HERE=Path(__file__).resolve().parent
WORK=HERE.parents[1]
SOURCE=WORK/'scalar_ground_mpc_v1.py'
MODEL=WORK/'MPC8_V1/MODEL_AND_QP_CHECKS.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def condensed():
 raw=json.loads(MODEL.read_text(encoding='utf-8'));assert sha(SOURCE)==raw['source_SHA']
 A=np.asarray(raw['A'],dtype=float);B=np.asarray(raw['B'],dtype=float);Q=np.asarray(raw['Q'],dtype=float);P=np.asarray(raw['P'],dtype=float);R=float(raw['R']);N=15
 assert A.shape==(9,9) and B.shape==(9,1) and Q.shape==P.shape==(9,9)
 F=np.concatenate([np.linalg.matrix_power(A,k) for k in range(1,N+1)],axis=0);G=np.zeros((9*N,N));W=np.zeros((9*N,9*N))
 for k in range(N):
  for j in range(k+1):G[9*k:9*k+9,j:j+1]=np.linalg.matrix_power(A,k-j)@B
  W[9*k:9*k+9,9*k:9*k+9]=Q if k<N-1 else P
 Hraw=2*(G.T@W@G+R*np.eye(N));H=(Hraw+Hraw.T)*.5;H32=H.astype(np.float32);H32=(H32+H32.T)*np.float32(.5)
 return raw,A,B,Q,P,F,G,W,Hraw,H,H32
if __name__=='__main__':
 raw,A,B,Q,P,F,G,W,Hraw,H,H32=condensed()
 info={'mode':'MATRIX_ALGEBRA_ONLY_NO_PARENT_IMPORT_OR_PHYSICS','source':{'path':str(SOURCE),'bytes':SOURCE.stat().st_size,'sha256':sha(SOURCE)},
  'model_json':{'path':str(MODEL),'bytes':MODEL.stat().st_size,'sha256':sha(MODEL)},'state8':raw['state8'],'input':raw['input'],
  'shapes':{'F':list(F.shape),'G':list(G.shape),'Qbar':list(W.shape),'H':list(H.shape)},
  'H_raw_asymmetry_max':float(np.max(np.abs(Hraw-Hraw.T))),'H32_exact_symmetric':bool(np.array_equal(H32,H32.T)),
  'H64_condition_2':float(np.linalg.cond(H)),'H32_as_double_condition_2':float(np.linalg.cond(H32.astype(float))),
  'H64_eigen_min_max':np.linalg.eigvalsh(H)[[0,-1]].tolist(),'H32_as_double_eigen_min_max':np.linalg.eigvalsh(H32.astype(float))[[0,-1]].tolist(),
  'H32_quantization_max':float(np.max(np.abs(H32.astype(float)-H))),'NumPy':np.__version__,'python':sys.version,
  'float64_Cholesky_min_pivot':float(np.min(np.diag(np.linalg.cholesky(H)))),
  'float32_Cholesky_min_pivot':float(np.min(np.diag(np.linalg.cholesky(H32)))),
  'H64':H.tolist(),'H32':H32.tolist()}
 (HERE/'HESSIAN_BASELINE.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in info.items() if k not in ['H64','H32']},indent=2))
