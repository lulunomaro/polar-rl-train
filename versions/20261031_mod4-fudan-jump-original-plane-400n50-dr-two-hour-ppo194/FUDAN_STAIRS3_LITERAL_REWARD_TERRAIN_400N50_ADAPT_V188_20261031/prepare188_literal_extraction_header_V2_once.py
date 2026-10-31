from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent
p=N/'build188_literal_stairs3_and_terrain_bridge_once.py';s=p.read_text(encoding='utf8')
s=s.replace("P=N/'package';P.mkdir()","P=N/'package_v2';P.mkdir()")
s=s.replace("license=rt[:rt.index('import')]","first_import=min(x.lineno for x in ra.body if isinstance(x,(ast.Import,ast.ImportFrom)));license=''.join(rt.splitlines(keepends=True)[:first_import-1])")
s=s.replace('ROOT188_LITERAL_REWARD_TERRAIN_EXTRACTION_FROZEN_SOURCE.json','ROOT188_LITERAL_REWARD_TERRAIN_EXTRACTION_V2_FROZEN_SOURCE.json')
ast.parse(s);(N/'build188_literal_stairs3_and_terrain_bridge_V2_header_once.py').write_text(s,encoding='utf8')
with (N/'reports/ROOT188_LITERAL_EXTRACTION_V1_ORIGINAL_HEADER_SYNTAX_FAILURE.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),returncode=1,original_error="SyntaxError: invalid syntax line31 'from wheel_legged_gym ' in generated outer header; prefix was cut at substring import inside from-import",before_any_reward_test=True,source_methods_original_bytes_unchanged=True,V1_package_retained=True,repair='New package_v2: stop license prefix before first AST Import/ImportFrom. No reward method/config edit.',no_GPU_or_model=True),f,indent=2)
