"""Select only this round and its intended documentation updates for the existing trial recorder."""
from pathlib import Path
import hashlib,json,subprocess,sys
T=Path(__file__).resolve().parent
R=T.parents[2]
A=Path(r"D:\claude2\fangzhen\tmp\step7_mixed_archive_20261111")
assert (T/"FINAL_REPORT.md").exists() and (T/"evidence/SELECTED_TRAINED_CANDIDATE.json").exists()
allowed=[str(T.relative_to(R)).replace("\\","/"),"README.md","docs/DR_TRAINING_INDEX_20261111.md","docs/DR_TRAINING_RESUME_20261111.md","sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json","sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md","sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md"]
def git(*args):return subprocess.run(["git","-C",str(R),*args],capture_output=True,text=True,check=True).stdout
assert not git("diff","--cached","--name-only").strip()
selected=set()
for args in [("diff","--name-only","--",*allowed),("ls-files","--others","--exclude-standard","--",*allowed)]:
    selected.update(x for x in git(*args).splitlines() if x)
selected=sorted(selected)
assert selected and all((R/x).is_file() for x in selected)
assert not any("MOD4V3_SCUT_INCREMENTAL_DR_20261109/" in x for x in selected)
assert all((R/x).stat().st_size<50_000_000 for x in selected)
A.mkdir(exist_ok=True)
(A/"selected_final.json").write_text(json.dumps(selected,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(A/"selected_final.nul").write_bytes(b"\0".join(x.encode() for x in selected)+b"\0")
(A/"FINAL_NOTE.md").write_bytes((T/"FINAL_REPORT.md").read_bytes())
print(json.dumps(dict(files=len(selected),weight_files=sum(x.endswith('.pt') for x in selected),bytes=sum((R/x).stat().st_size for x in selected),selection=str(A/"selected_final.json"),staging_paths=str(A/"selected_final.nul")),ensure_ascii=False))
