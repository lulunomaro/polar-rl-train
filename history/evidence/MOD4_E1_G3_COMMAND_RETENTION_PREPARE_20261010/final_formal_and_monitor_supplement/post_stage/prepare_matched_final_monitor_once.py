"""Prepare the actual saved boundary and the next read-only behavioral review handoff."""
from pathlib import Path
import hashlib,json,time

D=Path(__file__).resolve().parent;R=D/'reports'
read=lambda p:json.loads(p.read_bytes())
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(name,body):
 p=R/name;assert not p.exists(),str(p)
 p.write_bytes(body.encode('utf8') if isinstance(body,str) else json.dumps(body,ensure_ascii=False,indent=2).encode('utf8'))

def main():
 actual=read(sorted(R.glob('COMMAND_MATCHED_ACTUAL_*.json'))[-1])
 own=read(R/'COMMAND_MATCHED_FORMAL_FINAL_ACTUAL_REVIEW.json')
 sync=read(R/'COMMAND_MATCHED_FINAL_CLOSEOUT_METADATA_SYNCED.json')
 c=read(sorted(R.glob('CANDIDATE_130_COLLECTED_*.json'))[-1])
 assert own['actual_parent_guardian_child_all_exited'] and own['source365_ownfreeze_and_actual72snapshot_verified']
 assert own['phase']=='E1_G3_command_retention_matched_saved_review_ready'
 assert sync['matched900s_actual_final_closeout_synced'] and sync['two_real_locks_free']
 assert own['own_final']['checkpoint']['sha256']=='f5b1623e71fc5d6f3682ca19594bdf43db5a391ce9fc046ec48f8ce90dde234a'
 assert own['own_final']['actual_updates']==42 and own['own_final']['health']['actual_physics_callbacks']==4032
 previous=(R/'HEARTBEAT_COMMAND_MATCHED_20261010.md').read_text(encoding='utf8')
 paragraphs=previous.split('\n\n')
 assert paragraphs[0].startswith('最新Oct10约22:18') and paragraphs[1].startswith('当前唯一root=')
 assert paragraphs[2].startswith('此次实际startup')
 paragraphs[2]=paragraphs[2].split('自己的新save CPU102')[0]+'此次最终自己的完整保存已经CPU102/source365/72actualsnapshot+365ownfreeze/PIDreceipt/PASSED/唯一账段核验；不把活动快照或discard权重当formal final。'
 paragraphs[4]='130-e1-g3-command-retention-matched-terrain-flat及retention-flat/spin/world四case已实际自动发布，own model32104 SHAf5b1623e71fc5d6f3682ca19594bdf43db5a391ce9fc046ec48f8ce90dde234a/17615538bytes。积极复用read_matched_command_actual.py/read_matched_command_own_save_cpu.py仅读。collect_matched_command130_actual.py仅actualcomplete/errorfree才收2hostJSON byteexact/fullNPZ SHA；review_matched_command130_actual.py复用原128同35mm地形初始化和115旧技能合同；必须再用review_matched_command130_selected_source_actual.py对已完整129的实际source364 SHA3c97直接配对。保留全部signedcircle沿横向/去漂移摆幅、两signed方向、ordinary/truncation/有效failureprefix/root30q/contact数据及原容差。没有130完整行为决定不更多PPO/不自动第三同scope块或升50mm；完整合理结果后合理单轴或纠正，不无限hold/只排队/盲长训。terrain包858ad4ef431f188f3275dc8b3c3690bf1d987a5c074f9aed698e15343ad66d2b/36393703bytes；旧D7包8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871/seed20261002white3保持。'
 for i,p in enumerate(paragraphs):
  if p.startswith('solecanonical='):
   paragraphs[i]=p.replace('365前idle319770.51718330383s约88.825h只是历史快照，后续active/accounted和未accounted真实尾段优先','365完整保存退出后的实际idle318850.0927927494s约88.5695h只是当前快照，后续active/accounted和未accounted真实尾段优先')
  if p.startswith('3060 E1_G3_PACKAGE_REVIEW'):
   paragraphs[i]=p.replace('129后无GPU孩子/currentattentionnull是合法idle等待130','当前attentionnull；22:32只读collector已收130-retention-flat complete/errorfree跨两机byteexact，另外3case待结果，actualspin孩子32604/11160 creation1791642527.820/.837仅当时定位。以后actualCIM/argv/creation/children/results/锁优先；无GPU孩子可为合法idle，不按旧PID信号或假永久活跃')
 header='最新Oct10约22:32+08 actual优先：source365一个900s同35mm/同条件命令范围续训已自然完整保存并退出。先读中央E1_G3_COMMAND_RETENTION_MATCHED_FORMAL_FINAL_ACTUAL_REVIEW、MATCHED_OWN_FINAL_CPU_VERIFIED、MATCHED_FORMAL_FINAL_CURRENT_ACTUAL、130_CURRENT_COLLECTION、MATCHED_FINAL_CLOSEOUT_METADATA_SYNCED，以及本机MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010/reports最新COMMAND_MATCHED_ACTUAL/OWN_CPU/FORMAL_FINAL_ACTUAL_REVIEW/FINAL_CLOSEOUT_METADATA_SYNCED/CANDIDATE_130_COLLECTED/REVIEW/SELECTED_SOURCE_REVIEW。22:18的365active、旧364/338formalactive及129pending只是历史，自己的actual/fullsave/PIDreceipt/实际stage优先，不复活旧入口。\n\n当前root=/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010/source365=364全部逐字+一个独立controller。final own model32104 SHA f5b1623e71fc5d6f3682ca19594bdf43db5a391ce9fc046ec48f8ce90dde234a/17615538bytes/CPU102/72actualsnapshot+365ownfreeze/PID2313253-start79649880/PASSED已核。42updates/1008control/20.16Menvsteps/4032callbacks exact，ordinary/integrity/unknown0/nonfinitefalse/STOPnone；closure1.088974532mm、mimic.001691456rad。actualunique truncation15879；time_out8864和route7022有7个重叠，不能相加当unique，两coverageexact。目标900s含load-learn-save-exit，actual920.4243905544281s原parent仅一次结清，无扩展/重结。parent2313205/guardian2313251/child2313253实际均退出，phaseE1_G3_command_retention_matched_saved_review_ready/active-Sactive空及两真实锁free是合法审查边界，非监督故障/全课程finished。prepare/stage/dispatch/controller/sync/record及新finalcloseout均已执行once，不重跑main/resume/native/SDK/PPO/preflight/预算tail。\n\n来源为完整129已行为审查的source364 own32063 SHA3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e，不混旧source338同编号32063 SHAe912。新130目前只有flat complete，其余合法pending，尚无完整候选保留决定，不能借fullsave或129旧表现称source365成熟/永久抗遗忘或35mm全路线通过。中央final closeout已真实同步并保持master/approval/tracks/RM/canonical字节，旧sync不可重跑。\n\n'
 body=header+'\n\n'.join(paragraphs[2:]).rstrip()+'\n'
 save('HEARTBEAT_COMMAND_MATCHED_FINAL_20261010.md',body)
 save('COMMAND_MATCHED_FINAL_SUMMARY.md',f'''# E1命令保留修复：实际保存边界与下一审查

E1连续训练后的旧能力下降是真实行为问题。全旧actor/critic/std/optimizer、D1–D7及随机流恢复已有实际验证；gate未训练。当前证据不支持把退化归因于漏恢复或MoE路由。窄范围新课缺少旧命令练习是待验证解释。

华南虎公开源码使用持续、受地形条件限制的旧直行/旋转等命令采样。已审V14运行的是ActorCritic/PPO；CLI支持MoE/CMoE不能作为永久抗遗忘证明。我们借鉴持续旧命令练习：保持原35mm和五族比例，只在实际plane网格支撑、净空核验环境加入signed直行和低速world命令，其他地形保持gentle yaw0，额外私有随机流明确保存与恢复。没有改reward、学习率、硬件、时钟或训练地形配额。

首300s source364的完整129四case审查，对选定32058来源：world62/64→63/64，负4π5/8→7/8，正4π仍8/8；35mm完整后支撑前23/27→24/27，倒仍27/27。三个前进有效前缀未完成后支撑，原false/残差保留。这只证明一次短窗的行为改善。

随后唯一900s同范围source365已自然完整保存。own32104 SHA `{own['own_final']['checkpoint']['sha256']}`，CPU102/source365/72snapshot，42updates、20.16M环境策略步、4032实际回调，ordinary/integrity/unknown0、nonfinitefalse；原父实际920.4243905544281s仅一次结清，剩318850.0927927494s为退出后的idle快照，新增预算0。完整sameG3地形与新增command-private状态恢复通过。父、guardian、trainer均实际退出；这是合法审查边界。

新130冻结四case已自动发布，当前已完成 `{', '.join(c['cases'])}`；其余{len(c['pending'])}份结果尚未生成，attention为空。需完整跨机字节、NPZ、ground/contact/参数/root30q和signedcircle审查，再直接与129来源比较。该900s的旧能力保持尚未宣告通过，不能自动第三块或升50mm。

RewardManager签名、SDK选格、额外私有RNG归属、savedepisode+1断言的四次拒绝与独立修复均保留；没有用失败预检权重继续正式训练，没有热改活跃源码。全部新报告和monitor回执纳入该阶段普通Git补充，最终remote/tracked以工具输出为准。
''')
 save('LOCAL_CLOSEOUT_REPORT_PATH_READ_REFUSAL.json',dict(epoch=time.time(),trial_id='E1-G3-COMMAND-MATCHED-LOCAL-REPORT-LOCATOR-01',requested_path=str(R/'REPORT.md'),result='Get-Content path_not_found',existing_actual_reports_read_successfully=True,not_a_GPU_or_physical_failure=True,repair='Use actual named final review and create a new independently named final summary; no old evidence overwritten',no_production_or_canonical_mutation=True))
 print(json.dumps(dict(prepared_final_prompt=str(R/'HEARTBEAT_COMMAND_MATCHED_FINAL_20261010.md'),prompt_sha256=sha(body.encode()),actual_source365_final=True,pending130=len(c['pending']),new_budget_seconds=0)))

if __name__=='__main__':main()
