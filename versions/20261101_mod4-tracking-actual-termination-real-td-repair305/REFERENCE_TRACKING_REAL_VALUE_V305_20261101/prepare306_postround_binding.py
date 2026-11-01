"""Bind actual305 and set sole local afterround306 evaluation/replay workflow."""
from pathlib import Path
import ast,hashlib,importlib.util,json,re,time
from datetime import datetime,timezone,timedelta
N=Path(__file__).resolve().parent;T=N.parent;O=T/'REFERENCE_TRACKING_BPTT_V300_20261101';R=N/'reports';P=N/'postround306';P.mkdir(exist_ok=False)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(s.encode())
 ast.parse(s,filename=str(p))
def change(s):
 keep=[]
 def h(m):keep.append(m.group());return'@HASH'+str(len(keep)-1)+'@'
 s=re.sub(r'\b[0-9a-f]{64}\b',h,s)
 for old,new in(('300','305'),('303','306')):s=re.sub(r'(?<=[A-Za-z_])'+old+r'(?!\d)',new,s)
 for i,v in enumerate(keep):s=s.replace('@HASH'+str(i)+'@',v)
 return s
snapshot=json.loads((R/'ROOT305_STATUS_FIRST_UPDATED.json').read_bytes());files={Path(x['path']).name:json.loads(x['UTF8'])for x in snapshot['full_selected_UTF8']}
task=json.loads((N/'TASK305_FROZEN.json').read_bytes());go=files['GO_PRODUCTION.json'];first=files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT305_UPDATE.json']
spec=importlib.util.spec_from_file_location('p305',N/'teacher_task305.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.validate_first(first,task,go)
assert not any(n in files for n in('ORIGINAL_ERROR.json','NODE_ORIGINAL_ERROR.json','OWNER_ORIGINAL_ERROR.json'))
put(R/'ROOT305_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json',dict(epoch=time.time(),passed=True,run_id=task['run_id'],current=files['OWNER_CURRENT.json'],canonical_None=False,files=files,first=first,actual_paired_H32=files['ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json'],source_snapshot=str(R/'ROOT305_STATUS_FIRST_UPDATED.json'),model_reads=0,exact_original_owner=json.loads((R/'ROOT305_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').read_bytes())['owner']))
for p in(O/'postround303').rglob('*.py'):
 s=change(p.read_text('utf8'))
 if p.name=='run303_eval_once_template.py':
  s=s.replace(".replace('246','303')",".replace('246','306')")
  s=s.replace("patterns='", "patterns='collect300_|launch300_|run303_eval|postround303_finalize|",1)
 if p.name=='view303_actual_final300_replay_template.py':
  s=s.replace("r['result']['kind']=='heldout270'", "r['result']['kind']=='reference270'")
  s=s.replace("helptext='1 stairs | 2 standing | 3 forward | 4 reverse", "helptext='1 env1 | 2 env0 | 3 env10 | 4 env20")
  s=s.replace("i>=max(0,r['controls']-2)","i>=min(max(0,r['controls']-2),15)")
 write(P/change(str(p.relative_to(O/'postround303'))),s)
s=change((O/'postround303_finalize300_replay_eval_once.py').read_text('utf8'))
s=s.replace("INDEX306_POSTROUND_FOR305_FROZEN.json","INDEX306_POSTROUND_FOR305_FROZEN.json")
s=s.replace("INDEX306_POSTROUND_FOR300_FROZEN.json","INDEX306_POSTROUND_FOR305_FROZEN.json")
s=s.replace("N/'INDEX303_POSTROUND_FOR305_FROZEN.json'", "N/'INDEX306_POSTROUND_FOR305_FROZEN.json'")
# A finite recorded-frame render completes even if the interactive window is
# closed early; no new modelread or physics replay.
needle="    decision='Review reference tracking errors"
insertion="""    render_source=(T/'TRACKING300_FAILURE_DIAGNOSIS_V304_20261101/render304_recorded303_frames.py').read_text('utf8')
    render_source=render_source.replace('REFERENCE_TRACKING300_POSTROUND_EVAL_V303_20261101','REFERENCE_TRACKING305_POSTROUND_EVAL_V306_20261101').replace('view303_actual_final300_replay.py','view306_actual_final305_replay.py')
    render_source=render_source.replace('VISIBLE_REPLAY303','VISIBLE_REPLAY306').replace('VIEW303','VIEW306').replace('FINAL300','FINAL305')
    render_source=render_source.replace('ACTUAL303','ACTUAL306').replace('RECORDED303','RECORDED306').replace('recorded303','recorded306').replace('final300','final305')
    renderer=E/'render306_recorded_frames.py';renderer.write_bytes(render_source.encode())
    put('POSTROUND305_NATIVE_RECORDED_FRAMES_RETURNED.json',call(CONTROL,[renderer]))
"""
assert needle in s;s=s.replace(needle,insertion+needle)
script=N/'postround306_finalize305_replay_eval_once.py';write(script,s)
# Validate exact generated remote parent without executing any SDK/model.
tree=ast.parse((P/'run306_eval_once_template.py').read_text('utf8'));main=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='main');env={'T':T}
for stmt in main.body:
 if isinstance(stmt,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='parent'for x in stmt.targets):exec(compile(ast.Module(body=[stmt],type_ignores=[]),'<parent306>','exec'),env)
parent=env['parent'];ast.parse(parent)
assert 'from contract306 import'in parent and "str(P/'source/evaluate306.py')"in parent and 'RESULT306.json'in parent
assert "q.suffix in ('.py','.json','.npz')"in parent
assert "REFERENCE_TRACKING_BPTT305_COMPLETE"in(P/'eval306_source/evaluate306.py').read_text('utf8')
assert "r['result']['kind']=='reference270'"in(P/'view306_actual_final305_replay_template.py').read_text('utf8')
filesforindex=[script,*sorted(P.rglob('*.py'))]
index=N/'INDEX306_POSTROUND_FOR305_FROZEN.json';put(index,dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in filesforindex]))
put(R/'SOURCE306_POSTROUND305_VALIDATED.json',dict(epoch=time.time(),passed=True,original305normalCPUcontracts=True,new306independent80firstepisodes=True,seed9137=True,samefixedreferencecourse=True,parentworkercontract306=True,viewerplatformreference270visible=True,nativeframefinitecapture=True,model_reads=0,SDK=0,GO=0))
tz=timezone(timedelta(hours=8));fmt=lambda x:datetime.fromtimestamp(x,tz).isoformat()
put(R/'CURRENT_ACTUAL305_REPAIR_WORK_ORDER.json',dict(epoch=time.time(),status='ACTUAL305_RUNNING_FIRST_UPDATE_FULLSAVE_AND_PAIRED_H32_MEASURED',run_id=task['run_id'],task=str(N/'TASK305_FROZEN.json'),binding=str(R/'ROOT305_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json'),GO=go,FIRST=first,progress=files['LATEST_PROGRESS.json'],actual_paired_H32=files['ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json'],times=dict(GO=fmt(go['learning_started_epoch']),SAVE=fmt(go['save_deadline']),NOMINAL=fmt(go['nominal_end_epoch']),normal_earliest=fmt(go['nominal_end_epoch']-900)),source300=dict(finalSHA=task['model_SHA'],Pi2593=True,WM9712=True,eval303='0of80cross/success,66orientation,14full8s; native recordedbodyframes viewed after correcting old viewer hiddenplatform'),repair='matched .75rad actualorientation surrogate, criticactualownTD+donezero+EMA.01target; clampbootstrap0..100; resumeallthreeAdam',postround_script=str(script),postround_index=str(index),postround_index_SHA=H(index),postround_result=str(R/'POSTROUND305_REPLAY_EVAL_DECISION.json'),eval_root=str(T/'REFERENCE_TRACKING305_POSTROUND_EVAL_V306_20261101'),next='One localtimer invokes originalnormal305/fullCPU/eval306/actualreplay; natively review results then act oncontinuation or targetedrepair within authorizedtask/funds. Do not duplicate once or hotpatch healthy source.'))
print(json.dumps(dict(passed=True,times=json.loads((R/'CURRENT_ACTUAL305_REPAIR_WORK_ORDER.json').read_bytes())['times'],script=str(script),index_SHA=H(index))))
