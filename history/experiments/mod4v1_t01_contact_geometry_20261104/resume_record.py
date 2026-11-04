"""Resume after the proven import-path error; do not recopy or rerun physics."""
from pathlib import Path
import subprocess
import sys
REPO=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
ID='mod4v1-terrain-t01-contact-geometry'
def gr(*a):return subprocess.run(['git','-C',str(REPO),*a],capture_output=True,text=True,check=True).stdout.strip()
if gr('branch','--show-current')!='mod4v1-lqr-mpc-robust' or gr('diff','--cached','--name-only'):raise RuntimeError('Branch/staging changed')
if (REPO/f'history/experiments/20261104-{ID}.json').exists():raise RuntimeError('Record already exists; preserve objects')
sys.path.insert(0,str(REPO/'archive_tools'))
import record_experiment as m
old=m.git
def git(*a):
    if a and a[0]=='add':a=('add','--sparse',*a[1:])
    try:return old(*a)
    except subprocess.CalledProcessError as e:print(e.stdout,e.stderr,flush=True);raise
m.git=git
selected=(OUT/'SELECTED_FILES.txt').read_text(encoding='utf8').splitlines()
sys.argv=['record_experiment.py','--id',ID,'--title','Record T01 zero-contact geometry probe and human J200 delegation','--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation','Read-only C2 probe complete; original contact gates still fail. Zero-contact gaps classified, finite separation not measured. One archive import failure preserved; no physics rerun.','--files',*selected]
m.main()
