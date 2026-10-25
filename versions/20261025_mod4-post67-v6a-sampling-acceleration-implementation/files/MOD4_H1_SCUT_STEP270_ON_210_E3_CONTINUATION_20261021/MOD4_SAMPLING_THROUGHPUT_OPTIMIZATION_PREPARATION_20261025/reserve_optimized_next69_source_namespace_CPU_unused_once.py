"""Reserve next69 controllers/reward source only after actual68 GO/PPO."""
from pathlib import Path
import ast,hashlib,json,shutil,time
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports'
P=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V1_RESOURCE_V69_20261025'
meta=json.loads((P/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
assert meta['passed'] and meta['H1_new_step270_actual_GO_and_positive_PPO'] and meta['E3_same50Hz_actual_GO_and_positive_PPO']
assert not N.exists();N.mkdir();(N/'reports').mkdir()
for name in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(P/name,N/name)
oldname='H1step270_reward_sagtuck6a_2510v68';newname='H1step270_sampling_opt1_sagtuck6a_2510v69'
for name in ('collect_selected_pair_finals_unused_once.py','collect_selected_H1_final_unused_once.py','collect_selected_pair_first_PPO_unused_once.py','collect_selected_H1_first_PPO_unused_once.py','deploy_selected_pair_unused_once.py','deploy_selected_H1_only_unused_once.py','review_selected_pair_models_unused_once.py','review_selected_H1_model_unused_once.py'):
 text=(P/name).read_text('utf8').replace(oldname,newname);ast.parse(text)
 with (N/name).open('x',encoding='utf8') as f:f.write(text)
source_only=dict(epoch=time.time(),passed=True,current68=str(P),current68_actual_runid=meta['run_id'],future69=str(N),future_remote_basename=newname,scope='controllers and unchanged V6A reward/checker source only; optimization admission/source integration still pending',no_payload_models_Task_GO_remote_install_or_fee=True,no_future70_reserved=True,no_live68_source_change=True)
with (N/'reports/AFTER_ACTUAL68_GO_PPO_NEXT69_SOURCE_ONLY_RESERVED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(source_only,f,indent=2)
with (R/'AFTER_ACTUAL68_NEXT69_SOURCE_ONLY_RESERVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(source_only,f,indent=2)
print(json.dumps(source_only))
