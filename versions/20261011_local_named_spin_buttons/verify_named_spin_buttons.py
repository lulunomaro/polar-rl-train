"""Actual new callbacks/control-loop check; fixture focus is isolated to this test."""
from pathlib import Path
import json,threading,time
import drive_series as mod

D=Path(__file__).resolve().parent;T=D/'NAMED_SPIN_BUTTON_CHECK';T.mkdir(exist_ok=False)
mod.D=T
focus={'active':True};mod.focused_keys=lambda:(set(),focus['active'])
app=mod.Driver(start_sim=False);app.root.update()
checks=[]
def descendants(w):
    for c in w.winfo_children():yield c;yield from descendants(c)
buttons={str(w.cget('text')):w for w in descendants(app.root) if w.winfo_class()=='TButton'}
labels=['左小陀螺 ⟲','右小陀螺 ⟳','停车 / 空格']
for label in labels:
    b=buttons[label];y=b.winfo_rooty()-app.root.winfo_rooty();assert b.winfo_ismapped() and 0<y<app.root.winfo_height()
app.thread=threading.Thread(target=app.simulate,daemon=True);app.thread.start()
def capture(id,sign):
    with app.guard:s=dict(app.snapshot)
    passed=(s.get('command_mode')==1 and s.get('command_vx')==0 and (s.get('command_yaw',0)*sign>0 if sign else s.get('command_yaw')==0))
    checks.append(dict(id=id,expected_yaw_sign=sign,actual=s,passed=passed))
app.root.after(1800,buttons[labels[0]].invoke)
app.root.after(3900,lambda:capture('left_named_button',1))
app.root.after(4300,buttons[labels[1]].invoke)
app.root.after(6500,lambda:capture('right_named_button',-1))
app.root.after(6900,buttons[labels[2]].invoke)
app.root.after(8200,lambda:capture('named_stop_button',0))
app.root.after(8500,buttons[labels[0]].invoke)
app.root.after(9100,lambda:focus.update(active=False))
app.root.after(10300,lambda:capture('lost_focus_clears_latch',0))
app.root.after(10800,app.close)
app.run()
r=dict(epoch=time.time(),id='named-local-spin-buttons-actual-control-loop',visible_labels=labels,fixture_input_focus=True,UI_callbacks_and_real_MuJoCo=True,all_passed=all(c['passed'] for c in checks),checks=checks,error=app.error,remote_mutations=0)
(D/'NAMED_SPIN_BUTTON_REVIEW.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print([(c['id'],c['passed']) for c in checks]);assert r['all_passed'] and app.error is None
