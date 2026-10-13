from pathlib import Path
import zipfile,json,hashlib,time,sys
R=Path(__file__).resolve().parent;out=R/'install_reports/LABRL_BOUND_COMPATIBILITY_ARTIFACTS_CPU_ACTUAL.json';assert not out.exists()
p=R/'packages/OFFICIAL_LABRL_BOUND_DEPENDENCY_COMPATIBILITY_20261013.zip';dest=R/'official_dependency_compatibility_wheels_v6';assert not dest.exists();dest.mkdir()
with zipfile.ZipFile(p) as z:
 m=json.loads(z.read('COMPATIBILITY_ACTUAL_MANIFEST.json'));assert m['packaging_preserved']=='23.0' and len(m['wheels'])==3
 rows=[]
 for x in m['wheels']:
  assert x['filename'] in z.namelist() and '/' not in x['filename'] and '\\' not in x['filename']
  b=z.read(x['filename']);assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']==x['published_sha256']
  q=dest/x['filename'];q.write_bytes(b);rows.append(dict(**x,actual_remote_path=str(q),actual_published_SHA_exact=True))
req=R/'ACTUAL_LABRL_BOUND_COMPATIBILITY_PINS_V6.txt';assert not req.exists()
req.write_text(''.join(x['name']+'=='+x['version']+' --hash=sha256:'+x['sha256']+'\n' for x in rows),encoding='utf8')
report=dict(epoch=time.time(),python=sys.executable,packaging_preserved='23.0',core_Torch_Sim_TensorDict_fourEditable_unchanged=True,wheels=rows,pins=str(req),only_new_owned_env_preparation=True,no_GPU_Kit_PPO=True)
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),pins=str(req))))
