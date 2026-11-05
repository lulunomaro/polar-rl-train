"""Archive new manual joint/step UI and actual window evidence, not native/skill verification."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/mod4v2_joint_step_interactive_ui_20261105');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout);print(p.stderr,file=sys.stderr);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists();G('merge-base','--is-ancestor','db0ad77b70868f751b5739b8dac03fcab4fd1538','HEAD')
scene=json.loads((D/'SCENE_RECEIPT.json').read_bytes());launch=json.loads((D/'GUI_LAUNCH.json').read_bytes());window=json.loads((D/'WINDOW_VERIFICATION.json').read_text(encoding='utf-8-sig'));functional=json.loads((D/'FUNCTIONAL_CHECK.json').read_bytes());assert scene['step']['height_m']==.2 and scene['step']['collidable']is True and len(scene['joint_names'])==30 and scene['source_assets_modified']is False and window['launcher_pid']==launch['pid']and window['opened_and_rendered']is True and window['render_count']==408 and window['current_state']=='CLOSED_NORMALLY_AFTER_ACTUAL_GUI_INTERACTION'and window['visible']is False and functional['passed']is True and all(functional['checks'].values())and launch['training_started']is False
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
from capture_history import redact
dest.mkdir(parents=True);files=[];rows=[]
for p in sorted(D.rglob('*')):
 rp=p.relative_to(D)
 if '__pycache__'in rp.parts:continue
 if p.suffix.lower()in('.pt','.pth','.ckpt','.npz','.npy','.usd','.usdc','.zip','.png','.jpg','.jpeg','.webp','.stl','.obj','.pyc','.pyo','.tmp','.partial','.jsonl'):
  rows.append(dict(source_path=str(p),status='binary_or_transient_skipped_before_stat_read_hash',known_sha256=window.get('capture_sha256')if p.name=='WINDOW_PREVIEW.png'else None));continue
 if not p.is_file():continue
 raw=p.read_bytes();text,n=redact(raw.decode('utf8'));data=text.encode('utf8')if n else raw;target=dest/'files'/rp;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);ar=target.relative_to(repo).as_posix();files.append(ar);rows.append(dict(source_path=str(p),original_bytes=len(raw),original_SHA256=hashlib.sha256(raw).hexdigest(),archive_path=ar,archive_bytes=len(data),archive_SHA256=hashlib.sha256(data).hexdigest(),redactions=n,status='point_in_time_live_telemetry'if p.name=='CURRENT.json'else'complete_text'))
(dest/'INDEX.json').write_text(json.dumps(dict(epoch=time.time(),rows=rows,original_asset_unchanged=True,new_training_or_native_PhysX=False,UI_lifecycle_state=window['current_state'],assistant_reopened_after_window_closed=False,live_telemetry_is_point_in_time_only=True,original_validation_redaction_hashes=True),indent=2),encoding='utf8');(dest/'.gitattributes').write_text('* -text\n',encoding='utf8');(dest/'NOTE.md').write_text((D/'README.md').read_text(encoding='utf8')+'\n\n## Actual launch evidence\n'+json.dumps(window,ensure_ascii=False,indent=2)+'\n\nThis is a manually editable real MuJoCo-rendered local GUI, not a policy performance/PhysX/physical-task pass. One own window, real200mm collision box, mechanical closed-branch mappings and all30joint controls. Originalv2 assets/models/Registry/budget untouched. Saved live telemetry is only snapshot; subsequent user edits are not automatically committed. No GUI/physics/oldonce/model rerun for Git.\n',encoding='utf8');files.extend((rel/x).as_posix()for x in('INDEX.json','.gitattributes','NOTE.md'))
old=record_experiment.git

def short_add(*a):
 if a[:2]==('add','--'):
  rp=a[2];assert rp.startswith('history/experiments/20261105-mod4v2-joint-step-interactive-ui')and set(a[3:])==set(files);result=old('add','--',rel.as_posix(),rp);assert set(old('diff','--cached','--name-only').splitlines())==set(files)|{rp};return result
 return old(*a)

record_experiment.git=short_add;trial='mod4v2-joint-step-interactive-ui';sys.argv=['record_experiment.py','--id',trial,'--title','MOD4v2 manual30joint closed-chain editor and actual200mm step GUI opened','--kind','diagnostic','--note-file',str(dest/'NOTE.md'),'--validation','actual-scene-compile31body30joint10eq-real200mm-collision-step;v2-mechanical-IK-not-v1-operating-window;actual-owned-MOD4v2-window-started408frames100seconds-then-normal-close-noerror;Windowsredirector-and-postclose-verification-failures-preserved;capture-unavailable-not-fake;hidden-isolated-controls-functional-check-pass;manual-forward-not-dynamic-skill;original-assets-models-Registry-budget-unchanged;no-training-or-native-probe;original-recordvalidation-redaction-hashes;exact2scopedstagedset-featureonly-mainreadonly','--files',*files];record_experiment.main();head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial;obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag);remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,index_entries=len(rows),actual_GUI_session_pid=window['pid'],GUI_lifecycle_state=window['current_state'],original_assets_or_models_modified=False,training_or_old_once_replayed=False,main_push_or_reset=False),indent=2))
