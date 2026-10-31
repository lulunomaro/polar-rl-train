"""Freeze local actual reports/source scope before the one archival record."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
F=T/'W35_SHARED_MATERIAL_NEXT_SOLO_SOURCE_V218_20261101'
Q=T/'W35_SHARED_MATERIAL_20K_ORIGINAL_PHYSX_ADMISSION_V217_20261101'
def read(p):return json.loads(Path(p).read_bytes())
def put(name,value):
 with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2)
index=F/'INDEX218_FROZEN.json';sha=hashlib.sha256(index.read_bytes()).hexdigest()
assert sha=='6578d66cd1aa1e68da9c054f3efc09bfe38dc20194e7ae6524165b390911f365'
for row in read(index)['files']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
cpu=read(F/'reports/CPU218_ACTUAL.json')
v=read(R/'CURRENT_ACTUAL210_E0_CONTINUES_AND217_20K_MATERIAL_REPAIR_PASS_V3.json')
v.update(epoch=time.time(),frozen218=dict(path=str(F),INDEX_SHA=sha,files=24,status='SOURCE_CPU_PASS_NO_GO',
 selected_wrapper='source/worker_full218.py',entrypoint_SHA='bb6dd0d17ba201996e8507b45fe974ee0caa14dad5a52809a713337c696cb8f9',
 delegate214_worker_SHA='3abbbbd66351380e2b287d8490cac73cfbc5dd27681c1b2d008085a88c082170',
 CPU_report=str(F/'reports/CPU218_ACTUAL.json'),new_CPU_groups=3,refusals=17,model_or_remote_calls=0,
 requires_E0_normal_closed_NEWformalCPU_freshCNone_before_next_solo=True),
 W35_next='Frozen218 source/CPU ready to ROOT-review; next W35-only one-hour original writer after original210 E0 complete closure+NEWformalCPU+freshCNone. No current W35 learning.')
put('CURRENT_ACTUAL210_E0_CONTINUES_217_CAPACITY_PASS_218_FROZEN_NEXT_SOLO_V4.json',v)
req=read(R/'AUTOMATION210_ACTUAL217_FULL20K_REPAIR_PASS_UPDATE_REQUEST_V3.json')
req['prompt']=req['prompt'].replace('CURRENT_ACTUAL210_E0_CONTINUES_AND217_20K_MATERIAL_REPAIR_PASS_V3.json',
 'CURRENT_ACTUAL210_E0_CONTINUES_217_CAPACITY_PASS_218_FROZEN_NEXT_SOLO_V4.json')
req['prompt']='''LATEST218_SOURCE_FROZEN_NOT_NEW_TRAINING。218已FROZEN T/W35_SHARED_MATERIAL_NEXT_SOLO_SOURCE_V218_20261101/INDEX218_FROZEN.json SHA6578d66cd1aa1e68da9c054f3efc09bfe38dc20194e7ae6524165b390911f365/24files；LOCAL新CPU一次3groups17reject PASS，模型rawNPZUSDSDKGPUremote0。source/worker_full218.py1439B SHAbb6dd0d17ba201996e8507b45fe974ee0caa14dad5a52809a713337c696cb8f9包装原worker_full214字节不变；contract218/solo218_protocol及HANDOFF/CONTROL218_ORIGINAL_TEMPLATE_INSERTIONS给ROOT原solo owner三处最小插入点。Task/Ready/Schedule模板未激活，GO.source_CPU_SHA按原owner整份Ready VALUE hash，非历史模型CPU SHA，不把ReadySHA塞进Task造成manifest循环。E0仍原active，下一W35-only 3900/save3600/exit300须210正常完整保存/close+matching新formalCPU PASS+freshCNone，ROOT再冻结真实evidence/Task/manifest/Ready并执行原唯一owner；不可hotadd当前owner或把sourceCPU称W35已开训。生产仍原mildDR，无probe额外setter。218所有冻结文件纳入同210实际phase归档，无218GPU标签。
''' + req['prompt']
put('AUTOMATION210_ACTUAL217_218_FROZEN_UPDATE_REQUEST_V4.json',req)
first=read(R/'ROOT210_E0_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json')['first']
probe=read(Q/'reports/ROOT217_ORIGINAL_20K_SHARED_MATERIAL_NATIVE_OR_ERROR_RETURNED_ACTUAL.json')
put('CAPTURE210_ACTUAL217_COMPLETE_FROZEN_SCOPE_V3.json',dict(epoch=time.time(),
 automation_request_file='AUTOMATION210_ACTUAL217_218_FROZEN_UPDATE_REQUEST_V4.json',
 additional_frozen_roots=[dict(path=str(F),index='INDEX218_FROZEN.json',SHA=sha)],
 trials=['208 original RM70 sourceCPU and V1/V2 errors/V3 selected source',
  '209 mixed E0/JUMP source/CPU and original80env zeroPT admission; unused one-hour launch',
  '210 user three-hour source/static solewriter two roles/Windows join fixture refusal and corrected new fixture',
  '210 original E0 genuine firstnewPPO/fullsave; W35 original startup0PPO64Kfailure',
  '211 original CAD scene zeroPT', '212 initial lease-prefix refusal then actual ownMOD4 xyzw80env zeroPT',
  '213 old-expert saved-schema join/sourceCPU/new E2 full-world fields source only',
  '214 shared original CAD material sourceCPU/corrected force of evidence/necessary E0 source comparison',
  '215 exact owned original stop+one SIGINT unsuccessful',
  '216 user-authorized exact PID termination/post-signal readerRC1/readonly exit success',
  '217 V1 relative-CIM refusal before marker/network then V2 actual20k model-free restore/reset/native8/material PASS',
  '218 frozen next-solo sourceCPU only; no actual new W35 GO or learning'],
 pending_excluded=['Original210 E0 normal FINAL/fee/NEWformalCPU not due; ordinary supplements only',
  'W35 future fullPPO restore/native24/FIRST/fullRM70 skills not executed after repair',
  'E2/E3 full skills and complete SuperMimic conversion remain pending',
  'Future any unfrozen/active sources excluded until their exact index exists',
  'GUI windows preserved; no new replay or display action in210 phase'],
 remote_artifacts_metadata_only=dict(E0_first=first['first_complete'],
  E0_saved_snapshot=dict(epoch_BJT='2026-11-01T01:12:38.65+08:00',iteration=32133,
   bytes=22962066,SHA='0d82b616e45b1b90408fc2726af2e83698f93aef7bbb9f228f064a60bc3c8151'),
  W35_original_source=dict(iteration=32336,bytes=17619013,SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'),
  generated217_USD=[dict(path=x['path'],bytes=x['bytes'],SHA=x['SHA'])for x in probe['full_UTF8']if Path(x['path']).suffix in('.usd','.usda','.usdc')]),
 no_binary_model_raw_or_hostGPU_for_Git=True,all_original_errors_retained=True))
print(json.dumps(dict(passed=True,frozen218_SHA=sha,source_cpu_only=True,current210_still_original_E0_window=True)))
