"""Fetch only project model-source paths explicitly referenced by the active contract."""
from pathlib import Path
import json,sys,hashlib,time
D=Path(__file__).resolve().parent;O=D/'native_model_sources';assert not O.exists();O.mkdir();T=D.parent/'mod4v1_experts_fulldr_rm70_20261101';sys.path.insert(0,str(T));from project_connector import connect72
B='/home/lc01/Zonglin Li/zonglin2';paths=['incoming/mod4_rolling_20260913/chassis_mod4/scene.xml','incoming/mod4_fixed_20260912/chassis_mod4/scene.xml','incoming/mod4_rolling_20260913/tools/build_rolling_rollers_usd.py'];want='fbb0393883d31ac96f8cd58a184585470222f7daf96af6aa5d0748a1752c366c';rows=[];c=connect72();s=c.open_sftp()
try:
 for i,p in enumerate(paths):
  full=B+'/'+p
  try:st=s.stat(full)
  except FileNotFoundError:rows.append(dict(path=full,exists=False));continue
  assert st.st_size<2000000,'Source text cap only; no native protocol mutation'
  with s.open(full,'rb')as f:raw=f.read(st.st_size+1)
  assert len(raw)==st.st_size;h=hashlib.sha256(raw).hexdigest();out=O/(str(i)+'_'+Path(p).name);out.write_bytes(raw);rows.append(dict(path=full,bytes=len(raw),SHA=h,local=str(out),matches_contract_source_mjcf_SHA=h==want,physical_reads=1))
finally:s.close();c.close()
r=dict(epoch=time.time(),purpose='Functional native-asset/MuJoCo source alignment using contract-declared lineage only',files=rows,checkpoint_raw_SDK_GPU_budget_lease_or_foreign_operations=0);(D/'NATIVE_MODEL_SOURCE_LINEAGE.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))
