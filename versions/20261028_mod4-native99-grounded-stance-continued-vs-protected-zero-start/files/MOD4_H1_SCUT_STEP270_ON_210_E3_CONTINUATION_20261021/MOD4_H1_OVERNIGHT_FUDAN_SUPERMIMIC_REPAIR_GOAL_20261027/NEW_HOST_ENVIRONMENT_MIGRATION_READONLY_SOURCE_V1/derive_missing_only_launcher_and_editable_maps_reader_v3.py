"""Source-only missing exact referenced text/ABI closure; no footprint rescan."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;p=B/'read_known72_mod4_runtime_portability_footprint_finite_v2_no_Kit_userdata.py';s=p.read_text();t=ast.parse(s);n=next(n for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CODE' for x in n.targets));old=ast.get_source_segment(s,n.value)
code=r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time
START=time.monotonic();ROOT=Path('/home/lc01/Zonglin Li/zonglin2');ENV=ROOT/'envs/mod4';SITE=ENV/'lib/python3.12/site-packages';assert sys.flags.no_site
def text(p):
 assert p.resolve().is_relative_to(ROOT)
 with p.open('rb') as f:raw=f.read(262145)
 assert len(raw)<=262144
 return dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'))
files=[ROOT/'run-python-compat.sh',ROOT/'compat/glibc240/copyright']
for name in ['__editable___isaaclab_6_1_14_finder','__editable___isaaclab_assets_0_3_4_finder','__editable___isaaclab_rl_0_5_5_finder','__editable___isaaclab_tasks_1_10_9_finder','__editable___isaaclab_visualizers_0_1_0_finder','_cuda_bindings_redirector','cmeel_pth']:files.append(SITE/(name+'.py'))
for name in ['isaaclab-6.1.14','isaaclab_assets-0.3.4','isaaclab_rl-0.5.5','isaaclab_tasks-1.10.9','isaaclab_visualizers-0.1.0']:files.append(SITE/(name+'.dist-info')/'direct_url.json')
rows=[]
for p in files:
 if p.is_file():rows.append(text(p))
 else:rows.append(dict(path=str(p),missing_exact_path=True,no_alternative_path_guess=True))
argv=['/usr/bin/readelf','-l',str(ENV/'bin/python3.12')];r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=12)
tools={x:shutil.which(x) for x in ['tar','gzip','pigz','zstd','conda-pack']}
print(json.dumps(dict(epoch=time.time(),scope='missing only exact launcher/registration/loader/license/tool paths; no repeated footprint',rows=rows,source_python_ELF_interpreter=dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),packaging_tool_paths=tools,source_root_available_bytes=shutil.disk_usage(ROOT).free,no_Torch_SDK_GPU_model_raw_ledger_or_source_write=True,elapsed_seconds=time.monotonic()-START,env_inventory=dict(logical_bytes=None,partial_time_bound='not_rescanned'),compat_inventory=dict(logical_bytes=None,partial_time_bound='not_rescanned'))))
'''
s=s.replace(old,repr(code)).replace('KNOWN72_ENV_PORTABILITY_V2','KNOWN72_ENV_PORTABILITY_V3_MISSING_TEXT').replace('maximum_remote_seconds=120','maximum_remote_seconds=45').replace('ch.settimeout(120)','ch.settimeout(45)')
ast.parse(s);ast.parse(code);out=B/'read_known72_exact_missing_launcher_maps_and_license_finite_v3.py'
with out.open('x',encoding='utf8') as f:f.write(s)
v=dict(epoch=time.time(),source_AST_passed=True,remote_AST_passed=True,missing_only_no_model_or_env_footprint_rescan=True,old_source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_source_SHA=hashlib.sha256(out.read_bytes()).hexdigest(),remote_timeout_seconds=45,actual_execution_pending_root_global_lease=True)
with (B/'SOURCE_V3_MISSING_EXACT_REFERENCED_TEXT_DERIVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
