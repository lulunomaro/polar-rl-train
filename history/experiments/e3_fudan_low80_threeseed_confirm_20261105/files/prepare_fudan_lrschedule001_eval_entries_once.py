"""Prepare five UNUSED LR001 CLIs from the successful current lowstd005 entries.
Local Python-source text/AST only. No source import, model stat/read/decode,
connector, SDK, Torch, evaluation, subprocess, accounting or old-once execution.
This generator is the only executable preparation artifact; its caller runs it once.
"""
from pathlib import Path
import ast
import hashlib
import json

D = Path(__file__).resolve().parent
OLD_NATIVE = "source_fudan_frozen_native_eval_v6_lowstd005"
NEW_NATIVE = "source_fudan_frozen_native_eval_v7_lrschedule001"
OLD_PARENT = "source_fudan_frozen_parent_v6_lowstd005"
NEW_PARENT = "source_fudan_frozen_parent_v7_lrschedule001"
MEAN_SHA = "c2253bc20b40b09b0d5d131ddeee528a8eba708c48e9c74e2699212e12b3ccae"
OLD_MEAN_SHA = "8b44c3f9d1472acc24cc5f6ed150476af82743648265881eb746791f4b442210"
BRANCH = "FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_LOWSTD005_LRSCALE001"
SOURCE_KIND = "fdn_fresh_mlp_warm_1cd_n20000_timeout8_lowstd005_lrscale001"
WAIT_KIND = "FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V7_LRSCHEDULE001"
LOWSTD_SHA = "cc41bd5b8787a00be9a5d42fb7c52f8959344c9b58cedf9c24229211b4e55244"
ENTRIES = (
    ("stage_fudan_lowstd005_frozen_original_once.py", "stage_fudan_lrschedule001_frozen_original_once.py", 20017, "c64623fc771331d435f8d51d396efb1141d6ada9a8fe8c3d24be029d9f827815"),
    ("export_fudan_lowstd005_pi_for_mujoco_once.py", "export_fudan_lrschedule001_pi_for_mujoco_once.py", 25512, "b85c9ec0e4517ae38a3680df58f416581acb860010a17983edb056a6c649e333"),
    ("dispatch_fudan_lowstd005_frozen_original_once.py", "dispatch_fudan_lrschedule001_frozen_original_once.py", 8737, "bbc1d9cafc459766588553a43c7d37c96fea40dcd24360820dc377587030f8fc"),
    ("collect_fudan_lowstd005_frozen_original_once.py", "collect_fudan_lrschedule001_frozen_original_once.py", 14822, "e4cc68cd5a0726dd5134bb60c4d7f150304060be551d854634ba4a182d563896"),
    ("evaluate_fudan_lowstd005_pi_mujoco31_lowrise_once.py", "evaluate_fudan_lrschedule001_pi_mujoco31_lowrise_once.py", 11649, "04422da2c8d0bc2d0d40e93e6fc5ca0d9c1e8a0550e403b8f041f8bdd5680f55"),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Patch:
    def __init__(self, name, raw):
        self.name, self.raw, self.text, self.edits = name, raw, raw.decode("utf8"), []

    def edit(self, old, new, count=1):
        need(self.text.count(old) == count, ("Locate before any output", self.name, old, self.text.count(old), count))
        self.text = self.text.replace(old, new)
        self.edits.append((old, new, count))
        return self

    def finish(self):
        back = self.text
        for old, new, count in reversed(self.edits):
            need(back.count(new) == count, ("Reverse metadata boundary", self.name, new))
            back = back.replace(new, old)
        need(back.encode("utf8") == self.raw, ("Original entry byte reconstruction", self.name))
        return self.text


def assignment_values(tree):
    """Interpret string constants and string concatenation only, never source code."""
    values = {}

    def value(node):
        if isinstance(node, ast.Constant) and type(node.value) is str:
            return node.value
        if isinstance(node, ast.Name) and node.id in values:
            return values[node.id]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return value(node.left) + value(node.right)
        raise ValueError("Not a string-only metadata expression")

    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                values[node.targets[0].id] = value(node.value)
            except ValueError:
                pass
    return values


def frontdoor(text, ending):
    start = "    closed_path = Path(args.closed)\n"
    need(text.count(start) == text.count(ending) == 1, "Unique closed-metadata frontdoor anchors required")
    first, last = text.index(start), text.index(ending)
    need(first < last, "Frontdoor order changed")
    return text[first:last]


def main():
    need(all(not (D / dst).exists() for _, dst, _, _ in ENTRIES), "All five new CLI names must be unused")
    originals = {}
    for src, _, size, sha in ENTRIES:
        raw = (D / src).read_bytes()
        need((len(raw), hashlib.sha256(raw).hexdigest()) == (size, sha), ("Successful current v6 entry pin differs", src))
        originals[src] = raw
    mean_raw = (D / NEW_NATIVE / "frozen_sequence_mean.py").read_bytes()
    need(hashlib.sha256(mean_raw).hexdigest() == MEAN_SHA, "New LR001 extraction source pin differs")
    mean_tree = ast.parse(mean_raw, filename=NEW_NATIVE + "/frozen_sequence_mean.py")
    values = assignment_values(mean_tree)
    need(values["BRANCH_KIND"] == BRANCH and values["SOURCE_KIND"] == SOURCE_KIND and
         values["EXCLUDED_LOWSTD005_SHA"] == LOWSTD_SHA, "Actual new source declarations differ")
    labels = ("MOTHER", "EXCLUDED_N4096", "EXCLUDED_PREVIOUS_N20000", "EXCLUDED_TIMEOUT8", "EXCLUDED_FRESH25", "EXCLUDED_HEIGHTGATE", "EXCLUDED_LOWSTD005")
    paths = tuple(values[label + "_PATH"] for label in labels)
    shas = tuple(values[label + "_SHA"] for label in labels)
    need(len(set(paths)) == len(set(shas)) == 7, "Exactly seven actual excluded old inputs required")
    exclusions = "EXCLUDED_SOURCE_PATHS = " + repr(paths) + "\nEXCLUDED_SOURCE_SHAS = " + repr(shas) + "\n"
    patches = {src: Patch(src, raw) for src, raw in originals.items()}
    stage, export, dispatch, collect, nominal = (patches[row[0]] for row in ENTRIES)
    stage.edit(OLD_NATIVE, NEW_NATIVE).edit(OLD_PARENT, NEW_PARENT).edit("FDNLOWSTD005_FROZEN_", "FDNLR001_FROZEN_", 8)
    export.edit(OLD_NATIVE, NEW_NATIVE).edit("FDNLOWSTD005_PI_ONLY_EXPORT_", "FDNLR001_PI_ONLY_EXPORT_", 2).edit(OLD_MEAN_SHA, MEAN_SHA, 2)
    for patch in (stage, export):
        patch.edit("FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_LOWSTD005", BRANCH)
        patch.edit("fdn_fresh_mlp_warm_1cd_n20000_timeout8_lowstd005", SOURCE_KIND)
        patch.edit('["version"] == 6', '["version"] == 7', 4)
        patch.edit("Qualified version6 lowstd005 E3 full save required", "Qualified version7 LR001 E3 full save required")
        prefix = 'PREFIX = "FDNLR001_' + ("FROZEN_" if patch is stage else "PI_ONLY_EXPORT_") + '"\n'
        patch.edit(prefix, exclusions + prefix)
    old_sha_check = 'selected["sha256"] not in (MOTHER_SHA, SOURCE_4K_SHA, LEARNER_SHA, "3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e", "246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2", "bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2") and'
    stage.edit(old_sha_check, 'selected["sha256"] not in EXCLUDED_SOURCE_SHAS and\n          str(selected_path) not in EXCLUDED_SOURCE_PATHS and')
    old_init = '    need(init["learner_config"]["initial_std"] == .05, "Actual fresh learner initial policy STD0.05 required")\n'
    new_init = ('    for key, expected in dict(initial_std=.05, learning_rate=1e-5, min_learning_rate=1e-7,\n'
                '                              max_learning_rate=1e-4, encoder_learning_rate=.001).items():\n'
                '        need(init["learner_config"].get(key) == expected, "Actual fresh LR001 learner initialization differs: " + key)\n')
    stage.edit(old_init, new_init)
    stage.edit("SINGLE_GPU_E3_FDN_LOWSTD005_ORIGINAL_FRESH80_FROZEN_EVALUATION_PLAN", "SINGLE_GPU_E3_FDN_LR001_ORIGINAL_FRESH80_FROZEN_EVALUATION_PLAN")
    stage_end = "    # All closure validation above precedes every mkdir, connector import and upload.\n"
    export_end = "    # Every check above is the existing closed metadata gate, before marker/mkdir/connect.\n"
    stage_gate = frontdoor(stage.text, stage_end)
    export.edit(frontdoor(export.text, export_end), stage_gate)
    need(frontdoor(export.text, export_end) == stage_gate, "Export must share EXACT new stage frontdoor")
    export.edit("EXCLUDED_HEIGHTGATE_PATH,EXCLUDED_HEIGHTGATE_SHA\n", "EXCLUDED_HEIGHTGATE_PATH,EXCLUDED_HEIGHTGATE_SHA,EXCLUDED_LOWSTD005_PATH,EXCLUDED_LOWSTD005_SHA\n")
    export.edit("EXCLUDED_FRESH25_PATH,EXCLUDED_HEIGHTGATE_PATH))and", "EXCLUDED_FRESH25_PATH,EXCLUDED_HEIGHTGATE_PATH,EXCLUDED_LOWSTD005_PATH))and")
    export.edit("EXCLUDED_FRESH25_SHA,EXCLUDED_HEIGHTGATE_SHA),'Qualified own NEW N20000 source only'", "EXCLUDED_FRESH25_SHA,EXCLUDED_HEIGHTGATE_SHA,EXCLUDED_LOWSTD005_SHA),'Qualified own NEW N20000 source only'")
    dispatch.edit("FDNLOWSTD005_FROZEN_", "FDNLR001_FROZEN_", 8).edit("fdn_lowstd005_frozen_outer_wait.py", "fdn_lrschedule001_frozen_outer_wait.py", 2)
    collect.edit("FDNLOWSTD005_FROZEN_", "FDNLR001_FROZEN_", 4).edit("FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V6_LOWSTD005", WAIT_KIND)
    nominal.edit(OLD_NATIVE, NEW_NATIVE, 2).edit("FDN_LOWSTD005_MUJOCO31_", "FDN_LR001_MUJOCO31_", 2).edit(OLD_MEAN_SHA, MEAN_SHA)
    nominal.edit("p['schema_version']==6", "p['schema_version']==7")
    nominal.edit("'bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2')", "'bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2','" + LOWSTD_SHA + "')")
    texts = {dst: patches[src].finish() for src, dst, _, _ in ENTRIES}
    trees = {}
    for name, text in texts.items():
        tree = ast.parse(text, filename=name)
        compile(tree, name, "exec")
        trees[name] = tree
    export_tree = trees[ENTRIES[1][1]]
    remote = next(node.value.value for node in export_tree.body if isinstance(node, ast.Assign) and
                  any(isinstance(target, ast.Name) and target.id == "REMOTE_EXPORT" for target in node.targets))
    remote_tree = ast.parse(remote, filename="LR001_cpu_export.py")
    compile(remote_tree, "LR001_cpu_export.py", "exec")
    imported = {alias.name for node in ast.walk(remote_tree) if isinstance(node, ast.ImportFrom) and node.module == "frozen_sequence_mean" for alias in node.names}
    available = {node.name for node in mean_tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    available |= {target.id for node in mean_tree.body if isinstance(node, ast.Assign) for target in node.targets if isinstance(target, ast.Name)}
    required = {label + suffix for label in labels for suffix in ("_PATH", "_SHA")}
    need(imported <= available and required <= imported, ("Remote import names must all exist and include all seven old-input pairs", sorted(imported - available), sorted(required - imported)))
    need(remote.count("with Path(source['path']).open('rb')as stream:") == 1 and
         remote.count("root=torch.load(io.BytesIO(source_raw),map_location='cpu',weights_only=False)") == 1 and
         remote.index("EXCLUDED_LOWSTD005_SHA),'Qualified own NEW N20000 source only'") < remote.index("with Path(source['path']).open('rb')as stream:"),
         "Exactly one whole-source CPU read/decode after lexical path/SHA exclusions required")
    need('FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V6_LOWSTD005' not in texts[ENTRIES[3][1]] and WAIT_KIND in texts[ENTRIES[3][1]], "Collector must explicitly consume V7 LR001 wait qualification")
    dispatch_tree = trees[ENTRIES[2][1]]
    for node in ast.walk(dispatch_tree):
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in ("controller", "start") for target in node.targets):
            value = node.value
            need(isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and isinstance(value.func.value, ast.Constant) and type(value.func.value.value) is str, "Original dispatch literal remote script shape changed")
            remote_code = value.func.value.value
            remote_ast = ast.parse(remote_code, filename="LR001_dispatch_literal.py")
            compile(remote_ast, "LR001_dispatch_literal.py", "exec")
    before = ast.parse(originals[ENTRIES[4][0]], filename=ENTRIES[4][0])
    after = trees[ENTRIES[4][1]]
    preserved = ("body_contact_forces", "reset_pose", "run_case", "MotherMean")
    for name in preserved:
        old_node = next(node for node in before.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name)
        new_node = next(node for node in after.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name)
        need(ast.dump(old_node, include_attributes=False) == ast.dump(new_node, include_attributes=False), ("Nominal behavior AST must remain exact", name))
    need(all("eval_admission2" not in text and "zero_start_retryguard" not in text.lower() and "failedsource" not in text.lower() for text in texts.values()), "New LR001 purpose must not inherit Eval1 retryguard or failed-source generator")
    need(all(not (D / dst).exists() for dst in texts), "New five-entry namespace changed before publication")
    for name, text in texts.items():
        with (D / name).open("xb") as stream:
            stream.write(text.encode("utf8"))
    print(json.dumps(dict(files={name: dict(bytes=len(text.encode("utf8")), sha256=hashlib.sha256(text.encode("utf8")).hexdigest()) for name, text in texts.items()},
        CLI_AST_compile_checked_once=5, remote_export_AST_and_import_names_checked=True, dispatch_remote_literals_AST_checked=True,
        exact_shared_stage_export_frontdoor=True, original_nominal_four_AST_exact=True, lexical_old_input_exclusions=7,
        new_frozen_mean_sha256=MEAN_SHA, metadata_edits_reversible=True, generated_CLIs_executed=False,
        input_model_stat_read_hash_decode_operations=0, source_import_SDK_Torch_CPUfixture_SSH_GPU_C_Git_operations=0), indent=2))


if __name__ == "__main__":
    main()
