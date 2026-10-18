"""Bind the actual human reply to one prepared ce3 finite segment; no transport."""
from pathlib import Path
import ast, hashlib, json, time, copy

B = Path(__file__).resolve().parent
E = B / 'proposal_ce3_same_candidate_finite_v1'
Q = E / 'payload/h1'
R = E / 'reports'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCE_SHA = 'ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90'
APPROVAL = R / 'HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json'
DEPLOYER = E / 'deploy_human_approved_ce3_new_native_then_one_finite1800_once.py'

def save(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

def main():
    assert not APPROVAL.exists() and not DEPLOYER.exists()
    prep = json.loads((B / 'reports/H1_CE3_NEXT_SAME_CANDIDATE_FINITE_REVIEWABLE_LOCAL_CPU_PREPARED_ACTUAL.json').read_bytes())
    assert prep['passed_LOCAL_CPU_only'] and prep['source']['SHA'] == SOURCE_SHA
    assert H(Q / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json') == prep['manifest']['SHA']
    manifest = json.loads((Q / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
    assert len(manifest['files']) == 478
    for row in manifest['files']:
        p = Q / row['relative']
        assert p.resolve().is_relative_to(Q.resolve()) and not p.is_symlink()
        assert p.stat().st_size == row['bytes'] and H(p) == row['SHA'], row['relative']
    prior = B / 'paid_mean_public4_v2'
    oldprep = json.loads((prior / 'reports/PUBLIC4_REPAIR_V2_H1_FINITE_NEW_SOURCE_NATIVE_PAYLOAD_CPU_ACTUAL.json').read_bytes())
    specs = copy.deepcopy(oldprep['specs'])
    specs['h1'] = prep['proposed_spec']
    assert specs['h1']['source_Adamstep'] == 646100
    grant = dict(epoch=time.time(), question_item_id='request_user_input_async/call_7e02c655b41142a7afe0fd1895e4f15a/0',
        actual_human_answer='批准这一有限段', explicit_human_grant_received=True,
        question='从最新完整模型ce3接续相同H1配置，72GPU0最多24次更新、总上限1800秒，原预算；自己的native和独立CPU准入后一个GO，另一4090可并行评测新模型。',
        source_SHA=SOURCE_SHA, source_Adam=646100, source_owned_updates=24,
        manifest_SHA=prep['manifest']['SHA'], package=prep['package'],
        target_root=prep['proposed_target_root'], owner_root=prep['proposed_owner_root'],
        GPU_UUID=specs['h1']['GPU_UUID'], max_completed_updates=24, max_parent_seconds=1800,
        exit_headroom_seconds=300, start_free_GiB=25, saved_stop_free_GiB=8,
        original_budget_seconds=1188000, unchanged_public4_V2_coefficient001_and_other_recipe=True,
        E2_E3_hold_zero_worker_GO_charge=True, no_following_window_authorization=True,
        no_old_native_or_case_replay=True, actual_deployment_not_yet_run=True,
        initial_local_repo_lookup_error_preserved='git status/rev-parse attempted from workspace parent: fatal not a git repository; corrected to polar-rl-train; no host or GPU failure')
    save(APPROVAL, grant)
    save(R / 'HUMAN_APPROVED_CE3_PREPARED_PAYLOAD_BOUND_DEPLOY_SPEC_ACTUAL.json', dict(
        epoch=time.time(), passed_CPU_only=True, specs=specs, approval_path=str(APPROVAL), approval_SHA=H(APPROVAL),
        manifest_file_count=478, all_local_manifest_files_revalidated=True,
        source_SHA=SOURCE_SHA, no_new_native_or_PPO_yet=True))
    text = (prior / 'deploy_public4_repair_V2_new_native_then_original_finite1800_once.py').read_text('utf8')
    replacements = {
        "SOURCE='/mnt/mod4_linux_durable_20261013/H1mp_1810p2/owner';TARGET='/home/lc01/Zonglin Li/zonglin2/tasks/H1mp_1810p2'":
        "SOURCE='/mnt/mod4_linux_durable_20261013/H1cq_1810p3/owner';TARGET='/home/lc01/Zonglin Li/zonglin2/tasks/H1cq_1810p3';Q=B/'payload/h1'",
        "old=owned/'H1mb_1810p1/owner'": "old=owned/'H1mp_1810p2/owner'",
        "previous_P1_original_cost_settled_all_children_out": "previous_P2_original_cost_settled_all_children_out",
        "r['name']).read_bytes()).hexdigest()==r['SHA']": "r['name']).read_bytes()).hexdigest()==r['SHA']",
        "sf.put(str(B/n),SOURCE+'/'+n)": "sf.put(str(Q/n),SOURCE+'/'+n)",
        "SHA=a.H(B/n)": "SHA=a.H(Q/n)",
        "H1_TARGET72_CLOSED24_FINITE_": "H1_CE3_EXPLICIT_HUMAN_SINGLE_FINITE_",
        "H1_source_Adam645620=True": "H1_source_Adam646100=True",
        "strict_same_source_native_reuse=True": "own_ce3_native180_and_independent_CPU=True",
        "PUBLIC4_REPAIR_V2_H1_NEW_FINITE_DEPLOY_STARTED_ACTUAL.json": "HUMAN_APPROVED_CE3_NEW_NATIVE_FINITE_DEPLOY_STARTED_ACTUAL.json",
        "PUBLIC4_REPAIR_V2_H1_STRICT_NATIVE_REUSE_NEW_FINITE_PPO_DETACHED_ACTUAL.json": "HUMAN_APPROVED_CE3_OWN_NEW_NATIVE_SINGLE_FINITE_CHAIN_DETACHED_ACTUAL.json",
        "H1_TARGET72_DEPLOY_ORIGINAL_ERROR_": "CE3_APPROVED_DEPLOY_ORIGINAL_ERROR_",
        "Host72 human-requested H1 new finite training (hidden): ": "Host72 approved ce3 one finite segment (hidden): ",
    }
    for old, new in replacements.items():
        assert old in text, old
        text = text.replace(old, new)
    start = text.index(" prep=json.loads((R/'PUBLIC4_REPAIR_V2_H1_FINITE_NEW_SOURCE_NATIVE_PAYLOAD_CPU_ACTUAL.json')")
    end = text.index("\n put('HUMAN_APPROVED_CE3_NEW_NATIVE_FINITE_DEPLOY_STARTED_ACTUAL.json'", start)
    text = text[:start] + " prep=json.loads((R/'HUMAN_APPROVED_CE3_PREPARED_PAYLOAD_BOUND_DEPLOY_SPEC_ACTUAL.json').read_bytes());grant=json.loads((R/'HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json').read_bytes());assert a.H(R/'HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json')==prep['approval_SHA'] and grant['explicit_human_grant_received'] and grant['actual_human_answer']=='批准这一有限段' and grant['no_following_window_authorization'];assert grant['source_SHA']=='" + SOURCE_SHA + "';specs=prep['specs'];assert specs['h1']['source_SHA']==grant['source_SHA'] and specs['h1']['manifest_SHA']==grant['manifest_SHA'] and specs['h1']['source_Adamstep']==646100 and specs['h1']['max_parent_seconds']==1800 and specs['h1']['execution_backend']=='target72';assert a.H(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')==grant['manifest_SHA']" + text[end:]
    # Bind old node metadata and original owner terminal identity without old PT rehash.
    text = text.replace("assert not alive,alive\nfor p in", "assert not alive,alive\nassert t['final']['final']['SHA']=='" + SOURCE_SHA + "'\nfor p in")
    old = "p=psutil.Process(i['pid']);assert abs(p.create_time()-i['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE"
    new = old + "\nalive=[]\nfor p in psutil.process_iter(['pid','create_time','cmdline']):\n try:\n  if p.pid!=os.getpid() and any(s.startswith(str(old)+'/') for s in p.info['cmdline'] or []):alive.append(p.info)\n except psutil.Error:pass\nassert not alive,alive\nassert json.loads((old/'COHORT_FINAL.json').read_bytes())['rows']['h1']['final']['final']['SHA']=='" + SOURCE_SHA + "'"
    assert old in text
    text = text.replace(old, new)
    ast.parse(text)
    with DEPLOYER.open('x', encoding='utf8') as f:
        f.write(text)
    save(R / 'HUMAN_APPROVED_CE3_DEPLOYER_CPU_BINDING_ACTUAL.json', dict(epoch=time.time(),
        source_file=str(DEPLOYER), SHA=H(DEPLOYER), approval_SHA=H(APPROVAL), AST_passed=True,
        one_human_grant_only_no_following_window=True, original_four_controllers_unchanged=True,
        deployer_calls_original_node_own_native_not_unused_reuse_helpers=True,
        original_prior_P2_identity_terminal_SHA_cost_and_OS_locks_must_be_actual=True,
        no_transport_or_GPU_or_accounting_in_this_preparation=True))
    print(json.dumps(dict(passed_CPU_preparation_only=True, approval_bound=True, deployer=str(DEPLOYER),
                          controller_files_unchanged=True, new_native_not_yet_run=True)))

if __name__ == '__main__':
    main()
