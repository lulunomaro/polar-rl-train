from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'collect_actual.py').read_text(encoding='utf8')
s=s.replace("R/'own/STATIC_OWN_SOURCE_VERIFIED.json'", "R/('own/STATIC_OWN_SOURCE_VERIFIED_'+str(int(proof['epoch']))+'.json')")
s=s.replace("trial_id='E1-G1-ACTUAL-COLLECTOR-01'", "trial_id='E1-G1-ACTUAL-COLLECTOR-02-VERSIONED-SNAPSHOT'")
p=D/'collect_actual_versioned.py';assert not p.exists();p.write_text(s,encoding='utf8')
