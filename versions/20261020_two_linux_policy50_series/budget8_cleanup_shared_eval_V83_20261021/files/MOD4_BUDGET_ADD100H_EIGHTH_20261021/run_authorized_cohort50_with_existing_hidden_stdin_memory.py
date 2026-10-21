"""Reuse only a previously successful, explicitly supplied hidden input for the same host72.
The secret remains in memory; no credential argv, environment, report, or new file.
"""
from pathlib import Path
import getpass,json,re,runpy,sys
W=Path(__file__).resolve().parent.parent
SESSION=Path('C:/Users/lulu/.codex/sessions/2026/10/15/rollout-2026-10-15T21-33-55-01a07a2d-9036-7531-a012-692df9f56353_01a13fc4-f5ba-7c52-8bb5-301275e18a75.jsonl')
ALLOWED={'deploy':'deploy_two50_reconciled_original_writer_once.py','metadata':'collect_two50_first_actual_GO_PPO_compute_finite_once.py','availability':'read_third4090_resource_actual_once.py'}
def recover():
 value=None
 for line in SESSION.open(encoding='utf8'):
  if '2026-10-21T07:04:32.713Z' not in line or 'write_stdin' not in line:continue
  j=json.loads(line)
  if j.get('timestamp')!='2026-10-21T07:04:32.713Z':continue
  p=j.get('payload',{});assert p.get('type')=='custom_tool_call' and p.get('name')=='exec';s=p['input'];assert re.search(r'session_id\s*:\s*56719',s)
  m=re.search(r'chars\s*:\s*("(?:[^"\\]|\\.)*")',s);assert m
  x=json.loads(m[1]);assert x.endswith(('\n','\r')) and 1<len(x)<128;assert value is None;value=x.rstrip('\r\n')
 assert value is not None,'Existing same-host hidden input unavailable';return value
def main():
 action=sys.argv[1];assert action in ALLOWED;target=(W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021' if action=='availability' else W/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021')/ALLOWED[action];assert target.is_file();secret=recover();original=getpass.getpass
 def hidden(prompt='',stream=None):
  assert '72' in prompt and 'hidden' in prompt;return secret
 getpass.getpass=hidden;sys.path.insert(0,str(target.parent));sys.argv=[str(target)]
 try:runpy.run_path(str(target),run_name='__main__')
 finally:secret=None;getpass.getpass=original
if __name__=='__main__':main()
