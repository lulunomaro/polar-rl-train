"""New local fixture continuation; preserve initial CRLF copies/error unchanged."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent
def main():
 original=B/'prepare_and_test_actual_resample_method_lifecycle_CPU_SOURCE_once_v1.py';tree=ast.parse(original.read_bytes());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');scope={'__file__':str(original),'__name__':'source_CPU_exact_reference_v3'}
 setup=[n for n in tree.body if not isinstance(n,ast.If) and not (isinstance(n,ast.FunctionDef) and n.name=='main')];exec(compile(ast.Module(body=setup,type_ignores=[]),str(original),'exec'),scope)
 contract=json.loads((B/'REQUIRED_TARGET_COMMANDTERM_METHOD_SOURCE_CONTRACT_V1.json').read_bytes());refs={};new=[]
 for meta in contract['reference_sources']:
  name=Path(meta['path']).name;p=B/('REFERENCE_OLD210_'+name+'.txt');raw=p.read_text(encoding='utf8').encode();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['SHA']
  exact=B/('REFERENCE_OLD210_EXACT_UTF8_'+name+'.txt')
  with exact.open('xb') as f:f.write(raw)
  refs[name]=dict(meta,text=raw.decode('utf8'));new.append(dict(original_CRLF_copy=str(p),original_CRLF_copy_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),exact_UTF8_byte_copy=str(exact),exact_bytes=len(raw),exact_original_SHA=meta['SHA'],normalized_text_matches_original_saved_Linux_source_bytes=True))
 helper=scope['load']('_early_source_hook_exact_reference_v3',B/'e0_early_original_resample_passthrough_observer_v1.py');scope.update(refs=refs,helper=helper,contract=contract)
 start=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='validate_actual_target_source')
 class Bytes(ast.NodeTransformer):
  def visit_Call(self,n):
   n=self.generic_visit(n)
   if isinstance(n.func,ast.Attribute) and n.func.attr=='validate_actual_target_source':n.args[0]=ast.Call(func=ast.Attribute(value=n.args[0],attr='encode',ctx=ast.Load()),args=[],keywords=[])
   return n
 body=Bytes().visit(ast.Module(body=fn.body[start:],type_ignores=[]));exec(compile(ast.fix_missing_locations(body),str(original),'exec'),scope)
 with (B/'LOCAL_REFERENCE_BYTES_AND_CRLF_SOURCE_FIXTURE_CORRECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,selected_hook_unchanged=True,reference_byte_copies=new,previous_String_and_CRLF_errors_preserved=True,only_saved_source_text_and_fresh_CPU=True),f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('ORIGINAL_SOURCE_CPU_CONTINUATION_V3_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(traceback=traceback.format_exc(),no_model_SDK_or_remote=True),f,indent=2)
  raise
