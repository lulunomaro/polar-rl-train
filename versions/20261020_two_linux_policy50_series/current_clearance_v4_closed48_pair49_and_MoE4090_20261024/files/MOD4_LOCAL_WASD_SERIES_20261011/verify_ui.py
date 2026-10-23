"""Exercise our own GUI requests and viewer; no input injected into other apps."""
from pathlib import Path
import json,time
from drive_series import Driver

D=Path(__file__).resolve().parent
if (D/'UI_SWITCH_REVIEW.json').exists():raise RuntimeError('Already checked')
app=Driver();checks=[]
def capture(label,expected):
    with app.guard:s=dict(app.snapshot)
    ok=all(s.get(k)==v for k,v in expected.items()) and s.get('finite') is True and app.error is None
    checks.append(dict(id=label,expected=expected,actual=s,passed=ok))
app.root.after(2500,lambda:capture('initial_e0_flat',dict(model_id='e0',scene_id='flat')))
app.root.after(2800,lambda:app.request('model','terrain'))
app.root.after(5200,lambda:capture('model_switch_resets',dict(model_id='terrain',scene_id='flat')))
app.root.after(5500,lambda:app.request('scene','wave35'))
app.root.after(8200,lambda:capture('viewer_scene_rebuild',dict(model_id='terrain',scene_id='wave35')))
app.root.after(8500,lambda:app.request('reverse',True))
app.root.after(10500,lambda:capture('reverse_entry',dict(model_id='terrain',scene_id='wave35',reverse=True)))
app.root.after(10800,lambda:app.request('pause'))
app.root.after(12200,lambda:capture('pause_zero_command',dict(paused=True,command_vx=0.,command_yaw=0.)))
app.root.after(12600,app.close)
app.run()
r=dict(epoch=time.time(),id='local-actual-tk-mujoco-switch-check',checks=checks,error=app.error,all_passed=all(x['passed'] for x in checks),keys_only_own_foreground_pid=True,no_native_input_injection=True)
(D/'UI_SWITCH_REVIEW.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print([(c['id'],c['passed']) for c in checks])
assert r['all_passed'],r
