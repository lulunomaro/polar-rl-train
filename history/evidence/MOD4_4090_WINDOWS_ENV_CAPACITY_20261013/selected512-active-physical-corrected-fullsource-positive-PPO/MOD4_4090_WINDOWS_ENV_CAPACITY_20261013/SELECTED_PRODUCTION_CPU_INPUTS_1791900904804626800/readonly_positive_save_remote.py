from pathlib import Path;import json,hashlib,base64,time
s=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/capacity512_selected_ownstate_production_v1_20261013');a=s/'attempts/temporary2048_train_v1';o=a/'output'
def j(p):return json.loads(p.read_bytes())
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
mf=j(s/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json');latest=j(o/'WINDOWS4090_LATEST_COMPLETE.json');assert latest['actual_updates']>0
out=dict(epoch=time.time(),scope=str(s),manifest=mf,latest=latest,startup=j(o/'WINDOWS4090_FULLSTATE_STARTUP_VERIFIED.json'),left=j(o/'LEFT_HEAD_ACTUAL_INIT_VERIFIED.json'),guardian=j(a/'GUARDIAN_CURRENT.json'),dispatch=j(a/'DISPATCH_RECEIPT.json'),files=[ref(Path(mf['source']['path'])),ref(Path(latest['path']))])
raw=(a/'worker_stdout.log').read_bytes();assert not any(x in raw for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'PhysX error:'));out['whole_current_stdout']=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode(),no_PhysX_error=True,activity_snapshot_not_final=True)
out['payload']={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),base64=base64.b64encode(p.read_bytes()).decode()) for p in (s/'payload').iterdir() if p.suffix in ('.py','.json')}
print(json.dumps(out))
