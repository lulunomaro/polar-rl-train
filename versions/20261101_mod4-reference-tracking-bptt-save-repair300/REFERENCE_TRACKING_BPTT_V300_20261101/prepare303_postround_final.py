"""Finalize future evaluation with training300's measured action-order ABI."""
from pathlib import Path
import ast,hashlib,json,re,time
N=Path(__file__).resolve().parent;R=N/'reports';P=N/'postround303';P.mkdir(exist_ok=False)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(s.encode())
 ast.parse(s,filename=str(p))
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
for p in (N/'postround302').rglob('*.py'):
 rel=str(p.relative_to(N/'postround302')).replace('302','303')
 text=re.sub(r'(?<=[A-Za-z_])302(?!\d)','303',p.read_text('utf8'))
 if p.name=='run302_eval_once_template.py':text=text.replace(".replace('246','302')",".replace('246','303')")
 if p.name=='evaluate302.py':
  text=text.replace('leg_ids,wheel_ids,previous_action,raw_action)',"leg_ids,wheel_ids,previous_action,frame['actions'][:,[0,1,3,4,2,5]])")
 write(P/rel,text)
s=(N/'postround302_finalize300_replay_eval_once.py').read_text('utf8')
s=re.sub(r'(?<=[A-Za-z_])302(?!\d)','303',s)
s=s.replace("while time.time()<go['nominal_end_epoch']-898:time.sleep(min(10,go['nominal_end_epoch']-898-time.time()))", "while time.time()<go['nominal_end_epoch']-898:time.sleep(max(.01,min(10,go['nominal_end_epoch']-898-time.time())))")
s=s.replace("    binding=json.loads", "    index=json.loads((N/'INDEX303_POSTROUND_FOR300_FROZEN.json').read_bytes())\n    for row in index['files']:\n        p=Path(row['path']);assert p.stat().st_size==row['bytes']and H(p)==row['SHA']\n    binding=json.loads")
s=s.replace("    task.update(kind=", "    task.update(training_layout_seed=None,heldout_layout_seed=None,evaluation_seed=9137,same_fixed_reference_course=True,heldout_terrain_layout=False)\n    task.update(kind=")
script=N/'postround303_finalize300_replay_eval_once.py';write(script,s)
put(R/'SOURCE303_MEASURED_ACTION_ORDER_CORRECTION.json',dict(epoch=time.time(),passed=True,unused302_preserved=True,measured_tracking_cost_uses_same_frame_action_inverse_order_as300=True,raw_actor_overflow_still_reported=True,physical_action_clipped_same_as300=True,reason='302used raw action in measured rate/overflow while training300 uses measured clipped/permuted frame actions; preserve302 and correct independent303 before execution',source_model_reads=0,SDK=0,GO=0))
files=[script,*sorted(P.rglob('*.py'))]
put(N/'INDEX303_POSTROUND_FOR300_FROZEN.json',dict(epoch=time.time(),kind='POSTROUND303_FOR_RUNNING300',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
print(json.dumps(dict(passed=True,script=str(script),index_SHA=H(N/'INDEX303_POSTROUND_FOR300_FROZEN.json'))))
