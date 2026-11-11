from pathlib import Path
import json,sys,shlex,time
R=Path('D:/claude2/fangzhen');B=Path(__file__).resolve().parent
for n in ['model','config','runtime','firmware','tools','plant','evidence','docs','examples']:(B/n).mkdir()
p=json.loads((R/'_mod4v2_src_20261106/sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/PLAN.json').read_text(encoding='utf-8'))
sys.path.insert(0,str(R/'tmp'));from step7_remote_access import connect;c=connect();s=c.open_sftp()
# Read the actual frozen runtime configuration without importing an Isaac app.
code='import sys,os,json; sys.path[:0]='+repr([p['shared_package'],p['package'],p['support']])+'; os.environ["MOD4_SCUT_SOURCE_PATHS"]='+repr(p['source_paths'])+'; from mod4v3_ppo_v1.scut_flat_rewards import configuration_v2; from kinematics import mechanical_delta_bounds; cfg=configuration_v2(); print(json.dumps({"scale":cfg.obs_input_scale_cfg,"clip":cfg.obs_input_clip_cfg,"scale_enabled":cfg.obs_input_scale_enabled,"scale_streams":cfg.obs_input_scale_streams,"ctrl_mode_obs_enabled":cfg.ctrl_mode_obs_enabled,"delta_bounds":[mechanical_delta_bounds(s) for s in ["left","right"]]}))'
_,o,e=c.exec_command(' '.join(map(shlex.quote,[p['python'],'-B','-c',code])),timeout=40);stdout=o.read().decode();stderr=e.read().decode();print(stdout);print(stderr);data=json.loads(stdout.strip().splitlines()[-1]);(B/'evidence/TRAINING_OBSERVATION_CONFIG.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
for name in ['runtime_config.json','semantics.json','semantics.py','kinematics.py','model_parameters.json','PROVENANCE.json','PHYSX_COMPATIBILITY.json','RELEASE_R3.json','SCUT_LICENSE']:
 try:s.get(p['package']+'/'+name,str(B/'plant'/name))
 except FileNotFoundError:pass
(B/'plant/assets').mkdir();s.get(p['package']+'/assets/import_contract.json',str(B/'plant/assets/import_contract.json'));s.get(p['package']+'/assets/robot_physx.usda',str(B/'plant/assets/robot_physx.usda'))
# The existing local MJCF is checked byte-for-byte against the actual training package.
import shutil,hashlib
local=R/'tmp/mod4v3_r3_extract_20261107/MOD4v3_HW300N60_R3';remote_xml=s.open(p['package']+'/mjcf/scene.xml').read();assert hashlib.sha256(remote_xml).digest()==hashlib.sha256((local/'mjcf/scene.xml').read_bytes()).digest();shutil.copytree(local/'mjcf',B/'plant/mjcf');shutil.copytree(local/'legacy',B/'plant/legacy',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
(B/'evidence/ORIGINAL_TRAINING_PLAN.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('MATCHING_TRAINING_PLANT_COPIED',hashlib.sha256(remote_xml).hexdigest());s.close();c.close()
