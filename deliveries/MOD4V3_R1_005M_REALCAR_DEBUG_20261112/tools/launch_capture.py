from pathlib import Path
import json,sys,shlex
R=Path('D:/claude2/fangzhen');B=Path(__file__).resolve().parents[1];p=json.loads((B/'evidence/ORIGINAL_TRAINING_PLAN.json').read_text(encoding='utf-8'));sys.path.insert(0,str(R/'tmp'));from step7_remote_access import connect
c=connect();s=c.open_sftp();remote=p['root']+'/realcar_debug_capture_20261112_r1';s.mkdir(remote);s.put(str(B/'tools/capture_training_runtime.py'),remote+'/capture.py')
with s.open(remote+'/PLAN.json','w') as f:f.write(json.dumps(p))
checkpoint=p['support'].rsplit('/support',1)[0]+'/train040m_rough_r1_round2_r1/model_005m.pt';cmd=[p['python'],'-B','-u',remote+'/capture.py','--plan',remote+'/PLAN.json','--out',remote+'/capture01','--checkpoint',checkpoint]
e={'CUDA_VISIBLE_DEVICES':'0','OMNI_KIT_ACCEPT_EULA':'YES','ISAACSIM_ACCEPT_EULA':'Y','WARP_CACHE_PATH':p['root']+'/cache/warp','XDG_CACHE_HOME':p['root']+'/cache','TMPDIR':p['root']+'/tmp'}
code='import subprocess,os,json; e=dict(os.environ); e.update('+repr(e)+'); p=subprocess.Popen('+repr(cmd)+',env=e,stdin=subprocess.DEVNULL,stdout=open('+repr(remote+'/capture.log')+',"xb"),stderr=subprocess.STDOUT,start_new_session=True); print(json.dumps({"pid":p.pid}))'
_,o,err=c.exec_command(' '.join(map(shlex.quote,[p['python'],'-B','-c',code])),timeout=30);reply=o.read().decode();print(reply,err.read().decode());(B/'evidence/CAPTURE_LAUNCH.json').write_text(json.dumps(dict(remote=remote,command=cmd,response=reply),indent=2)+'\n',encoding='utf-8');s.close();c.close()

