"""CPU-only export of the latest complete source pool selected on the human request."""
from pathlib import Path
import ast,hashlib,json,os,shutil,sys,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
import torch,onnx,onnxruntime as ort
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';P=B/'player';POL=B/'policy'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def export(model,path):
 torch.onnx.export(model,torch.zeros(1,35),str(path),input_names=['observation'],output_names=['action'],dynamic_axes={'observation':{0:'batch'},'action':{0:'batch'}},opset_version=18,dynamo=False)
 g=onnx.load(str(path));g.graph.output[0].type.tensor_type.shape.dim[1].dim_value=6;onnx.checker.check_model(g);onnx.save(g,str(path))
def main():
 assert not (R/'EXPORT_STARTED_ACTUAL.json').exists();put('EXPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),human_request='最新检查点moe混合专家策略轮腿拉过来播放器让我玩玩试试',local_CPU_export_only=True))
 torch.set_num_threads(2);sys.path.insert(0,str(W/'mod4-onnx-mujoco-launcher'));from export_latest_moe import ManualMoE,SOURCES
 t=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
 hp=t/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V47_20261023/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'
 ep=W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021/reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'
 h=json.loads(hp.read_bytes());e=json.loads(ep.read_bytes());assert h['passed'] and e['passed'] and h['original_canonical_cost_settled'] and e['original_canonical_cost_settled']
 src={k:v for k,v in SOURCES.items() if k in ('E0','W35','gate148')};refs={}
 for role,key,proof,proofpath,hz in [('H1','h1',h,hp,100),('E2','e2',e,ep,50),('E3','recovery',h,hp,50)]:
  row=proof['models'][key];f=row['final'];assert f['twohost_complete_SHA'];src[role]=(Path(f['local_path']),f['SHA']);refs[role]=dict(complete_checkpoint=f,Adam=row['Adam'],policy_hz=hz,proof=str(proofpath),proof_SHA=H(proofpath))
 checks={};index={}
 for role,(path,digest) in src.items():
  assert H(path)==digest,role;ck=torch.load(path,map_location='cpu',weights_only=False);checks[role]=ck
  if role!='gate148':assert tuple(ck['actor_state_dict']['mlp.0.weight'].shape)==(256,35)
  index[role]=dict(path=str(path),bytes=path.stat().st_size,SHA=digest,iteration=ck.get('iter'),**refs.get(role,{}))
 model=ManualMoE(checks).eval();POL.mkdir();out=POL/'hybrid_moe.onnx';export(model,out)
 for role in ('E0','W35','H1','E2','E3'):export(model.experts[role],POL/(role+'.onnx'))
 rng=np.random.default_rng(20261023);x=rng.normal(0,.1,(700,35)).astype(np.float32);x[:,3]=1.25;x[:,7:10]=[0,0,-1];modes=np.arange(len(x))%7;x[:,28:35]=np.eye(7,dtype=np.float32)[modes];tx=torch.from_numpy(x)
 with torch.no_grad():
  y=model(tx).numpy();choices=model.choice(tx).numpy();routed=[]
  for i,mode in enumerate(modes):
   role='H1' if mode==4 else 'E3' if mode==3 else 'E2' if mode==6 else ('E0','W35')[choices[i]]
   view=tx[i:i+1] if role in ('H1','E3') else model.normal_view(tx[i:i+1]);assert torch.equal(model(tx[i:i+1]),model.experts[role](view).clamp(-6,6));routed.append(role)
 z=ort.InferenceSession(str(out),providers=['CPUExecutionProvider']).run(None,{'observation':x})[0];err=float(np.max(np.abs(y-z)));assert z.shape==(len(x),6) and np.isfinite(z).all() and err<=1e-4 and set(routed)=={'E0','W35','H1','E2','E3'}
 manifest=dict(epoch=time.time(),onnx_SHA=H(out),sources=index,deterministic_mean=True,whole_six_action_selection=True,weight_or_action_averaging=False,original_E0_W35_gate=True,new_five_way_learned_gate=False,policy_hz={'E0':100,'W35':100,'H1':100,'E2':50,'E3':50},parity_rows=len(x),parity_clipped_max_abs=err,skill_qualification=False,source_cutoff='Latest complete locally verified pool at human request; active48 excluded and no live reload.',no_training_or_budget_or_remote_change=True)
 (POL/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 source=W/'MOD4_LATEST_HYBRID_MOE_PACKAGE_20261020/delivery/MOD4_HybridMoE_20261020/player';shutil.copytree(source,P,ignore=shutil.ignore_patterns('__pycache__','rm7v7_moe_runs','*.lock'))
 sim=P/'rm7v7_moe_sim.py';s=sim.read_text('utf8');assert "D.parent/'policy/hybrid_moe.onnx'" in s
 s=s.replace("self.reset_route('flat_run')","self.policy = ExpertClockPolicy(self.policy, lambda: self.command.mode)\n        self.reset_route('flat_run')")
 s += '''\n\nclass ExpertClockPolicy:\n    """100 Hz outer loop; native 50 Hz E2/E3 outputs held for two ticks."""\n    def __init__(self, base, mode):\n        self.base=base;self.mode=mode;self.path=base.path;self.input_width=base.input_width;self.reset()\n    def reset(self):\n        self.last_mode=None;self.phase=0;self.held=None;self.calls={};self.ticks={}\n    def __call__(self, obs):\n        mode=int(self.mode());period=2 if mode in (3,6) else 1\n        if mode!=self.last_mode:self.phase=0;self.last_mode=mode\n        if self.phase==0 or self.held is None:\n            self.held=self.base(obs);self.calls[mode]=self.calls.get(mode,0)+1\n        self.ticks[mode]=self.ticks.get(mode,0)+1;self.phase=(self.phase+1)%period\n        return self.held.copy()\n'''
 # Reset the local clock only when the human resets the simulator.
 s=s.replace('super().reset(x,y,yaw,ground_z)','super().reset(x,y,yaw,ground_z)\n        if isinstance(self.policy, ExpertClockPolicy): self.policy.reset()')
 ast.parse(s);sim.write_text(s,encoding='utf8')
 driver=P/'drive_rm7v7_moe.py';s=driver.read_text('utf8').replace('最新完整源 H1第16小时 / E2第17小时 / E3第17小时 + 原 E0/W35门控','最新完整源 H1第47轮 / E2第52轮 / E3第47轮 + 原 E0/W35门控').replace('MuJoCo 物理 · 100 Hz 策略 · 无扶正/航向辅助','MuJoCo · H1/普通100 Hz，自旋/恢复50 Hz · 无扶正/航向辅助')
 s=s.replace("if sim.jump_pending or sim.command.mode in (3,4):target_v=target_w=0.","if sim.jump_pending or sim.command.mode==3:target_v=target_w=0.\n                    elif sim.command.mode==4:target_v=.8;target_w=0.")
 s=s.replace('J 跳跃0.8秒；','J 向前跳跃0.8秒（指令0.8 m/s）；');ast.parse(s);driver.write_text(s,encoding='utf8')
 launch='@echo off\nchcp 65001 >nul\ncd /d "%~dp0"\n"'+str(W/'.venv/Scripts/pythonw.exe')+'" -B -X utf8 "player/drive_rm7v7_moe.py"\n'
 (B/'试玩最新MoE.bat').write_text(launch,encoding='utf8')
 put('LATEST_COMPLETE_MOE_EXPORT_PLAYER_BUILD_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),manifest=manifest,player=str(P),source_player=str(source),original_player_untouched=True,player_changes=['new pinned complete source pool','per-expert action sample-and-hold 100/50Hz','H1 public forward command .8 m/s during existing jump request'],initial_search_permission_error='rg broad file inventory encountered rmuc2026_work/unpack_verify_4zomhj13 access denied; narrowed existing-player reads succeeded. No permissions changed.',no_new_training_or_skill_graduation=True))
 print(json.dumps(dict(passed=True,player=str(P),onnx_SHA=manifest['onnx_SHA'],parity_max=err,sources={k:v['SHA'] for k,v in index.items()})))
if __name__=='__main__':
 try:main()
 except BaseException:put('EXPORT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
