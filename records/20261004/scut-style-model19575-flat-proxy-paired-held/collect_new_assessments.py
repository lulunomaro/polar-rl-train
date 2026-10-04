"""Read already-completed assessments; never launch probes or change production."""
import json,sys,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
P='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002'
DEST=D/'existing_assessments_0066_0069'
DEST.mkdir(exist_ok=True)
c=connect()
try:
    with c.open_sftp() as s:
        names=sorted(n for n in s.listdir(P+'/reports')
                     if n.startswith(('auto_0066_','auto_0067_','auto_0069_')) and n.endswith('.json'))
        for n in names:
            target=DEST/n
            raw=s.open(P+'/reports/'+n,'rb').read()
            if target.exists():
                assert target.read_bytes()==raw,'Existing frozen evidence changed'
            else:target.write_bytes(raw)
        index={n:hashlib.sha256((DEST/n).read_bytes()).hexdigest() for n in names}
        (DEST/'SOURCE_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf8')
        for n in names:
            if n.endswith('_decision.json'):
                r=json.loads((DEST/n).read_text(encoding='utf8'))
                print(json.dumps(dict(name=n,keys=list(r),physical=r.get('continue_current_rate'),
                     skill=r.get('current_rate_skill_pass'),paired=r.get('pass_'),checkpoint=r.get('checkpoint'),
                     pairs=r.get('pairs'),assessment=r.get('loaded_contact_assessment',{}).get('groups'),
                     failed=[v for v in r.get('loaded_contact_assessment',{}).get('individual',[]) if not v['pass_']],
                     severe=r.get('loaded_contact_assessment',{}).get('severe_individual_veto'))))
        print(json.dumps(dict(files=names,read_only=True)))
finally:c.close()
