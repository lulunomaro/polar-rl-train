from pathlib import Path
import ast
B=Path(__file__).resolve().parent
s=(B/'build_h1_normal_mod4v1_source_v2.py').read_bytes().decode('utf-8')
a="d=get(driver_rel)"
z="d=get(driver_rel);driver_original_AST=ast.dump(ast.parse(d),include_attributes=False);d=''.join(' '+line if line.startswith(' ') else line for line in d.splitlines(keepends=True));assert ast.dump(ast.parse(d),include_attributes=False)==driver_original_AST"
assert s.count(a)==1;s=s.replace(a,z,1)
s=s.replace("generator_attempt='H1SRC_GENERATOR_V2_CRLF'","generator_attempt='H1SRC_GENERATOR_V3_DRIVER_INDENT',prior_generator_error2=str(B/'H1SRC_GENERATOR_ORIGINAL_ERROR_1793563210336441300.json')",1)
s=s.replace("trial_id='H1SRC_GENERATOR_V2_CRLF'","trial_id='H1SRC_GENERATOR_V3_DRIVER_INDENT'",1)
ast.parse(s)
with (B/'build_h1_normal_mod4v1_source_v3.py').open('x',encoding='utf-8',newline='') as f:f.write(s)
print('V3 preserves V1+V2 errors; indentation-only preparatory transform proved AST identical.')
