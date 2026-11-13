"""Archive this new viewer and frozen teacher-retention diagnostic once."""
from pathlib import Path
import json,sys,subprocess,tempfile
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/"evidence/retained_abilities_r1"
assert (E/"SUMMARY.json").is_file()
sys.path.insert(0,str(R.parent/"tmp/step7_archive_helper"))
import record_experiment as rec
original=rec.git
NET=("-c","http.proxy=http://127.0.0.1:7897","-c","http.sslVerify=true")
def git(*args):
 if args[0]=="add":return original("--literal-pathspecs",*NET,"add","--sparse","-f",*args[1:])
 if args[0]=="tag" and "-m" in args:
  i=args.index("-m")
  with tempfile.NamedTemporaryFile(mode="w",encoding="utf8",newline="\n",dir=R.parent/"tmp",prefix="teacher-retention-tag-",delete=False) as f:
   f.write(args[i+1]);path=Path(f.name)
  try:return original(*NET,*args[:i],"-F",str(path),*args[i+2:])
  finally:path.unlink()
 return original(*NET,*args)
rec.git=git
branch=git("branch","--show-current")
assert branch=="mod4v1-experts-fulldr-rm70"
ID="stair-teacher-view-retention-01";TAG="trial-20261113-"+ID
assert not git("tag","--list",TAG),"Already recorded; only push existing objects if sync is pending"
files=[T/name for name in ("README.md","FINAL_REPORT.md","weights/SELECTED_STAIR_TEACHER.json","manual_replay/teacher_player.py","manual_replay/TEACHER_PLAYER.md","manual_replay/TEACHER_PLAYER_READY.json","evaluate_retained_abilities.py","summarize_retained_abilities.py","archive_teacher_view_and_retention.py")]
files += [p for p in sorted(E.rglob("*")) if p.is_file() and p.suffix in (".json",".md",".py",".log")]
main_before=git("ls-remote","origin","refs/heads/main").split()[0]
sys.argv=["record_experiment.py","--id",ID,"--title","Record controllable stair teacher and paired flat/rough retention evidence","--kind","diagnostic","--note-file",str(E/"REPORT.md"),"--validation","Frozen715c teacher; successful visible200mmx2 demonstration; original flat60 plus paired parent/teacher Rough-v1 L9 traverse/gyro/landing; no optimizer or training; source and all diagnostic reports archived","--files",*[p.relative_to(R).as_posix() for p in dict.fromkeys(files)]]
rec.main()
head=git("rev-parse","HEAD");obj=git("rev-parse",TAG);assert git("rev-parse",TAG+"^{}")==head
git("push","--atomic","origin","HEAD","refs/tags/"+TAG)
names=["refs/heads/"+branch,"refs/heads/main","refs/tags/"+TAG,"refs/tags/"+TAG+"^{}"]
refs={line.split()[1]:line.split()[0] for line in git("ls-remote","origin",*names).splitlines()}
assert refs["refs/heads/"+branch]==head
assert refs["refs/tags/"+TAG]==obj and refs["refs/tags/"+TAG+"^{}"]==head
print(json.dumps(dict(committed=head,tag=TAG,tag_object=obj,remote_verified=True,main_before=main_before,main_after=refs["refs/heads/main"],files=len(files)),indent=2),flush=True)
