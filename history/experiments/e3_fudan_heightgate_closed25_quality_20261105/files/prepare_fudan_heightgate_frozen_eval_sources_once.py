"""Source-only, one-shot metadata adapter; this file has only been prepared.

Run explicitly only after the final training overlay is frozen. The generator
reads exactly the ten named v4 Python sources plus that final overlay's bytes.
It never imports/executes those sources, opens any PT, builds a fixture, launches
anything, or installs the training overlay into the original N80 evaluator.
The only publications are the ten Python files in the two absent v5 directories.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import ast
import hashlib
from pathlib import Path


D = Path("F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104")
SOURCE_DIRS = {
    "native": D / "source_fudan_frozen_native_eval_v4_fresh1cd_timeout8",
    "parent": D / "source_fudan_frozen_parent_v4_fresh1cd_timeout8",
}
OUTPUT_DIRS = {
    "native": D / "source_fudan_frozen_native_eval_v5_lowheightgate",
    "parent": D / "source_fudan_frozen_parent_v5_lowheightgate",
}
FINAL_OVERLAY = D / "source_task_runtime_v3_lowheightgate" / "e3_fudan_task_runtime_v1.py"
FILES = {
    "native": (
        "frozen_sequence_mean.py",
        "fudan_frozen_eval_safe.py",
        "worker_fudan_original_n80.py",
        "resume_runtime_contracts_v3.py",
        "app_close_semantics_v6.py",
        "n80_gpu_capacity.py",
        "launch_storage_contract.py",
    ),
    "parent": (
        "fudan_eval_parent_wait_contract_v1.py",
        "fudan_task_contract_v2.py",
        "single_gpu_group_supervisor.py",
    ),
}
PINNED_INPUT_SHA = {
    ("native", "frozen_sequence_mean.py"):
        "b183b7d3b0e168220ffdbdfb9d25187266ee8e62e9b289ce41af59ebc405ea0f",
    ("native", "fudan_frozen_eval_safe.py"):
        "9d3f5dfe1cbaf955670d87a4315d2c67f19d3c2bd638d175ec29e4cb54fb4e89",
    ("parent", "fudan_eval_parent_wait_contract_v1.py"):
        "206187777e83b6466e0ced15cbfbfb322112b8db71181b9ef937e686379bc785",
}
OLD_OVERLAY_SHA = "386107b02983505518e1dcfb5bbdeb6f243392d390dfd48e16a61d75cb2c51e2"
OLD_OVERLAY_BYTES = 8571
OLD_SAFE_SHA = PINNED_INPUT_SHA[("native", "fudan_frozen_eval_safe.py")]
OLD_BRANCH = "FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8"
NEW_BRANCH = OLD_BRANCH + "_HEIGHTGATE"
OLD_SOURCE = "fdn_fresh_mlp_warm_1cd_n20000_timeout8"
NEW_SOURCE = OLD_SOURCE + "_heightgate"
EXCLUDED_FRESH25_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_W8_ADMISSION2_20261105_013118_1793813478778262400/roles/E3/production/fudan_seq_full_u000025_c00001200_s0002.pt"
EXCLUDED_FRESH25_SHA = "246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2"
TIMEOUT8_SHA = "3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e"


def need(condition: bool, message: str) -> None:
    # Keep fail-closed checks active even if the caller selects python -O.
    if not condition:
        raise AssertionError(message)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def utf8_lf(raw: bytes, label: str) -> str:
    need(bool(raw) and raw.endswith(b"\n"), label + ": missing complete final LF")
    need(b"\r" not in raw and not raw.startswith(b"\xef\xbb\xbf"),
         label + ": expected existing UTF-8 LF bytes, not newline/BOM conversion")
    text = raw.decode("utf-8", errors="strict")
    need(text.encode("utf-8") == raw, label + ": UTF-8 round trip differs")
    return text


def require_absent_outputs() -> None:
    for directory in OUTPUT_DIRS.values():
        need(not directory.exists() and not directory.is_symlink(),
             "One-shot output already exists (including symlink): " + str(directory))


class MetadataPatch:
    """Counted literal edits plus an exact reverse-diff proof, never code evaluation."""

    def __init__(self, name: str, raw: bytes):
        self.name = name
        self.original = raw
        self.text = utf8_lf(raw, name)
        self.edits: list[tuple[str, str, str, int]] = []

    def replace(self, label: str, old: str, new: str, *, count: int = 1) -> None:
        need(bool(old) and type(count) is int and count > 0, self.name + ": invalid anchor")
        need(all(previous[0] != label for previous in self.edits),
             self.name + ": duplicate metadata edit label " + label)
        actual = self.text.count(old)
        need(actual == count,
             f"{self.name}:{label}: expected {count} actual old anchors, found {actual}: {old!r}")
        self.text = self.text.replace(old, new)
        self.edits.append((label, old, new, count))

    def finish(self, allowed_labels: tuple[str, ...]) -> bytes:
        need(tuple(edit[0] for edit in self.edits) == allowed_labels,
             self.name + ": metadata edit allowlist/order differs")
        restored = self.text
        for label, old, new, count in reversed(self.edits):
            actual = restored.count(new)
            need(actual == count,
                 f"{self.name}:{label}: inverse anchor count {actual} != {count}")
            restored = restored.replace(new, old)
        need(restored.encode("utf-8") == self.original,
             self.name + ": change outside the counted metadata-only diff")
        raw = self.text.encode("utf-8")
        utf8_lf(raw, self.name)
        return raw


def adapt_mean(raw: bytes, overlay_size: int, overlay_sha: str) -> bytes:
    patch = MetadataPatch("frozen_sequence_mean.py", raw)
    patch.replace("branch_kind",
                  f'BRANCH_KIND = "{OLD_BRANCH}"\n',
                  f'BRANCH_KIND = "{NEW_BRANCH}"\n')
    patch.replace("source_kind",
                  f'SOURCE_KIND = "{OLD_SOURCE}"\n',
                  f'SOURCE_KIND = "{NEW_SOURCE}"\n')
    old = f'EXCLUDED_TIMEOUT8_SHA = "{TIMEOUT8_SHA}"\n'
    patch.replace("fresh25_lexical_constants", old,
                  old + f'EXCLUDED_FRESH25_PATH = "{EXCLUDED_FRESH25_PATH}"\n'
                      + f'EXCLUDED_FRESH25_SHA = "{EXCLUDED_FRESH25_SHA}"\n')
    patch.replace("training_overlay_sha",
                  f'TASK_RUNTIME_OVERLAY_SHA = "{OLD_OVERLAY_SHA}"\n',
                  f'TASK_RUNTIME_OVERLAY_SHA = "{overlay_sha}"\n')
    patch.replace("training_overlay_bytes",
                  f'TASK_RUNTIME_OVERLAY_BYTES = {OLD_OVERLAY_BYTES}\n',
                  f'TASK_RUNTIME_OVERLAY_BYTES = {overlay_size}\n')
    patch.replace("root_version5",
                  '    _require(root["kind"] == KIND and type(root["version"]) is int and root["version"] == 4,\n'
                  '             "checkpoint: wrong kind/version4")\n',
                  '    _require(root["kind"] == KIND and type(root["version"]) is int and root["version"] == 5,\n'
                  '             "checkpoint: wrong kind/version5")\n')
    patch.replace("receipt_schema5",
                  '    return dict(kind=KIND, run=run, schema_version=4, training_num_envs=20000,\n',
                  '    return dict(kind=KIND, run=run, schema_version=5, training_num_envs=20000,\n')
    return patch.finish(("branch_kind", "source_kind", "fresh25_lexical_constants",
                         "training_overlay_sha", "training_overlay_bytes", "root_version5",
                         "receipt_schema5"))


def adapt_safe(raw: bytes) -> bytes:
    patch = MetadataPatch("fudan_frozen_eval_safe.py", raw)
    # This original file has no overlay pin. Do not invent an overlay installation.
    need(patch.text.count(OLD_OVERLAY_SHA) == 0 and patch.text.count(str(OLD_OVERLAY_BYTES)) == 0,
         "Unexpected training-overlay pin in original safe module")
    patch.replace("fresh25_import",
                  'EXCLUDED_N4096_PATH, EXCLUDED_N4096_SHA)\n',
                  'EXCLUDED_N4096_PATH, EXCLUDED_N4096_SHA, EXCLUDED_FRESH25_PATH, EXCLUDED_FRESH25_SHA)\n')
    patch.replace("fresh25_normalized_path_tuple",
                  'EXCLUDED_PREVIOUS_N20000_PATH, EXCLUDED_TIMEOUT8_PATH)) and\n',
                  'EXCLUDED_PREVIOUS_N20000_PATH, EXCLUDED_TIMEOUT8_PATH, EXCLUDED_FRESH25_PATH)) and\n')
    patch.replace("fresh25_sha_tuple",
                  'EXCLUDED_PREVIOUS_N20000_SHA, EXCLUDED_TIMEOUT8_SHA),\n',
                  'EXCLUDED_PREVIOUS_N20000_SHA, EXCLUDED_TIMEOUT8_SHA, EXCLUDED_FRESH25_SHA),\n')
    patch.replace("fresh25_exclusion_diagnostic",
                  'Selected fresh1cd save must not be 1cd, 47937, 8af4 or 3e64 old input',
                  'Selected fresh1cd HEIGHTGATE save must not be 1cd, 47937, 8af4, 3e64 or 246ac6 old input')
    return patch.finish(("fresh25_import", "fresh25_normalized_path_tuple", "fresh25_sha_tuple",
                         "fresh25_exclusion_diagnostic"))


def adapt_parent(raw: bytes, overlay_size: int, overlay_sha: str, safe_sha: str) -> bytes:
    patch = MetadataPatch("fudan_eval_parent_wait_contract_v1.py", raw)
    # Actual full new safe-file bytes bind both the docstring and route constant.
    patch.replace("both_full_safe_route_sha_pins", OLD_SAFE_SHA, safe_sha, count=2)
    patch.replace("branch_kind",
                  f'_BRANCH_KIND = "{OLD_BRANCH}"\n',
                  f'_BRANCH_KIND = "{NEW_BRANCH}"\n')
    patch.replace("source_kind",
                  f'_SOURCE_KIND = "{OLD_SOURCE}"\n',
                  f'_SOURCE_KIND = "{NEW_SOURCE}"\n')
    patch.replace("training_overlay_sha",
                  f'_TRAINING_OVERLAY_SHA = "{OLD_OVERLAY_SHA}"\n',
                  f'_TRAINING_OVERLAY_SHA = "{overlay_sha}"\n')
    patch.replace("training_overlay_bytes",
                  f'audit.fields("source.training_overlay", overlay, dict(bytes={OLD_OVERLAY_BYTES}, sha256=_TRAINING_OVERLAY_SHA))\n',
                  f'audit.fields("source.training_overlay", overlay, dict(bytes={overlay_size}, sha256=_TRAINING_OVERLAY_SHA))\n')
    patch.replace("receipt_schema5",
                  'source_checkpoint_sha256=_MOTHER_SHA, schema_version=4,\n',
                  'source_checkpoint_sha256=_MOTHER_SHA, schema_version=5,\n')
    patch.replace("qualification_kind",
                  'FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V4_FRESH1CD',
                  'FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V5_HEIGHTGATE')
    # Mirror only metadata-string exclusions; no model filesystem operation.
    old = f'_EXCLUDED_TIMEOUT8_SHA = "{TIMEOUT8_SHA}"\n'
    patch.replace("fresh25_lexical_constants", old,
                  old + f'_EXCLUDED_FRESH25_PATH = "{EXCLUDED_FRESH25_PATH}"\n'
                      + f'_EXCLUDED_FRESH25_SHA = "{EXCLUDED_FRESH25_SHA}"\n')
    patch.replace("fresh25_sha_tuple",
                  '_EXCLUDED_PREVIOUS_N20000_SHA, _EXCLUDED_TIMEOUT8_SHA))\n',
                  '_EXCLUDED_PREVIOUS_N20000_SHA, _EXCLUDED_TIMEOUT8_SHA, _EXCLUDED_FRESH25_SHA))\n')
    patch.replace("fresh25_normalized_path_tuple",
                  '(_MOTHER_PATH, _EXCLUDED_N4096_PATH, _EXCLUDED_PREVIOUS_N20000_PATH, _EXCLUDED_TIMEOUT8_PATH)))\n',
                  '(_MOTHER_PATH, _EXCLUDED_N4096_PATH, _EXCLUDED_PREVIOUS_N20000_PATH, _EXCLUDED_TIMEOUT8_PATH, _EXCLUDED_FRESH25_PATH)))\n')
    return patch.finish(("both_full_safe_route_sha_pins", "branch_kind", "source_kind",
                         "training_overlay_sha", "training_overlay_bytes", "receipt_schema5",
                         "qualification_kind", "fresh25_lexical_constants", "fresh25_sha_tuple",
                         "fresh25_normalized_path_tuple"))


def exact_tail(text: str, anchor: str, label: str) -> str:
    need(text.count(anchor) == 1, label + ": protected-tail anchor count differs")
    return text[text.index(anchor):]


def exact_between(text: str, start: str, end: str, label: str) -> str:
    need(text.count(start) == text.count(end) == 1,
         label + ": protected-range anchor count differs")
    first, last = text.index(start), text.index(end)
    need(first < last, label + ": protected-range order differs")
    return text[first:last]


def check_preserved_contracts(originals: dict, outputs: dict) -> None:
    protected_tails = {
        ("native", "frozen_sequence_mean.py"): '\ndef extract_pi_state_dict(',
        ("native", "fudan_frozen_eval_safe.py"):
            '\n        self.raw = Path(self.binding["path"]).read_bytes()\n',
        ("parent", "fudan_eval_parent_wait_contract_v1.py"):
            '\n        close = audit.mapping("intent.original_bound_close", intent.get("original_bound_close"))\n',
    }
    for key, anchor in protected_tails.items():
        before, after = originals[key].decode("utf-8"), outputs[key].decode("utf-8")
        need(exact_tail(before, anchor, str(key)) == exact_tail(after, anchor, str(key)),
             str(key) + ": inference/cache/barrier/close/acceptance suffix changed")
    key = ("parent", "fudan_eval_parent_wait_contract_v1.py")
    before, after = originals[key].decode("utf-8"), outputs[key].decode("utf-8")
    start = '\n    audit.eq("wait.actual_waited", actual_waited, True)\n'
    end = '\n        binding = dict(path=t.get("source_path"), bytes=t.get("source_bytes"),\n'
    need(exact_between(before, start, end, "original actual wait/task") ==
         exact_between(after, start, end, "original actual wait/task"),
         "Original actual-wait/task/resource checks changed")
    need(exact_between(before, '\ndef _same(', '\ndef qualify_waited_eval(', "parent helpers") ==
         exact_between(after, '\ndef _same(', '\ndef qualify_waited_eval(', "parent helpers"),
         "Original parent JSON/error/metadata-reading helpers changed")


def main() -> None:
    require_absent_outputs()
    originals = {}
    for group, names in FILES.items():
        for name in names:
            key = (group, name)
            raw = (SOURCE_DIRS[group] / name).read_bytes()
            utf8_lf(raw, str(SOURCE_DIRS[group] / name))
            if key in PINNED_INPUT_SHA:
                need(sha256(raw) == PINNED_INPUT_SHA[key], "Original input SHA differs: " + str(key))
            originals[key] = raw
    need(len(originals) == 10, "Expected exactly seven native plus three parent sources")

    # Intentionally deferred until explicit invocation, after the other owner has
    # finalized this file. Never read a partial overlay while preparing this script.
    overlay_raw = FINAL_OVERLAY.read_bytes()
    overlay_size, overlay_sha = len(overlay_raw), sha256(overlay_raw)
    need(overlay_size > 0 and overlay_sha != OLD_OVERLAY_SHA,
         "Final HEIGHTGATE training overlay is empty or still the old overlay")

    outputs = dict(originals)
    mean_key = ("native", "frozen_sequence_mean.py")
    safe_key = ("native", "fudan_frozen_eval_safe.py")
    parent_key = ("parent", "fudan_eval_parent_wait_contract_v1.py")
    outputs[mean_key] = adapt_mean(originals[mean_key], overlay_size, overlay_sha)
    outputs[safe_key] = adapt_safe(originals[safe_key])
    safe_sha = sha256(outputs[safe_key])
    need(safe_sha != OLD_SAFE_SHA, "New complete safe source unexpectedly has the old SHA")
    outputs[parent_key] = adapt_parent(originals[parent_key], overlay_size, overlay_sha, safe_sha)

    changed = {key for key in originals if outputs[key] != originals[key]}
    need(changed == set(PINNED_INPUT_SHA), "Only the three metadata modules may differ")
    unchanged = set(originals) - set(PINNED_INPUT_SHA)
    need(len(unchanged) == 7 and all(outputs[key] == originals[key] for key in unchanged),
         "Other seven Python files must remain BYTE identical")
    check_preserved_contracts(originals, outputs)
    need(OLD_SAFE_SHA.encode("ascii") not in outputs[parent_key] and
         outputs[parent_key].count(safe_sha.encode("ascii")) == 2,
         "Both parent zero-argument-close source pins must use the full new safe SHA")
    for key in (mean_key, parent_key):
        need(OLD_OVERLAY_SHA.encode("ascii") not in outputs[key] and
             outputs[key].count(overlay_sha.encode("ascii")) == 1,
             "Final training-overlay SHA binding differs: " + str(key))

    # Exactly one syntax AST and one in-memory compile per generated module.
    # No exec/eval/importlib/runpy/py_compile, model decode, fixture or pyc output.
    identities = []
    for (group, name), raw in outputs.items():
        destination = OUTPUT_DIRS[group] / name
        text = utf8_lf(raw, str(destination))
        tree = ast.parse(text, filename=str(destination), mode="exec")
        code = compile(tree, str(destination), "exec", dont_inherit=True, optimize=0)
        del code, tree
        identities.append((destination, len(raw), sha256(raw)))
    need(len(identities) == 10, "Expected ten syntax-only compile checks")

    # All input pins, edit counts, exact reverse diffs, seven byte copies and ten
    # syntax checks have passed BEFORE creating either directory or any output.
    require_absent_outputs()
    for directory in OUTPUT_DIRS.values():
        directory.mkdir(parents=False, exist_ok=False)
    for (group, name), raw in outputs.items():
        destination = OUTPUT_DIRS[group] / name
        with destination.open("xb") as stream:
            need(stream.write(raw) == len(raw), "Short Python-source write: " + str(destination))

    print(f"FINAL_TRAINING_OVERLAY_METADATA_ONLY path={FINAL_OVERLAY} bytes={overlay_size} SHA256={overlay_sha}")
    for destination, size, digest in identities:
        print(f"{destination} bytes={size} SHA256={digest}")
    print("source_only=True native=0 deployed=0 source_imports=0 PT_opens=0 SDK=0 Torch=0 fixtures=0")
    print("metadata_adapted=3 other7_BYTE_identical=True syntax_AST_compile=10 training_overlay_installed_in_eval=False")


if __name__ == "__main__":
    main()
