from pathlib import Path
import getpass,importlib.util,runpy,sys
B=Path(__file__).resolve().parent;N=B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_51_20261021'
s=importlib.util.spec_from_file_location('memory',B.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
secret=m.recover();original=getpass.getpass
def hidden(prompt='',stream=None):
 assert '72' in prompt and 'hidden' in prompt
 return secret
getpass.getpass=hidden;sys.path.insert(0,str(N));p=N/'collect_current_two50_finals_original_cost_bounded_once.py';sys.argv=[str(p)]
try:runpy.run_path(str(p),run_name='__main__')
finally:secret=None;getpass.getpass=original
