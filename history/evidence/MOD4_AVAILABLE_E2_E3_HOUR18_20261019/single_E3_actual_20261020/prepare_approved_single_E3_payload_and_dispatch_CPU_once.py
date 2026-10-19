"""Apply explicit one-window offline-cost approval to the reviewed E3-only proposal."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';C=B/'single_E3_proposal';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 p=json.loads((C/'PROPOSAL.json').read_bytes());test=json.loads((R/'SINGLE_E3_PENDING_COST_OWNER_CPU_ACTUAL.json').read_bytes());assert test['passed'] and test['owner_SHA']==H(C/'single_E3_pending_cost_owner_v1.py')
 approval=dict(epoch=time.time(),proposal_id=p['proposal_id'],explicit_offline_cost_approval=True,question='E3单卡方案已通过CPU检查：72上按原配方训练1小时，另留最多3900秒生命周期的真实费用记录，等210切回Linux后从原剩余预算回账一次。是否允许这一次离线挂账？不增加预算、不自动续第二小时。',actual_human_answer='单卡继续训呗，时间不能浪费算力不能浪费',scope='One E3 window only; actual pending cost once later against original remaining budget; no extra budget or automatic second hour.');put('SINGLE_E3_EXPLICIT_OFFLINE_COST_APPROVAL_ACTUAL.json',approval)
 dst=C/'payload/recovery';shutil.copytree(p['payload'],dst,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));old=(dst/'three_slot_finite_node_v1.py').read_bytes();new=(C/'three_slot_finite_node_local_owner_v1.py').read_bytes();(dst/'three_slot_finite_node_v1.py').write_bytes(new)
 m=json.loads((dst/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());changed=[]
 for r in m['files']:
  if r['relative']=='three_slot_finite_node_v1.py':r.update(bytes=len(new),SHA=H(dst/r['relative']));changed.append(r['relative'])
 assert changed==['three_slot_finite_node_v1.py'];(dst/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8');spec=copy.deepcopy(p['spec']);spec['manifest_SHA']=H(dst/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 for r in m['files']:
  f=dst/r['relative'];assert f.stat().st_size==r['bytes'] and H(f)==r['SHA']
 listener=(B/'controllers/owner_listener_ready_available_two_cpu_v1.py').read_text('utf8').replace("{'e2':{},'recovery':{}}","{'recovery':{}}")
 ast.parse(listener);(C/'owner_listener_ready_single_cpu_v1.py').write_text(listener,encoding='utf8',newline='\n');shutil.copy2(B/'controllers/three_slot_common_v1.py',C/'three_slot_common_v1.py')
 out=dict(epoch=time.time(),passed=True,proposal=p,approval=approval,specs={'recovery':spec},roots={'recovery':p['node_root']},payloads={'recovery':str(dst)},owner_root=p['owner_root'],changed_payload_files=changed,production_worker_reward_PPO_runtime_assets_source_unchanged=True,source_SHA=p['source_SHA'],node_endpoint_only_reviewed=True,owner_files={n:H(C/n) for n in ('single_E3_pending_cost_owner_v1.py','three_slot_common_v1.py','owner_listener_ready_single_cpu_v1.py')},no_remote_GO_GPU_or_account_IO=True)
 put('APPROVED_SINGLE_E3_PAYLOAD_CPU_PREPARED_ACTUAL.json',out);print(json.dumps(dict(approved_single_E3_payload_ready=True,source_SHA=p['source_SHA'],only_node_endpoint_changed=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('APPROVED_SINGLE_E3_PAYLOAD_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
