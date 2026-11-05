"""One finite transport for the exact v2 native failure and its scoped repair test."""
from pathlib import Path
import importlib.util,json,time
ROOT=Path(__file__).resolve().parent
attempt='04'
s=importlib.util.spec_from_file_location('v2_discovery_transport',ROOT/'discover.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
REPORTS=ROOT/'reports'

if __name__=='__main__':
    plan=json.loads((ROOT/'PLAN.json').read_bytes());job=plan['remote_root']
    with m.local.connection('V2_NATIVE_REPRESENTATION_CHECK_'+attempt)as(client,d):
        sf=client.open_sftp()
        try:
            layer=(ROOT/'physx_finite_representation.usda').read_text(encoding='utf8')
            layer=layer.replace('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/assets/robot.usd',job+'/hardware/assets/robot.usd')
            for name,raw in [('physx_representation.usda',layer.encode()),('native_representation_worker.py',(ROOT/'native_representation_worker.py').read_bytes())]:
                with sf.file(job+'/'+name.replace('.usda','_'+attempt+'.usda').replace('.py','_'+attempt+'.py'),'wx')as f:
                    if name.endswith('.py'):raw=raw.replace(b'physx_representation.usda',('physx_representation_'+attempt+'.usda').encode()).replace(b'NATIVE_REPRESENTATION_',('NATIVE_REPRESENTATION_'+attempt+'_').encode())
                    f.write(raw);f.flush()
        finally:sf.close()
        code=r'''
from pathlib import Path
import subprocess,json,os,time
j=Path(v['job']);env=dict(os.environ,CUDA_VISIBLE_DEVICES='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',PYTHONDONTWRITEBYTECODE='1')
with(j/'NATIVE_REPRESENTATION.log').open('xb')as log:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(j/'native_representation_worker.py')],cwd=j,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
 rc=p.wait(timeout=180)
files={}
for name in ['NATIVE_REPRESENTATION_RESULT.json','NATIVE_REPRESENTATION_LIMITS.json','NATIVE_REPRESENTATION_ERROR.json','NATIVE_REPRESENTATION_CLOSE_INTENT.json']:
 q=j/name
 if q.exists():files[name]=json.loads(q.read_bytes())
files['log']=(j/'NATIVE_REPRESENTATION.log').read_text(encoding='utf8',errors='replace')
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes())
print(json.dumps(dict(epoch=time.time(),returncode=rc,files=files,remaining=c['remaining_training_seconds'],active=c['active_segment'])))
'''
        code=code.replace('native_representation_worker.py','native_representation_worker_'+attempt+'.py').replace('NATIVE_REPRESENTATION','NATIVE_REPRESENTATION_'+attempt)
        value=d.code(client,d.PY72,code,dict(job=job),timeout=210)
        (REPORTS/('NATIVE_REPRESENTATION_'+attempt+'_ACTUAL.json')).write_text(json.dumps(value,indent=2),encoding='utf8')
        print(json.dumps({k:v for k,v in value.items()if k!='files'}))
        print(json.dumps({k:v for k,v in value['files'].items()if k!='log'}))
