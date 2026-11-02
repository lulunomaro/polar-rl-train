"""One declared byte/hash-only transport of existing71db to a NEW72source; no decode/retype/SDK.
Original frozen/local file unchanged. Actual SDK gets a separate one-cache read purpose.
"""
from pathlib import Path
import json,hashlib,datetime,time
from project_connector import connect72
R=Path(__file__).resolve().parent;source=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027\NORMAL_H1_PPO86B_400N50_NEW86_SOURCE_PREPARATION_V1\typed_source\NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt');expected='71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4';stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');purpose='H1_TYPED71DB_EXACT_TRANSPORT_'+stamp+'_'+str(time.time_ns());guard=R/'H1_TYPED71DB_TRANSPORT_PURPOSE_CONSUMED.json';assert not guard.exists();guard.write_text(json.dumps({'purpose':purpose,'source_path':str(source),'bytes':16879851,'SHA':expected,'byte_opens':1,'decodes':0,'no_auto_replay':True},indent=2),encoding='utf-8')
before=source.stat()
with source.open('rb')as f:raw=f.read()
after=source.stat();actual=hashlib.sha256(raw).hexdigest();assert len(raw)==16879851 and actual==expected and before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns
root='/home/lc01/Zonglin Li/zonglin2/tasks/'+purpose;remote=root+'/NORMAL_H1_TYPED71DB_PRESERVED_SOURCE.pt';receipt={'kind':'H1_TYPED71DB_ONE_PURPOSE_PRESERVED_BYTE_TRANSPORT_ACTUAL','purpose':purpose,'source_path':str(source),'remote_source_path':remote,'source_bytes':len(raw),'source_SHA':actual,'local_physical_byte_opens':1,'local_SHA_computations':1,'local_or_remote_decodes':0,'original_unchanged_size_mtime':True,'remote_existing_file_overwritten':False,'remote_source_hash_scope':'TransportwriterSHA from same exactverifiedbuffer; remoteindependentcontentSHA deferredtoactualonecache SDK load','SDK_or_GPU_or_canonical_access':False}
c=connect72();s=c.open_sftp()
try:
 try:s.stat(root)
 except FileNotFoundError:s.mkdir(root)
 else:raise FileExistsError('Preserve unused-target transport uniqueness; no overwrite')
 with s.open(remote,'wx')as f:f.write(raw);f.flush()
 st=s.stat(remote);assert st.st_size==len(raw);receipt.update(remote_stat_bytes=st.st_size,remote_stat_mtime=st.st_mtime,transport_returned=True)
 with s.open(root+'/TRANSPORT_ACTUAL.json','wx')as f:f.write(json.dumps(receipt,indent=2))
finally:s.close();c.close()
p=R/'reports'/('H1_typed71db_transport_actual_'+stamp+'.json');p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(receipt,ensure_ascii=False,indent=2))
