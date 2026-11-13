"""Archive this completed local pose stage using the existing project workflow."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=Path(r"C:\Users\lulu\.codex\scratch\sim2real_20261113\polar")
REL=Path("history/reviews/20261113-mod4v3-gas200-rear-ground-pose")
DEST=REPO/REL

def git(*args):
    return subprocess.check_output(["git","-C",str(REPO),*args])

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__=="__main__":
    # This is the task's disposable no-checkout clone. Populate its index from
    # main without changing the user's working repository or checking out assets.
    assert git("branch","--show-current").decode().strip()=="main"
    git("read-tree","HEAD")
    assert not git("diff","--cached","--name-only").strip()
    for name in ("record_experiment.py","capture_history.py"):
        path=REPO/"archive_tools"/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(git("show","HEAD:archive_tools/"+name))
    (REPO/"history/experiments").mkdir(parents=True,exist_ok=True)
    DEST.mkdir(parents=True,exist_ok=True)
    rows=[]
    selected=[]
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.name=="ARTIFACT_INDEX.json":
            continue
        rel=path.relative_to(ROOT)
        row=dict(source=str(path),relative=rel.as_posix(),bytes=path.stat().st_size,SHA256=sha(path))
        if path.suffix.lower() in {".py",".json",".md",".txt",".log",".png"}:
            target=DEST/rel
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(path,target)
            row.update(status="full",archive=(REL/rel).as_posix(),archive_SHA256=sha(target))
            selected.append((REL/rel).as_posix())
        else:
            row.update(status="external_original_index",reason="Keep NPZ, animation and binary originals at their source")
        rows.append(row)
    asset=Path(r"F:\RMPOLAR-RL\mod4v3_scut_semantics_20261106\review_r3\corrected")
    inputs=[]
    for rel in ("mjcf/scene.xml","kinematics.py","semantics.py","runtime_config.json","model_parameters.json",
                "legacy/kinematics_v2.py","legacy/model_parameters.json","legacy/reports/model_manifest.json"):
        path=asset/rel
        inputs.append(dict(path=str(path),bytes=path.stat().st_size,SHA256=sha(path),status="unchanged_external_input"))
    manifest=dict(stage="MOD4V3_GAS200_REAR_GROUND_STATIC_POSE",artifacts=rows,inputs=inputs,
                  manifest_self_hash_not_recursive=True,live_viewer_state_is_capture_time_only=True)
    index=ROOT/"ARTIFACT_INDEX.json"
    index.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    shutil.copyfile(index,DEST/index.name)
    selected.append((REL/index.name).as_posix())
    command=[sys.executable,str(REPO/"archive_tools/record_experiment.py"),
             "--id","mod4v3-gas200-rear-ground-pose",
             "--title","Record MOD4v3 gas-200mm guide and rear-wheel ground pose",
             "--kind","diagnostic","--note-file",str(ROOT/"README.md"),
             "--validation","Static geometry only: 200mm gas springs, four bottom guides and both rear tires at floor; limits and closure checked; superseded candidates retained; no policy or hardware run.",
             "--files",*selected]
    result=subprocess.run(command,cwd=REPO,capture_output=True,text=True,encoding="utf-8",errors="replace")
    print(result.stdout)
    print(result.stderr)
    if result.returncode:raise SystemExit(result.returncode)
    print(json.dumps(dict(archive=str(DEST),files=len(selected),input_files=len(inputs)),ensure_ascii=False))
