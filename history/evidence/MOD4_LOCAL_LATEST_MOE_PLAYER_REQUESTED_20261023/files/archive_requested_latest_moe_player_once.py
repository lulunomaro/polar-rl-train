"""One unique requested player deployment record; CPU/local files only."""
from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';G=W/'polar-rl-train';DEST=G/'history/evidence'/B.name
ID='latest-complete-moe-native-clocks-local-player';TAG='trial-20261023-'+ID;BASE='9dda825a35f624c5412b2c57a602ad6ddc7bdc67'
H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*a):
 p=subprocess.run(['git','-C',str(G),*a],capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').strip()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert not (R/'UNIQUE_RECORD_STARTED_ACTUAL.json').exists();assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists()
 export=json.loads((R/'LATEST_COMPLETE_MOE_EXPORT_PLAYER_BUILD_CPU_ACTUAL.json').read_bytes());smoke=json.loads((R/'LATEST_MOE_LOCAL_PLAYER_CLOCK_AND_MUJOCO_CPU_ACTUAL.json').read_bytes());live=json.loads((R/'REQUESTED_PLAYER_MISSING_ONLY_LIVE_WINDOW_READBACK_ACTUAL.json').read_text('utf-8-sig'));assert export['passed'] and smoke['passed'] and live['passed'] and live['window_handle']
 old=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(old.splitlines())==1427
 put(R/'UNIQUE_RECORD_STARTED_ACTUAL.json',dict(epoch=time.time(),base_HEAD=BASE,tag=TAG,no_old_record_or_training_replay=True))
 note='Human requested the latest complete MoE wheeled-leg policy in the local interactive player. Exported pinned H1 pair47 Adam745740/4fb8e475, E2 cohort52 Adam839920/67895d10, E3 pair47 Adam808520/2e3362ca, plus unchanged gate148 E0/W35. CPU ONNX parity700 rows max5.245208740234375e-06 <=1e-4; whole six-action routing. H1/normal100Hz and E2/E3 native50Hz sample-and-hold verified, four modes30 MuJoCo controls each finite. Existing RM7v7 map/assets/camera/status fixes retained in a separate copy. Public J forward command .8m/s during existing .8-second request; no scripted actions/forces. Original env import error, launch run-directory race, missing-only original live window verification and PowerShell preview-null wording all retained. Live actual pid/window/finite snapshots prove the requested player opened, not skill graduation. Source checkpoints and assets indexed from producer receipts; no training/GPU/remote/budget changes or active48 intermediate model use.'
 (B/'STAGE_NOTE.md').write_text(note+'\n',encoding='utf8');(B/'TAG_NOTE.txt').write_text(note+'\n',encoding='utf8')
 sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);entries=[];files=[];known={};binary=[]
 portable=W/'MOD4_LATEST_HYBRID_MOE_PACKAGE_20261020/delivery/MOD4_HybridMoE_20261020/PACKAGE_MANIFEST.json';pm=json.loads(portable.read_bytes());assetSHA={x['path']:x for x in pm['files']}
 for p in sorted(B.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  rel=p.relative_to(B).as_posix();st=p.stat()
  if p.suffix.lower() in ('.onnx','.pt','.npz','.stl','.mesh','.bin','.png','.mjb','.zip','.lock'):
   ref=assetSHA.get(rel);digest=export['manifest']['onnx_SHA'] if rel=='policy/hybrid_moe.onnx' else ref.get('SHA') if ref else None
   binary.append(dict(path=str(p),bytes=st.st_size,SHA=digest,SHA_kind='existing producer' if digest else 'unknown; no archive rehash',original_retained=True));continue
  raw=p.read_bytes();text=raw.decode('utf8-sig') if raw.startswith(b'\xef\xbb\xbf') else raw.decode('utf8');clean,n=redact(text);data=clean.encode('utf8') if n else raw;sha=H(raw)
  if sha in known:entries.append(dict(path=str(p),bytes=len(raw),SHA=sha,**known[sha]));continue
  q=DEST/'files'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data);target=q.relative_to(G).as_posix();row=dict(path=str(p),bytes=len(raw),SHA=sha,archive=target,archive_SHA=H(data),redactions=n,capture_epoch=time.time(),mode='redacted' if n else 'full',original_retained=True);entries.append(row);known[sha]={k:row[k] for k in ('archive','archive_SHA','mode')};files.append(target)
 index=dict(epoch=time.time(),entries=entries,source_checkpoints=export['manifest']['sources'],binary_artifacts=binary,all_reports_errors_full_sources_and_window_snapshot=True,live_player_logs_are_capture_time_snapshots=True,original1427_tags=old,no_PT_raw_or_asset_rehash_for_Git=True)
 q=DEST/'REPORT_CAPTURE_INDEX.json';q.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf8');files.append(q.relative_to(G).as_posix())
 rec=importlib.import_module('record_experiment')
 def rg(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(B/'TAG_NOTE.txt'))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=rg;sys.argv=['record_experiment.py','--id',ID,'--title','Deliver requested latest complete MoE player with native expert clocks','--kind','deployment','--note-file',str(B/'STAGE_NOTE.md'),'--files',*files,'--validation',note,'--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for line in old.splitlines():
  a=line.split();assert remote[a[0]]==a[1]
  if len(a)>2:assert remote[a[0]+'^{}']==a[2]
 for row in entries:assert H(subprocess.run(['git','-C',str(G),'show',head+':'+row['archive']],capture_output=True,check=True).stdout)==row['archive_SHA']
 assert not git('status','--porcelain') and len(git('tag','--list').splitlines())==1428
 print(json.dumps(dict(remote_main=head,tag=TAG,tag_object=obj,peeled=head,old1427_objects_peels_unchanged=True,total_tags=1428,full_text_references=len(entries),new_Git_files=len(files),no_remote_training_or_budget_change=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('UNIQUE_RECORD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True));raise
