"""Publish one exact-source S0E SDK job and its frozen self-contained runtime."""
from pathlib import Path
import hashlib,json,time,zipfile,os
ROOT=Path(__file__).resolve().parent;R=ROOT/'reports';Q=ROOT/'eval_queue';A=ROOT/'artifacts'
C=Path('/home/egde/rl_candidates/MOD4_CONTINUOUS_MIX_BASELINE_20261006')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
approval=json.loads((R/'PLAN_APPROVAL.json').read_text());assert approval['approved'] and 'S0E' in approval['allowed_stages']
assert sha(R/'MOD4_MOE_MASTER_PLAN.md')==approval['approved_plan_sha256']
receipt=R/'S0E_CALIBRATION_PUBLISHED.json';assert not receipt.exists(),'Already published; do not rerun once entry'
Q.mkdir(exist_ok=True);A.mkdir(exist_ok=True)
freeze=json.loads((C/'reports/SOURCE_FREEZE.json').read_text())['sha256']
files={};payload=[]
for rel,digest in freeze.items():
 p=C/rel;assert sha(p)==digest,rel;files['runtime/'+rel]=digest;payload.append((p,'runtime/'+rel))
for name in ['robot.usd','import_contract.json']:
 p=Path('/home/egde/fangzhen_linux/incoming/_from_target_20260928')/name
 files['assets/'+name]=sha(p);payload.append((p,'assets/'+name))
assert files['assets/robot.usd']=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
package=A/'s0e-c198-runtime.zip'
with zipfile.ZipFile(str(package)+'.partial','w',compression=zipfile.ZIP_DEFLATED) as z:
 for p,rel in payload:z.write(p,rel)
 z.writestr('SOURCE_MANIFEST.json',json.dumps({'files':files,'original_runtime_source_count':198,'asset_originals_unchanged':True,'source_freeze_sha256':sha(C/'reports/SOURCE_FREEZE.json')}))
os.replace(str(package)+'.partial',package)
source=json.loads((R/'STAGE_S0_CHECKPOINTS_CPU.json').read_text())['sources']['E0_anchor']
checkpoint=Path(source['path']);assert sha(checkpoint)==source['sha256']
job='s0e-23509-white3-flat-sdk300'
d={'job_id':job,'stage':'S0E','immutable':True,'plan_id':approval['plan_id'],'plan_sha256':approval['approved_plan_sha256'],
 'published_epoch':time.time(),'kind':'flat','profile':'white_v3','seed':20261002,'num_envs':80,'steps':300,'max_wall_seconds':1800,
 'protocol':'SDK300 startup and readback only; not1500-step formal capability','source_CPU_verified':source,
 'artifacts':{k:{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for k,p in [('runtime',package),('checkpoint',checkpoint)]},
 'no_learning':True,'canonical_write_authority':False,'GPU_concurrency':1}
target=Q/(job+'.json');assert not target.exists();temp=target.with_suffix('.json.partial');temp.write_text(json.dumps(d,indent=2));temp.replace(target)
proof={'epoch':time.time(),'job':d,'runtime_sources_unchanged':198,'original_assets_not_modified':True,'learning_started':False}
receipt.write_text(json.dumps(proof,indent=2));print(json.dumps({'job':job,'runtime_bytes':package.stat().st_size,'runtime_sha256':sha(package),'checkpoint_SHA':sha(checkpoint)}))
