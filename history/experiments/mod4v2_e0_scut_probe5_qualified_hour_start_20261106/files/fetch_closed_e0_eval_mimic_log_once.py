"""Read bounded own CLOSED evaluation log only; no model/raw dataset/GPU/SDK/C actions."""
from pathlib import Path
import sys,json,re
D=Path(__file__).resolve().parent;out=D/'E0_EVAL_MIMIC_LOG_FIRST_LAST.txt';assert not out.exists();closed=json.loads(Path(json.loads((D/'E0_SINGLE_FROZEN_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());assert closed['closed']is closed['execution_qualified']is True and closed['metadata']['PARENT_EXIT_SCOPE.json']['all_own_children_waited']is True
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();f=c.open_sftp()
try:
 with f.open(closed['root']+'/cases/E0/SDK_FULL_STDOUT_STDERR.log','rb')as h:
  n=h.stat().st_size;head=h.read(min(n,220000));tail=b''
  if n>len(head):h.seek(max(len(head),n-40000));tail=h.read(40000)
 text=(head+b'\n--- bounded own last40k ---\n'+tail).decode('utf8','replace');out.write_text(text,encoding='utf8');rows=[x for x in text.splitlines()if re.search(r'mimic|referenceJoint|Invalid.*joint|joint.*invalid|Error:',x,re.I)];print(json.dumps(dict(path=str(out),own_log_bytes=n,matching_bounded_lines=rows[:45],matching_count=len(rows),closed_ownpurpose_only=True,model_SDK_C_GPU_or_foreign_operations=0),indent=2))
finally:f.close();c.close()
