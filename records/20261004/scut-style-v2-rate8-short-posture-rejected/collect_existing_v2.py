"""Read only the existing v2 controller and landed reports. Never launch probes."""
import json, shlex, sys
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
code=r'''import json,os,sys,time
from pathlib import Path
C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004');P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
sys.path.insert(0,str(C));import supervise_scut_style_continue_v2 as v
read=v.read
state=read(C/'reports/SCUT_STYLE_V2_STATE.json');status=read(P/'status.json')
launch=read(C/'reports/SCUT_STYLE_V2_LAUNCHED.json');guard=read(C/'reports/SCUT_STYLE_V2_GUARDIAN_STARTED.json')
parent=v.helpers.identity(launch['pid']);guardian=v.helpers.identity(guard['pid'])
planned_stop=state['phase']=='repair_hold' or status['stage']=='finished'
if not planned_stop:
    assert parent and parent['start_ticks']==launch['start_ticks'] and guardian and guardian['start_ticks']==guard['start_ticks']
    assert os.getsid(parent['pid'])==parent['pid'] and os.getsid(guardian['pid'])==guardian['pid']
else:
    assert not v.base.budget_state()['active_segment'] and not v.base.trainers()
landed={};review={}
for p in sorted((P/'reports').glob('auto_007*_scut_style_v2*.json')):
    raw=read(p);landed[p.name]=raw
    if p.name.endswith('_flat.json') or '_flat_' in p.name:
        result=v.assess_flat(raw);review[p.name]=dict(kind='flat',versioned_pass=result['pass_'],original_pass=result['prior_original_flat_admission']['eligible_for_mild_dr_trial'],severe_veto_pass=v.ctl.safety_veto(raw))
    elif p.name.endswith('_rate.json') or '_spin_' in p.name:
        result=v.assess(raw);review[p.name]=dict(kind='spin',versioned_pass=result['pass_'],original_mesh_pass=raw.get('spin_skill_pass'),legacy_pass=raw.get('spin_skill_pass_legacy_reference'),severe_veto_pass=v.ctl.safety_veto(raw))
budget=v.base.budget_state();active=budget.get('active_segment');tail=max(0,time.time()-active['accounted_through_epoch']) if active else 0
print(json.dumps(dict(epoch=time.time(),state=state,status=status,parent=parent,guardian=guardian,
    processes={k:v.helpers.identity(status.get(k+'_pid')) for k in ('training','evaluation','validation')},
    budget=dict(authorized=budget['authorized_training_seconds'],charged=budget['charged_training_seconds'],active_segment=active,remaining_effective_s=max(0,budget['remaining_training_seconds']-tail)),
    existing_report_review=review,landed_reports=landed,read_only=True)))'''
c=connect()
try:
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40)
    raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err+raw
    x=json.loads(raw);landed=x.pop('landed_reports');dest=D/'existing_reports';dest.mkdir(exist_ok=True)
    for name,r in landed.items():(dest/name).write_text(json.dumps(r,indent=2),encoding='utf8')
    (D/'LATEST_EXISTING_V2.json').write_text(json.dumps(x,indent=2),encoding='utf8')
    print(json.dumps(dict(phase=x['state']['phase'],cap=x['state'].get('cap',6),processes=x['processes'],budget=x['budget'],existing_report_review=x['existing_report_review']),ensure_ascii=False))
finally:c.close()
