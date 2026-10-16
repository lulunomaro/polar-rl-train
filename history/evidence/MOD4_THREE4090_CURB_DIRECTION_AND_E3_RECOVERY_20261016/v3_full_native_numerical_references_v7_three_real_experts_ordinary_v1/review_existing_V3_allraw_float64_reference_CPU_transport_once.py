from pathlib import Path
import os,sys,time,json,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'recovery_receipt_schema_v3';T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/recovery_receipt_schema_v3';sys.path.insert(0,str(D));from deploy_threeway_V4_actual_saved_sources_and_native_reuse_once import code,H,connect72,PY
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('V3_EXISTING_RAW_FP64_REFERENCE_CPU_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,CPU_only_existing_raw_no_GPU_replay=True));s=(Q/'native_CPU.py').read_text('utf8');s=s.replace('err=geom=force=0.','err=geom=force=cliperr=0.').replace("y=torch.from_numpy(x.reshape(-1,35));sd=s['actor_state_dict']","y=torch.from_numpy(x.reshape(-1,35)).double();sd={k:v.double() for k,v in s['actor_state_dict'].items()}");old="err=max(err,float(abs(y.numpy()-d['raw6'].reshape(-1,6)).max()));assert err<=1e-4;";assert old in s;s=s.replace(old,"err=max(err,float(abs(y.numpy()-d['raw6'].reshape(-1,6)).max()));cliperr=max(cliperr,float(abs(np.clip(y.numpy(),-6,6)-d['executed6'].reshape(-1,6)).max()));").replace('passed=True,source_SHA=task',"passed=bool(err<=1e-4 and cliperr<=1e-4),diagnostic_FP64_reference=True,original_raw_absolute_threshold_1e_4_not_changed=True,actual_clipped6_CPU_reference_maxabs=cliperr,original_FP32_rejection_retained=True,source_SHA=task").replace('NATIVE_ALL_ROWS_CPU_ADMITTED.json','NATIVE_ALL_ROWS_NUMERICAL_REFERENCE_DIAGNOSTIC_V2.json');p=D/'native_CPU_FP64_reference_diagnostic_v2.py';assert not p.exists();p.write_text(s,encoding='utf8');pw=getpass.getpass('Host72 existing raw CPU numerical review (hidden): ');c=None
 try:
  c=connect72(pw);pw=None;sf=c.open_sftp()
  try:sf.put(str(p),T+'/native_CPU_FP64_reference_diagnostic_v2.py')
  finally:sf.close()
  script="from pathlib import Path;import os,sys,json,time,subprocess,hashlib;B=Path(sys.argv[1]);p=B/'native_CPU_FP64_reference_diagnostic_v2.py';assert hashlib.sha256(p.read_bytes()).hexdigest()==sys.argv[2];e=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1');begun=time.time();r=subprocess.run([sys.argv[3],'-B',str(p),'--job','0'],cwd=B,env=e,capture_output=True,text=True);v=dict(epoch=time.time(),elapsed=time.time()-begun,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,existing_raw_CPU_only=True,no_PPO_or_source_mutation=True);q=B/'NUMERICAL_REFERENCE_CPU_V2_COMMAND_ACTUAL.json';assert not q.exists();q.write_text(json.dumps(v,indent=2));report=B/'job0/native/NATIVE_ALL_ROWS_NUMERICAL_REFERENCE_DIAGNOSTIC_V2.json';v['report']=json.loads(report.read_bytes()) if report.exists() else None;print(json.dumps(v))";v=code(c,PY,script,T,H(p),PY,timeout=600);put('V3_ALL336_EXISTING_RAW_FP64_NUMERICAL_REFERENCE_CPU_ACTUAL.json',v);print(json.dumps(v),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('FP64_EXISTING_RAW_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_retry=True));raise
