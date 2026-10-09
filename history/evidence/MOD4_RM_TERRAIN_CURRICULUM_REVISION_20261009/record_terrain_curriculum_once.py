"""One unique human-requested terrain plan revision archive, no GPU operation."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train';P=REPO/'history/plans';R=D/'reports'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf8'))
receipt=R/'RM_TERRAIN_CURRICULUM_GIT_RECORDED.json';assert not receipt.exists(),'Already archived; do not repeat'
prep=load(R/'TERRAIN_CURRICULUM_PREPARED.json');v=load(P/'MOD4_RM_TERRAIN_TRAINING_REVISION.json')
assert digest(P/'MOD4_MOE_MASTER_PLAN.md')==v['master_sha256']
assert all(digest(P/n)==s for n,s in prep['files_sha256'].items())
assert all(digest(P/n)==s for n,s in v['prior_documents_sha256'].items())
folder=REPO/'history/evidence/MOD4_RM_TERRAIN_CURRICULUM_REVISION_20261009';assert not folder.exists();folder.mkdir(parents=True)
files=['history/plans/'+n for n in prep['files_sha256']]
for src in [D/'prepare_terrain_curriculum_once.py',D/'sync_terrain_curriculum_once.py',D/'record_terrain_curriculum_once.py',R/'TERRAIN_CURRICULUM_PREPARED.json',R/'PLAN_ANNOTATIONS_BEFORE_003.md']:
 dst=folder/src.name;shutil.copyfile(src,dst);assert digest(src)==digest(dst);files.append(dst.relative_to(REPO).as_posix())
note='''# Human-requested RM terrain curriculum revised from the audited source geometry

The human asked to modify terrain training according to the verified RM field geometry. A concrete S3 independent-E1 progression and S7 spin work order now separate shallow foundation, actual70mm continuous rough roads, local slope bases, and complete outside-curb-inside central-island routes. The selected inside44/92-94mm and outside149.929/200.069mm support differences are not collapsed into a5cm curb; original vertical walls, original CAD wave period/directions and finite-measurement limitations remain explicit. Synthetic scaled intermediate stages are labeled derived, not real RM.

Traversal remains yaw0; spin is separately staged on previously admitted support/clearance surfaces with existing tunnel/stair/deck exclusions. Original frozen master SHA and both prior supplements remain byte-exact. This revision follows the direct human request, preserves S8 approval boundaries and does not manufacture a new master approval, skill pass or new learning launch.

Existing S3/S7 planning caps include prior work and do not add budget. Existing same-scope clock/contracts are reused; genuine new geometry/contact/reset scopes require their own complete state and necessary preflight with discarded weights counted once. Current training, PPO/runtime and canonical ledger are untouched. Central metadata-only sync is prepared with compare-before-write and full protection of actual learning/evaluation/budget fields; it is pending at archive time and must have its own receipt before reported synced. Healthy2h monitoring and the human's optional shallow/MuJoCo cancellation remain.
'''
nf=folder/'RECORD_NOTE.md';nf.write_text(note,encoding='utf8');files.append(nf.relative_to(REPO).as_posix())
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id','rm-terrain-curriculum-revised-from-audited-rough-and-outer-curb',
 '--title','Revise planned RM terrain progression from verified rough-road and outer-curb geometry','--kind','deployment','--note-file',str(nf),'--files',*files,
 '--validation','Source dimensions/units and staged JSON verified; frozen master and001/002 byte SHA unchanged; no GPU/PPO/runtime/canonical writes; guarded central metadata sync prepared','--push']
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
 (R/'GIT_RECORD_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,do_not_repeat_record=True),ensure_ascii=False,indent=2),encoding='utf8')
 raise RuntimeError('Archive failed; inspect existing objects, do not repeat record')
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
proof=dict(epoch=time.time(),id=v['id'],tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,
 terrain_plan_revision_only=True,central_metadata_sync_pending_at_archive=True,master_SHA_unchanged=v['master_sha256'],production_runtime_GPU_PPO_canonical_writes=0,new_budget_seconds=0)
receipt.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(proof,ensure_ascii=True))
