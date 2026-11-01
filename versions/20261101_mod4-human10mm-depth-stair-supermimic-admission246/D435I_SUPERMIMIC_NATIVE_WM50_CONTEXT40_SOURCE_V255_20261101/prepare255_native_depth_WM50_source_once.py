from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True);B=T/'EXPERTS_RM70_SUPERMIMIC_READY_QUEUE_V190_20261031'
source=B/'teacher_world_model50_core190_v3.py';b=source.read_bytes();s=b.decode('utf8')
s=s.replace('class FlatTeacherWorldModel:','class DepthTeacherWorldModel:').replace('FlatTeacherWorldModel.make','DepthTeacherWorldModel.make').replace('class TeacherWM50:','class DepthTeacherWM50:')
s=s.replace('Original E0/E2 flat local ground z=0. No fictitious H1 edge.','No privileged terrain feature: observed depth9 is in context40. This is not the old flat-ground assumption.')
s=s.replace('return torch.stack((torch.zeros_like(p[...,0]),torch.zeros_like(p[...,1]),-p[...,2]),-1)','return torch.zeros_like(p)')
s=s.replace('world.AugmentedWheelLegWorldModel,31,hidden','world.AugmentedWheelLegWorldModel,40,hidden').replace('context_dim=31,action_dim=6','context_dim=40,action_dim=6')
s=s.replace('static31=True,actions6=True','static31=True,depth9=True,context40=True,actions6=True').replace("kind='NATIVE_SUPERMIMIC_WM50_FROZEN_PPO_TEACHER'","kind='NATIVE_SUPERMIMIC_OWN_FULLSTATE_DEPTH_CONTEXT40_WM50'")
s=s.replace('from compact_episode_static31_v1 import normalize_static31','normalize_static31=normalize_context40')
needle='    def add(self,transition,*,physics_end_tick,physics_us,feedback_samples):'
assert s.count(needle)==1
s=s.replace(needle,"""    def add(self,transition,*,physics_end_tick,physics_us,feedback_samples,producer,synthetic_CPU_test=False):
        expected='SYNTHETIC_CPU_INTERFACE_ONLY' if synthetic_CPU_test else 'ACTUAL_OWN_MOD4_FULLSTATE_DEPTH_PRODUCER'
        if producer.get('kind')!=expected or producer.get('plant')!='own_MOD4_live_USD':raise ValueError('Own fullstate/depth producer required')
        if not all(producer.get(k) for k in ('run_id','generation','source_admission_SHA')):raise ValueError('Missing actual producer binding')
        if not 0<=producer['max_depth_age_seconds']<=.20:raise ValueError('Future/stale depth')
""")
s+='''\n\ndef normalize_context40(x):
    from compact_episode_static31_v1 import normalize_static31
    if x.shape[-1]!=40:raise ValueError('static31 raw plus raw depth9 required')
    scale=x.new_tensor([4.,.4,2.,3.141592653589793,2.,4.,1.,.2,1.])
    return torch.cat((normalize_static31(x[...,:31]),x[...,31:]/scale),-1)
'''
ast.parse(s);p=N/'native_depth_world_model50_v255.py';p.write_text(s,encoding='utf8')
purpose=json.loads((B/'reports/SOURCE190_V2_BOUNDED_LOCAL_CPU_PURPOSE_FROZEN.json').read_bytes())
with(R/'FROZEN255_NEW_CONTEXT40_SYNTHETIC_CPU_PURPOSE.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),source190_path=str(source),source190_SHA=hashlib.sha256(b).hexdigest(),native_source_directory=purpose['source_directory'],source255_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_scope='Native augmented127-state/30joint/54aux/17bit lineage and action6, newcontext40=static31+depth9, originalH32replay/loss/clip/own50Hz clock. New2env synthetic64pairs/1WMoptimizer update only; old190fixture0, realmodel/raw/SDK/GPU0.',complete_literal_Fudan_adapter_or_nativePiCritic_conversion=False),f,indent=2)
print(json.dumps(dict(passed=True,path=str(p),native_source=purpose['source_directory'])))
