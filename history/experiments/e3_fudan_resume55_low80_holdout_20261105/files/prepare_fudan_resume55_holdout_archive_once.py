"""Prepare a new Root8 three-seed actual holdout archive, never execute old record or physics."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;target=D/'record_fudan_resume55_low80_holdout_closed_once.py';assert not target.exists();s=(D/'record_fudan_low80_confirm_quality_once.py').read_text(encoding='utf8')
changes={
 'e3_fudan_low80_threeseed_confirm_20261105':'e3_fudan_resume55_low80_holdout_20261105',
 'FDNLOW80_CONFIRM_ADMISSION2_':'FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_',
 'FDNLOW80_CONFIRM_':'FDNRESUME55_LOW80_HOLDOUT_',
 'FDN_LOW80_3SEED_ACTUAL_WAIT_QUALIFICATION_V1':'FDN_LOW80_3SEED_RESUME55_ACTUAL_WAIT_QUALIFICATION_V2',
 '55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7':'8e27c2f35d5e1ed5ad2f71324e729bdbda9a10e1486b151ca1dd9384d3ecfe32',
 '146247985':'146251569','20260929':'20261002','20260930':'20261003','20261001':'20261004',
 '7e02452024fb70460a46b1ec17e4b006f5bd7233':'af7639f66ed2677c905318c2cd79e102e06a35a4',
 'CURRENT_PROGRESS_V26_LOW80_THREESEED_ACTUAL_RESULT.md':'CURRENT_PROGRESS_V33_RESUME55_LOW80_HOLDOUT_ACTUAL.md',
 'FDN_LOW80_THREESEED_CONFIRMATION_RESULTS_V1.md':'FDN_RESUME55_LOW80_HOLDOUT_RESULTS_V1.md',
 'e3-fudan-low80-three-seed-frozen-confirmation':'e3-fudan-resume55-low80-holdout-closed',
 'Candidate55afa':'Candidate8e27','candidate55afa':'candidate8e27','frozen55afa':'frozen8e27'
}
restore={}
for i,(old,new)in enumerate(sorted(changes.items(),key=lambda x:len(x[0]),reverse=True)):
 assert old in s,old;token='[REDACTED]'+str(i)+'__';s=s.replace(old,token);restore[token]=new
for token,new in restore.items():s=s.replace(token,new)
a='if r[\'execution_qualified\']:\n';assert s.count(a)==1
extra="analysis=json.loads((D/'FDN_RESUME55_LOW80_HOLDOUT_ANALYSIS_V1.json').read_bytes());ag=analysis['aggregate'];assert analysis['source']==r['source']and analysis['execution_qualified']is True and analysis['strict_terminal_current_streak_serialized']is True and ag['denominator']==240 and ag['first_episode_continuous25_credit']==r['first_episode_stable_credits']and ag['ever_credited_and_final_frame_good']==r['credited_and_stable_at_end']and 0<=ag['strict_terminal_continuous25_good_count']<=ag['ever_credited_and_final_frame_good']and analysis['goal_complete']is False\n"
s=s.replace(a,extra+a)
a='terminalContinuous25=null';assert s.count(a)==1;s=s.replace(a,'terminalContinuous25={ag[\"strict_terminal_continuous25_good_count\"]}')
s=s.replace('First episode credits/max good/first time/physical endings/endpoint conditions separated,','Strict terminal current controls>=25 is serialized and distinct from loose ever+final-frame-good; first episode credits/max good/first time/physical endings/endpoint conditions separated,')
ast.parse(s);compile(s,str(target),'exec');target.write_text(s,encoding='utf8',newline='\n');print('New actual Root8 holdout archive source prepared; original recorder validation/redaction/hashes preserved, no record or model operations')
