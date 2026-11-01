"""Exact already-joined H1 typed source candidates: file metadata only, no PT opens/hash/decode."""
from pathlib import Path
import json,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;local=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027\NORMAL_H1_PPO86B_400N50_NEW86_SOURCE_PREPARATION_V1\typed_source\NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt');remote='/data/robemo/polar-rl-train/validation_runs/NORMAL_H1_PPO86B40050_WHOLECPU_NATIVE24_20261029v2/job0/source/NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt'
v={'kind':'EXACT_H1_71DB_EXISTING_SOURCE_LOCATION_METADATA_ONLY','expected_bytes':16879851,'expected_SHA_from_producer':'71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4','local_source':{'path':str(local),'exists':local.is_file()},'old_executed_driver_declared_source_on_its_original_target':remote,'PT_opens':0,'PT_hashes':0,'PT_decodes':0,'canonical_or_SDK_access':False}
if local.is_file():st=local.stat();v['local_source'].update(bytes=st.st_size,mtime_ns=st.st_mtime_ns,expected_size_matches=st.st_size==16879851)
c=connect72();s=c.open_sftp()
try:
 try:st=s.stat(remote);v['exact_original_target_path_on_current72']={'exists':True,'bytes':st.st_size,'expected_size_matches':st.st_size==16879851}
 except FileNotFoundError:v['exact_original_target_path_on_current72']={'exists':False,'no_alternate_directory_enumeration':True}
finally:s.close();c.close()
v['next_transport_if_needed']='After newH1sourcefinal, declare one separate transport purpose for exact local71db bytes+SHA and exclusive new72source file; original remains unchanged; actualSDK purpose separately caches one byte/hash/decode. No source transfer performed here.'
p=R/'reports'/('H1_typed_source_location_metadata_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(v,ensure_ascii=False,indent=2))
