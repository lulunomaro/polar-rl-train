"""Supplement the actually finished user-requested GUI review; do not reopen it for Git."""
from pathlib import Path
import json,sys,hashlib,time,subprocess
D=Path(__file__).resolve().parent;S=D/'sessions/reopen_20261105_164916';repo=D.parent/'repo-lqr';rel=Path('history/experiments/mod4v2_joint_step_user_review_20261105');dest=repo/rel

def G(*args):
 p=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout);print(p.stderr,file=sys.stderr);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists();G('merge-base','--is-ancestor','639d6543a3002eb133c03bd85cac27b86e750389','HEAD')
start=json.loads((S/'STARTED.json').read_bytes());end=json.loads((S/'CLOSED.json').read_bytes());current=json.loads((S/'CURRENT.json').read_bytes());assert end['reason']=='window_closed'and end['render_count']==205 and end['joint_count']==30 and end['step_height_m']==.2 and end['source_asset_modified']is False and end['integration_enabled']is end['policy_or_training']is False and current=={k:v for k,v in end.items()if k!='reason'}and not(S/'ERROR.json').exists()and not(S/'GUI_STDERR.log').read_bytes()
assert set(p.name for p in S.iterdir())=={'interactive_scene.xml','GUI_STDOUT.log','GUI_STDERR.log','STARTED.json','CURRENT.json','CLOSED.json'}
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
from capture_history import redact
dest.mkdir(parents=True);rows=[];files=[]
selected=sorted(S.iterdir())+[D/'USER_REVIEW_SESSION_V1.md',Path(__file__)]
for p in selected:
 assert p.is_file()and p.suffix.lower()in('.xml','.log','.json','.md','.py');raw=p.read_bytes();text,n=redact(raw.decode('utf8'));data=text.encode('utf8')if n else raw;rp=p.relative_to(D);target=dest/'files'/rp;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);ar=target.relative_to(repo).as_posix();files.append(ar);rows.append(dict(source_path=str(p),original_bytes=len(raw),original_SHA256=hashlib.sha256(raw).hexdigest(),archive_path=ar,archive_bytes=len(data),archive_SHA256=hashlib.sha256(data).hexdigest(),redactions=n,status='complete_text'))
index=dict(epoch=time.time(),rows=rows,prior_tool_source_commit='639d6543a3002eb133c03bd85cac27b86e750389',prior_tool_source_archive='history/experiments/mod4v2_joint_step_interactive_ui_20261105/files/joint_step_viewer.py',prior_tool_source_SHA='1cfb1357e7e015aa265bb64921a0c4bead508aa41b3296124755eb0f533c8ba3',current_review_normal_closed=True,human_viewed_not_declared_engineering_acceptance=True,new_training_or_original_assets_or_Registry_changes=False,GUI_model_or_old_once_replayed_for_Git=False)
(dest/'INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf8');(dest/'.gitattributes').write_text('* -text\n',encoding='utf8');(dest/'NOTE.md').write_text((D/'USER_REVIEW_SESSION_V1.md').read_text(encoding='utf8'),encoding='utf8');files.extend((rel/x).as_posix()for x in('INDEX.json','.gitattributes','NOTE.md'))
original=record_experiment.git

def scoped(*args):
 if args[:2]==('add','--'):
  rp=args[2];assert rp.startswith('history/experiments/20261105-mod4v2-joint-step-user-review')and set(args[3:])==set(files);r=original('add','--',rel.as_posix(),rp);assert set(original('diff','--cached','--name-only').splitlines())==set(files)|{rp};return r
 return original(*args)

record_experiment.git=scoped;trial='mod4v2-joint-step-user-review';sys.argv=['record_experiment.py','--id',trial,'--title','MOD4v2 user-requested reopened joint/200mm-step GUI review; actual205frames normal close','--kind','diagnostic','--note-file',str(dest/'NOTE.md'),'--validation','actual-independent-reopen-session20261105_164916;30joints-real200mm-collision-step;actual-windowPID57612-HWND135135562observed;205renderframes-normal-closed-noerror;userfinished-review-not-engineering-graduation;complete30joint-root-gas-closure-contacts-state-and-logs-preserved;originalassets-weights-Registry-budget-unchanged;noGUI-model-physics-oldonce-replay-forGit;original-recordvalidation-redaction-hashes-exact2scopedstagedset;featureonly-mainreadonly','--files',*files];record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial;obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head;G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,complete_text_entries=len(rows),original_recorder_validation_redaction_hashes_retained=True,staged_set_verified=True,GUI_or_physics_or_model_or_old_once_replayed=False,main_push_or_reset=False),indent=2))
