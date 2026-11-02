"""Generate NEW bootstrap version; consumed CPU V1/V2 and frozen tests stay intact."""
from pathlib import Path
R=Path(__file__).resolve().parent;old=R/'run_command_candidate_core_integration_cpu_v2_dependency_once.py';new=R/'run_command_candidate_core_integration_cpu_v3_explicit_path_once.py';assert not new.exists();text=old.read_text(encoding='utf-8')
text=text.replace('CPU_V2','CPU_V3').replace('CPU_V2_ONCE','CPU_V3_ONCE').replace('CPU_V2_DEPS','CPU_V3_EXPLICIT_PATH').replace("R/'reports/COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V1.json'","R/'reports/COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V2.json'")
start=text.index(' cmd="CUDA_VISIBLE_DEVICES=');end=text.index('\n _,so,se=c.exec_command(cmd',start)
replacement=''' argv=[job+'/test_command_tracking_core_integration_cpu_v1.py','--vendor-parent',native+'/roles/E0/worker_sources','--fixture',job+'/synthetic_cpu_contract_check.py','--bridge-source',job+'/native_supermimic_bridge.py','--candidate-dir',job,'--output-dir',resultdir]
 bootstrap="import sys,runpy,importlib.util,json;sys.path[:0]=[%r,%r];p=importlib.util.find_spec('rich');assert p and p.origin.startswith(%r);print('ACTUAL_RICH_DEPENDENCY '+json.dumps(dict(origin=p.origin)));sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(job,deps,deps,argv,argv[0])
 cmd="CUDA_VISIBLE_DEVICES='' "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(bootstrap)'''
text=text[:start]+replacement+text[end:];text=text.replace('SYNTHETIC_CORE_DEPENDENCY_CORRECTION_NO_SOURCE_HOTPATCH','SYNTHETIC_CORE_EXPLICIT_AFTER_LAUNCHER_SYS_PATH_NO_SOURCE_HOTPATCH').replace('SYNTHETIC_ACTUAL_CANDIDATE_CORE_CPU_TEST_DEPENDENCY_V2','SYNTHETIC_ACTUAL_CANDIDATE_CORE_CPU_TEST_EXPLICIT_PATH_V3')
import ast
ast.parse(text);new.write_text(text,encoding='utf-8',newline='\n');print(new)
