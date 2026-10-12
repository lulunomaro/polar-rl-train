from wave_direction_io import *
import ast
path=D/'prepare_second900_payload_once.py';s=path.read_text()
save('SECOND900_BUILDER_SECOND_PREEXEC_QUOTE_REJECTION.json',dict(epoch=time.time(),source=str(path),error="SyntaxError: closing parenthesis ']' does not match opening parenthesis '(' at line19 after first quote review",before_new_scope_directory_file_CPU_GPU_or_budget=True,original_sources_kept=True))
for bad,good in ((".replace('finite_tensors']==102','finite_tensors']==104')",'''.replace("finite_tensors']==102","finite_tensors']==104")'''),(".replace('remaining_training_seconds']>1920','remaining_training_seconds']>1020')",'''.replace("remaining_training_seconds']>1920","remaining_training_seconds']>1020")''')):
 assert s.count(bad)==1;s=s.replace(bad,good)
ast.parse(s);exec(compile(s,'<only-unexecuted-second900-builder-two-quotes-reviewed>','exec'),dict(__file__=str(path),__name__='__main__'))
