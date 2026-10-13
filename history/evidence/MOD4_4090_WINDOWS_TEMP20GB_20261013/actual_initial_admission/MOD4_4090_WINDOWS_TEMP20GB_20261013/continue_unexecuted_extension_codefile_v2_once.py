"""Only unexecuted CPU extension completion after command-line length refusal."""
from pathlib import Path
import ast,json,hashlib,time,sys,base64,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';OLD=R+'/temporary_scope2048_memory20GB_left_repair_20261013';NEW=R+'/temporary_scope2048_memory20GB_extension_ready_v2_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 report=D/'reports/UNEXECUTED_EXTENSION_CODEFILE_V2_ACTUAL.json';assert not report.exists()
 s=(D/'payload/temporary_state_binding.py').read_text(encoding='utf8')
 anchor="assert len(perenv_inventory(ck))==99 and floating_count(ck)==107"
 assert s.count(anchor)==1
 s=s.replace(anchor,anchor+"\n assert t['seed']==20260928 and t['layout']==[40,40] and t['command_vx_range']==[-.3,.3] and t['command_vy_yaw']==[0.,0.]\n assert (ck['actor_state_dict']['distribution.std_param']>0).all()\n assert len(b['family_counts'])==5 and sum(b['family_counts'])==N and all(type(x) is int and x>0 for x in b['family_counts'])")
 strict=D/'temporary_state_binding_strict_v2.py';assert not strict.exists();strict.write_text(s,encoding='utf8');compile(s,str(strict),'exec')
 original=ast.parse((D/'repair_missing_extension_and_new_scope_once.py').read_text(encoding='utf8'))
 mainnode=next(n for n in original.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 assignment=next(n for n in mainnode.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='code' for x in n.targets))
 package=D/'EXACT_TESTED_SDK_MIMIC_EXTENSION_MISSING_COMPLETION_20261013.zip'
 code=eval(compile(ast.Expression(assignment.value),'original-unexecuted-extension-source','eval'),dict(R=R,OLD=OLD,NEW=NEW,package=package,H=H))
 anchor="mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());"
 assert code.count(anchor)==1
 code=code.replace(anchor,"strict=r/'temporary_state_binding_strict_v2.py';assert H(strict)=='"+H(strict)+"';shutil.copy2(strict,new/'payload/temporary_state_binding.py');\n"+anchor)
 f=D/'extension_CPU_unexecuted_codefile_v2.py';assert not f.exists();f.write_text(code,encoding='utf8');compile(code,str(f),'exec')
 remote=R+'/'+f.name;upload(strict,R+'/'+strict.name,60);upload(f,remote,60)
 assert powershell(connect(),"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",30)==H(f)
 raw=powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+remote+"'",90)
 actual=json.loads(raw)
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_sdk_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode sdk -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35)
 report.write_text(json.dumps(dict(epoch=time.time(),actual=actual,original_preCPU_command_length_error_retained=True,original_oldGPU_not_replayed=True,strict_validator_source=dict(path=str(strict),sha256=H(strict)),actual_new_CPU_codefile=dict(path=str(f),sha256=H(f)),new_task_requested_once=True,PPO_not_claimed=True),indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(report),new_scope=NEW,newGPU_stage_requested=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('EXT_CODEFILE_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_no_replay=True),indent=2),encoding='utf8');raise
