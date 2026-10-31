"""Append the material failure/authorized termination; E0 continues unchanged."""
from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def read(p):return json.loads(p.read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
done=read(T/'W35_USER_AUTHORIZED_EXACT_PROCESS_TERMINATION_V216_20261101/reports/ROOT216_ORIGINAL_POST_SIGNAL_EXIT_AND_NODE_RECEIPTS_ACTUAL.json')
assert done['original_worker_status']['original_out'] and done['private_EX_free'] and done['original_node_exit']['all_own_children_waited']
assert done['original_node_terminal']['row']['returncode']==-9
request=read(R/'AUTOMATION210_ACTUAL_FIRST_THREE_HOUR_AND_RM70_UPDATE_REQUEST.json')
work=read(R/'CURRENT_ACTUAL210_E0_THREE_HOUR_FULL_RM70_TWO_ROLE_FIRST_AND_NORMAL_WORK_ORDER.json')
work.update(epoch=time.time(),current_update='E0 actual firstPASS/3hour continues; W35 noPPO64K materials startup failure terminated by exact human authorization216',
 original_W35_failure=dict(engine='PxPhysics::createMaterial: limit of64K materials reached',first_PPO=False,fullstate_native24_not_qualified=True,
  original_worker_PID=990366,original_create=1793463868.49,original_node_wait_returncode=-9,worker_OUT=True,private_EX_free=True,
  original_STOP_and_single_SIGINT_not_sufficient=True,human_exact='授权只终止W35故障进程',only_original_worker_termination_permission_CONSUMED=True,
  post_signal_identity_reader_RC1_preserved=True,independent_readonly_exit_collection_PASS=True,normal_SDK_App_close_not_claimed=True,original_source_checkpoint_retained=True),
 E0_original_owner_row_at216=done['current_owner_rows']['e0_72'],W35_next='214source shared original CAD material repair; new full20k0PT before future training, no hotadd/current-owner secondwriter')
put('CURRENT_ACTUAL210_E0_THREE_HOUR_CONTINUES_W35_MATERIAL_FAILURE_AND216_EXIT_V2.json',work)
prefix=f'''CURRENT_ACTUAL210_E0_THREE_HOUR_CONTINUES_W35_64K_MATERIAL_STARTUP_FAILURE_AND216_AUTHORIZED_EXIT_20261101。覆盖两路均开训/仍W35startup pending/准许kill所有新worker措辞。
FIRST READ {R/'CURRENT_ACTUAL210_E0_THREE_HOUR_CONTINUES_W35_MATERIAL_FAILURE_AND216_EXIT_V2.json'}；KNOWN_ACTIVE210_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json；T/W35_USER_AUTHORIZED_EXACT_PROCESS_TERMINATION_V216_20261101/reports/ROOT216_ORIGINAL_POST_SIGNAL_EXIT_AND_NODE_RECEIPTS_ACTUAL.json。
W35原FIRST850已实际消费返回False，setup后实际PhysX64K material上限错误，未fullrestore/native24/FIRST。原STOP_AFTER_SAVE+一次SIGINT无响应；人类明确“授权只终止W35故障进程”，216严格核验PID990366/create1793463868.49/exe/fullargv/cwd+原owner/go后TERM→必要KILL；原终止入口在post-signal身份切换检查RC1保留，独立只读续收不重发信号，证明原workerOUT、原node p.wait=-9/NODE_EXIT/allwaited/privateEXfree/ownerACK true。没有W35新Pi/FINAL/技能成功，不能声称正常App.close。此kill许可仅此原PID，已消费，不是允许杀未来probe或新进程。E0行仍production，未signal/热改/重启，3小时原GO/save/nominal不变。故障费用由原owner自然记录，正常结束时SUMONCE，不退款/补款/idlefee/重计。
同一个已授权子代理/root/w35_rm70_expert_normalization208正在NEW {T/'W35_FULL_RM70_MATERIAL_LIMIT_REPAIR_SOURCE_V214_20261101'}仅LOCAL修复：保留原完整CAD mesh、70mm峰谷与1.5deg及原D0μ桶/采样/RNG/物理guards；只消除每arena重复材质并共享原实际material，不凭空更改摩擦/恢复。原CAD material来源(.9,.8,0)，TerrainImporter最终绑定须actual SDK readback。64K是已见错误，不声称唯一未FIRST原因。214未冻结源排除直到INDEX。需要独立NEW20k无PT probe覆盖fresh构造→自身原DR physical setter restore→new episode reset→8controls、材料绑定/值/已知64K错误检查，不能80小case代替规模。216后c27 privateEX已探明free，只是当时证明；新probe要fresh light资源/当前210exactowner/run/go/CLOSE72后才他机/globalseriallease。当前owner仍E0 active，绝不能假CNone/重跑launch/hotadd/newwriter；新W35学习放原E0完整正常保存后的下一staticready cohort，除非人类新指示安全handoff。
213旧专家source已冻结：{T/'OLD_EXPERTS_NORMALIZATION_NEXT_READY_SOURCE_V213_20261101/INDEX213_FROZEN.json'} SHA54ca90c1a4970d9fe137a12b5435c46585b6524d3b97089d33fd1b14c4a37690/39files；新CPU3groups/12saved-schema joins/4拒绝PASS，0模型rawNPZSDKGPUremote；E2新1200controls24s/20k/1680worker完整sameUID along/cross/signedyaw/pre-reset caller是source-only，原900目的已消费，不重放；E3 V14仅未用metadata组件，无完整N1bootstrap，不能假runtime ready。完整技能与SuperMimic转换仍未完成。213可本phase归档，214active不收。
以下原210实际首轮/时限/约束作为未被本段覆盖的完整交接：
'''
request['prompt']=prefix+request['prompt']
put('AUTOMATION210_ACTUAL216_W35_FAILED_E0_CONTINUES_UPDATE_REQUEST_V2.json',request)
print(json.dumps(dict(passed=True,W35_terminal=True,E0_preserved=True,old_kill_permission_consumed=True)))
