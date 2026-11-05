from pathlib import Path
import json
from shared_control_access import connection
N=Path(__file__).resolve().parent;R=N/'reports/newton_setup01'
code="""from pathlib import Path
import json,time,subprocess,psutil
b=Path('/home/lc01/Zonglin Li/zonglin2');a=b/'tasks/MOD4V2_SCUT_JUMP200_1793870808568676500_rewardapi03'
hardware=b/'tasks/MOD4V2_SCUT_JUMP200_1793870808568676500_representation02/hardware'
out={}
for p in [hardware,hardware/'mjcf/scene.xml',hardware/'assets/import_contract.json',a/'package/mod4v2_scut/BINDINGS.json']:
 out[str(p)]=dict(exists=p.exists(),text=p.read_text()if p.name=='BINDINGS.json'else None)
out['launcher']=(b/'run-python.sh').read_text()
out['gpu']=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,name,memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
out['apps']=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
print(json.dumps(dict(epoch=time.time(),files=out,ram=psutil.virtual_memory().available)))
"""
with connection(R,'NEWTON_REFERENCE_INSPECTION')as(c,t):out=t.code(c,t.PY72,code,{},timeout=45)
with(R/'REFERENCES_RETURNED01.json').open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
print(json.dumps(out))
