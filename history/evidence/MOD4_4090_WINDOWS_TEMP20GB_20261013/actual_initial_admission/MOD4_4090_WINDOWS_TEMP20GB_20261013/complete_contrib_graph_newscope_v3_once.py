"""Complete remaining exact local Lab extension dependency; retain both failed scopes."""
from pathlib import Path
import ast,json,hashlib,time,zipfile,sys,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
OLD=R+'/temporary_scope2048_memory20GB_extension_ready_v2_20261013';NEW=R+'/temporary_scope2048_memory20GB_contrib_ready_v3_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 receipt=D/'reports/CONTRIB_COMPLETE_GRAPH_NEW_V3_ACTUAL.json';assert not receipt.exists()
 src=Path('F:/isaacsim/IsaacLab/source/isaaclab_contrib');files=[p for p in src.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p) and p.suffix not in ('.pyc','.pyo')]
 package=D/'EXACT_TESTED_SDK_CONTRIB_EXTENSION_GRAPH_COMPLETION_20261013.zip';assert not package.exists();rows=[]
 with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(files):
   row=dict(archive=p.relative_to(src).as_posix(),bytes=p.stat().st_size,sha256=H(p));rows.append(row);z.write(p,row['archive'])
  z.writestr('EXACT_EXTENSION_MANIFEST.json',json.dumps(dict(file_rows=rows,original_tested_source=str(src),extension_version='0.0.2'),indent=2))
 remote=R+'/packages/'+package.name;upload(package,remote,60)
 assert powershell(connect(),"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",30)==H(package)
 original=ast.parse((D/'repair_missing_extension_and_new_scope_once.py').read_text(encoding='utf8'));f=next(x for x in original.body if isinstance(x,ast.FunctionDef) and x.name=='main');node=next(x for x in f.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='code' for t in x.targets))
 code=eval(compile(ast.Expression(node.value),'unexecuted-new-contrib-component','eval'),dict(R=R,OLD=OLD,NEW=NEW,package=package,H=H))
 code=code.replace("sdk_exact/source/isaaclab_mimic","sdk_exact/source/isaaclab_contrib").replace("temporary2048_memory20GB_extension_ready_sequence_v2","temporary2048_memory20GB_contrib_ready_sequence_v3")
 # Actual six Lab source extension graph must now be fully present before Kit.
 anchor="assert not new.exists();new.mkdir();"
 code=code.replace(anchor,"import tomllib\nfor name in ('isaaclab','isaaclab_assets','isaaclab_tasks','isaaclab_rl','isaaclab_mimic','isaaclab_contrib'):\n cfg=tomllib.loads((r/'sdk_exact/source'/name/'config/extension.toml').read_text(encoding='utf8'))\n for dep in cfg.get('dependencies',{}):\n  if dep.startswith('isaaclab'):assert (r/'sdk_exact/source'/dep/'config/extension.toml').exists(),dep\n"+anchor)
 file=D/'contrib_exact_graph_newscope_v3_cpu.py';assert not file.exists();file.write_text(code,encoding='utf8');compile(code,str(file),'exec');remote_file=R+'/'+file.name;upload(file,remote_file,60)
 actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+remote_file+"'",90))
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_sdk_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode sdk -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35)
 receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,actual_six_Lab_dependency_source_graph_completed_CPU=True,actual_new_task_requested_once=True,old_failures_no_PPO_costs_retained=True,package=dict(path=str(package),bytes=package.stat().st_size,sha256=H(package))),indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(receipt),new_scope=NEW,new_SDK_stage_requested=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('CONTRIB_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_no_replay=True),indent=2),encoding='utf8');raise
