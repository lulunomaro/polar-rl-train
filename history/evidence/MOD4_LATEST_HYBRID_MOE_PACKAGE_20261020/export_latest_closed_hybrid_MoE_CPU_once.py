"""Export the latest actually closed per-expert pool into a new delivery only."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,os,sys,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
import torch,onnx,onnxruntime as ort
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';P=B/'delivery/MOD4_HybridMoE_20261020';POL=P/'policy';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 R.mkdir(exist_ok=True)
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def export(model,path):
 assert not path.exists();torch.onnx.export(model,torch.zeros(1,35),str(path),input_names=['observation'],output_names=['action'],dynamic_axes={'observation':{0:'batch'},'action':{0:'batch'}},opset_version=18,dynamo=False);g=onnx.load(str(path));g.graph.output[0].type.tensor_type.shape.dim[1].dim_value=6;onnx.checker.check_model(g);onnx.save(g,str(path))
def main():
 torch.set_num_threads(2);assert not P.exists();POL.mkdir(parents=True);sys.path.insert(0,str(W/'mod4-onnx-mujoco-launcher'));from export_latest_moe import ManualMoE,SOURCES
 proof=W/'MOD4_SCUT_FUDAN_SEVENTEENTH_HOUR_20261019/reports/PARTIAL_HOUR_ACTUAL_GO_FINALS_AND_NEXT_SOURCES_CPU_ACTUAL.json';v=json.loads(proof.read_bytes());assert v['passed_next_three_sources_whole_model_CPU'];expected={'h1':'cb118b2ac27cca44466fba9014f4583ee8db23fc2cb2d83c4034b15961178765','e2':'48150f0dc8f279a421cb84462fcefce7a0632c3ba5eaf721f37bb74d4c26bbb8','recovery':'f4837513bff985753b942d40887b44076493aea83b17214dbb07eeafb8c1e7c4'};src={k:value for k,value in SOURCES.items() if k in ('E0','W35','gate148')};index={};checkpoints={}
 for role,key in [('H1','h1'),('E2','e2'),('E3','recovery')]:
  row=v['experts'][key];f=row['final'];assert f['SHA']==expected[key] and f['twohost_complete_SHA'] and row['all_model_runtime_finite'];src[role]=(Path(f['local_path']),f['SHA'])
 for role,(path,digest) in src.items():
  assert H(path)==digest;ck=torch.load(path,map_location='cpu',weights_only=False);checkpoints[role]=ck;index[role]=dict(source_path=str(path),bytes=path.stat().st_size,SHA=digest,iteration=ck.get('iter'),completed_hour=16 if role=='H1' else 17 if role in ('E2','E3') else None,Adam_step=674740 if role=='H1' else 772320 if role=='E2' else 699640 if role=='E3' else None)
 model=ManualMoE(checkpoints).eval();output=POL/'hybrid_moe.onnx';export(model,output)
 # Deliver deterministic individual expert actors as well as the combined router.
 for role in ('E0','W35','H1','E2','E3'):export(model.experts[role],POL/(role+'.onnx'))
 rng=np.random.default_rng(20261020);x=rng.normal(0,.1,(1400,35)).astype(np.float32);x[700:,:28]*=10;x[:,3]=1.25;x[:,7:10]=[0,0,-1];modes=np.arange(len(x))%7;x[:,28:35]=np.eye(7,dtype=np.float32)[modes];tx=torch.from_numpy(x)
 with torch.no_grad():
  expected_actions=model(tx).numpy();choices=model.choice(tx).numpy();routed=[]
  for i,mode in enumerate(modes):
   role='H1' if mode==4 else 'E3' if mode==3 else 'E2' if mode==6 else ('E0','W35')[choices[i]];view=tx[i:i+1] if role in ('H1','E3') else model.normal_view(tx[i:i+1]);assert torch.equal(model(tx[i:i+1]),model.experts[role](view).clamp(-6,6));routed.append(role)
 session=ort.InferenceSession(str(output),providers=['CPUExecutionProvider']);actual=session.run(None,{'observation':x})[0];error=float(np.max(np.abs(actual-expected_actions)));assert actual.shape==(len(x),6) and np.isfinite(actual).all() and error<=1e-4;assert set(routed)=={'E0','W35','H1','E2','E3'}
 individual={}
 for role in ('E0','W35','H1','E2','E3'):
  with torch.no_grad():y=model.experts[role](tx).numpy()
  z=ort.InferenceSession(str(POL/(role+'.onnx')),providers=['CPUExecutionProvider']).run(None,{'observation':x})[0];e=float(np.max(np.abs(np.clip(y,-6,6)-np.clip(z,-6,6))));assert e<=1e-4;individual[role]=dict(path=role+'.onnx',SHA=H(POL/(role+'.onnx')),bytes=(POL/(role+'.onnx')).stat().st_size,clipped_parity_max_abs=e)
 meta=dict(schema_version=1,delivery_name='MOD4_HybridMoE_20261020',created_Beijing=datetime.now(timezone(timedelta(hours=8))).isoformat(),source_cutoff='Latest locally verified closed source pool at export time; current single E3 hour18 excluded until closed/fullCPU.',onnx_file='hybrid_moe.onnx',onnx_SHA=H(output),input={'name':'observation','shape':['batch',35],'dtype':'float32'},output={'name':'action','shape':['batch',6],'clamp':[-6,6]},sources=index,individual_experts=individual,deterministic_mean=True,whole_six_action_selection=True,weight_or_action_averaging=False,gate='original gate148 E0/W35 argmax',manual_skills={'mode4':'H1 jump','mode3':'E3 recover','mode6_player_alias':'E2 spin (rewrite mode vector to normal before E2 inference)'},mode_priority_for_invalid_multi_hot='H1(mode4) > E3(mode3) > E2(mode6) > gate; use exactly one mode.',new_learned_five_way_gate=False,closure_proof={'path':str(proof),'SHA':H(proof)},parity_rows=len(x),parity_clipped_max_abs=error,parity_bound=1e-4,routed_roles=sorted(set(routed)),skill_qualification=False,no_remote_or_training_or_original_player_change=True)
 (POL/'manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8');put('LATEST_CLOSED_HYBRID_MOE_EXPORT_AND_ROUTING_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,package_root=str(P),**meta));print(json.dumps(dict(exported=str(output),parity_rows=len(x),parity_max=error,source_hours={'H1':16,'E2':17,'E3':17},original_player_untouched=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('LATEST_HYBRID_MOE_EXPORT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_remote_GPU_or_training_or_original_player_change=True));raise
