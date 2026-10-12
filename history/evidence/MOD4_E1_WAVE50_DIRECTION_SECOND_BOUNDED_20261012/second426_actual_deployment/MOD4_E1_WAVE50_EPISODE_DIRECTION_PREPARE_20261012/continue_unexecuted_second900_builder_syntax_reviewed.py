"""Retain a parse refusal before any mkdir/write/GPU; complete only unexecuted build."""
from wave_direction_io import *
import ast
path=D/'prepare_second900_payload_once.py';s=path.read_text()
save('SECOND900_BUILDER_PREEXEC_SYNTAX_REJECTION.json',dict(epoch=time.time(),source=str(path),error="SyntaxError: closing parenthesis ']' does not match opening parenthesis '(' at line17",before_directory_file_CPU_GPU_or_budget_work=True,original_source_kept=True))
bad=".replace('finite_tensors']==102','finite_tensors']==104')";good='''.replace("finite_tensors']==102","finite_tensors']==104")'''
assert s.count(bad)==1;s=s.replace(bad,good);ast.parse(s)
exec(compile(s,'<only-unexecuted-second900-builder-syntax-reviewed>','exec'),dict(__file__=str(path),__name__='__main__'))
