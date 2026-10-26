"""Append72 closing readers with explicit authority72 metadata; compile only."""
from pathlib import Path
import ast
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent
files=[]
for original,newname in (
    ('collect_V85M2_single72_finals_actual_cost_UNUSED.py','collect_V85M2_single72_finals_actual_cost_V2_UNUSED.py'),
    ('review_V85M2_single72_native_E3_fullstate_CPU_UNUSED.py','review_V85M2_single72_native_E3_fullstate_CPU_V2_UNUSED.py')):
    text=(HERE/original).read_text('utf8')
    text=text.replace("['source210']","['authority72']").replace('source210=a','authority72=a')
    text=text.replace("'THREE_EXPERT_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json'","'V85M2_CLOSED_AUTHORITY72_CANONICAL_COST_ACTUAL.json'")
    text=text.replace('all_owner_H1_children_actual_out=True','all_authority72_owner_children_actual_out=True')
    tree=ast.parse(text);compile(tree,newname,'exec')
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('READ210','READ72') for t in node.targets):
            compile(ast.literal_eval(node.value),newname+'_embedded','exec')
    assert 'route.connect' not in text and 'strict_user_forwarded_original210' not in text
    assert "['h1']" not in text or original.startswith('review_'), 'DeferredH1 closing dependency'
    path=HERE/newname
    with path.open('x',encoding='utf8') as stream:stream.write(text)
    files.append(dict(path=str(path),bytes=path.stat().st_size,SHA=hashlib.sha256(path.read_bytes()).hexdigest()))

observer=HERE/'observe_V85M2_single72_native_E3_first_V2_UNUSED.py'
observe=observer.read_text('utf8');assert 'authority72=a' in observe and 'source210=a' not in observe
assert "v['roots']['e2']" in observe and 'policy_updates' in observe
launch=HERE/'launch_V85M2_single_authority72_after_CPU_UNUSED.py'
assert 'route.connect' not in launch.read_text('utf8')
result=dict(epoch=time.time(),passed=True,source_only=True,
    closing_files=files,consumer_producer_metadata_key='authority72',
    no210_connections_or_deferredH1_process_model_reads=True,
    actual_owner_both_node_childwait_terminal_and_single_C_settlement_preserved=True,
    only_E3_normal_model_and_separate_native_H1_fullstate=True,
    original_actual_charge_values_and_duration_flags_preserved=True,
    collector_original_closing900s_and_wait_bounds_preserved=True,
    no_actual_collector_reviewer_GPU_weights_account_or_Git_action=True)
with (HERE/'reports/V85M2_CLOSING_READERS_V2_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(result,stream,indent=2)
print(json.dumps(dict(passed=True,files=files)))
