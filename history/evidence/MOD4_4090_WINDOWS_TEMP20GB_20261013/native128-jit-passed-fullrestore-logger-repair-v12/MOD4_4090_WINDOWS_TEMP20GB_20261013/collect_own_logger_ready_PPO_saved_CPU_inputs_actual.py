"""Readonly own immutable saves and startup receipts, not a GPU or train launcher."""
from pathlib import Path
import json,time,sys,subprocess,hashlib,base64
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,base
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';S=R+'/temporary_scope128_memory20GB_logger_ready_v12_20261013'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 stamp=str(time.time_ns());dest=D/('OWN_PPO_CPU_INPUTS_'+stamp);dest.mkdir()
 code="""from pathlib import Path;import json,hashlib
s=Path('"""+S+"""');o=s/'attempts/temporary2048_train_v1/output';r=s/'attempts/temporary2048_fullrestore_v1/output'
def j(p):return json.loads(p.read_bytes())
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
assert (o/'WINDOWS4090_LATEST_COMPLETE.json').exists(),'Healthy pending own first PPO fullsave'
a=j(r/'WINDOWS4090_LATEST_COMPLETE.json');b=j(o/'WINDOWS4090_LATEST_COMPLETE.json');assert a['actual_updates']==0 and b['actual_updates']>0
refs=[ref(Path(x['path'])) for x in (a,b)]
assert [x['sha256'] for x in refs]==[x['sha256'] for x in (a,b)]
print(json.dumps(dict(scope=str(s),own_fullrestore=a,own_PPO_latest=b,files=refs,train_startup=j(o/'WINDOWS4090_FULLSTATE_STARTUP_VERIFIED.json'),left_initialization=j(o/'LEFT_HEAD_ACTUAL_INIT_VERIFIED.json'),sourcefreeze=j(s/'attempts/temporary2048_train_v1/SOURCEFREEZE_ACTUAL.json'),dispatch=j(s/'attempts/temporary2048_train_v1/DISPATCH_RECEIPT.json'),guardian=j(s/'attempts/temporary2048_train_v1/GUARDIAN_CURRENT.json'))))
"""
 encoded=base64.b64encode(code.encode()).decode();actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+encoded+"'))\"",60))
 for i,row in enumerate(actual['files']):
  p=dest/(('FULLRESTORE_SOURCE.pt' if i==0 else 'OWN_PPO_SAVED.pt'));subprocess.run(base('scp')+['-q','Win10@10.24.4.210:'+row['path'],str(p)],check=True,capture_output=True,timeout=60);assert H(p)==row['sha256'] and p.stat().st_size==row['bytes'];row['local_actual_path']=str(p)
 f=dest/'ACTUAL_COLLECTION.json';f.write_text(json.dumps(actual,indent=2),encoding='utf8');(D/'reports'/('OWN_PPO_SAVED_ACTUAL_COLLECTION_'+stamp+'.json')).write_text(json.dumps(dict(epoch=time.time(),collection=str(f),twohost_state_SHA_exact=True),indent=2),encoding='utf8');print(str(f))
if __name__=='__main__':main()
