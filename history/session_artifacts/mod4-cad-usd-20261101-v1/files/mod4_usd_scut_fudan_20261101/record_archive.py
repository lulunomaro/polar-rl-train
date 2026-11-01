"""Invoke the project's required experiment recorder on the already frozen stage manifest.
Do not rerun if its record/tag already exists; a failed push must reuse the same objects.
"""
from pathlib import Path
import sys,json,subprocess
REPO=Path(r'F:\RMPOLAR-RL\repo-lqr')
p=REPO/'history/session_artifacts/mod4-cad-usd-20261101-v1/STAGE_MANIFEST.json'
m=json.loads(p.read_text(encoding='utf-8'))
branch=subprocess.check_output(['git','-C',str(REPO),'branch','--show-current'],text=True).strip()
assert branch==m['branch'],'Do not record on another task branch'
sys.path.insert(0,str(REPO/'archive_tools'))
import record_experiment
sys.argv=['record_experiment.py','--id',m['id'],'--title',m['title'],'--kind',m['kind'],'--note-file',str(REPO/m['note_file']),'--validation',m['validation'],'--files',*m['files']]
record_experiment.main()
