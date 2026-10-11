"""Preserve prelaunch syntax rejection and execute the still-unexecuted410 dispatch."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent
with (D/'reports/INITIALIZATION_DISPATCH_PRELAUNCH_SYNTAX_REJECTION.json').open('x') as f:
 json.dump(dict(epoch=time.time(),source='dispatch_initialization_reviewed_once.py',error="SyntaxError: closing parenthesis ']' does not match opening parenthesis '(' at line6",rejected_before_any_tool_network_or_GPU_call=True,original_source_kept=True),f,indent=2)
s=(D/'dispatch_initialization_reviewed_once.py').read_text()
lines=s.splitlines();assert lines[5].startswith("s=s.replace('ENTRY_TARGET_CPU_PASSED.json'")
lines[5]="s=s.replace('ENTRY_TARGET_CPU_PASSED.json','INITIALIZATION_REVIEWED_TARGET_CPU_PASSED.json')"
s='\n'.join(lines)+'\n';ast.parse(s)
exec(compile(s,'<syntax-checked-unexecuted410-dispatch>','exec'),{'__file__':str(D/'dispatch_initialization_reviewed_once.py'),'__name__':'__main__'})
