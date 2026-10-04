"""Inspect exact v2 migration, supervision, receipts and one budget; no launch."""
import argparse,json,shlex,sys
from pathlib import Path
D=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
assert Path(a.name).name==a.name
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
code=r'''import json,sys,time,os
from pathlib import Path
C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004');P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
D=Path('/home/egde/rl_candidates/MOD4_SCUT_STYLE_FLAT_GATE_FIX_20261004');R=C/'reports'
sys.path.insert(0,str(C));import supervise_scut_style_continue as old
old.repair.verify();read=old.read
__import__('torch').set_num_threads(1)
def get(path):return read(path) if path.exists() else None
names=('SCUT_STYLE_V2_MIGRATION','SCUT_STYLE_V2_HANDOVER','SCUT_STYLE_V2_LAUNCHED','SCUT_STYLE_V2_GUARDIAN_STARTED','SCUT_STYLE_V2_STATE','SCUT_STYLE_V2_RATE6_MATURE_ACCEPTED')
x={n:get(R/(n+'.json')) for n in names};status=read(P/'status.json')
ident=lambda r:old.helpers.identity(r['pid']) if r else None
parent=ident(x['SCUT_STYLE_V2_LAUNCHED']);guardian=ident(x['SCUT_STYLE_V2_GUARDIAN_STARTED'])
processes={k:old.helpers.identity(status.get(k+'_pid')) for k in ('training','evaluation','validation')}
budget=old.base.budget_state();checkpoint=manifest=freeze=None
routing=None
if (C/'supervise_scut_style_continue_v2.py').exists():
    import supervise_scut_style_continue_v2 as v2
    checks=dict(flat_and_spin_gate=v2.previous.gate is v2.gate and v2.ctl.gate is v2.gate,
        single_assessment=v2.previous.decision is v2.decision and v2.ctl.current_decision is v2.decision,
        paired_regression=v2.previous.pairs is v2.pairs,
        final_assessment=v2.previous.finish is v2.finish,
        flat_UI_version=v2.previous.probe is v2.probe and v2.ctl.probe is v2.probe)
    assert all(checks.values());routing=checks
if x['SCUT_STYLE_V2_LAUNCHED']:
    assert parent and parent['start_ticks']==x['SCUT_STYLE_V2_LAUNCHED']['start_ticks']
    assert str(C/'supervise_scut_style_continue_v2.py') in parent['argv']
if guardian:assert guardian['start_ticks']==x['SCUT_STYLE_V2_GUARDIAN_STARTED']['start_ticks']
if processes['training'] and processes['training']['state']!='Z':
    pid=processes['training']['pid'];assert old.base.trainers()==[pid] and budget['active_segment']['pid']==pid
    try:
        run=old.rate.trainer_run(P/'logs',pid);saved=read(run/'latest_complete.json')
        checkpoint=old.base.checkpoint(Path(saved['checkpoint']));manifest=get(run/'run_manifest.json');freeze=get(run/'rolling_source_freeze.json')
    except AssertionError:pass
elif x['SCUT_STYLE_V2_HANDOVER']:
    checkpoint=old.base.checkpoint(Path(x['SCUT_STYLE_V2_HANDOVER']['complete_checkpoint']['path']))
def tail(path,n=2500):return path.read_text(errors='replace')[-n:] if path.is_file() else ''
prep=read(D/'PREPARED.json')
prior={k:ident(v) for k,v in prep['expected_processes'].items()}
x.update(epoch=time.time(),parent=parent,guardian=guardian,processes=processes,old_processes=prior,
    parent_session=os.getsid(parent['pid']) if parent else None,guardian_session=os.getsid(guardian['pid']) if guardian else None,
    status=status,budget=budget,active_training=read(old.ctl.STATE_PATH).get('active_training'),
    checkpoint=checkpoint,run_manifest=manifest,rolling_source_freeze=freeze,
    qualification_route_checks=routing,
    source_count=len(read(R/'SOURCE_FREEZE.json')['sha256']),all_source_hashes_match=True,
    migration_log=tail(D/'migration.log'),supervisor_log=tail(C/'supervisor_scut_style_continue_v2.log'),
    active_log_tail=tail(Path(status.get('active_log',''))),read_only=True)
print(json.dumps(x))'''
c=connect()
try:
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40)
    raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err+raw
    x=json.loads(raw);(D/a.name).write_text(json.dumps(x,indent=2),encoding='utf8')
    for n,v in x.items():
        if n.startswith('SCUT_STYLE_V2_') and v:(D/(n+'.json')).write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(migration_stage=(x['SCUT_STYLE_V2_MIGRATION'] or {}).get('stage'),
        state=x['SCUT_STYLE_V2_STATE'],parent=x['parent'],guardian=x['guardian'],processes=x['processes'],
        old_processes=x['old_processes'],source_count=x['source_count'],remaining=x['budget']['remaining_training_seconds'],
        checkpoint=x['checkpoint'],migration_log=x['migration_log'],supervisor_log=x['supervisor_log'])))
finally:c.close()
