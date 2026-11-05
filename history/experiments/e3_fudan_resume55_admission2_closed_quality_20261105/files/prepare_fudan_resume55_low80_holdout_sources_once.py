#!/usr/bin/env python3
"""Prepare only the independent resume55 LOW80 holdout's thirteen source files.

Fixed stdlib-only, no-argument generator. It never imports or executes generated
source. All inputs are pinned .py source bytes. The already-present strict worker
is verified and retained, never rewritten. No model or runtime artifact is read.
Actual preparation, AST13/compile13 and byte/inverse checks run only under main.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).absolute().parent
OLD_NATIVE = "source_fudan_frozen_low80_confirm_v1"
OLD_PARENT = "source_fudan_frozen_low80_parent_v1"
NEW_NATIVE = "source_fudan_frozen_low80_holdout_v2_resume55"
NEW_PARENT = "source_fudan_frozen_low80_parent_v2_resume55"
NATIVE_V8 = "source_fudan_frozen_native_eval_v8_resume55"
PARENT_V8 = "source_fudan_frozen_parent_v8_resume55"
GENERATOR_NAME = "prepare_fudan_resume55_low80_holdout_sources_once.py"
OLD_KIND = "E3_FDN_FROZEN_LOW80_CONFIRM_V1"
NEW_KIND = "E3_FDN_FROZEN_LOW80_HOLDOUT_RESUME55_V2"
OLD_SCOPE = "LOW80_FIVE_POSE16_8S_FULLDR_FIRSTEPISODE_CONFIRM"
NEW_SCOPE = "LOW80_FIVE_POSE16_8S_FULLDR_HOLDOUT_FIRSTEPISODE_CONFIRM"
OLD_SEEDS = "(20260929,20260930,20261001)"
NEW_SEEDS = "(20261002,20261003,20261004)"
WORKER = "worker_fudan_original_n80.py"
MEAN = "frozen_sequence_mean.py"
SAFE = "fudan_frozen_eval_safe.py"
QUALIFIER = "fudan_eval_parent_wait_contract_v1.py"
NATIVE_FILES = (
    "app_close_semantics_v6.py", "e3_fudan_task_runtime_v1.py", MEAN, SAFE,
    "launch_storage_contract.py", "low80_confirmation_phase_v1.py",
    "n80_gpu_capacity.py", "pose_cache_runtime_adapter_v4.py",
    "resume_runtime_contracts_v3.py", WORKER,
)
PARENT_FILES = (QUALIFIER, "fudan_task_contract_v2.py", "single_gpu_group_supervisor.py")
WORKER_PIN = (13638, "ede3a192883a99863762980af97be028c346ba586e60fb7a8dbdc7fa3ecb0c5a")
MEAN_PIN = (36414, "cebb165f7f2d97aac0125568075d197c82e8ddadef83d654fcb0861a33715c4a")
ORIGINAL_SAFE_PIN = (22479, "2a61e972955543caa6cfad786b0eaa28b013f6ab6084bcc795e2b771d1e28476")
ORIGINAL_QUALIFIER_PIN = (38092, "da95a6ae43813ac1bb6f8629f9fa9409365936738ae9f21061b8e21004914675")

# BEGIN_INPUT_SOURCE_PINS
INPUT_SOURCE_PINS = {
    'source_fudan_frozen_low80_confirm_v1/app_close_semantics_v6.py': (27769, '3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39'),
    'source_fudan_frozen_low80_confirm_v1/e3_fudan_task_runtime_v1.py': (12745, 'a84823a59731f9cd805aa0bf6a91af10e0e26e729652df39b8cbd17dc6def3f9'),
    'source_fudan_frozen_low80_confirm_v1/frozen_sequence_mean.py': (27458, 'c2253bc20b40b09b0d5d131ddeee528a8eba708c48e9c74e2699212e12b3ccae'),
    'source_fudan_frozen_low80_confirm_v1/fudan_frozen_eval_safe.py': (22606, '8fad1d62bcf851f659ef3708240cc1eabe96604c9b55b0e42d23ba9a9fa4bcb9'),
    'source_fudan_frozen_low80_confirm_v1/launch_storage_contract.py': (117, 'e40b51db4bca2f322cc2c9b4b0fe011eed292ae605f4f175f268a5bf90326047'),
    'source_fudan_frozen_low80_confirm_v1/low80_confirmation_phase_v1.py': (5990, '520764dd4f9d0350be8039a601966e5d8b9a19bf43ddd0c677f8385831b38b9c'),
    'source_fudan_frozen_low80_confirm_v1/n80_gpu_capacity.py': (653, 'ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc'),
    'source_fudan_frozen_low80_confirm_v1/pose_cache_runtime_adapter_v4.py': (18161, '7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f'),
    'source_fudan_frozen_low80_confirm_v1/resume_runtime_contracts_v3.py': (22337, 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7'),
    'source_fudan_frozen_low80_confirm_v1/worker_fudan_original_n80.py': (13008, '00ace0c15f7246773ea6adfa4a6fd99daff5e5bc9ae08bc164972560c308a0a3'),
    'source_fudan_frozen_low80_parent_v1/fudan_eval_parent_wait_contract_v1.py': (32458, '9a594b59820d0cbb61a4f05b03bf1a331bf92df1295ba59f13782d402b701748'),
    'source_fudan_frozen_low80_parent_v1/fudan_task_contract_v2.py': (999, 'f0b99ed8185d26fe49886aa791ce17c8e4dad4b91b06eaf93b7be80eeacf04fb'),
    'source_fudan_frozen_low80_parent_v1/single_gpu_group_supervisor.py': (9775, 'c9cc481aa7d06d9d8d01db0b51ffb6386c8b6142ee18d50bf4a21bcb3668c9e1'),
    'source_fudan_frozen_native_eval_v8_resume55/frozen_sequence_mean.py': (36414, 'cebb165f7f2d97aac0125568075d197c82e8ddadef83d654fcb0861a33715c4a'),
    'source_fudan_frozen_native_eval_v8_resume55/fudan_frozen_eval_safe.py': (22479, '2a61e972955543caa6cfad786b0eaa28b013f6ab6084bcc795e2b771d1e28476'),
    'source_fudan_frozen_parent_v8_resume55/fudan_eval_parent_wait_contract_v1.py': (38092, 'da95a6ae43813ac1bb6f8629f9fa9409365936738ae9f21061b8e21004914675'),
    'source_fudan_frozen_low80_holdout_v2_resume55/worker_fudan_original_n80.py': (13638, 'ede3a192883a99863762980af97be028c346ba586e60fb7a8dbdc7fa3ecb0c5a'),
}
# END_INPUT_SOURCE_PINS

STRICT_METADATA_BLOCK = '''        # Strict terminal evidence is distinct from the compatible loose count.
        audit.eq("scope.loose_compatibility_label", skill.get("credited_and_stable_at_end_label"),
                 "compatibility_only_ever_credited_and_final_frame_good_not_strict_continuous25")
        streaks = skill.get("terminal_current_good_streak_controls_by_env")
        credit_steps = skill.get("first_credit_control_per_env")
        maximum_good = skill.get("maximum_first_episode_good_controls")
        live400 = skill.get("control400_first_episode_physically_live")
        flags400 = skill.get("control400_flags")
        arrays_ok = (type(streaks) is list and len(streaks) == 80 and
                     all(_integer(v) and v <= 400 for v in streaks) and
                     type(maximum_good) is list and len(maximum_good) == 80 and
                     all(_integer(v) and v <= 400 for v in maximum_good) and
                     type(credit_steps) is list and len(credit_steps) == 80 and
                     all(type(v) is int and (v == -1 or 1 <= v <= 400) for v in credit_steps) and
                     type(live400) is list and len(live400) == 80 and
                     all(type(v) is bool for v in live400) and
                     type(flags400) is list and len(flags400) == 80 and
                     all(type(row) is list and len(row) == 7 and
                         all(type(v) is bool for v in row) for row in flags400))
        audit.check("scope.strict.eighty_typed_terminal_rows", arrays_ok)
        for name in ("first_episode_stable_credits", "credited_and_stable_at_end",
                     "terminal_continuous25_good_count", "ever_credited_and_final_frame_good",
                     "first_episode_physical_terminated", "first_episode_truncated"):
            audit.check("scope.typed_bounded_count." + name,
                        _integer(skill.get(name)) and skill[name] <= 80, actual=skill.get(name))
        pose_rows_ok = (type(rows) is list and len(rows) == 5 and
                        all(type(row) is dict and type(row.get("pose")) is int and
                            row["pose"] == pid and type(row.get("first_episode_denominator")) is int and
                            row["first_episode_denominator"] == 16
                            for pid, row in enumerate(rows)))
        audit.check("scope.strict.five_pose16_metadata_rows", pose_rows_ok)
        if pose_rows_ok:
            for pid, row in enumerate(rows):
                for name in ("first_episode_stable_credits", "credited_and_stable_at_end",
                             "terminal_continuous25_good_count", "first_episode_physical_terminated",
                             "first_episode_truncated"):
                    audit.check("scope.strict.pose." + str(pid) + ".typed_count." + name,
                                _integer(row.get(name)) and row[name] <= 16, actual=row.get(name))
        if arrays_ok:
            credited = [v >= 1 for v in credit_steps]
            loose = [credited[i] and live400[i] and flags400[i][6] for i in range(80)]
            strict = [credited[i] and live400[i] and streaks[i] >= 25 for i in range(80)]
            audit.check("scope.strict.current_streak_matches_current_joint_good",
                        all((streaks[i] > 0) == flags400[i][6] for i in range(80)))
            audit.eq("scope.strict.credit_formula", skill.get("first_episode_stable_credits"), sum(credited))
            audit.eq("scope.loose.final_frame_formula", skill.get("credited_and_stable_at_end"), sum(loose))
            audit.eq("scope.loose.alias_formula", skill.get("ever_credited_and_final_frame_good"), sum(loose))
            audit.eq("scope.strict.terminal_continuous25_formula", skill.get("terminal_continuous25_good_count"), sum(strict))
            if pose_rows_ok:
                for pid, row in enumerate(rows):
                    audit.fields("scope.strict.pose." + str(pid) + ".formula", row,
                                 dict(first_episode_stable_credits=sum(credited[i] for i in range(pid, 80, 5)),
                                      credited_and_stable_at_end=sum(loose[i] for i in range(pid, 80, 5)),
                                      terminal_continuous25_good_count=sum(strict[i] for i in range(pid, 80, 5))))
        if pose_rows_ok:
            for name in ("first_episode_stable_credits", "credited_and_stable_at_end",
                         "terminal_continuous25_good_count", "first_episode_physical_terminated",
                         "first_episode_truncated"):
                values = [row.get(name) for row in rows]
                if all(type(v) is int for v in values):
                    audit.eq("scope.strict.pose_sum." + name, skill.get(name), sum(values))
'''


def need(value, message):
    if not value:
        raise RuntimeError(message)


def digest(raw):
    return len(raw), hashlib.sha256(raw).hexdigest()


def section(raw, first, following):
    if isinstance(first, str):
        first, following = first.encode(), following.encode()
    need(raw.count(first) == 1 and raw.count(following) == 1,
         "Source metadata block boundary changed: " + first.decode())
    start = raw.index(first)
    end = raw.index(following, start + len(first))
    return raw[start:end]


def main():
    need(Path(__file__).name == GENERATOR_NAME, "Fixed generator filename differs")
    src = BASE / NEW_NATIVE
    par = BASE / NEW_PARENT
    expected_inputs = ({OLD_NATIVE + "/" + name for name in NATIVE_FILES} |
                       {OLD_PARENT + "/" + name for name in PARENT_FILES} |
                       {NATIVE_V8 + "/" + MEAN, NATIVE_V8 + "/" + SAFE,
                        PARENT_V8 + "/" + QUALIFIER, NEW_NATIVE + "/" + WORKER})
    need(set(INPUT_SOURCE_PINS) == expected_inputs and len(expected_inputs) == 17,
         "Seventeen fixed source-byte pins are required")
    need(not src.is_symlink() and src.is_dir() and
         {p.name for p in src.iterdir()} == {WORKER},
         "Native target must contain only the preexisting strict worker")
    need(not par.exists() and not par.is_symlink(), "Parent target already exists")
    inputs = {}
    for relative, pin in INPUT_SOURCE_PINS.items():
        path = BASE / relative
        need(path.suffix == ".py" and not path.is_symlink(), "Only ordinary pinned .py input files are permitted")
        raw = path.read_bytes()
        need(digest(raw) == tuple(pin), "Pinned source bytes/SHA differ: " + relative)
        inputs[relative] = raw
    need(digest(inputs[NEW_NATIVE + "/" + WORKER]) == WORKER_PIN, "Existing strict worker pin differs")
    need(len(inputs[NEW_NATIVE + "/" + WORKER].splitlines()) == 99, "Existing strict worker line count differs")
    need(digest(inputs[NATIVE_V8 + "/" + MEAN]) == MEAN_PIN, "Frozen Root8 mean pin differs")
    need(digest(inputs[NATIVE_V8 + "/" + SAFE]) == ORIGINAL_SAFE_PIN, "Frozen original Safe pin differs")
    need(digest(inputs[PARENT_V8 + "/" + QUALIFIER]) == ORIGINAL_QUALIFIER_PIN, "Frozen original qualifier pin differs")
    for name, size in (("low80_confirmation_phase_v1.py", 5990),
                       ("e3_fudan_task_runtime_v1.py", 12745),
                       ("pose_cache_runtime_adapter_v4.py", 18161)):
        need(len(inputs[OLD_NATIVE + "/" + name]) == size, "Unchanged low80 dependency size differs: " + name)

    original = {("n", f): inputs[OLD_NATIVE + "/" + f] for f in NATIVE_FILES}
    original.update({("p", f): inputs[OLD_PARENT + "/" + f] for f in PARENT_FILES})
    output = dict(original)
    edits = {key: [] for key in original}

    def replace(key, old, new, count=1):
        newline = b"\r\n" if b"\r\n" in original[key] else b"\n"
        old = old.encode().replace(b"\n", newline) if isinstance(old, str) else old
        new = new.encode() if isinstance(new, str) else new
        new = new.replace(b"\r\n", b"\n").replace(b"\n", newline)
        need(output[key].count(old) == count, "Literal metadata anchor changed: " + str(key) + " " + repr(old[:90]))
        output[key] = output[key].replace(old, new)
        edits[key].append((old, new, count))

    def replace_section(key, first, following, new):
        replace(key, section(output[key], first, following), new)

    m, w = ("n", MEAN), ("n", WORKER)
    s, q = ("n", SAFE), ("p", QUALIFIER)
    t, v = ("p", "fudan_task_contract_v2.py"), ("p", "single_gpu_group_supervisor.py")
    output[m] = inputs[NATIVE_V8 + "/" + MEAN]
    output[w] = inputs[NEW_NATIVE + "/" + WORKER]
    original_q = inputs[PARENT_V8 + "/" + QUALIFIER]

    for key in (s, q, t):
        replace(key, OLD_KIND, NEW_KIND)
        replace(key, OLD_SCOPE, NEW_SCOPE)
        replace(key, OLD_SEEDS, NEW_SEEDS)
    replace(q, "FDN_LOW80_3SEED_ACTUAL_WAIT_QUALIFICATION_V1",
            "FDN_LOW80_3SEED_RESUME55_ACTUAL_WAIT_QUALIFICATION_V2")
    replace(v, "['E3_LOW80_20260929', 'E3_LOW80_20260930', 'E3_LOW80_20261001']",
            "['E3_LOW80_20261002', 'E3_LOW80_20261003', 'E3_LOW80_20261004']")
    replace(v, "ONEGPU_E3_LOW80_THREE_SEED_CONFIRM_NO_LEARNING",
            "ONEGPU_E3_LOW80_THREE_SEED_HOLDOUT_RESUME55_NO_LEARNING")
    replace(v, "ACTUAL_SINGLE_GPU_E3_LOW80_THREE_SEED_CONFIRM",
            "ACTUAL_SINGLE_GPU_E3_LOW80_THREE_SEED_HOLDOUT_RESUME55")

    gate_end = '        self.raw = Path(self.binding["path"]).read_bytes()'
    replace(s, "EXCLUDED_LOWSTD005_PATH, EXCLUDED_LOWSTD005_SHA)\n",
            "EXCLUDED_LOWSTD005_PATH, EXCLUDED_LOWSTD005_SHA, EXCLUDED_SOURCE55_PATH, EXCLUDED_SOURCE55_SHA)\n")
    replace(s, "EXCLUDED_HEIGHTGATE_PATH, EXCLUDED_LOWSTD005_PATH)) and\n",
            "EXCLUDED_HEIGHTGATE_PATH, EXCLUDED_LOWSTD005_PATH, EXCLUDED_SOURCE55_PATH)) and\n")
    replace(s, "EXCLUDED_HEIGHTGATE_SHA, EXCLUDED_LOWSTD005_SHA),\n",
            "EXCLUDED_HEIGHTGATE_SHA, EXCLUDED_LOWSTD005_SHA, EXCLUDED_SOURCE55_SHA),\n")
    replace(s, "Selected fresh1cd LR001 save must not be 1cd, 47937, 8af4, 3e64, 246ac6, bf824 or cc41 old input",
            "Selected Root8 continuation save must not be 1cd, 47937, 8af4, 3e64, 246ac6, bf824, cc41 or source55 old input")
    receipt_anchor = "rejected_timeout8_candidate_checkpoint_physically_opened=False,\n"
    replace(s, receipt_anchor, receipt_anchor + "                     source55_checkpoint_physically_opened=False,\n")
    replace(q, receipt_anchor, receipt_anchor + "                 source55_checkpoint_physically_opened=False,\n")

    replace_section(q, "_BRANCH_KIND = ", "_TRAINING_OVERLAY_SHA = ",
                    section(original_q, "_BRANCH_KIND = ", "_TRAINING_OVERLAY_SHA = "))
    replace(q, "_EXCLUDED_LOWSTD005_SHA))\n", "_EXCLUDED_LOWSTD005_SHA, _EXCLUDED_SOURCE55_SHA))\n")
    replace(q, "_EXCLUDED_LOWSTD005_PATH)))\n", "_EXCLUDED_LOWSTD005_PATH, _EXCLUDED_SOURCE55_PATH)))\n")
    prov_start = '        prov = audit.mapping("source.provenance", caches[1].get("provenance"))'
    close_start = '        close = audit.mapping("intent.original_bound_close", intent.get("original_bound_close"))'
    metadata = section(original_q, prov_start, close_start)
    need(b"controls=160" not in metadata and b"original_recovery_request_denominator" not in metadata,
         "Original-160 scope crossed into the source-only metadata block")
    replace_section(q, prov_start, close_start, metadata)
    strict_anchor = '        notes.append("No PT/source file SHA recomputation here:'
    replace(q, strict_anchor, STRICT_METADATA_BLOCK + strict_anchor)
    old_route_sha = "8fad1d62bcf851f659ef3708240cc1eabe96604c9b55b0e42d23ba9a9fa4bcb9"
    need(digest(original[s])[1] == old_route_sha, "Actual low1 Safe and parent route pin differ")
    safe_sha = digest(output[s])[1]
    replace(q, old_route_sha, safe_sha, 2)

    # Inverse the complete finite literal/metadata patch set; nothing else drifts.
    for key in (s, q, t, v):
        back = output[key]
        for old, new, count in reversed(edits[key]):
            need(back.count(new) == count, "Inverse metadata anchor ambiguity: " + str(key))
            back = back.replace(new, old)
        need(back == original[key], "Out-of-scope source-byte change: " + str(key))
    unchanged = tuple(("n", name) for name in NATIVE_FILES if name not in (MEAN, SAFE, WORKER))
    need(len(unchanged) == 7 and all(output[key] == original[key] for key in unchanged),
         "Seven unchanged low80 dependencies must remain byte exact")
    need(output[m] == inputs[NATIVE_V8 + "/" + MEAN] and output[w] == inputs[NEW_NATIVE + "/" + WORKER],
         "Frozen new mean/existing worker bytes changed")
    # The entire frozen mean is pinned/copied above, including all fourteen
    # selected weights, constructor/history/cache/math and clip6 source bytes.
    need(output[s].index(b"EXCLUDED_SOURCE55_PATH)) and") < output[s].index(gate_end.encode()) and
         output[s].index(b"EXCLUDED_SOURCE55_SHA),") < output[s].index(gate_end.encode()),
         "Source55 lexical path/SHA exclusions must precede the only selected read")
    need(section(output[s], gate_end, "    def receipt(self):") ==
         section(original[s], gate_end, "    def receipt(self):"),
         "Cache decode/guard/policy code changed")
    need(output[s].split(b"\ndef wait_start(", 1)[1] == original[s].split(b"\ndef wait_start(", 1)[1],
         "Safe barrier or actual close code changed")
    for first, following in (
        ('    audit.eq("wait.actual_waited"', "    try:"),
        ('        ids = dict(group_id=', "        caches, policies = [], []"),
        (close_start, '        rows=skill.get("pose_rows",[])'),
    ):
        # The wait prefix has another later try; select the first following one.
        left = first.encode()
        right = following.encode()
        def local_span(raw):
            need(raw.count(left) == 1, "Protected qualifier boundary changed")
            start = raw.index(left)
            return raw[start:raw.index(right, start + len(left))]
        need(local_span(output[q]) == local_span(original[q]), "Actual-wait/PID/low400/App-close proof changed")
    resource_start = b"\n  try:"
    final_prefix = b"   put('FINAL.json',dict(kind="
    need(section(output[v], resource_start, final_prefix) == section(original[v], resource_start, final_prefix),
         "Original parent resources, admission, actual wait or TERMINAL_ROWS changed")
    need(output[v].split(b"\n  except BaseException:", 1)[1] == original[v].split(b"\n  except BaseException:", 1)[1],
         "Original parent cleanup changed")
    need(output[v].count(b"rows=terminal") == 1 and b"assert len(children)==3" in output[v] and
         b"wait_until=time.monotonic()+1800" in output[v], "Original parent row shape/member count/wait changed")

    # Only syntax and static byte evidence: do not import or execute any source.
    need(len(output) == 13, "Exactly thirteen generated sources are required")
    parsed = 0
    for (group, name), raw in output.items():
        path = BASE / (NEW_NATIVE if group == "n" else NEW_PARENT) / name
        tree = ast.parse(raw.decode("utf-8"), filename=str(path))
        compile(tree, str(path), "exec", dont_inherit=True)
        parsed += 1
    need(parsed == 13, "One AST13/compile13 pass is required")

    # Recheck the sole allowed preexisting file immediately before exclusive writes.
    need({p.name for p in src.iterdir()} == {WORKER} and digest((src / WORKER).read_bytes()) == WORKER_PIN,
         "Preexisting strict worker/target inventory changed during preparation")
    need(not par.exists() and not par.is_symlink(), "Parent target appeared during preparation")
    par.mkdir()
    for (group, name), raw in output.items():
        if (group, name) == w:
            continue
        destination = (src if group == "n" else par) / name
        with destination.open("xb") as stream:
            stream.write(raw)
    need({p.name for p in src.iterdir()} == set(NATIVE_FILES) and
         {p.name for p in par.iterdir()} == set(PARENT_FILES), "Final output inventory differs from thirteen .py files")
    for (group, name), expected in output.items():
        need(((src if group == "n" else par) / name).read_bytes() == expected,
             "Written source bytes differ: " + name)
    print(json.dumps(dict(status="PASS", AST13=parsed, compile13=True, static_inverse_diff=True,
                         unchanged_dependencies=7, preexisting_worker_rewritten=False,
                         new_safe_source_sha256=safe_sha,
                         source_files=[dict(path=(NEW_NATIVE if g == "n" else NEW_PARENT) + "/" + f,
                                            bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                                       for (g, f), raw in output.items()]), indent=2))


if __name__ == "__main__":
    main()
