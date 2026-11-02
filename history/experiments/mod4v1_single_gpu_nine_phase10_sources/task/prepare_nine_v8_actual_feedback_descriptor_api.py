"""Descriptor-onlyactualFeedbackDelay.delay accessor; keepsphysics/DR/actor/geometry/criterion identicalV7."""
from pathlib import Path
import json,hashlib,ast
R=Path(__file__).resolve().parent;S=R/'NINE_N80_PARALLEL_SOURCE_V7';D=R/'NINE_N80_PARALLEL_SOURCE_V8';assert not D.exists();D.mkdir()
for p in S.iterdir():
 if p.is_file():(D/p.name).write_bytes(p.read_bytes())
old=json.loads((R/'E1_N80_G4_PURE_MATH_SOURCE_HANDOFF_V4.json').read_bytes());F=R/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR';assert not F.exists();F.mkdir()
for r in old['runtime_files_to_stage_same_directory']:
 p=Path(r['path']);raw=p.read_bytes();assert len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA'];(F/p.name).write_bytes(raw)
p=F/'e1_route80_factories.py';s=p.read_text(encoding='utf-8');assert s.count("feedback_delay=js(e._feedback_delay_mild.lag_steps)")==1;s=s.replace("feedback_delay=js(e._feedback_delay_mild.lag_steps)","feedback_delay=js(e._feedback_delay_mild.delay),feedback_delay_units='original100Hz_sampleticks_0or1_equals_0or10000us'");ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n');refs=[]
for base in('E1_actual_qualification_v1/SLOPE135_ACTUAL_TYPED_SOURCE_V1','E1_three_variants_GPU_actual_v1/CURB_PROTECTED878_ACTUAL_TYPED_SOURCE_V1','E1_three_variants_GPU_actual_v1/CURB_INDEPENDENT113_ACTUAL_TYPED_SOURCE_V1','E1_three_variants_GPU_actual_v1/SLOPE_INDEPENDENT50_ACTUAL_TYPED_SOURCE_V1'):
 p=R/base/'runtime/isaac/mod4/feedback_delay_mild.py';raw=p.read_bytes();txt=raw.decode();assert 'self.delay=torch.zeros(n' in txt and 'requested_delay_us=self.delay*10000'in txt;refs.append({'path':str(p),'SHA':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'actual_accessor':'delay','units':'100Hzsampleticks0or1'})
entries=[]
for p in sorted(F.iterdir()):
 if p.suffix not in('.py','.json'):continue
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
 raw=p.read_bytes();entries.append({'path':str(p),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
h=R/'E1_N80_FEEDBACK_DESCRIPTOR_ACTUAL_API_HANDOFF_V5.json';assert not h.exists();h.write_text(json.dumps({'kind':'DESCRIPTOR_ACTUAL_API_DELAY_NOT_LAG_STEPS','runtime_files_to_stage_same_directory':entries,'source_root':str(F),'feedback_API_source_refs':refs,'noDelayDataOrRNGOrPhysicsOrCriterionChanges':True,'oldV7zero_control_error_preserved':True},indent=2),encoding='utf-8');rows=[]
for p in D.glob('*.py'):
 raw=p.read_bytes();ast.parse(raw.decode('utf-8'));rows.append({'relative':p.name,'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
(D/'PARENT_FIVE_SOURCE_INDEX_V9.json').write_text(json.dumps({'kind':'SAME_PARENT_V7_PLUS_ACTUAL_FEEDBACK_DESCRIPTOR_READER','files':rows,'noPlantDRClockPolicyChanges':True,'SDK_PT_GPUcallsThisProducer':0,'sourceRefs':refs},indent=2),encoding='utf-8')
s=(R/'stage_and_dispatch_nine_single_gpu_eval_v7_once.py').read_text(encoding='utf-8').replace('NINE_N80_PARALLEL_SOURCE_V7','NINE_N80_PARALLEL_SOURCE_V8').replace('PARENT_FIVE_SOURCE_INDEX_V8.json','PARENT_FIVE_SOURCE_INDEX_V9.json').replace('NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V7.json','NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V8.json').replace('MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V7_','MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_').replace('E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V4_G4_MATH','E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR').replace('E1_N80_G4_PURE_MATH_SOURCE_HANDOFF_V4.json','E1_N80_FEEDBACK_DESCRIPTOR_ACTUAL_API_HANDOFF_V5.json');p=R/'stage_and_dispatch_nine_single_gpu_eval_v8_once.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
s=(R/'collect_nine_single_gpu_v7_until_closed_once.py').read_text(encoding='utf-8').replace('V7','V8');p=R/'collect_nine_single_gpu_v8_until_closed_once.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n');print('V8_ACTUAL4ROLE_FEEDBACK_API_SOURCECONFIRMED / descriptoronly / zeroPTOpensSDK')
