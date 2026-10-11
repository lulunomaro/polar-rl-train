"""Complete only unexecuted capture/record after missing new archive parent directory."""
from archive_wave_started_stage_once import *
import ast

def main():
 assert not DEST.exists() and (R/'WAVE_STAGE_ARCHIVE_STARTED.json').exists()
 assert not gitio.g('tag','--list','*'+ID) and not (REPO/'history/experiments'/('20261011-'+ID+'.json')).exists()
 assert not gitio.g('status','--porcelain')
 save('WAVE_ARCHIVE_PARENT_DIRECTORY_REJECTION_RETAINED.json',dict(epoch=time.time(),actual_error="FileNotFoundError: [WinError 3] at DEST.mkdir(): new history/evidence/MOD4_E1_WAVE35_EXPOSURE_REPAIR_20261011 parent missing",classification='archive_before_capture_record_commit_tag',old_source_preserved=True,record_commit_tag_not_executed=True,no_GPU_or_budget_effect=True))
 tree=ast.parse((D/'archive_wave_started_stage_once.py').read_text(encoding='utf8'));fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main');body=[]
 for s in fn.body:
  if isinstance(s,ast.Expr) and isinstance(s.value,ast.Call):
   c=s.value
   if isinstance(c.func,ast.Name) and c.func.id=='save' and c.args and isinstance(c.args[0],ast.Constant) and c.args[0].value=='WAVE_STAGE_ARCHIVE_STARTED.json':continue
   if isinstance(c.func,ast.Attribute) and isinstance(c.func.value,ast.Name) and c.func.value.id=='note' and c.func.attr=='write_text':continue
   if isinstance(c.func,ast.Attribute) and isinstance(c.func.value,ast.Name) and c.func.value.id=='DEST' and c.func.attr=='mkdir':c.keywords=[ast.keyword(arg='parents',value=ast.Constant(True))]
  if isinstance(s,ast.Assert) and 'not note.exists()'==ast.unparse(s.test):continue
  body.append(s)
 fn.body=body;fn.name='finish_unexecuted_capture_and_record'
 code=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]));ns=dict(globals());exec(compile(code,str(D/'archive_wave_started_stage_once.py'),'exec'),ns);ns['finish_unexecuted_capture_and_record']()

if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE_ARCHIVE_CONTINUATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_original_objects_if_any_only=True));raise
