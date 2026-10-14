from pathlib import Path
import sys,json,time
B=Path(__file__).resolve().parent;W=B.parent;REPORTS=B/'reports'
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as base
connect=base.connect;close=base.close;sha=base.sha;PY=base.PY;BASE=base.BASE
ROOT=BASE+'/bodyframe20k_second_resample_phase_remainder2470_v1_20261015'
SOURCE='1a370588db7706006a303e8d4ccd2efbb966201b826d3719ae42692a5339fd1a'
def save(name,value):
 p=REPORTS/(name+'_'+str(time.time_ns())+'.json')
 with p.open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
 return p
def run(c,code,context,label,timeout=180):
 compile('CONTEXT='+repr(context)+'\n'+code,'<new readonly bodysecond operation>','exec')
 si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+PY+' -',timeout=timeout);si.write('CONTEXT='+repr(context)+'\n'+code);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
 receipt=save(label,dict(epoch=time.time(),code=rc,stdout=out.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_automatic_retry=True));assert rc==0,str(receipt)
 return json.loads(out),receipt
