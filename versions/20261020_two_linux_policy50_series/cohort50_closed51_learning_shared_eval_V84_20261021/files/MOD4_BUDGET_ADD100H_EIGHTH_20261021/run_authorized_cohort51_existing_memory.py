from pathlib import Path
import getpass,importlib.util,runpy,sys
B=Path(__file__).resolve().parent;N=B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_51_20261021'
s=importlib.util.spec_from_file_location('memory',B/'run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
actions={'deploy':'deploy_two50_reconciled_original_writer_once.py','metadata':'collect_two50_first_actual_GO_PPO_compute_finite_once.py'}
action=sys.argv[1];assert action in actions;target=N/actions[action];assert target.is_file()
secret=m.recover();original=getpass.getpass
def hidden(prompt='',stream=None):
 assert '72' in prompt and 'hidden' in prompt
 return secret
getpass.getpass=hidden;sys.path.insert(0,str(N));sys.argv=[str(target)]
try:runpy.run_path(str(target),run_name='__main__')
finally:secret=None;getpass.getpass=original
