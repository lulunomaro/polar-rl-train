from pathlib import Path
import runpy
S=Path(__file__).resolve().parent;T=S.parent
m=runpy.run_path(str(T/"H1_NATIVE107_COHERENT20S_FROZEN_MOTION_WM_N1_V108_20261029/archive_reward_counterexample110_and_panel210_v2_failure_ordinary_once.py"),run_name="definitions_only")
s=m["s"];a=s.index("def run_stage(");b=s.find("\ndef ",a+5);f=s[a:b if b!=-1 else len(s)]
print("\n".join(f.splitlines()[:16]));print("\n".join(f.splitlines()[-23:]))

