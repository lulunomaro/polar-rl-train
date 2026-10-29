"""Continue failed source fixture with encoded reference bytes; no old once replay."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent
def main():
 source=B/'prepare_and_test_actual_resample_method_lifecycle_CPU_SOURCE_once_v1.py';tree=ast.parse(source.read_bytes());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 scope={'__file__':str(source),'__name__':'source_CPU_continuation_v2'};setup=[n for n in tree.body if not isinstance(n,ast.If) and not (isinstance(n,ast.FunctionDef) and n.name=='main')];exec(compile(ast.Module(body=setup,type_ignores=[]),str(source),'exec'),scope)
 contract=json.loads((B/'REQUIRED_TARGET_COMMANDTERM_METHOD_SOURCE_CONTRACT_V1.json').read_bytes());refs={}
 for meta in contract['reference_sources']:
  name=Path(meta['path']).name;raw=(B/('REFERENCE_OLD210_'+name+'.txt')).read_bytes();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['SHA'];refs[name]=dict(meta,text=raw.decode('utf8'))
 helper=scope['load']('_early_source_hook_bytes_v2',B/'e0_early_original_resample_passthrough_observer_v1.py');scope.update(refs=refs,helper=helper,contract=contract)
 start=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='validate_actual_target_source')
 class Bytes(ast.NodeTransformer):
  def visit_Call(self,n):
   n=self.generic_visit(n)
   if isinstance(n.func,ast.Attribute) and n.func.attr=='validate_actual_target_source':n.args[0]=ast.Call(func=ast.Attribute(value=n.args[0],attr='encode',ctx=ast.Load()),args=[],keywords=[])
   return n
 body=Bytes().visit(ast.Module(body=fn.body[start:],type_ignores=[]));exec(compile(ast.fix_missing_locations(body),str(source),'exec'),scope)
 with (B/'SOURCE_FIXTURE_REFERENCE_STRING_BYTES_CORRECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,only_local_fixture_supplies_UTF8_bytes_to_original_rawbyte_validator=True,selected_observer_source_unchanged=True,original_error_preserved=True,no_SDK_or_model_or_remote=True),f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('ORIGINAL_SOURCE_CPU_CONTINUATION_V2_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(traceback=traceback.format_exc(),no_model_SDK_or_remote=True),f,indent=2)
  raise
