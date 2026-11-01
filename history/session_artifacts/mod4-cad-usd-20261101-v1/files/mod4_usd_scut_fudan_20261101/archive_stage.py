"""Archive this CAD/USD stage to a dedicated branch; binary artifacts remain indexed locally.
No training, simulation, source-asset overwrite, branch deletion or push is performed here.
"""
from pathlib import Path
import sys,json,hashlib,subprocess,datetime
REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');ROOT=Path(__file__).resolve().parent
BRANCH='mod4-usd-scut-fudan-20261101';REL=Path('history/session_artifacts/mod4-cad-usd-20261101-v1');DEST=REPO/REL
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact

def git(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
assert not git('status','--porcelain'),'Do not mix another working tree change'
assert git('branch','--show-current')=='lqr','Unexpected branch; stop rather than switch another task'
assert not DEST.exists(),'Do not overwrite an earlier archive'
git('switch','-c',BRANCH);DEST.mkdir(parents=True)
roots=[Path(r'F:\RMPOLAR-RL\solidworks_mod4_mass_20261101'),ROOT]
index=[];archived=[]
binary={'.sldasm','.sldprt','.usd','.usdc','.zip','.pyc','.dll','.db','.running','.png','.jpg','.mp4','.npz','.npy','.pt','.pth','.onnx'}
for root in roots:
 for p in sorted(root.rglob('*')):
  if not p.is_file():continue
  raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest();rel=Path('files')/root.name/p.relative_to(root)
  item={'source_path':str(p),'bytes':len(raw),'source_sha256':h,'archive_path':None,'archive_sha256':None}
  if p.suffix.lower() in binary or '__pycache__' in p.parts or len(raw)>50_000_000:
   item['status']='large_or_binary_original_retained_index_only'
  else:
   try:text=raw.decode('utf-8')
   except UnicodeDecodeError:item['status']='non_utf8_original_retained_index_only'
   else:
    safe,n=redact(text);data=safe.encode('utf-8') if n else raw;target=DEST/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    item.update(status='text_redacted' if n else 'complete_text',archive_path=str((REL/rel).as_posix()),archive_sha256=hashlib.sha256(data).hexdigest(),redaction_count=n);archived.append((REL/rel).as_posix())
  index.append(item)
note='''# MOD4 CAD material calibration, crash recovery and USD enhancement v1\n\nUser requested source-groundedSCUT/Fudan robustness alignment, then backgroundSolidWorks material completion and CAD mass, corrected lower-leg material tocarbon and specified6061drivetrain parts, supplied131g stripped wheel motors, asked restart afterSolidWorks crash, then explicitly requested an enhancedMOD4USD.\n\nActual operations:14CAD material files backed up/saved; original mistaken confirmation preserved before correction. SolidWorks restart restored documented376component state with14material getters and file hashes matching; separate working copy saved. Source-reader/API failures and crash-cause uncertainty preserved.\n\nUSD source:latest declaredqualified240400Nwrapperbce9a774... referencing base694e9d54..., notold20260910artifact. Independent v1 candidate repairs standalone metre/Z-up metadata, updates known motor inputs963g/131g with first-moment/parallel-axis group inertia correction, supplies matching contract andopt-in runtime adapter, retains31bodies/36joints/6physical closures/all311geometries/34colliders/limits/drives/armature/gas400. Solver fallback32/4and2.5ms agree with selected current config. No running task/frozen asset/model/canonical/reward/training was modified or started.\n\nValidation:18staticchecks pass; fullgeometry arrays, body poses, closure/limits/materialbindings and filters unchanged; group mass/COM/fullinertia matchnewcontract; positive inertias; portable single-layer asset. Configmockpass is not PhysX. No available verified localIsaac launcher was found in inspected related paths; targetPhysX/dynamic/realrobot robustness remain unverified. Nominal enhanced14.294140kg is not the freshSolidWorks16.240934kg or realmeasuredcarweight; fullgroupcalibration remains outstanding.\n\nAll saved reports/scripts/configs in the two stage folders are copied or explicitly indexed withsourceSHA. USD/ZIP/CAD binaries and generated caches remain at recordedlocalpaths, SHA/size indexed only. Earlierrawerrors and superseded reports are retained, not rewrittenpass. Branchis dedicated; lqr andmain are not push targets.\n'''
(DEST/'NOTE.md').write_text(note,encoding='utf-8')
(DEST/'SOURCE_INDEX.json').write_text(json.dumps({'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':BRANCH,'roots':list(map(str,roots)),'entries':index},ensure_ascii=False,indent=2),encoding='utf-8')
archived+=[(REL/'NOTE.md').as_posix(),(REL/'SOURCE_INDEX.json').as_posix(),(REL/'STAGE_MANIFEST.json').as_posix()]
manifest={'branch':BRANCH,'id':'mod4-cad-usd-scut-fudan-v1','title':'Archive MOD4 CAD recovery and isolated SCUT Fudan USD enhancement v1','kind':'repair','note_file':(REL/'NOTE.md').as_posix(),'files':sorted(archived),'validation':'18staticchecks PASS; configmock PASS; targetPhysX and fullcurrentCADgroup calibration NOT_RUN/pending; no training'}
(DEST/'STAGE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'branch':BRANCH,'archive_directory':str(DEST),'indexed_source_files':len(index),'archived_text_files':len(archived),'binary_or_cache_index_only':sum(x['status'].endswith('index_only') for x in index)},ensure_ascii=False,indent=2))
