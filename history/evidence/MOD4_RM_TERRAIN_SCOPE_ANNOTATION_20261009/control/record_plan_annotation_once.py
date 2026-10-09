"""Archive one actual plan/metadata annotation; this is not a learning experiment."""
from pathlib import Path
import json,time,subprocess,shutil,sys,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';P=REPO/'history/plans'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf8'))
receipt=R/'RM_TERRAIN_SCOPE_GIT_RECORDED.json';assert not receipt.exists()
v=read(P/'MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json');assert sha(P/'MOD4_MOE_MASTER_PLAN.md')==v['master_sha256']
folder=REPO/'history/evidence/MOD4_RM_TERRAIN_SCOPE_ANNOTATION_20261009';assert not folder.exists();folder.mkdir(parents=True)
files=['history/plans/'+n for n in ('MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md','MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json','MOD4_PLAN_ANNOTATIONS.md')]
def cp(src,n):
 dest=folder/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);assert sha(src)==sha(dest);files.append(dest.relative_to(REPO).as_posix())
for n in ('prepare_scope_annotation.py','sync_plan_annotation_once.py','record_plan_annotation_once.py'):cp(D/n,'control/'+n)
cp(R/'ANNOTATION_PREPARED.json','ANNOTATION_PREPARED.json')
for src,n in [(W/'rmuc2026_work/upper_entry_audit.json','CAD_ENTRY_LIP_AUDIT.json'),(W/'rmuc2026_training/reports/source.json','SUPPLIED_CAD_SOURCE.json')]:cp(src,n)
note='''# User-requested RM terrain curriculum annotation

The user explicitly requested a concrete RM terrain spin-location scope excluding dog-tunnel interiors and stairs, and asked that the stair-access entry lip be included in terrain adaptation. This records a plan/metadata annotation, not a new training or physics experiment.

The supplement maps ordinary ground/road, both continuous rough roads, central-island connecting slope faces, highway connecting slopes and trapezoidal-highland slopes to E1/E2 terrain-spin targets. Tunnel interiors, stair surfaces/edges and stair-top decks are excluded; airborne/fly-gap tasks retain their separate later scope. Actual face masks and sweep clearance are required rather than selecting entire mixed-use CAD parts.

Existing supplied-CAD evidence identifies the upper-island y=0 access chamfer, part383/BREP_424: rise49.5617556mm over49.5617556mm, local45deg. It connects into a gentler ramp; it is not a separate rail above the deck. E1 stair traversal must cover the complete approach-lip-ramp/stair-deck path, up/down/reverse/oblique/stop-start cases and actual wheel support, with no spawn-after-lip shortcut. Separate part280/281 approximately100mm edge blocks are not silently treated as the same49.56mm feature or admitted into the existing5cm course.

Original approved masterv1.5 SHA812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b remains byte-identical. Explicit future geometry targets are distinguished from currently admitted/validated ranges. CurrentD7 sources, learning, budget, physics, actor interface and S8 dangerous-reset approval boundaries are unchanged. New terrain needs its own actual geometry/contact/ground/reset admission; valid prior clock/same-scope PPO evidence is reused. No GPU/PPO/ledger transaction was performed for this annotation. CAD geometry is from the user's supplied2026V2 file, not later rulebook certification.
'''
nf=folder/'PLAN_ANNOTATION_NOTE.md';nf.write_text(note,encoding='utf8');files.append(nf.relative_to(REPO).as_posix())
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id','rm-terrain-spin-exclusions-and-stair-entry-lip-plan-noted','--title','RM terrain spin scope and stair entry lip annotated from user request','--kind','deployment','--note-file',str(nf),'--files',*files,'--validation','Plan-only annotation; direct human request; master SHA unchanged; existing supplied-CAD part/route hashes; independent entry rise/run/angle arithmetic; no new learning measurement or GPU/PPO/budget change','--push']
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
 (R/'GIT_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,do_not_repeat_record=True),indent=2),encoding='utf8');raise RuntimeError(p.stdout+'\n'+p.stderr)
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag);remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
proof=dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,annotation_only_not_learning_experiment=True,master_SHA_unchanged=v['master_sha256'],new_budget_seconds=0)
receipt.write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
