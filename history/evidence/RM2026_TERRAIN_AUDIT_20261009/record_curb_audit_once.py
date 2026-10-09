"""One new static geometry diagnostic and plan correction, preserving old trials."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train';P=REPO/'history/plans'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=D/'RM_CURB_CLARIFICATION_GIT_RECORDED.json'
assert not receipt.exists()
v=json.loads((P/'MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.json').read_text(encoding='utf8'))
assert sha(P/'MOD4_MOE_MASTER_PLAN.md')==v['master_sha256']
folder=REPO/'history/evidence/RM2026_TERRAIN_AUDIT_20261009';assert not folder.exists();folder.mkdir(parents=True)
files=['history/plans/'+n for n in ['MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md','MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.json','MOD4_PLAN_ANNOTATIONS.md']]
names=['AUDIT_REPORT.md','GEOMETRY_AUDIT.json','audit_terrain.py','curb_locations.png','outer_curb_sections.png',
    'rough_profiles.png','CLARIFICATION_PREPARED.json','PLAN_ANNOTATIONS_BEFORE_CLARIFICATION.md',
    'prepare_curb_clarification_once.py','sync_curb_clarification_once.py','record_curb_audit_once.py']
for n in names:
    shutil.copyfile(D/n,folder/n);assert sha(D/n)==sha(folder/n);files.append((folder/n).relative_to(REPO).as_posix())
note='''# Central-island outer curb identification corrected and RM rough geometry audited

The human's arrow screenshot clarifies the intended obstacle as the outer left/right continuous central-island curb, not the previously annotated inner part383/BREP424 chamfer. Preserve that earlier geometry measurement, raw evidence and trial; supersede only its attribution to the user's target. A new plan supplement and index require the actual complete outside-curb-inside traversal and separate admissions for varying support levels and vertical walls, keeping original spin exclusions, current training and S8 approval bounds.

Static inspection of complete supplied V1.0/V1.5 rulebook pages and original supplied V2 CAD B-Rep verifies 150mm curb width, V1.5 drawing nominal50mm inside rise, selected delivered center44.241mm inside/149.929mm outside rises and selected transition92-94mm inside rises. They are finite position-dependent samples, not whole-perimeter extrema. Separate part280/281 650mm/~100mm blocks geometrically correspond to outpost pedestals; semantic attribution is explicitly inference.

Both original rough-road B-Rep sections have normal peak-to-trough69.999995mm, approximately240.642mm peak spacing and2.406423m section span, consistent with rulebook nominal70/240 to the recorded version difference. Finite collision-vs-BRep vertical section error is approximately1.4373mm, already present at original tessellation; do not claim whole-field or SDK precision. Current1cm shallow is not RM70mm. Original CAD SHA independently rechecked and read-only subset preserved. Local plan master SHA and old annotation bytes remain unchanged.

This is a static source audit and plan correction, not a GPU/PPO/SDK/hardware or training experiment. No production runtime, process, launch, canonical ledger or budget operation occurred. Central SSH credential environment is absent this turn, so central index sync is pending rather than falsely recorded complete; the new metadata-only sync entry is reviewable and guarded. Valid existing clock/same-scope tests remain reusable; no optional paused shallow evaluation or MuJoCo revival.
'''
nf=folder/'RECORD_NOTE.md';nf.write_text(note,encoding='utf8');files.append(nf.relative_to(REPO).as_posix())
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id','rm-outer-curb-target-corrected-and-rough-cad-dimensions-audited',
    '--title','Correct human RM outer-curb target and audit rough-road CAD geometry',
    '--kind','diagnostic','--note-file',str(nf),'--files',*files,
    '--validation','Original CAD SHA; B-Rep/mesh finite sections; visually reviewed full PDF figures; unchanged master/old annotation; no GPU/PPO/canonical writes; central metadata sync pending','--push']
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
    (D/'GIT_RECORD_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,do_not_repeat_record=True),ensure_ascii=False,indent=2),encoding='utf8')
    raise RuntimeError('Archive failed; inspect existing objects before resuming, never repeat record.')
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
proof=dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,
    static_geometry_audit_and_plan_clarification_only=True,central_metadata_sync_pending=True,
    master_SHA_unchanged=v['master_sha256'],production_runtime_GPU_PPO_canonical_writes=0,new_budget_seconds=0)
receipt.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(proof,ensure_ascii=False))
