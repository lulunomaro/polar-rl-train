"""Preserve one already evaluated checkpoint and its exact recipe; no training."""
from pathlib import Path
import argparse,base64,hashlib,json,shutil,stat,sys,time
TRIAL=Path(__file__).resolve().parent
ROOT=TRIAL.parents[3]
sys.path.insert(0,str(ROOT/"tmp"))
from step7_remote_access import connect
p=argparse.ArgumentParser();p.add_argument("--model",required=True);p.add_argument("--reason",required=True);p.add_argument("--secondary",action="store_true");a=p.parse_args()
plan=json.loads((TRIAL/"PLAN.json").read_text(encoding="utf-8"))
index=json.loads((TRIAL/"evidence/MODEL_ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
summary=json.loads((TRIAL/"evidence/ROUND_SUMMARY.json").read_text(encoding="utf-8"))
row=next(x for x in index["models"] if x["id"]==a.model)
label=a.model.replace("remaining_","").replace("m","")
paired_label="remaining_"+label
assert any(x["model"]==paired_label and x["variant"]=="Step7_all_remaining_DR" for x in summary["models"])
folder="step7_remaining_dr_"+label+"m_candidate_20261111"
local=ROOT/"frozen_models"/folder
assert not local.exists(),"Preserved candidate already exists; do not replace"
local.mkdir()
source=ROOT/"_mod4v2_src_20261106"/row["git_path"]
dest=local/source.name;shutil.copyfile(source,dest)
assert hashlib.sha256(dest.read_bytes()).hexdigest()==row["sha256"]
dest.chmod(stat.S_IREAD)
remote=plan["root"]+"/frozen/"+folder
code="""from pathlib import Path
import hashlib,json,shutil,stat,subprocess
src=Path(SOURCE);out=Path(DEST);out.mkdir(exist_ok=False)
assert hashlib.sha256(src.read_bytes()).hexdigest()==EXPECTED
dst=out/src.name;shutil.copyfile(src,dst);dst.chmod(0o444)
print(json.dumps({'path':str(dst),'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'mode':oct(dst.stat().st_mode&0o777),'gpu_compute_processes':subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout.strip()}))
""".replace("SOURCE",repr(row["original_remote_path"]),1).replace("DEST",repr(remote),1).replace("EXPECTED",repr(row["sha256"]),1)
c=connect()
try:
 command="python3 -c \"import base64;exec(base64.b64decode('"+base64.b64encode(code.encode()).decode()+"'))\""
 _,out,err=c.exec_command(command,timeout=40);text=out.read().decode();error=err.read().decode();assert out.channel.recv_exit_status()==0,error
 remote_receipt=json.loads(text)
finally:c.close()
assert remote_receipt["sha256"]==row["sha256"]
selection=dict(selected=paired_label,model_id=a.model,iteration=row["iteration"],sha256=row["sha256"],local_path=str(dest),remote=remote_receipt,parent="push_020m",parent_sha256=plan["parent_sha256"],main_frozen_sha256=plan["baseline_main_frozen_sha256"],role=("alternate highest total-task candidate" if a.secondary else "best forward-error combinedDR continuation candidate; not promoted"),reason=a.reason,paired_statistics=next(x for x in summary["models"] if x["model"]==paired_label and x["variant"]=="Step7_all_remaining_DR"),main_baseline_replaced=False,rough_started=False)
(TRIAL/"evidence"/("ALTERNATE_TRAINED_CANDIDATE.json" if a.secondary else "SELECTED_TRAINED_CANDIDATE.json")).write_text(json.dumps(selection,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
recipe=dict(checkpoint=selection,plan=plan,source_directory=str(TRIAL),training_method=json.loads((TRIAL/"evidence/train040m_remaining_r1_PPO_EFFECTIVE.json").read_text()),source_files={str(p.relative_to(TRIAL)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in (TRIAL/"support").rglob('*') if p.is_file() and p.suffix in ('.py','.json','.yaml')},evaluation_evidence="evidence/paired_final_r1_RESULT.json",resume_scope="complete PPO/globalRNG; fresh physical episode; not exact physical-state restore")
data=(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n").encode()
(local/"RECIPE.json").write_bytes(data);(TRIAL/"evidence"/("ALTERNATE_RECIPE.json" if a.secondary else "SELECTED_RECIPE.json")).write_bytes(data)
c=connect()
try:
 s=c.open_sftp()
 with s.open(remote+"/RECIPE.json","wb") as f:f.write(data)
 s.chmod(remote+"/RECIPE.json",0o444)
 with s.open(remote+"/RECIPE.json","rb") as f:assert f.read()==data
 s.close()
finally:c.close()
print(json.dumps({k:selection[k] for k in ('model_id','iteration','sha256','local_path','remote','reason')},ensure_ascii=False,indent=2))
