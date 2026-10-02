"""Append one real, user-reviewed experiment with a commit and annotated Git tag."""
import argparse
from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path
import re
import subprocess
from capture_history import redact

ROOT=Path(__file__).resolve().parents[1]

def git(*args):
    return subprocess.run(['git','-C',str(ROOT),*args],check=True,capture_output=True,text=True).stdout.strip()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--id',required=True,help='Unique suffix, e.g. yaw6-regression-01')
    p.add_argument('--title',required=True)
    p.add_argument('--kind',required=True,choices=['repair','training','diagnostic','evaluation','deployment','rejected'])
    p.add_argument('--note-file',required=True,type=Path,help='Describe the problem, exact change, checks and result')
    p.add_argument('--files',nargs='*',default=[],help='Changed repository source/config/evidence files')
    p.add_argument('--validation',default='See linked evidence; no result is inferred.')
    p.add_argument('--push',action='store_true')
    a=p.parse_args()
    if not re.fullmatch('[a-z0-9][a-z0-9-]{2,80}',a.id):raise ValueError('Invalid experiment id')
    date=datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')
    tag=f'trial-{date}-{a.id}'
    if git('tag','--list',tag):raise ValueError('Tag already exists; do not overwrite past evidence')
    note=a.note_file.read_text(encoding='utf8')
    if redact(note)[0]!=note:raise ValueError('Note contains a credential; redact it before recording')
    selected=[];hashes={}
    for value in a.files:
        file=(ROOT/value).resolve()
        if not file.is_relative_to(ROOT) or not file.is_file():raise ValueError('File must be inside this repository')
        if file.suffix.lower() in ('.pt','.pth','.onnx','.npz','.npy','.pem','.key'):raise ValueError('Index external artifacts instead of committing them')
        raw=file.read_bytes()
        if len(raw)>50_000_000:raise ValueError('Large artifact must be indexed externally')
        try:text=raw.decode('utf8')
        except UnicodeDecodeError:text=None
        if text is not None and redact(text)[0]!=text:raise ValueError('Credential detected in '+value)
        selected.append(file.relative_to(ROOT).as_posix());hashes[selected[-1]]=hashlib.sha256(raw).hexdigest()
    if git('diff','--cached','--name-only'):raise ValueError('Clear the existing staging area before recording an experiment')
    record={'id':date+'-'+a.id,'tag':tag,'title':a.title,'kind':a.kind,
            'recorded_at':datetime.now(timezone.utc).isoformat(),'repair_or_experiment_note':note,
            'validation':a.validation,'source_and_evidence_sha256':hashes,
            'real_robot_certified':False}
    dest=ROOT/'history/experiments'/f'{record["id"]}.json'
    if dest.exists():raise ValueError('Record already exists')
    dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    git('add','--',dest.relative_to(ROOT).as_posix(),*selected)
    git('commit','-m',a.title+'\n\nExperiment: '+tag+'\nValidation: '+a.validation)
    git('tag','-a',tag,'-m',a.title+'\n\n'+note)
    if a.push:git('push','--atomic','origin','HEAD','refs/tags/'+tag)
    print(tag,git('rev-parse','HEAD'))

if __name__=='__main__':main()
