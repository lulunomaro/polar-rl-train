"""Adjudicate actual3060 SDK evidence, then publish exact1500-step anchor jobs."""
from pathlib import Path
import json,hashlib,time,sys,importlib.util
ROOT=Path(__file__).resolve().parent;R=ROOT/'reports';Q=ROOT/'eval_queue';E=ROOT/'eval_results/s0e-23509-white3-flat-sdk300'
receipt=R/'S0E_SDK_REVIEW_AND_FUNCTIONAL_QUEUE.json';assert not receipt.exists()
spec=importlib.util.spec_from_file_location('v4',Path('/home/egde/rl_candidates/MOD4_CONTINUOUS_MIX_BASELINE_20261006/isaac/mod4/scut_curriculum_gate_v4.py'))
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finalized(name):
 p=E/name;proof=json.loads((E/(name+'.receipt.json')).read_text());assert sha(p)==proof['sha256'] and p.stat().st_size==proof['bytes']
 return json.loads(p.read_text())
raw=finalized('probe.json');result=finalized('result.json')
assert result['phase']=='complete' and result['checkpoint']['sha256']=='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'
admission=gate.evidence(raw,'flat',minimum_seconds=3);assert admission['pass_'],admission
assert raw['steps']==300 and len(raw['per_environment']['alive'])==80
start=json.loads((Q/'s0e-23509-white3-flat-sdk300.json').read_text());sources=json.loads((R/'STAGE_S0_CHECKPOINTS_CPU.json').read_text())['sources']
jobs=[]
for role,iteration in [('E0_anchor',23509),('balanced_anchor',23621)]:
 source=sources[role];ck=Path(source['path']);assert sha(ck)==source['sha256']
 for kind,n in [('flat',80),('spin',88),('world',88)]:
  job=f's0e-{iteration}-white3-{kind}-functional1500';target=Q/(job+'.json');assert not target.exists()
  d={**start,'job_id':job,'published_epoch':time.time(),'kind':kind,'num_envs':n,'steps':1500,
   'protocol':'Frozen functional cross-host calibration; exact matching23509 or23621 white_v3 seed20261002 existing4090 evidence reused',
   'source_CPU_verified':source,'artifacts':{'runtime':start['artifacts']['runtime'],'checkpoint':{'path':str(ck),'bytes':ck.stat().st_size,'sha256':sha(ck)}}}
  t=target.with_suffix('.json.partial');t.write_text(json.dumps(d,indent=2));t.replace(target);jobs.append(job)
proof={'epoch':time.time(),'plan_sha256':start['plan_sha256'],'SDK_admission':admission,'source_sha256':source['sha256'],
 'SDK_source_checkpoint_sha256':result['checkpoint']['sha256'],'actual_result':result,'formal_functional_calibration_complete':False,
 'SDK_not_skill_graduation':True,'new_learning':False,'jobs':jobs,'new4090_GPU_probes':0,'same_original_80_88_environment_counts_and1500_steps':True}
receipt.write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
