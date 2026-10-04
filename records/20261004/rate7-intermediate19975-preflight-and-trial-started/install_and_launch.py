"""One guarded install from verified planned hold; no migration accounting."""
import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
D=Path(__file__).resolve().parent
C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004')
sys.path.append(str(C))
import supervise_rate7_transition as t
from transition7_policy import validate_context
receipt=D/'INSTALL_AND_LAUNCH.json'
assert not receipt.exists(),'Never repeat one-shot install/launch'
prep=json.loads((D/'PREPARED.json').read_text());cpu=json.loads((D/'CPU_TARGET.json').read_text())
assert cpu['pass_'] and cpu['CPU_contracts']==prep['CPU_contracts'];validate_context(prep['context'])
for name,digest in prep['files'].items():assert hashlib.sha256((D/name).read_bytes()).hexdigest()==digest
t.ctl.S=t.read(t.ctl.STATE_PATH);t.ctl.idle();t.repair.verify()
t.helpers.acquire(t.P/'autonomy_controller.lock');t.helpers.acquire(t.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
t.ctl.S=t.read(t.ctl.STATE_PATH);t.ctl.idle();t.repair.verify()
assert not t.J.exists() and t.read(t.prior.J)['phase']=='repair_hold'
assert t.ctl.S['mature']==prep['context']['mature'] and t.ctl.S['chosen_checkpoint']==prep['context']['checkpoint']['path']
assert t.base.checkpoint(Path(t.ctl.S['chosen_checkpoint']))==prep['context']['checkpoint']
assert not t.ctl.S.get('active_training') and t.rate.current_limit()==6.
assert t.read(t.R/'SOURCE_FREEZE.json')==prep['old_candidate_freeze']
b0=t.ctl.CANONICAL.read_bytes();s0=t.ctl.STATE_PATH.read_bytes()
for name in ['supervise_rate7_transition.py','transition7_policy.py']:
    assert not (C/name).exists()
assert not (t.R/'RATE7_TRANSITION_PREPARED.json').exists()
t.base.atomic_json(receipt,dict(stage='installing',epoch=time.time(),source=prep['context']['checkpoint'],same_canonical=True,budget_added=False))
t.base.atomic_json(t.R/'SOURCE_FREEZE_BEFORE_RATE7_TRANSITION.json',prep['old_candidate_freeze'])
freeze=json.loads(json.dumps(prep['old_candidate_freeze']))
for name in ['supervise_rate7_transition.py','transition7_policy.py']:
    shutil.copyfile(D/name,C/name);freeze['sha256'][name]=prep['files'][name]
t.base.atomic_json(t.R/'SOURCE_FREEZE.json',freeze)
t.base.atomic_json(t.R/'RATE7_TRANSITION_PREPARED.json',prep)
t.repair.verify()
assert b0==t.ctl.CANONICAL.read_bytes() and s0==t.ctl.STATE_PATH.read_bytes()
t.base.atomic_json(receipt,dict(stage='installed_no_PPO',epoch=time.time(),source=prep['context']['checkpoint'],
    original134_sources_unchanged=True,candidate_source_count=len(freeze['sha256']),whole_ledger_bytes_exact=True,state_bytes_exact=True))
# The new controller must acquire these same real locks, rather than inherit
# the installer owner. Release only our descriptors before dispatching it.
for handle in t.helpers.LOCKS:handle.close()
with (C/'supervisor_rate7_transition.log').open('x') as log:
    p=subprocess.Popen([t.base.PY,str(C/'supervise_rate7_transition.py')],cwd=t.P,
        stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
identity=t.helpers.identity(p.pid);assert identity and identity['cwd']==str(t.P)
launched=dict(stage='launched',parent=identity,source=prep['context']['checkpoint'],epoch=time.time(),
    entry_sha256=prep['files']['supervise_rate7_transition.py'],candidate_source_count=len(freeze['sha256']),
    budget_added=False,CPU_contracts=cpu['CPU_contracts'],new_trial_not_yet_claimed=True)
t.base.atomic_json(t.R/'RATE7_TRANSITION_LAUNCHED.json',launched);t.base.atomic_json(receipt,launched)
print(json.dumps(launched))
