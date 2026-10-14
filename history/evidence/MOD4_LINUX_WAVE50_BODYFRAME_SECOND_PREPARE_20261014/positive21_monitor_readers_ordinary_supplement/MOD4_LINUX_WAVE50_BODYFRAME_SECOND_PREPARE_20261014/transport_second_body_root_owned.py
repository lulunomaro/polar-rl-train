from pathlib import Path
import sys,json,time
B=Path(__file__).resolve().parent;W=B.parent;REPORTS=B/'reports'
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as base
connect=base.connect;close=base.close;sha=base.sha;PY=base.PY;BASE=base.BASE
ROOT=BASE+'/bodyframe20k_second_formal3600_same_profile_v1_20261014'
SOURCE='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139'
def save(name,value):
 p=REPORTS/(name+'_'+str(time.time_ns())+'.json')
 with p.open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
 return p
def run(c,code,context,label,timeout=180):
 compile('CONTEXT='+repr(context)+'\n'+code,'<new readonly bodysecond operation>','exec')
 si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+PY+' -',timeout=timeout);si.write('CONTEXT='+repr(context)+'\n'+code);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
 receipt=save(label,dict(epoch=time.time(),code=rc,stdout=out.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_automatic_retry=True));assert rc==0,str(receipt)
 return json.loads(out),receipt
