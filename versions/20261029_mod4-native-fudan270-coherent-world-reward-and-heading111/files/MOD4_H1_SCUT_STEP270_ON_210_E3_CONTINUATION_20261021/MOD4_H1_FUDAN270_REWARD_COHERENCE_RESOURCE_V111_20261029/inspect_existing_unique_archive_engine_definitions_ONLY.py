from pathlib import Path
import runpy
B=Path(__file__).resolve().parent
m=runpy.run_path(str(B/"archive_actual111_coherent_reward_first_learning_unique_once.py"),run_name="definitions_only")
s=m["s"]
a=s.index("def run_stage(");b=s.find("\ndef ",a+5)
print(s[a:b if b!=-1 else len(s)])

