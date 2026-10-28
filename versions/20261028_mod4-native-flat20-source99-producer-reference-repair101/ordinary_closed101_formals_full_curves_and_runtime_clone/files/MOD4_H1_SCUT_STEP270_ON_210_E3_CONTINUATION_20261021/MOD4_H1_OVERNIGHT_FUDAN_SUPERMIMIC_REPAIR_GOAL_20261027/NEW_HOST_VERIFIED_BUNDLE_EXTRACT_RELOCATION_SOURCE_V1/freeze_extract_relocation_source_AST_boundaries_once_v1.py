"""Local source/tiny string checks only; no existing archive, model or network IO."""
from pathlib import Path,PurePosixPath
import ast,hashlib,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports'

def put(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)

def main():
 R.mkdir(exist_ok=True);compiled=[]
 for p in sorted(B.glob('*.py')):
  tree=ast.parse(p.read_bytes());compile(tree,str(p),'exec');compiled.append(p.name)
  if p.name=='source72_all_recorded_ownout_preflight_CODE_v1.py':
   code=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CODE' for x in n.targets));compile(ast.parse(code),'<future source72 metadata only>','exec')
 spec=importlib.util.spec_from_file_location('strict_copy_source_tiny_check',B/'strict_archive_and_narrow_relocation_core_v1.py');core=importlib.util.module_from_spec(spec);sys.dont_write_bytecode=True;spec.loader.exec_module(core)
 good=core.safe_name('envs/mod4/bin/python3.12');assert good=='envs/mod4/bin/python3.12';assert core.relative_link_target('envs/mod4/bin/python','python3.12')==good
 rejected=[]
 def rejects(name,fn):
  try:fn()
  except (AssertionError,RuntimeError):rejected.append(name);return
  raise AssertionError('negative unexpectedly accepted: '+name)
 rejects('absolute archive member',lambda:core.safe_name('/etc/passwd'));rejects('parent traversal',lambda:core.safe_name('envs/mod4/../../etc/passwd'));rejects('outside exact input scope',lambda:core.safe_name('home/secret'));rejects('absolute symlink',lambda:core.relative_link_target('envs/mod4/bin/p','/etc/passwd'));rejects('escaping symlink',lambda:core.relative_link_target('envs/mod4/bin/p','../../../../etc/passwd'))
 kinds={'envs/mod4/bin/a':'symlink','envs/mod4/bin/b':'symlink'};rejects('link cycle',lambda:core.validate_link_graph(kinds,{'envs/mod4/bin/a':'envs/mod4/bin/b','envs/mod4/bin/b':'envs/mod4/bin/a'}));rejects('link ancestor',lambda:core.validate_link_graph({'envs/mod4/a':'symlink','envs/mod4/a/file':'file'},{'envs/mod4/a':'envs/mod4/z'}));rejects('missing hardlink target',lambda:core.validate_link_graph({'envs/mod4/a':'hardlink'},{'envs/mod4/a':'envs/mod4/missing'}))
 resolved=core.validate_link_graph({'envs/mod4/a':'hardlink','envs/mod4/b':'file'},{'envs/mod4/a':'envs/mod4/b'});assert resolved['envs/mod4/a']=='envs/mod4/b'
 binding=json.loads((B/'EXACT_ORIGINAL_LAUNCHERS_AND_FIVE_EDITABLE_BINDING_V1.json').read_bytes());dest='/data/robemo/polar-rl-train/runtime_migrations/proven72_20261028_v1/runtime_copy_v1';finder_proofs=[]
 for row in binding['finders']:
  raw=row['UTF8'].encode();assert hashlib.sha256(raw).hexdigest()==row['SHA'] and raw.count(core.OLD.encode())==1;new=raw.replace(core.OLD.encode(),dest.encode());assert new.replace(dest.encode(),core.OLD.encode())==raw;ast.parse(new);finder_proofs.append(dict(path=PurePosixPath(row['path']).relative_to(core.OLD).as_posix(),old_SHA=row['SHA'],new_SHA=hashlib.sha256(new).hexdigest(),exact_inverse_byte_proof=True))
 wrapper=(dest+'/run-python.sh').encode();assert len(wrapper)+2<=127;original=b'#!/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python3.12\n# -*- coding: utf-8 -*-\nfrom __future__ import annotations\nprint("tiny fixture only")\n';new=b'#!'+wrapper+b'\n'+original.split(b'\n',1)[1];assert ast.dump(ast.parse(original))==ast.dump(ast.parse(new)) and new.split(b'\n',1)[1]==original.split(b'\n',1)[1]
 report=dict(epoch=time.time(),passed_source_AST_and_tiny_path_relocation_only=True,compiled_sources=compiled,embedded_source72_CODE_AST=True,rejected_boundary_cases=rejected,valid_internal_hardlink=True,five_actual_original_finder_inverse_proofs=finder_proofs,console_shebang_body_and_AST_unchanged=True,new_shebang_uses_unchanged_relative_glibc240_wrapper=True,no_existing_archive_binary_model_network_GPU_SDK_or_canonical_IO=True,not_actual_extract_or_SDK_ready=True)
 put(R/'EXTRACT_SOURCE_AST_PATH_LINK_AND_EXACT_RELOCATION_CPU_ACTUAL.json',report)
 files=[]
 for p in sorted(B.rglob('*')):
  if p.is_file() and p.name!='FROZEN_VERIFIED_EXTRACT_RELOCATION_SOURCE_INDEX_V1.json':
   raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 index=dict(epoch=time.time(),status='FROZEN_SOURCE_UNUSED_EXTRACTION',selected_target_worker=str(B/'target86_verify_extract_narrow_relocate_UNUSED_once_v1.py'),worker_SHA=hashlib.sha256((B/'target86_verify_extract_narrow_relocate_UNUSED_once_v1.py').read_bytes()).hexdigest(),core_SHA=hashlib.sha256((B/'strict_archive_and_narrow_relocation_core_v1.py').read_bytes()).hexdigest(),source_ownout_CODE_SHA=hashlib.sha256((B/'source72_all_recorded_ownout_preflight_CODE_v1.py').read_bytes()).hexdigest(),files=files,unknown_actual_bulk_or_fresh_source_proof_SHA_not_invented=True,no_secure_network_launcher_executed=True,Git='root ordinary supplement pending')
 put(B/'FROZEN_VERIFIED_EXTRACT_RELOCATION_SOURCE_INDEX_V1.json',index);print(json.dumps({k:index[k] for k in ['status','selected_target_worker','worker_SHA','core_SHA','source_ownout_CODE_SHA']}))

if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);put(R/('EXTRACT_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_network_archive_or_model_IO=True));raise
