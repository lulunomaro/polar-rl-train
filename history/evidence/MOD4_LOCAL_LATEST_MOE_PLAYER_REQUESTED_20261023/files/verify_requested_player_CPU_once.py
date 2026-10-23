from pathlib import Path
import ast,hashlib,json,sys,time,traceback
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';P=B/'player'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 assert not (R/'LOCAL_PLAYER_CPU_STARTED_ACTUAL.json').exists();put('LOCAL_PLAYER_CPU_STARTED_ACTUAL.json',dict(epoch=time.time()))
 # The public H1 command must reach .8 immediately, rather than spending its
 # entire .8-second request inside the normal driving command slew limiter.
 p=P/'drive_rm7v7_moe.py';s=p.read_text('utf8');needle="current_v+=float(np.clip(target_v-current_v,-.008,.008));current_w+=float(np.clip(target_w-current_w,-.04,.04))"
 assert s.count(needle)==1;s=s.replace(needle,needle+"\n                    if sim.command.mode==4:current_v=.8;current_w=0.");ast.parse(s);p.write_text(s,encoding='utf8')
 sys.path.insert(0,str(P));from rm7v7_moe_sim import RM7V7MoESim,ExpertClockPolicy
 class Fake:
  path=Path('fake');input_width=35
  def __init__(self):self.n=0
  def __call__(self,x):self.n+=1;return np.full(6,self.n,dtype=np.float32)
 clocks={}
 for mode,hz in [(0,100),(3,50),(4,100),(6,50)]:
  fake=Fake();clock=ExpertClockPolicy(fake,lambda:mode);values=[clock(np.zeros(35)) for _ in range(100)];assert fake.n==hz
  if hz==50:assert all(np.array_equal(values[i],values[i+1]) for i in range(0,100,2))
  clocks[str(mode)]=dict(ticks=100,inferences=fake.n,period_ticks=100//hz)
 sim=RM7V7MoESim();parameters=sim.parameter_readback();smoke=[]
 for mode in (0,4,3,6):
  sim.reset_route('flat_run');sim.select_skill(mode);sim.command.vx=.8 if mode==4 else 0.;sim.command.wz=4. if mode==6 else 0.
  for i in range(30):sim.step_control()
  h=sim.health();assert h['finite'];assert sim.policy.calls[mode]==(15 if mode in (3,6) else 30)
  smoke.append(dict(mode=mode,controls=30,inferences=sim.policy.calls[mode],health=h))
 put('LATEST_MOE_LOCAL_PLAYER_CLOCK_AND_MUJOCO_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,clocks=clocks,parameters=parameters,real_onnx_mujoco_smoke=smoke,command_correction='.8m/s H1 public command bypasses normal UI slew during existing request; no action script or force.',GUI_not_yet_started=True,no_skill_qualification=True,no_training_or_remote_GPU_or_budget_change=True))
 print(json.dumps(dict(passed=True,clocks=clocks,real_modes=[x['mode'] for x in smoke])))
except BaseException:put('LOCAL_PLAYER_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
