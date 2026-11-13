"""Archive this evaluation using record_experiment in the task's private partial clone.

The helper's commit call uses Git plumbing, because ordinary commit status in
this intentionally unpopulated clone tries to fetch unrelated missing blobs.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = Path(r"C:\Users\lulu\.codex\scratch\sim2real_20261113\polar")
REL = Path("history/reviews/20261113-mod4v3-r1-gas200-stand-test")
EXPERIMENT_ID = "mod4v3-r1-gas200-stand-test"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args, data=None):
    env = os.environ.copy()
    env["GIT_NO_LAZY_FETCH"] = "1"
    return subprocess.run(["git", "-c", "diff.renames=false", "-c", "status.renames=false",
                           "-C", str(REPO), *args], input=data, check=True, capture_output=True,
                          text=True, encoding="utf-8", env=env).stdout.strip()


if __name__ == "__main__":
    assert git("branch", "--show-current") == "main"
    assert not git("diff-index", "--cached", "--no-renames", "--name-only", "HEAD")
    assert not (REPO / REL).exists(), "Do not overwrite an earlier archive or rerun this stage"
    source_identity = json.loads((ROOT / "SOURCE_IDENTITY.json").read_text(encoding="utf-8"))
    artifacts = []
    selected = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.name == "ARTIFACT_INDEX.json":
            continue
        local = p.relative_to(ROOT)
        row = dict(source=str(p), relative=local.as_posix(), bytes=p.stat().st_size, SHA256=sha(p))
        if p.suffix.lower() in {".md", ".py", ".json", ".csv", ".png", ".log"}:
            dest = REPO / REL / local
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)
            row.update(status="full", archive=(REL / local).as_posix(), archive_SHA256=sha(dest))
            selected.append((REL / local).as_posix())
        else:
            row.update(status="external_original_index", reason="Keep ONNX, NPZ, animation and other binary originals at source")
        artifacts.append(row)
    inputs = []
    asset = Path(source_identity["asset"])
    for rel in ("mjcf/scene.xml", "runtime_config.json", "semantics.json", "model_parameters.json",
                "legacy/model_parameters.json", "legacy/reports/model_manifest.json"):
        p = asset / rel
        inputs.append(dict(path=str(p), bytes=p.stat().st_size, SHA256=sha(p), status="unchanged_external_input"))
    p = Path(r"F:\RMPOLAR-RL\mod4v3_limit_fold_pose_20261113\POSE_RESULT.json")
    inputs.append(dict(path=str(p), bytes=p.stat().st_size, SHA256=sha(p), status="previous_pose_stage_input"))
    manifest = dict(stage="MOD4V3_R1_GAS200_STAND_TEST", artifacts=artifacts, inputs=inputs,
                    policy_source=source_identity, manifest_self_hash_not_recursive=True)
    index = ROOT / "ARTIFACT_INDEX.json"
    index.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(index, REPO / REL / index.name)
    selected.append((REL / index.name).as_posix())

    helper = REPO / "archive_tools/record_experiment.py"
    sys.path.insert(0, str(helper.parent))
    spec = importlib.util.spec_from_file_location("_record_gas200_stand_evaluation", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    base = git("rev-parse", "HEAD")

    def archive_git(*args):
        if args[0] == "commit":
            assert args[1] == "-m"
            tree = git("write-tree", "--missing-ok")
            changed = git("diff-tree", "--no-commit-id", "--name-only", "--no-renames", "-r", base, tree).splitlines()
            record_rel = "history/experiments/20261113-" + EXPERIMENT_ID + ".json"
            assert set(changed) == set(selected) | {record_rel}
            commit = git("commit-tree", tree, "-p", base, data=args[2] + "\n")
            git("update-ref", "refs/heads/main", commit, base)
            return commit
        return git(*args)

    module.git = archive_git
    sys.argv = [str(helper), "--id", EXPERIMENT_ID,
                "--title", "Test selected MOD4v3 R1 policy standing from exact gas200 rear-ground pose",
                "--kind", "evaluation", "--note-file", str(ROOT / "README.md"),
                "--validation", "Frozen R1/22959; exact 37D initial qpos; 3x12s actual MuJoCo; direct stand from0.74s to12s; forward drift explicit; zero-torque stays stowed; initial parity-unit caller failure retained; no training or hardware",
                "--files", *selected]
    module.main()
    print(json.dumps(dict(commit=git("rev-parse", "HEAD"), archived_files=len(selected), inputs=len(inputs))))
