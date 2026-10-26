"""Prepare exact future entry points and handoff, without connecting to any host."""
from pathlib import Path
import ast
import hashlib
import json
import time

N = Path(__file__).resolve().parent
T = N.parent
F = T / 'H1_STEP270_THREE_EXPERTS_RESOURCE_V81_20261026'
R = N / 'reports'
B = T / 'H1_STEP270_REWARD_PATH_V1_20261022'
proof = json.loads((F / 'reports/SOURCE_ONLY81_SAME_JOURNAL_LINEAGE_AND_REJECTION_CPU_ACTUAL.json').read_bytes())
assert proof['passed_source_only_CPU'] and len(proof['cases']) == 27
old = B / 'same_authorized_session_compressed_transport_v124.py'
new = B / 'same_authorized_session_compressed_transport_v125.py'
data = old.read_text('utf8')
needle = '    assert target.name in {\n'
assert data.count(needle) == 1
names = [
    'deploy_actual_three_experts81_same_V8_journal_original_writer_unused_once.py',
    'collect_three_experts81_same_V8_journal_first_PPO_finite_unused_once.py',
    'collect_actual_three81_finals_original_cost_unused_once.py',
]
addition = ''.join('        ' + repr(name) + ',\n' for name in names)
updated = data.replace(needle, needle + addition, 1)
assert updated.replace(needle + addition, needle, 1) == data
ast.parse(updated)
with new.open('x', encoding='utf8', newline='\n') as f:
    f.write(updated)
monitor = (R / 'CURRENT_ACTUAL80_THREE4090_V8_LANDING_JOURNAL_MONITOR_SOURCE.txt').read_text('utf8')
notice = '''SOURCE_ONLY81_PREPARATION_ACTUAL_NOT_INSTALLED: F=T/H1_STEP270_THREE_EXPERTS_RESOURCE_V81_20261026 now has candidate guard, byte-exact metadata2536bytes, binder/deployer/firstPPO/collector/reviewer sources only. Read F/reports/SOURCE_ONLY81_SAME_V8_EXACT_JOURNAL_PROTOCOL_PREPARED_ACTUAL.json and SOURCE_ONLY81_SAME_JOURNAL_LINEAGE_AND_REJECTION_CPU_ACTUAL.json.27 source/text-lineage and rejection fixtures passed; they are not source80 model closure, actual81 installedSDK/GO or skill evidence. No81 payload/controller/model/Task/GO/fee. Before any binding, complete80 threeFINAL/fullCPU/originalwriter cost/allout and inspect its new journal evidence; do not blindly run identical windows or infer reward changes from a censored first case. Only if same-V8 continuation remains appropriate, use F/bind_complete80_sources_same_V8_exact_journal_unused_once.py once. It inherits original V8/trace/counter/sampling checker/journal/auth/reference bytes, changes root guard role only and exact E3 savedAdam assertion. New guard handles journal's historical pre-migration base links while requiring every current journal file exact on both old/new roots; it does not admit another journal migration, addedPython or metadata newline normalization. Fresh actual target SDK/RSL/fullsourceCPU/resources/originalvalid_ready remain required. New transport125 only adds the exact81 deployer/firstPPO/collector basenames to124, does not change credentials/pins/finite protocol, and has not been run. Current80 collector may continue using124 unchanged. All current80 once remain consumed/unused exactly as above. Source-only81 preparation is an ordinary80 supplement, not a new trial/tag or training authorization. Existing actual80 unique tag objectbe1fe04421965cd0cf97a02d8740807177bb3f8b, peeled d90e500f36d55a02565e6bc48035b3a9871c04a8 is consumed; protect all1452old objects/peels. New ordinary actual Git tool receipt wins over the prior pending wording. PostGit only conversation, no report chasingHEAD. Healthy unchanged/pending remains DONT_NOTIFY.'''
source = R / 'CURRENT_ACTUAL80_THREE4090_V8_JOURNAL_AND_SOURCE_ONLY81_MONITOR_SOURCE_V2.txt'
with source.open('x', encoding='utf8') as f:
    f.write(monitor + '\n\n' + notice)
with (R / 'SOURCE_ONLY81_TRANSPORT125_AND_MONITOR_V2_PREPARED_ACTUAL.json').open('x', encoding='utf8') as f:
    json.dump(dict(epoch=time.time(), exact_added_basenames=names, previous_wrapper_SHA=hashlib.sha256(old.read_bytes()).hexdigest(), new_wrapper_SHA=hashlib.sha256(new.read_bytes()).hexdigest(), wrapper_other_bytes_unchanged=True, wrapper_not_executed=True, no_remote_query_or_current80_mutation=True, monitor_source=str(source), next_stage_model_SHA_Adam_closing_not_assigned=True), f, indent=2)
print(json.dumps(dict(source_only81_transport_monitor_prepared=True, no_remote_action=True)))
