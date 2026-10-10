"""Unique complete133 evaluation/diagnosis and new independent slope deployment Git stage."""
from review133_io import *
import subprocess,traceback
REPO=D.parent/'polar-rl-train';DEST=REPO/'history/evidence'/D.name
ID='e1-curb20-full-prefix-regression-reviewed-and-independent-slope5-deployed'

def g(*args):
 p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()

def known_refs():
 tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());known={}
 for p in (REPO/'history/evidence').rglob('REPORT_CAPTURE_INDEX.json'):
  v=json.loads(p.read_bytes())
  for group in ('entries','reports_and_implementation','reports','report_entries'):
   for r in v.get(group,[]):
    gp=r.get('Git_path');sha=r.get('sha256');ah=r.get('archived_sha256')
    if gp and sha and ah and gp in tracked and (REPO/gp).is_file() and H((REPO/gp).read_bytes())==ah:known[sha]=r
 return known

def capture(dest):
 assert not dest.exists();dest.mkdir(parents=True);known=known_refs();entries=[];files=[]
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 for scope in (P,D):
  for p in sorted(scope.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   raw=p.read_bytes();h=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h)
   if p.suffix.lower() in ('.npz','.npy','.pt','.pth','.usd','.zip','.partial') or len(raw)>50_000_000:
    row.update(capture='actual_large_original_index_only',original_retained=True);entries.append(row);continue
   assert p.suffix.lower() in ('.py','.md','.json','.txt','.log','.toml'),str(p)
   if h in known:
    ref=known[h];row.update(capture='existing_same_SHA_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256']);entries.append(row);continue
   clean,n=redact(raw.decode('utf8'));out=dest/scope.name/p.relative_to(scope);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(clean.encode());gp=out.relative_to(REPO).as_posix();files.append(gp)
   row.update(capture='redacted_full' if n else 'complete_exact_bytes',redactions=n,Git_path=gp,archived_bytes=out.stat().st_size,archived_sha256=H(out.read_bytes()));entries.append(row)
 for name in ('SLOPE134_PUBLISHED.json',):
  for job in json.loads((R/name).read_bytes())['jobs']:
   for kind,x in job['artifacts'].items():entries.append(dict(source_path=x['path'],bytes=x['bytes'],sha256=x['sha256'],capture='actual_remote_artifact_index_only',role=kind,original_retained=True,actual_remote_delivery_SHA_verified=True))
 ip=dest/'REPORT_CAPTURE_INDEX.json';ip.write_bytes(json.dumps(dict(epoch=time.time(),entries=entries,all_current_saved_local_reports_sources_errors_workorders_captured=True,all_original_false_and_valid_prefixes_retained=True,large_originals_index_only=True,credentials_excluded=True,poststage_reports_need_supplement=True),ensure_ascii=False,indent=2).encode());files.append(ip.relative_to(REPO).as_posix())
 return entries,files

def main():
 assert not g('status','--porcelain') and not (R/'COMPLETE133_STAGE_ARCHIVE_STARTED.json').exists()
 assert json.loads((R/'COMPLETE133_SLOPE134_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 before=g('rev-parse','HEAD');old={x.split()[2]:dict(object=x.split()[0],type=x.split()[1],peeled=g('rev-parse',x.split()[2]+'^{}')) for x in g('for-each-ref','--format=%(objectname) %(objecttype) %(refname)','refs/tags').splitlines()}
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==before
 for t,v in old.items():assert remote[t]==v['object'] and remote.get(t+'^{}',v['peeled'])==v['peeled']
 save('COMPLETE133_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=before,prior_tag_objects=old,no_replay_if_Git_objects_created=True))
 entries,files=capture(DEST)
 args=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review complete curb20 direction regression and deploy independent slope5 frozen scope','--kind','evaluation',
  '--note-file',str(R/'NEXT_E1_SLOPE5_FROZEN_AND_INDEPENDENT_WORK_ORDER.md'),'--files',*files,'--validation','All133cases complete/errorfree/twohost8JSON byteexact/fullraw180876080bytes SHA9c7a209b andfullroot30q/D0D7/contactintegral/hardware/fullsignedcircle reviewed. Ascending26/27 to22/27; descending27/27; ordinary0; five valid original-positive prefixes retained. Independentxyzw heading/prereset/wheel/contact/routeboundary diagnosis; no shorterwindow relabel or blindCURB900s/height. Negative/positive4pi8/8 and world64/64 oldskills diagnostic only; E0frozen/gateuntrained. Own389df0c fullsaveCPU102/PASSED/unique330.2590408s settled/actual3processesexit/twofcntlOSlocksfree/canonicalidle verified. Approved004 next independentSLOPE5 continuous2m ramp with mirror/198triangle rays onlyCPU; pkgf94fc989 36556260bytes285manifestSHAexact oldphysics-health-contactauditorASTexact. New134 actuallypublished to unchangedhealthy3060demandworker; actualchildren18796/17648 pending result, no4090PPO/canonicalwrite orbudgetextension. Source3643c97 selected; alloldfalse/raw/cost/readlocatorandquaternionerrors preserved. Centralcomplete133/new134CAS synced masterapprovaltracksRMcanonicalbytes unchanged; allcurrentnewreports/sources captured oractualsameSHA Gitrefs, largeoriginals indices only; future134results/contracts/admission notclaimed.','--push']
 run=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace')
 if run.returncode:
  save('COMPLETE133_STAGE_RECORD_ERROR.json',dict(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,may_have_committed_do_not_repeat_record=True));raise RuntimeError('Inspect existing Git objects; only continue original pending push')
 tag,commit=run.stdout.strip().splitlines()[-1].split();obj=g('rev-parse',tag);remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==commit and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 for t,v in old.items():assert remote[t]==v['object'] and remote.get(t+'^{}',v['peeled'])==v['peeled']
 tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked
 for row in entries:
  if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 assert not g('status','--porcelain')
 result=dict(epoch=time.time(),tag=tag,commit=commit,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,captured_new_files=len(files),existing_same_SHA_refs=sum(x['capture']=='existing_same_SHA_Git_reference' for x in entries),large_indices=sum('index_only' in x['capture'] for x in entries),all_old_tag_objects_unchanged=True,all_current_reports_index_verified=True)
 save('STAGE_GIT_RECORDED.json',result);print(json.dumps(result))

if __name__=='__main__':
 try:main()
 except BaseException:
  if not (R/'COMPLETE133_STAGE_ARCHIVE_ERROR.json').exists():save('COMPLETE133_STAGE_ARCHIVE_ERROR.json',dict(error=traceback.format_exc(),do_not_repeat_record_or_tag=True))
  raise
