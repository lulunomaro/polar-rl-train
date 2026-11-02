"""Preserve fresh80-v1 storage error; derive complete dependency installation v2."""
from pathlib import Path
import json,ast,sys,runpy
R=Path(__file__).resolve().parent
M=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101\A_PPO_SOURCE\reports\INSTALL227_SOURCE_ROWS_FROZEN.json')
manifest=json.loads(M.read_text(encoding='utf-8'))
outside=[r['relative'] for r in manifest['files'] if not r['relative'].startswith('runtime/') and Path(r['relative']).suffix.lower() not in ('.pt','.pth','.pyc')]
(R/'reports/FRESH80_V1_STORAGE_ERROR_AND_V2_DEPENDENCIES.json').write_text(json.dumps({'v1':'failed before SDK creation: launcher208 requires kit_isolation directly under MOD4_NEW208_JOB_ROOT; v1 put it under output gpu0','no_model_or_optimizer_calls':True,'v2':'new unused job, exact job-only Kit path and all existing non-PT outside-runtime install dependencies','outside_runtime_candidates':outside},indent=2),encoding='utf-8')
p=R/'probe_w35_fresh80_full_dr_v2.py';assert not p.exists();src=(R/'probe_w35_fresh80_full_dr.py').read_text(encoding='utf-8').replace("storage=out/'kit_isolation'","storage=job/'kit_isolation'");ast.parse(src);p.write_text(src,encoding='utf-8')
src=(R/'deploy_fresh80_full_dr_once.py').read_text(encoding='utf-8').replace("sup=R/'fresh80_supervisor_v1.py'","sup=R/'fresh80_supervisor_v2.py'").replace("R/'probe_w35_fresh80_full_dr.py'","R/'probe_w35_fresh80_full_dr_v2.py'").replace('MOD4V1_W35_FRESH80_FULLDR_','MOD4V1_W35_FRESH80_FULLDR_V2_')
needle="shutil.copy2(S/'original_run_manifest.json',B/'original_run_manifest.json')"
extra="\nfor relative in "+repr(outside)+":\n source=S/relative\n if source.is_file():\n  destination=B/relative;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,destination)\n"
assert src.count(needle)==1;src=src.replace(needle,needle+extra)
p=R/'deploy_fresh80_full_dr_v2_once.py';assert not p.exists();ast.parse(src);p.write_text(src,encoding='utf-8');sys.path.insert(0,str(R));runpy.run_path(str(p),run_name='__main__')
