"""Read-only actual target admission. Imports new entry but never calls it."""
import hashlib,json,sys,time
from pathlib import Path
D=Path(__file__).resolve().parent
C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004')
sys.path.append(str(C))
import supervise_rate7_transition as t
from cpu_contracts import run
prep=json.loads((D/'PREPARED.json').read_text());context=prep['context']
for name,digest in prep['files'].items():assert hashlib.sha256((D/name).read_bytes()).hexdigest()==digest,name
before=t.ctl.CANONICAL.read_bytes();state_before=t.ctl.STATE_PATH.read_bytes()
t.ctl.S=t.read(t.ctl.STATE_PATH);t.ctl.idle();t.repair.verify()
assert not (C/'reports/RATE7_TRANSITION_STATE.json').exists()
assert t.read(t.prior.J)['phase']=='repair_hold'
assert t.ctl.S['mature']==context['mature'] and t.ctl.S['chosen_checkpoint']==context['chosen_checkpoint']
assert not t.ctl.S.get('active_training') and not t.helpers.active_processes(t.ctl.PROBES)
actual=t.base.checkpoint(Path(context['checkpoint']['path']));assert actual==context['checkpoint']
assert t.read(C/'reports/SCUT_STYLE_V2_RATE6_MATURE_ACCEPTED.json')==context['accepted6']
assert t.read(C/'reports/SOURCE_FREEZE.json')==prep['old_candidate_freeze']
b=t.base.budget_state();assert not b['active_segment'] and b['authorized_training_seconds']==context['budget']['authorized']
assert b['charged_training_seconds']==context['budget']['charged'] and b['remaining_training_seconds']==context['budget']['remaining']
assert t.rate.current_limit()==6. and t.rate.validate_limit(7.)==7. and t.rate.next_limit(6.)==7.
assert t.prior.VERSION==t.GATE_VERSION and t.prior.previous.assess is t.prior.assess
assert t.ctl.gate is t.prior.gate and t.ctl.probe is t.prior.probe and t.ctl.current_decision is t.prior.decision
assert t.prior.previous.gate is t.prior.gate and t.prior.previous.pairs is t.prior.pairs
assert t.read(t.repair.CODE/'env.json')['RM_SPIN_ROLLING_PROFILE']=='v1'
tests=run(context)
assert before==t.ctl.CANONICAL.read_bytes() and state_before==t.ctl.STATE_PATH.read_bytes()
result=dict(pass_=True,CPU_contracts=tests,actual_source=actual,source_hashes_match=True,
    candidate_original_sources=len(prep['old_candidate_freeze']['sha256']),PPO_performed=False,
    acceptance_routes_verified=True,whole_ledger_bytes_exact=True,state_bytes_exact=True,epoch=time.time())
(D/'CPU_TARGET.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
