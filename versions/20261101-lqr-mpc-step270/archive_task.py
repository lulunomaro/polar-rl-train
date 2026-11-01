"""Archive all task artifacts, preserving failed trials, with per-file hashes."""
from pathlib import Path
import argparse,hashlib,json,tarfile
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');args=p.parse_args()
    evidence=ROOT/'results/FINAL_EVIDENCE_V2'
    if not args.final:
        dst=ROOT/'FINAL_EVIDENCE_V2.tar.gz'
        if dst.exists():raise FileExistsError(dst)
        with tarfile.open(dst,'w:gz') as tf:tf.add(evidence,arcname='FINAL_EVIDENCE_V2')
        print(json.dumps({'artifact':dst.name,'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}),flush=True)
    else:
        dst=ROOT/'MOD4_LQR_MPC_STEP270_20261101.tar.gz'
        if dst.exists():raise FileExistsError(dst)
        files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.gz','.pyc') and p.name!='TASK_ARCHIVE_MANIFEST.json')
        manifest={str(p.relative_to(ROOT)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
        (ROOT/'TASK_ARCHIVE_MANIFEST.json').write_text(json.dumps({'schema':'mod4.traditional.270mm.all_trials.v2','files':manifest,'all_historical_failures_preserved':True,'credentials_embedded':False},indent=2))
        files.append(ROOT/'TASK_ARCHIVE_MANIFEST.json')
        with tarfile.open(dst,'w:gz',compresslevel=6) as tf:
            for p in files:tf.add(p,arcname=str(Path(ROOT.name)/p.relative_to(ROOT)),recursive=False)
        print(json.dumps({'artifact':dst.name,'files':len(files),'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}),flush=True)
