"""Freeze inventory/auth/native-admission evidence; staged training source remains next phase."""
from pathlib import Path
import subprocess,hashlib,json,sys,datetime,os
ROOT=Path(__file__).resolve().parent;REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');REL=Path('history/experiments/mod4v1_native_phase1_sources');D=REPO/REL
BRANCH='mod4v1-experts-fulldr-rm70';sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact

def git(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
def sha(b):return hashlib.sha256(b).hexdigest()
assert not git('status','--porcelain'),'Do not mix other changes'
assert git('branch','--show-current')=='mod4-usd-scut-fudan-20261101'
assert not D.exists();git('switch','-c',BRANCH);D.mkdir(parents=True)
files=[];entries=[]
source_files=[p for p in ROOT.rglob('*') if p.is_file() and 'staged_sources' not in p.relative_to(ROOT).parts]
source_files +=[Path(r'C:\Users\lulu\Desktop\claude\mjcf\AGENTS.md')]
for p in sorted(source_files,key=str):
 raw=p.read_bytes();relative=Path('task')/p.relative_to(ROOT) if p.is_relative_to(ROOT) else Path('project_AGENTS.md')
 item={'source_path':str(p),'bytes':len(raw),'source_sha256':sha(raw)}
 if p.suffix.lower() in {'.usd','.usdc','.zip','.pyc','.pt','.pth','.npz','.npy'} or '__pycache__' in p.parts:
  item['status']='binary_or_cache_index_only'
 else:
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:item['status']='non_utf8_index_only'
  else:
   safe,n=redact(text);data=safe.encode('utf-8') if n else raw;dest=D/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);item.update(status='text_redacted' if n else 'complete_text',redactions=n,archive_path=(REL/relative).as_posix(),archive_sha256=sha(data));files.append((REL/relative).as_posix())
 entries.append(item)
(D/'.gitattributes').write_text('* -text\n',encoding='utf-8')
(D/'SOURCE_INDEX.json').write_text(json.dumps({'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entries':entries,'pending_next_phase':'staged_sources under active child derivation, additional source-generation errors and all later native/fullDR/training outputs must be appended separately'},ensure_ascii=False,indent=2),encoding='utf-8')
note='''# MOD4v1 all-expert fullDR/RM70 phase1: inventory and real native admission\n\nHuman requests all frozen experts normalized to the newly generated MOD4v1, plus two genuinely free GPUs and W25 enteringRM70. User explicitly confirmed W25=W35/E1_WAVE35. TargetrootUSD2c421a8e.../contractbae3203a..., notoldbce9/source694e assets. Selected400N50 formals E0/W35/E2/E3 bound by frozen source manifests/CPU/index; W35 latest32481SHA2d0bc7b8. Historical H1/curb/slope lineages remain provenance joins, not silently discarded or declared completed.\n\nActual resource/auth attempts: initialF SSH helper failed missingMOD4_SSH_PASSWORD; user-env same name absent. Existing authorized project provider plus pinnedconnect72 was reused in process memory, no secret output/storage or credential-store search. Project Python314 supports its exact bound compressed-session reader;3.12 runtimes lacked it. Another original project Linux endpoint timed out; local5070Ti laptop was not claimed a free4090. Actual72 GPU0 free, GPU1 occupied; transient both-free snapshot did not imply reservation. Canonical17MB read was initiallysizebounded then parsed in place: finite original2268000s, remaining386875.298s at23:17, reserve86412.861s; no canonical copied/written or budget added.\n\nNative attempts preserved: v1ParamikoSFTP mode x failed before parent/SDK; local inline builder had PowerShell quoting ParserError; newv2 fixed wx and actualSDK SimulationCfg.physics name (old companion mock usedphysx). v2pair parent failed busy private lock with0children/SDK. v3NEWGPU0-only model-free property probe used privateEX plus shared finite-environment lease; no sourcePT/NN/PPO or ledger writes, did not touch busyGPU1. Existing production writer remained unchanged; inherited RESOURCE_ACTUAL canonical_before=null is template text, not aCNone admission.\n\nACTUAL v3PASS: parent1415803, worker1415813, CUDA UUID16828...,31bodies/30coordinates/6spherical physical closures, pinnednewasset andnewcontract. Native mass/COM errors0 in authoredfloat32; finite rawinertia/poses;8physicssteps at2.5ms. Initial maxclosure~0.268mm/final~0.266mm are tiny-window observations, not locomotion/robustness graduation. OriginalApp.close bridge + actualwaitRC0, allownchildrenwaited, private lock release, errors[]; no post-close marker invented. Targetnominalimport PASS is NOT fullDR restore, expertadaptation, fullcurrentCADgroupcalibration orrealrobotpass.\n\nNewFreshDR guard and16NumPy API-double tests: checks sourceidentity/caches and wraps ONE originalreset without extra physics/random/setter/PTopens. Source inspection showed oldrestore already captures constructor nominals and restores RNG/delta, not a known oldmass overwrite bug. D6 remains gasdamping scope, not hardware-widejointfriction. SourceW35 derivation is still in progress, excluded explicitly until nextphase freeze; its V1/mimic.05 andGBKreadererror remain pending append. No expert training/adaptation/skill is claimed. RootAGENTS captures human model-version/alias/budget/save invariants for coordination, no frozen source overwritten.\n'''
(D/'NOTE.md').write_text(note,encoding='utf-8')
files +=[(REL/n).as_posix() for n in ('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
manifest={'branch':BRANCH,'id':'mod4v1-experts-native-phase1','title':'Record MOD4v1 all-expert inventory and actual GPU0 native admission','note_file':(REL/'NOTE.md').as_posix(),'files':files,'validation':'Targetnative31bodies/30coordinates/6closures/8steps PASS;16API-double tests only; fullDR/expert adaptation NOT_RUN; failures retained; no model/PPO/budget writes'}
p=D/'ARCHIVE_MANIFEST.json';files.append((REL/p.name).as_posix());p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
import record_experiment
sys.argv=['record_experiment.py','--id',manifest['id'],'--title',manifest['title'],'--kind','diagnostic','--note-file',str(REPO/manifest['note_file']),'--validation',manifest['validation'],'--files',*files]
record_experiment.main()
print(json.dumps({'branch':BRANCH,'source_entries':len(entries),'archive_text_files':len(files),'commit':git('rev-parse','HEAD'),'status':git('status','--porcelain')},ensure_ascii=False,indent=2))
