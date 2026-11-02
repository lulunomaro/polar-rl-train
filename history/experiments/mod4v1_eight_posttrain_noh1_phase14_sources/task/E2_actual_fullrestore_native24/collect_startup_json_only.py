"""Collect this NEW case's original helper JSON proofs only; never read PT."""
from pathlib import Path,PurePosixPath
import hashlib,json,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from project_connector import connect72
COL=ROOT/'reports/E2_b3_no_update_final_20261102_024838'
B='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E2_B3_N20K_NATIVE24_NOUPDATE_20261102_024108_1793558468484021400'

def main():
    before=json.loads((COL/'gpu1/E2_N20K_FULLRESTORE_BEFORE_NATIVE24.json').read_bytes())
    files=list(before['original_seven_helper_receipts'].values());log=str(PurePosixPath(files[0]).parent)
    files.extend(log+'/'+n for n in ['MOD4V1_E2_NOMINAL_RESTORE_ACTUAL.json','CLOCK_TRAINING_HEALTH.json','run_manifest.json'])
    out=COL/'ORIGINAL_HELPER_JSON_PROOFS';out.mkdir(exist_ok=False)
    c=connect72();sf=None;rows=[]
    try:
        sf=c.open_sftp()
        for name in files:
            p=PurePosixPath(name);assert p.is_relative_to(PurePosixPath(B)) and p.suffix=='.json'
            try:
                with sf.open(name,'r') as f:raw=f.read()
            except FileNotFoundError:continue
            target=out/p.name;target.write_bytes(raw);value=json.loads(raw)
            rows.append(dict(remote=name,local=str(target),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),source_SHA=value.get('source_sha256',value.get('source_SHA'))))
        index=out/'JSON_PROOF_INDEX.json';index.write_text(json.dumps(dict(files=rows,source_PT_reads=0,canonical_access=False),indent=2),encoding='utf-8')
        print(json.dumps(dict(JSON_proofs=len(rows),index=str(index),source_PT_reads=0),indent=2))
    finally:
        if sf is not None:sf.close()
        c.close()

if __name__=='__main__':main()
