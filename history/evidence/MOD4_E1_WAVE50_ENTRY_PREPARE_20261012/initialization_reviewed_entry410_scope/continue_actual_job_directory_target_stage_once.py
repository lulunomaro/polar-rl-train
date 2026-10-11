"""Windows actual result files live inside jobs/<id>; continue missing admission only."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'continue_missing_target_stage_once.py').read_text()
s=s.replace("s=s.replace('  checks=[]'", "s=s.replace(\"(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/results'),\",'')\ns=s.replace(\",(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/results')\",'')\ns=s.replace('  checks=[]'")
exec(compile(s,'<continue-actual-job-directory-missing-stage>','exec'),{'__file__':str(D/'continue_missing_target_stage_once.py'),'__name__':'__main__'})
