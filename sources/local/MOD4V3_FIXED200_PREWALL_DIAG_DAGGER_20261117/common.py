"""Independent pre-wall diagnosis; reuse frozen teacher without modifying its source."""
from pathlib import Path
import sys,json,hashlib,datetime
import numpy as np,torch,mujoco as mj
T=Path(__file__).resolve().parent
R=T.parents[2]
S=R/'sources/local/MOD4V3_FIXED200_DAGGER_SEMANTIC_10M_20261116'
P=R/'sources/local/MOD4V3_FIXED200_SETTLE_CRUISE_REPAIR_10M_20261116'
F=R/'sources/local/MOD4V3_SERIAL_TEACHER_FIXED200_40M_20261116'
E=R/'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1'
sys.path.insert(0,str(S))
import collect_dagger as frozen
setup=frozen.setup;observation=frozen.observation;student_step=frozen.student_step
fullstate=frozen.fullstate;read_features=frozen.read_features;ActorMLP=frozen.ActorMLP
PPO_TO_NATIVE=frozen.PPO_TO_NATIVE
MODE=frozen.MODE
PROFILE=frozen.PROFILE
torch.set_num_threads(1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def actor_load(p):
 ck=torch.load(p,map_location='cpu',weights_only=False);a=ActorMLP()
 state=ck['actor_state_dict'];extra=set(state)-set(a.state_dict());assert extra<= {'distribution.std_param'},extra
 a.load_state_dict({k:v for k,v in state.items()if k in a.state_dict()},strict=True);a.eval();return a,ck

def protected():
 files=[R/'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt',R/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json',S/'weights/model_010m.pt',S/'skill_dataset/qualified_mod4_skills.npz',S/'skill_dataset/MANIFEST.json',P/'weights/model_005m.pt',P/'weights/model_010m.pt',P/'skill_dataset/qualified_mod4_skills.npz',E/'forward_capture_repair_20261116/CANDIDATE_PROFILE.json']
 idx=json.loads((F/'teacher_snapshot/SOURCE_INDEX.json').read_text(encoding='utf-8'))
 for row in idx['files']:
  p=Path(row['path']);assert sha(p)==row['sha256'],str(p)+' changed since authorized teacher snapshot'
  files.append(p)
 return {str(p):sha(p) for p in dict.fromkeys(files) if p.is_file()}
def guard():
 current=protected();f=T/'evidence/PROTECTED_INPUTS.json'
 if f.exists():assert json.loads(f.read_text(encoding='utf-8'))['sha256']==current,'Protected input changed'
 else:put(f,dict(created_at=datetime.datetime.now().astimezone().isoformat(),sha256=current))
 return current
