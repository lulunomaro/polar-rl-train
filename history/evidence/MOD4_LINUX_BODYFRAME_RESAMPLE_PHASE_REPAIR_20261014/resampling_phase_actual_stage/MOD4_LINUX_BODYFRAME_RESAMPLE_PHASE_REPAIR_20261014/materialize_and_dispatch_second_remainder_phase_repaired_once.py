"""Root only, after actual finite owner exit and complete fourcase decision. No retries."""
from pathlib import Path
import json,sys,time,os,traceback,hashlib,subprocess,base64
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=D/'payload_v1'
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as base
ROOT=base.BASE+'/bodyframe20k_second_resample_phase_remainder2470_v1_20261015';STAGE=base.BASE+'/.bodyframe_second_phase_remainder2470_unique_upload_v1_20261015';FAILED=base.BASE+'/bodyframe20k_second_formal3600_same_profile_v1_20261014';PRIOR=base.BASE+'/bodyframe20k_repair_pipeline_v7_original_startup_order_20261014'
SHA='1a370588db7706006a303e8d4ccd2efbb966201b826d3719ae42692a5339fd1a'
def save(name,v):
 p=R/name;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def run(c,code,context,label,timeout=180):
 compile('CONTEXT='+repr(context)+'\n'+code,'<new body second operation>','exec')
 si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+base.PY+' -',timeout=timeout);si.write('CONTEXT='+repr(context)+'\n'+code);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
 save(label+'_'+str(time.time_ns())+'.json',dict(epoch=time.time(),code=rc,stdout=out.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_automatic_retry=True));assert rc==0,(rc,err.decode('utf8','replace')[-1800:]);return json.loads(out)
def main():
 decision=R/'RESAMPLING_PHASE_RECOVERY_SCOPE_DECISION_ACTUAL.json';v=json.loads(decision.read_bytes());assert v['passed'] and v['original_fourcase_actual_scope_bound'] and v['remaining_second_allocation_recovery_reasonable'] and v['selected_source_SHA']==SHA
 # A local snapshot only. No remote connection is made while the finite coordinator still owns transport.
 code="[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false);$p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match 'python' -and $_.CommandLine -match 'run_.*retention.*(batch|fixed_three)'});ConvertTo-Json -InputObject $p -Depth 4 -Compress"
 rr=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(code.encode('utf-16-le')).decode()],capture_output=True,check=True);assert not json.loads(rr.stdout.decode('utf-8-sig'))
 files={p.name:p for p in P.glob('*.py')};files['recovery_target_CPU_materialize_v1.py']=D/'recovery_target_CPU_materialize_v1.py';files[decision.name]=decision
 for key,row in v['evidence'].items():
  p=Path(row['path']);assert base.sha(p)==row['sha256'] and p.stat().st_size==row['bytes'];files['evidence_'+key+'.json']=p
 for n,p in files.items():
  if n.endswith('.py'):compile(p.read_bytes(),str(p),'exec')
 intent=R/'SECOND_BODY_PHASE_REPAIR_MATERIALIZE_DISPATCH_INTENT_ACTUAL.json';assert not intent.exists();save(intent.name,dict(epoch=time.time(),root=ROOT,upload_stage=STAGE,source_SHA=SHA,files={n:dict(path=str(p),bytes=p.stat().st_size,sha256=base.sha(p)) for n,p in files.items()},unknown_outcome_read_before_any_continuation=True))
 c=None;sf=None
 try:
  c=base.connect();run(c,"from pathlib import Path\nimport json\ns=Path(CONTEXT['stage']);r=Path(CONTEXT['root']);assert not s.exists() and not r.exists();s.mkdir();print(json.dumps(dict(new_upload_stage=str(s))))",dict(stage=STAGE,root=ROOT),'SECOND_BODY_PHASE_REPAIR_NEW_UPLOAD_STAGE')
  sf=c.open_sftp();sf.get_channel().settimeout(60)
  for name,p in files.items():sf.put(str(p),STAGE+'/'+name)
  sf.close();sf=None
  context=dict(upload_stage=STAGE,root=ROOT,base=base.BASE,failed=FAILED,original=PRIOR,source_SHA=SHA,files={n:base.sha(p) for n,p in files.items()})
  target=run(c,(D/'recovery_target_CPU_materialize_v1.py').read_text(encoding='utf8'),context,'SECOND_BODY_PHASE_REPAIR_TARGET_CPU_MATERIALIZE_ACTUAL',240);assert target['passed'] and not target['GPU_dispatched']
  launch='''from pathlib import Path
import json,subprocess,time,os,psutil
r=Path(CONTEXT['root']);assert not (r/'ROOT_UNIQUE_DISPATCH_INTENT.json').exists() and not (r/'PIPELINE_ONCE_CONSUMED.json').exists()
proof=json.loads((r/'PIPELINE_TARGET_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['target_CPU_actual'] and proof['actual_fourcase_decision_bound']
with (r/'ROOT_UNIQUE_DISPATCH_INTENT.json').open('x') as f:json.dump(dict(epoch=time.time(),root=str(r),source_SHA=proof['source']['sha256']),f);f.flush();os.fsync(f.fileno())
env=os.environ.copy();env.pop('CUDA_VISIBLE_DEVICES',None)
p=subprocess.Popen([CONTEXT['python'],'-u',str(r/'bodyframe_recovery_formal_parent_v1.py')],cwd=r,env=env,start_new_session=True,stdin=subprocess.DEVNULL,stdout=(r/'pipeline_parent.log').open('xb'),stderr=subprocess.STDOUT)
q=psutil.Process(p.pid);out=dict(epoch=time.time(),pid=p.pid,created=q.create_time(),argv=q.cmdline(),cwd=q.cwd(),source=proof['source'],target_CPU_passed=True,PPO_NOT_yet_claimed=True)
with (r/'ROOT_UNIQUE_DISPATCH_ACTUAL.json').open('x') as f:json.dump(out,f,indent=2);f.flush();os.fsync(f.fileno())
print(json.dumps(out))
'''
  dispatched=run(c,launch,dict(root=ROOT,python=base.PY),'SECOND_BODY_PHASE_REPAIR_FORMAL_UNIQUE_DISPATCH_ACTUAL');print(json.dumps(dict(targetCPU=target,dispatch=dispatched)))
 except BaseException:
  save('SECOND_BODY_PHASE_REPAIR_MATERIALIZE_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_requires_readonly_recovery=True));raise
 finally:
  if sf:sf.close()
  base.close(c)
if __name__=='__main__':main()
