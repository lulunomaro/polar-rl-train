"""Extract source definitions only, not old main/fixture/model reading."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent;old=D.parent/'native87R5_closing_typed_source/review_H1_native87R5_finals_CPU_unused_once.py'
source=old.read_text('utf8');tree=ast.parse(source)
names=('exact','finite','OneInitialLoadPool','PinnedSource','original_physical_state','frozen_bootstrap','native_modules','role_terminal')
out='''"""Exact reviewed reader primitives with native88 source-config extension only."""
from pathlib import Path
import ast,sys,hashlib,io,json,math,traceback
from dataclasses import dataclass,asdict
from native88_closing_protocol_v1 import BOOTSTRAP_SHA,require
SOURCE_SHA=BOOTSTRAP_SHA # Original reader name: only the normal86 shared witness.
'''
checks={};lineage={}
for name in names:
 node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
 text=ast.get_source_segment(source,node);new=text
 if name=='native_modules':
  new=new.replace('source/native_own_fudan87_training.py','source/native_own_fudan88_gas400_training_v2.py')
  new=new.replace("validate_native_optimizer(module,s[opt_name],args['lr'],betas)","validate_native_optimizer(module,s[opt_name],betas)")
 else:checks[name+'_AST_exact']=ast.dump(ast.parse(text))==ast.dump(ast.parse(new))
 out+='\n'+new+'\n';lineage[name]=dict(original_AST_SHA=hashlib.sha256(ast.dump(node).encode()).hexdigest(),new_AST_SHA=hashlib.sha256(ast.dump(ast.parse(new).body[0]).encode()).hexdigest())
helper=D.parent/'native88_installed_source_CPU_candidate_v1/native88_installed_cpu_helpers_v1.py';hsource=helper.read_text('utf8');hnode=next(n for n in ast.parse(hsource).body if isinstance(n,ast.FunctionDef) and n.name=='validate_native_optimizer')
out+='\n'+ast.get_source_segment(hsource,hnode)+'\n'
ast.parse(out)
with (D/'native88_initial_CPU_reader_primitives_v1.py').open('x',encoding='utf8',newline='\n') as f:f.write(out)
assert all(checks.values())
with (D/'EXACT_READER_SOURCE_DERIVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,checks=checks,functions=lineage,old_reader_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),strict_native_optimizer_source_SHA=hashlib.sha256(helper.read_bytes()).hexdigest(),no_old_main_or_fixture_executed=True),f,indent=2)
print(json.dumps(dict(passed=True,reader_primitives_extracted=True)))
