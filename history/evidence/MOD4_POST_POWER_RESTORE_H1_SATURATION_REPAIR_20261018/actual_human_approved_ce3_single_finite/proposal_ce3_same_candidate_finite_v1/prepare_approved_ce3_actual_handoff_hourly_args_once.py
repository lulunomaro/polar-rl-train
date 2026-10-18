"""Save new explicit approval and actual detached chain into the same hourly monitor."""
from pathlib import Path
import json,time,hashlib,tomllib,subprocess
B=Path(__file__).resolve().parent;R=B/'reports';TOP=B.parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 raw=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_bytes();old=tomllib.loads(raw.decode('utf8'))
 assert old['id']=='mod4-10' and old['status']=='ACTIVE' and old['rrule']=='FREQ=HOURLY;INTERVAL=1' and old['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 grant=json.loads((R/'HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json').read_bytes());dispatch=json.loads((R/'HUMAN_APPROVED_CE3_OWN_NEW_NATIVE_SINGLE_FINITE_CHAIN_DETACHED_ACTUAL.json').read_bytes());current=json.loads((R/'CE3_NATIVE_FIRST_FINITE_CURRENT_ACTUAL.json').read_bytes());identity=json.loads((R/'CE3_V2_SOURCE_LISTENER_ACTUAL_READY.json').read_bytes())['actual_identity']
 assert grant['explicit_human_grant_received'] and grant['actual_human_answer']=='批准这一有限段'
 original=TOP/'ORIGINAL_PRE_HUMAN_APPROVED_CE3_PENDING_MOD4_10_PROMPT_UTF8.txt'
 with original.open('x',encoding='utf8') as f:f.write(old['prompt'])
 cmd="@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python(?:w)?\\.exe$' -and $_.CommandLine -like '*collect_ce3_own_native_and_first_missing_finite_once.py*'} | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine) | ConvertTo-Json -Depth 4"
 # Use basename because exact actual argv is relative to this workspace, not an absolute path.
 cmd=cmd.replace('\\.exe','\.exe')
 out=subprocess.check_output(['powershell','-NoProfile','-Command',cmd],text=True,encoding='utf8').strip();cim=json.loads(out) if out else []
 if isinstance(cim,dict):cim=[cim]
 assert len(cim)<=1
 handoff=dict(epoch=time.time(),human_approval=grant,actual_detached_chain=dispatch,actual_source_owner_identity=identity,
     latest_local_target_epoch=current['epoch'],latest_local_target_row=current['rows'].get('NODE_CURRENT.json'),
     current_transport_owner_only_if_CIM_identity_alive=cim,known_original_deployer_and_partial_finisher_returned=True,
     initial_deployer_missing_listener_preowner_error_retained_and_V2_verified_partial_finish=True,
     native_first_CPU_reader='review_ce3_own_native_and_first_complete_local_CPU_once.py',
     current_finite_collector='collect_ce3_own_native_and_first_missing_finite_once.py',
     complete_collection='CE3_OWN_NATIVE_FIRST_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json',
     complete_CPU='CE3_OWN_NATIVE_FIRST_COMPLETE_LOCAL_CPU_ACTUAL.json',
     next_final_collector='collect_existing_ce3_final_original_cost_exit_once.py',
     next_final_reader='review_ce3_closed_final_whole_model_original_cost_CPU_once.py',
     next_final_frozen_builder='prepare_ce3_closed_final_Linux_GPU1_frozen_CPU_once.py',
     no_more_paid_window_authorized=True,source_Adam646100_first646120_final_expected646100_plus20updates=True,
     old_proposal_PENDING_TASK_label_is_historical_not_current_human_grant=False,
     actual_source_manifest_SHA=grant['manifest_SHA'],old_prompt=dict(path=str(original),bytes=original.stat().st_size,SHA=H(original)),
     unique_stage_helper=str(TOP/'archive_human_approved_ce3_single_finite_unique_stage_once.py'),
     unique_stage_once_only_if_HEAD_ffaf64_no_note_DEST_tag_and_receipt=True,
     all_old_stage_unique_ordinary_helpers_consumed=True,large_artifacts_index_only_all_text_sources_errors_reports_Git=True)
 # The manifest-bound TASK is immutable: inherited pending/old Adam labels are explicitly historical.
 handoff['manifest_TASK_historical_pending_and_645140_labels_preserved_unchanged']=True
 wp=TOP/'NEXT_HUMAN_APPROVED_CE3_OWN_NATIVE_ONE_FINITE_ACTUAL_HANDOFF_V8_WORK_ORDER.json'
 with wp.open('x',encoding='utf8') as f:json.dump(handoff,f,ensure_ascii=False,indent=2)
 prompt='''最新真实人类答复优先：人类已明确回答上一轮具体问题“批准这一有限段”。旧pending未答/不能创建deployer字段已被此答复与本轮actual覆盖，不再为同段问确认。只批准从完整ce3接续同H1 public4-only V2的一段，最多24updates/1800秒，300退出预留、free<8GiB完整update后savedstop、25GiBstart，原1188000s预算不变；不授权下一窗口、奖励/LR/STD/动作边界/物理阈值变更，E2/E3paid hold零worker/GO/账。
R=C:/Users/lulu/Desktop/claude/mjcf/MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018，E=R/proposal_ce3_same_candidate_finite_v1。先读R/NEXT_HUMAN_APPROVED_CE3_OWN_NATIVE_ONE_FINITE_ACTUAL_HANDOFF_V8_WORK_ORDER.json、E/reports/HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json、HUMAN_APPROVED_CE3_OWN_NEW_NATIVE_SINGLE_FINITE_CHAIN_DETACHED_ACTUAL.json、CE3_NATIVE_FIRST_FINITE_CURRENT_ACTUAL.json，随后存在的CE3_OWN_NATIVE_FIRST_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json和CE3_OWN_NATIVE_FIRST_COMPLETE_LOCAL_CPU_ACTUAL.json优先；再以自己的laterCURRENT/FINAL/ORIGINAL_ERROR/实际PID创建argv-root-save-EXIT/原canonical/真实fcntl优先，PID与排程不永久alive或未来FINAL。
本轮已实际派出source唯一owner81434/create1792297628.59 root=/mnt/mod4_linux_durable_20261013/H1cq_1810p3/owner；72GPU0 UUID16828f91节点16510/create1792297630.24，nativeworker16513/create1792297630.68，root=/home/lc01/Zonglin Li/zonglin2/tasks/H1cq_1810p3。来源就是ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90/owned24/17Adam646100，不回退b326、不重设STD/actor。原478文件包已实际完整target manifest/199tensor105float finite/17Adam/source/actualinstalledRSLrunnerPPO和SDKmath SHA CPU过，原public4-only coeff.001/clip6/LR/可学STD/所有环境reward、DR、physics、hardware不变。原fourcontroller byteexact，节点真正spawn自己的新20knative180/720/all3.6Mpolicy14.4Mphysical；独立全rowCPU必须真正过才原owner给一个GO。当前最初capture仍native/noerror/go空；later actual优先，不冒新native全CPU或PPOpositive。原native独立Torch/NumPyFP64同绝对1e-4，原FP32false诊断分列，query1e-6/COM1e-5/closure.002/mimic.01/geometry1e-6/event1e-6不降。
初次deployer在任何owner/node/native/GO前因source-only listener本机路径缺失停止，target全包和source3controller上传已完成。原FileNotFoundError/source/report保留。新V2只按实际两端无owner/node/native/GO、target已有CPU、原P2成本结清/canonicalNone/两真实fcntl/同GPU private和shared free/portfree/三已传文件SHA核后，补唯一缺的original listener并核四fileSHA/AST，再新owner实际listenerready+signedE2E3holdACK和node。没有重run原deployer、native、Task/once或热改live。原TASK中pending-human/source645140字面历史标签不覆盖真实新sourceSHA/Adam646100/manifest与人类授权；原件未改。
E/collect_ce3_own_native_and_first_missing_finite_once.py同一target连接最多900秒metadata后，只收缺的新native initial/complete及production startup0/immutablefirst完整PT，再一次source readonly状态+原账；不是永久watcher。只有actualCIM PID/create/exe/argv真alive才独占210/72/249transport。已核本collector PID63304/create北京时间12:27:34.261371（快照非永久owner），argv是workspace相对路径；不要用绝对root字符串过滤误判不存在。root/agents其alive时仅本机reports+CIM，不能另SSH/为Git连host/新watcher。actual返回再root收回；若900s缺first或nativeCPU如实pending，后来新有界只取缺失，不能重复完整PT/native/raw为hash。完整collection存在才执行E/review_ce3_own_native_and_first_complete_local_CPU_once.py。first期望17Adam646100→646120，twohost全PT+本机199tensor105float全model/runtimefinite、startup0源9STD8critic17Adam literalexact/sourceepisode+1/phaseage0/all17项变化后才本轮PPOpositive。原100normal先于80public4，first正常行不冒aux效果。0PPO native owner活着而canonicalNone/两锁未held是正常，不准另开writer。
下一只收缺本段真正完整FINAL/PT/原费用once/父孩子actualout/canonicalNone/两原fcntl和targetprivate/sharedfree，E/collect_existing_ce3_final_original_cost_exit_once.py、review_ce3_closed_final_whole_model_original_cost_CPU_once.py已prepared未执行，actual闭合才全CPU审。max24最终Adam=646100+20*实际updates，不按nominalend猜FINAL/保证bound。只有originalwriter真正GO后productionloadlearnsaveSDKclosechildwait/ownerterminal独立interval一次扣原账；native/frozen/E2E3未GO0。无复制canonical/clearactive/refund/tail/二扣/自动预算/热延当前grant/新paid窗。
本批准允许另一空闲4090独立冻结新模型、不能为了评测停健康训练。最终新source本机全CPU后可用prepared E/prepare_ce3_closed_final_Linux_GPU1_frozen_CPU_once.py生成它自己的完整新包，再fresh实际资源/privatefcntl/shared短准入/sourceSDKCPU和unused native120→全rowCPU→unusedfull1500；不得复用ce3旧frozen native或重放旧full。当前仅准备未来helper，无新冻结结果。旧ce3原39起跳/12落地/0恢复、ready79/80、267ordinary、60bad_orientation(主pitch58/roll2)+1closure、19/80全15s、12落地恢复最长153callback<原200等所有false有效prefix与FP32失败/新双FP64同1e-4审计保留，不改成技能PASS。orientation名字两项实际projectedgravity非rate；legacy _mod4_jump.active未保存unknown，不能冒唯一因果或擅改reward/command/STD/LR/门槛。
E2 behavior paid hold保留fixed1093/64、10122/64(+22,-0)、1050/64、1121/64；E3paidhold strict0/96但57/96有效prefix直立≥50并15s存活/normal8/8/39closure首败，不说都没站起。210单4090 D上次21.6GB<25GiB无GPUworker，metadataowner不冒GPU准入；D /dev/nvme0n1p5原授权ntfs3rw已恢复，WindowsC系统readonly，189旧NPZ精确清理consume不追加、不写C/force/remount/fstab/搬原件/tmpfs。3060SSH恢复但无新当前desktop签名/MSVCRT准入，LaptopGPU暂停。不能称三卡PPO或100%。72只zonglin2新写，source只owned/mnt，不改系统driverglibc/profile/installedSDK/旧env/其它AI。
原master812a4b+004005/RM003002001/solecanonical1188000s330h七extensions/20k60928原source/24/LR1e-4adaptiveKEEPSTD1/35-38-6/.0025×4TGS32/4/100Hz/history5msbin3/D0D7white_v3+noise+rewardhardware保持。STD可学非单独freeze/reset；nonfinite/unknown/missingcallback自己durable failedprefix save-stop；无H2H3/fullS8/70/±6-8-10/第二gate/teacher/envID地形truth/futurecontact/liveheadingposition纠偏/外力/hysteresis/NCCL/平均。保护E0/W35/gate148/f51650mm26/26/all祖先false/失败prefix/CURB27.5及35/20/H1旧25。S3S5未毕业，world数descriptive、35seed60928六dev02/03profiles缺/heldout61011/12不调参；publicSDK非loadedbinarybitexact/authored34非cookedShapeLocal-manifold/COM未实物标定/hostlatency非板deadline。Windows9400.8606925旧pending与512未知尾分列。
凭据/HMAC只SSHstdin+childstdin-memory不argvlog盘Git，旧Nargv披露保留不冒无OSaudit。全部成功失败/source/读者/helper未执行/实际pathsizesHA/工作单monitor/appreceipt成本按AGENTS归档，大PTNPZUSDZIPraw只actualindex保原件，partialdeferred。新真实stage唯一ID human-approved-ce3-public4-single-finite-native180，helper R/archive_human_approved_ce3_single_finite_unique_stage_once.py只HEAD仍ffaf64且无note/DEST/tag/commit才一次record_experiment/exacttitle+note-F annotatedtag；lateractualHEAD/receipt/remote main/tag/peel/alloldobjects/tracked优先。已record不能重helper/record/tag/同stagecommit，pushfail existingobjects。后报告ordinarysupplement，不为写回HEAD无限补档。旧unique65d508/ordinary03035、58e648、ffaf64及全部旧stage/helper/Task/native/once不重。
same mod4-10 ACTIVE每1h/同target01a07a2d-9036-7531-a012-692df9f56353，旧停电延期撤销，无第二monitor/watcher/驻守/5minSSH/旧RPCmirrorTUI-SCUTresumeonce/killotherjob/删锁/自动budget。继续推进已批本段/新模型冻结与安全交接，不机械等hourly、盲失败轴/重consume/降guard/干扰别人/扩scope。实际本段完成不等全课完成；不再自动新paid窗。本轮人类获实际native启动通知后，正常健康pending静默不重复；只真正新完整firstCPU/FINAL/新冻结/实质修复/重大退化/新增必要人类动作NOTIFY。旧pending完整prompt原件R/ORIGINAL_PRE_HUMAN_APPROVED_CE3_PENDING_MOD4_10_PROMPT_UTF8.txt只历史，later真实human/ownactual优先。'''
 args=dict(mode='update',id=old['id'],kind='heartbeat',name=old['name'],prompt=prompt,rrule=old['rrule'],status=old['status'],targetThreadId=old['target_thread_id'])
 with (TOP/'AUTOMATION_HUMAN_APPROVED_CE3_ACTUAL_HOURLY_ARGS_V8.json').open('x',encoding='utf8') as f:json.dump(args,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(prepared_workorder=str(wp),actual_collector_CIM=cim,same_hourly_target=True),ensure_ascii=False))

if __name__=='__main__':main()
