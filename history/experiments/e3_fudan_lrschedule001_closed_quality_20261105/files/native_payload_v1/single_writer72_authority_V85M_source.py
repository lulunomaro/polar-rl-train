"""Source-only72 authority adapter; never creates/copies/initializes a ledger."""
from pathlib import Path
import hashlib
import json
import math
import re

STATE=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026')
CANONICAL=STATE/'TRAINING_BUDGET_10H.json'
LOCKS=(STATE/'native_floor_supervisor.lock',STATE/'autonomy_controller.lock')
AUTHORIZATION=STATE/'HUMAN_TEMPORARY_UNLIMITED_AUTHORIZATION_ACTUAL.json'
HANDOFF=STATE/'AUTHORITY_HANDOFF_ACTUAL.json'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
MODE='temporary_unlimited_until_single4090_returns'
FINITE_MODE='finite_original_limits_restored_after_single4090_return'
RESTORATION=STATE/'BUDGET_LIMITS_RESTORED_ACTUAL.json'
AUTH_SHA='fc029e1ec254bf64b86a0428be6695a564c23fbc67794daaea0b13b6adcd04cf'
OLD_SHA='fa47cf989898d9c771f35dcaa1e25330456694fda044502aaf82a5887b205bb1'
HISTORICAL_CHARGED=1672743.1759386063
HISTORICAL_REMAINING=595256.8240613937


def validate_authority_handoff(handoff,authorization_SHA):
    assert authorization_SHA==AUTH_SHA and handoff['authorization_file_SHA256']==AUTH_SHA
    assert handoff['schema']=='mod4.single_writer72.authority_handoff.v1'
    assert handoff['authority_generation']==GENERATION and handoff['authority_host']=='72'
    assert handoff['activated'] is True and handoff['approved'] is True and handoff['old_authority_retired'] is True
    assert handoff['canonical_path']==str(CANONICAL)
    assert handoff['owner_locks']==[str(path) for path in LOCKS]
    assert handoff['canonical_copied'] is False and handoff['historical_records_reconstructed'] is False
    assert handoff['old_canonical_SHA256']==OLD_SHA
    assert handoff['known_last_settled_run_id']=='THREE4090_EXPERT_ORIGINAL_1792994651814636100'
    assert handoff['latest_original_owner_allout'] is True and handoff['latest_original_active_segment'] is None
    assert re.fullmatch('[0-9a-f]{64}',handoff['seed_canonical_SHA256'])
    assert handoff['budget_mode']==MODE
    return True


def read_authority():
    raw=AUTHORIZATION.read_bytes();handoff=json.loads(HANDOFF.read_bytes())
    validate_authority_handoff(handoff,hashlib.sha256(raw).hexdigest())
    return handoff


def validate_tracking_schema(c,handoff):
    assert c['authority_generation']==GENERATION
    assert c.get('budget_mode',c.get('mode')) in (MODE,FINITE_MODE)
    if c.get('budget_mode',c.get('mode'))==MODE:assert c['active_spending_cap_seconds'] is None
    assert c['authorized_training_seconds']==2268000
    assert c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[]
    assert c.get('budget_extensions',[])==[], 'Do not synthesize nine old extension objects'
    assert c['historical_charged_training_seconds']==HISTORICAL_CHARGED
    assert isinstance(c['completed_segments'],list)
    for key in ('charged_training_seconds','remaining_training_seconds'):
        assert isinstance(c[key],(int,float)) and not isinstance(c[key],bool) and math.isfinite(c[key])
    assert c['charged_training_seconds']>=HISTORICAL_CHARGED-1e-5
    assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-2268000)<1e-5
    # Negative tracking remainder is truthful tracking, not an unlimited-mode GO limit.
    assert handoff['authority_generation']==c['authority_generation']
    return True


def authority_tracking_schema_admitted(c):
    return validate_tracking_schema(c,read_authority())


def authority_original_extension_count(c):
    authority_tracking_schema_admitted(c)
    return c['historical_budget_extension_count']+len(c['new_authority_budget_extensions'])


def authority_budget_GO_allowed(c):
    handoff=read_authority();validate_tracking_schema(c,handoff)
    if c.get('budget_mode',c.get('mode'))==FINITE_MODE:
        receipt=json.loads(RESTORATION.read_bytes())
        assert receipt['approved'] is True and receipt['limits_restored'] is True
        assert receipt['authority_generation']==GENERATION and receipt['single4090_returned'] is True
        assert receipt['budget_mode']==FINITE_MODE and receipt['minimum_remaining_seconds']==86412.86069250107
        return c['remaining_training_seconds']>86412.86069250107
    assert not RESTORATION.exists(), 'Finite restoration receipt blocks stale unlimited GO'
    assert handoff.get('single4090_returned',False) is False and handoff.get('temporary_unlimited_ended',False) is False
    # Explicit human mode overrides only the numeric spending cap. No Infinity,
    # fake extension, refund, cost clamp, second writer, or old210 fallback.
    return True
