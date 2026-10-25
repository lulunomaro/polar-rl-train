"""Generate reviewable69 admission copies only inside this review directory.

No PT, NumPy, torch, native, SDK, scene, remote, source69 edit or checker run.
"""
from __future__ import annotations
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPT = HERE.parent
STAGE = OPT.parent
BASE = STAGE / "H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025/payloads"
CHECKER = OPT / "your_agent/implementation_v1/revision_v2/verification/sampling_acceleration_installed_CPU_v2.py"
CHECKER_SHA = "256f803270d8ec6702e0d120670d57bf79c9145c169a71bc4742dad7ac0dcf15"
SCOPE = "source68_v6a_to_unused69_sampling_trace_deflate1_e3_fixed_reset_cache_v1"
ORIGINALS = {
 "h1/closed_production_continuation_CPU_v2.py": "683c8f7f17999f8330f55daa45a2ad90c04059e8f26afaf81dae4af8c1801e0e",
 "h1/target_H1_step270_closed_source_sdk_cpu_review_v1.py": "95109377c925d08e98fcd95c687f42ea1d1f973b9f04f0fc3089fceedfd878c8",
 "recovery/original_account_policy50_source_CPU.py": "fc92c311249af23ceb88420313d4630d7b1b15231654c15b6e5eff9932af6470",
 "recovery/target_two50_source_sdk_cpu_review.py": "218908455bdeaad2b95b8239542c46496c1a8407c57b323e9c764018bc0a06f3"}
CANDIDATES = {
 "h1": {"h1_production_control_prefix_trace_v1.py": "a24011df3a43e580fa15037791c30e9f8dacdaf4d0f6b9dd62b00276798414bd",
        "sampling_trace_npz_lossless_v1.py": "ce2335df8ac300fb52659d69fd41df82dd8a58964adc990448709cd332d8057f"},
 "recovery": {"job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py": "7e1d28e8ef1622f7923c00358f2683ea8682cf4553f0e1aacf40e68446b2ae2d",
              "job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py": "ba4f5cd584f911a9313de2f60f6465b1114f645a47c1ffcda5fcc9930dd8109a"}}
BASE_CHANGE = {"h1": {"h1_production_control_prefix_trace_v1.py": "d14f69cd14a1297f558ea7f7df83f17f735cec2f99da037f3b2d623a2f590dd6"},
               "recovery": {"job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py": "0f8fd2c24b25a4a80f18bb4c3aae016acfa6873b418d6e2e32a3f72ff6199fbd"}}
FROZEN_H1 = {"H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json": "966c624297ac409bd4a644b4509e30b450b5dbab09e8e1dce41743baad5e05e6",
             "H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json": "3b9fdd0ac632003d301572ca131b46161366b0e60c730ab615b903072385c22e",
             "h1_prefix_pair_retention_v1.py": "92d713e44fc1381b9c6a7d12d965608789deda671bd74266ca98844535555e85",
             "H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json": "652d2c602a870df562ba7d98c06cdd001400c9e748b684776aaddf76f50a56cb"}
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after, 1)


def add_target_check(text, key):
    block = ("from sampling_acceleration_installed_CPU_v2 import check as sampling_acceleration_check\n"
             f"v['sampling_acceleration_CPU']=sampling_acceleration_check(B,'{key}')\n")
    if key == "h1":
        anchor = "(B / 'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json').write_text"
        new = once(text, anchor, block + anchor)
    else:
        anchor = ";(B/'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json').write_text"
        new = once(text, anchor, "\n" + block + anchor[1:])
    # Exact old target AST retained; only these adjacent import/call nodes added.
    tree = ast.parse(new)
    expected = ast.parse(block).body
    for index in range(len(tree.body) - 1):
        if all(ast.dump(tree.body[index + j], include_attributes=False) == ast.dump(expected[j], include_attributes=False) for j in range(2)):
            tree.body[index:index + 2] = []
            break
    else:
        raise AssertionError("exact target append nodes not found")
    assert ast.dump(tree, include_attributes=False) == ast.dump(ast.parse(text), include_attributes=False)
    return new


def receipt_function(key, old_guard, old_target, new_target):
    # This is source/receipt validation ONLY. In particular it never calls the
    # acceleration checker and never rereads a reset bank or checkpoint.
    return f'''
def _sampling_receipt(B,old,key,m,before,cpu):
    assert key=={key!r}
    read=lambda p:json.loads(Path(p).read_bytes())
    auth=read(B/'SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json')
    assert auth['approved'] is True and auth['approval_scope']=={SCOPE!r}
    slot=auth['slots'][key]
    assert slot['base_guard_SHA']=={ORIGINALS[f"{key}/{old_guard}"]!r} and H(old/{old_guard!r})==slot['base_guard_SHA']
    assert slot['old_target_CPU_SHA']=={ORIGINALS[f"{key}/{old_target}"]!r} and H(old/{old_target!r})==slot['old_target_CPU_SHA']
    assert slot['new_target_CPU_SHA']=={hashlib.sha256(new_target.encode()).hexdigest()!r} and H(B/{old_target!r})==slot['new_target_CPU_SHA']
    assert slot['installed_checker_SHA']=={CHECKER_SHA!r} and H(B/'sampling_acceleration_installed_CPU_v2.py')==slot['installed_checker_SHA']
    expected={CANDIDATES[key]!r};base={BASE_CHANGE[key]!r}
    assert slot['candidate_SHA']==expected and slot['base_SHA']==base
    current={{x['relative']:x for x in m['files']}}
    for rel,digest in base.items():
        assert before[rel]['SHA']==digest and H(old/rel)==digest
    for rel,digest in expected.items():
        assert current[rel]['SHA']==digest and H(B/rel)==digest
    # A hard inventory equality closes extra/deleted runtime/assets/SDK files.
    protected=lambda rel:rel.startswith(('job0/runtime/','job0/assets/','lib/'))
    prior_set={{rel for rel in before if protected(rel)}}
    current_set={{rel for rel in current if protected(rel)}}
    cache='job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py'
    additions={{cache}} if key=='recovery' else set()
    assert current_set==prior_set|additions
    if key=='recovery':assert cache not in before
    for rel in prior_set:
        if rel not in expected:
            assert current[rel]['SHA']==before[rel]['SHA'] and current[rel]['bytes']==before[rel]['bytes']
    # Never rerun check(): recovery's fresh-bank branch is called once by the
    # target CPU checker, and its already-saved receipt is checked below.
    speed=cpu['sampling_acceleration_CPU']
    assert speed['passed'] is True and speed['key']==key and Path(speed['base']).resolve()==B.resolve()
    assert speed['expected_base_SHA']==base and speed['candidate_SHA']==expected
    assert set(speed['exact_source_allowlist'])==set(expected) and speed['no_GPU_API_SDK_scene_policy_physics_or_canonical'] is True
    if key=='h1':
        assert speed['status']=='CPU_exact_installed_sources_and_lossless_fixture_passed'
        assert speed['NPZ_array_bytes_dtype_shape_exact'] and speed['full_SHA_preserved']
        frozen={FROZEN_H1!r}
        for rel,digest in frozen.items():assert H(B/rel)==H(old/rel)==digest
    else:
        assert speed['status']=='CPU_exact_installed_sources_and_fresh_bank_geometry_context_passed'
        assert speed['bank_SHA']=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
        assert speed['bank_bytes']==32022178 and speed['fresh_bank_physical_read_count']==1
    return speed

'''


def main():
    out = HERE / "copies_69_ready"
    assert not out.exists(), "Never overwrite a prior patch attempt"
    assert H(CHECKER) == CHECKER_SHA
    original = {}
    for relative, expected in ORIGINALS.items():
        path = BASE / relative
        assert H(path) == expected, f"source changed before review: {relative}"
        original[relative] = path.read_text(encoding="utf-8")
    generated = {}
    target_names = {"h1": "target_H1_step270_closed_source_sdk_cpu_review_v1.py", "recovery": "target_two50_source_sdk_cpu_review.py"}
    guard_names = {"h1": "closed_production_continuation_CPU_v2.py", "recovery": "original_account_policy50_source_CPU.py"}
    for key in ("h1", "recovery"):
        relative = key + "/" + target_names[key]
        generated[relative] = add_target_check(original[relative], key)
    h1 = original["h1/" + guard_names["h1"]]
    h1 = once(h1, "def load(spec,B):", receipt_function("h1", guard_names["h1"], target_names["h1"], generated["h1/" + target_names["h1"]]) + "def load(spec,B):")
    h1 = once(h1, "assert H(B/trace)==current[trace]['SHA']==retention['candidate_trace']['SHA']",
              "assert H(old/trace)==prior[trace]['SHA']==retention['candidate_trace']['SHA']\n    assert prior[trace]['SHA']==retention['candidate_trace']['SHA']")
    h1 = once(h1, "assert H(B/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')==reward['target_CPU_SHA']",
              "assert H(old/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')==reward['target_CPU_SHA']")
    h1 = once(h1, "    v=dict(explicit_human_authorized_reward_change=True,",
              "    _sampling_receipt(B,old,'h1',m,prior,cpu)\n    v=dict(explicit_human_authorized_reward_change=True,")
    generated["h1/" + guard_names["h1"]] = h1
    e3 = original["recovery/" + guard_names["recovery"]]
    e3 = once(e3, "import hashlib,json,os,psutil", "import hashlib,json,os,psutil")
    e3 = once(e3, "def load(spec,B):", receipt_function("recovery", guard_names["recovery"], target_names["recovery"], generated["recovery/" + target_names["recovery"]]) + "def load(spec,B):")
    old_loop = "  if x['relative'].startswith(('job0/runtime/','job0/assets/','lib/')):assert x['SHA']==before[x['relative']]['SHA'] and x['bytes']==before[x['relative']]['bytes']"
    new_loop = """  if x['relative'].startswith(('job0/runtime/','job0/assets/','lib/')):
   rel=x['relative']
   if rel=='job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py':
    assert key=='recovery' and before[rel]['SHA']=='0f8fd2c24b25a4a80f18bb4c3aae016acfa6873b418d6e2e32a3f72ff6199fbd' and x['SHA']=='7e1d28e8ef1622f7923c00358f2683ea8682cf4553f0e1aacf40e68446b2ae2d'
   elif rel=='job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py':
    assert key=='recovery' and rel not in before and x['SHA']=='ba4f5cd584f911a9313de2f60f6465b1114f645a47c1ffcda5fcc9930dd8109a'
   else:assert x['SHA']==before[rel]['SHA'] and x['bytes']==before[rel]['bytes']"""
    e3 = once(e3, old_loop, new_loop)
    e3 = once(e3, " v=dict(kind='closed_same_backend_policy50_production',",
              " _sampling_receipt(B,old,key,m,before,cpu)\n v=dict(kind='closed_same_backend_policy50_production',")
    generated["recovery/" + guard_names["recovery"]] = e3
    out.mkdir()
    schema = {"status": "TEMPLATE_ONLY_NOT_AN_APPROVAL_OR_CPU_RESULT", "approved": None,
              "approval_scope": SCOPE, "human_authorization_source": None, "slots": {}}
    diffs, files = [], []
    for relative, content in generated.items():
        ast.parse(content)
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        files.append({"relative": relative, "original_SHA": ORIGINALS[relative],
                      "candidate_SHA": H(path), "candidate_bytes": path.stat().st_size})
        diffs.extend(difflib.unified_diff(original[relative].splitlines(True), content.splitlines(True),
                                         fromfile="N68/" + relative, tofile="N69_PROPOSED/" + relative))
    for key in ("h1", "recovery"):
        schema["slots"][key] = {"base_guard_SHA": ORIGINALS[key + "/" + guard_names[key]],
                               "new_guard_SHA": H(out / key / guard_names[key]),
                               "old_target_CPU_SHA": ORIGINALS[key + "/" + target_names[key]],
                               "new_target_CPU_SHA": H(out / key / target_names[key]),
                               "installed_checker_SHA": CHECKER_SHA,
                               "base_SHA": BASE_CHANGE[key], "candidate_SHA": CANDIDATES[key]}
    (HERE / "N68_TO_N69_ADMISSION_REVIEW_ONLY.diff").write_text("".join(diffs), encoding="utf-8")
    (HERE / "SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_SCHEMA_TEMPLATE.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    report = {"review_id": "N69_MINIMAL_SOURCE_ADMISSION_PATCH_LOCAL_20261025", "status": "SOURCE_COPIES_AST_PARSE_ONLY_NOT_APPLIED_NOT_RUN",
              "base": str(BASE), "source_files": files, "installed_checker_SHA": CHECKER_SHA,
              "target_AST_exact_except_two_inserted_nodes_each": True,
              "recovery_guard_reads_saved_CPU_receipt_never_reruns_bank_checker": True,
              "no_PT_native_GPU_SDK_policy_training_remote_or_source69_edit": True,
              "no_more_subagents_after_current_turn": True, "git_status": "PENDING_ROOT_UNIFIED_ARCHIVE"}
    (HERE / "SOURCE_PATCH_REVIEW_ACTUAL.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
