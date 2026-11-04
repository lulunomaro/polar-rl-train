"""Record returned final376 and the single queued target projection segment."""
from pathlib import Path
from datetime import datetime
import json
import time

N=Path(__file__).resolve().parent;S=N.parents[1]
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261103-mod4v1-scut-native-training'
P=N/'env20000_jump200_retry_ascent_1h_20261105'
A=N/'env20000_jump200_target_projection_1h_20261105'
read=lambda p:json.loads(Path(p).read_bytes())
review=read(P/'reports/ACTUAL_JUMP200_FINAL_LEARNING_AND_ALL80_REVIEW.json')
plan=read(A/'PLAN.json');controller=read(A/'reports/CONTINUATION_EXACT_CIM.json')
returned=read(P/'reports/POSTROUND_FULL_RETURNED.json');f=returned['files']
status='JUMP200_FINAL376_REVIEWED_0FLIGHT__TARGET_PROJECTION_PREPARED_SOLE16444_LOCAL_WAIT'
next_text=('A='+str(A)+'. Source fullfinal376/17Adam7520/SHA132a74d7 fullstate; target projection reward repair19jump+8oldstairsCPU passed. '
    'Only local16444/create2026-11-05T04:40:09.633017+08 jump200_training_control.py continue_segment --root A. CONTINUATION_BIND_ONCE/ONCE consumed, logs0, '
    'noINDEX/LAUNCH/GO/FIRST yet. Wait true otherSSH39496/create04:19:29.490276 collect_fudan_lowstd005_w10_window_once.py; its local latestPREGO Errno11/0GO, '
    'not canonicalowner. Current known canonicalowner is SCUT32/1633096/create1793823091.1 actualGO04:11:31.777429/SAVE05:11:31.777429/NOMINAL05:16:31.777429. '
    'Sole16444 finishes prior complete logs/error0 and originalownerrelease, exactSCUT32release/canonicalNone/locks/freshfour/originalbalance then sameoneunusedlaunch, '
    'validFIRST377/restore37617Adam7520/nonzeroactorcriticgrad/FULLV4/completeerrors0 and binds solepostround. Differentactualowner retains false, no抢锁. '
    'No secondSSH/probe/reader/FIRST/rebind/launch/hotpatch/PTdecode while solehealthy. Old4416/70820 ended, allpreviousonce consumed. '
    'Previous fullfinal376 completed113PPO54.24M/80timeouts/all4actualposeviewed,69requestenvs300requests/pushworldvz.449606, '
    '0groundflight/wholeclear/top/landing/success; complete full logs stillpending until sole16444 read. OriginaloldGO02:14:24.739725/SAVE03:14:24.739725/NOMINAL03:19:24.739725 unchanged, '
    'ownwaitsettledreleased03:16:14.949629/formal03:48:39.153871. Preserve100hcumulativeauthorization/originalcanonical/reserve, nohourpermission.')
closed=dict(root=str(P),review=str(P/'reports/ACTUAL_JUMP200_FINAL_LEARNING_AND_ALL80_REVIEW.json'),
    final=review['final'],owner_exit=review['owner_exit'],new_PPO_updates=113,new_samples=54240000,
    Adam=7520,full_save_diagnosis=review['full_save_diagnosis'],all80=review['all80'],
    all4_actual_images_reviewed=True,current_model_view_image=True,images=review['images'],skill_passed=False,
    complete_log_pending=review['complete_log_review_pending'],formal_returned_epoch=read(P/'reports/POSTROUND_COMPLETED.json')['epoch'])
for path in (S/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json'):
    value=read(path);old=value['jump200']
    if 'pre_target_projection_header_snapshot' not in old:
        old['pre_target_projection_header_snapshot']={k:old.get(k)for k in
            ('status','root','actual_GO','FIRST','sole_collector','local_deadlines','current_source_index','current_repair')}
    value.update(epoch=time.time(),status=status,current_training=status,next=next_text,
        human_latest_request='允许100小时',local_controller=controller['row'])
    if path.name=='WORK_ORDER.json':
        value.update(root=str(A),remote=plan['remote_root'],actual_plan=str(A/'PLAN.json'),frozen_index=None,
            FIRST=None,GO=None,launch=False,owner_current=None,worker=None,local_controller=controller['row'],
            local_controller_role='Sole authorized local continuation waiter16444; no productionGO yet',
            training_completed=False,evaluation_completed=False,trained_skill=False,
            current_training_root=str(A),current_training_remote=plan['remote_root'],current_training_plan=str(A/'PLAN.json'))
    old.update(epoch=time.time(),status=status,root=str(A),remote_root=plan['remote_root'],training_root=str(A),
        training_remote_root=plan['remote_root'],training_run_id=plan['run_id'],candidate_root=str(A),
        local_controller=controller['row'],current_segment_sole_launcher=controller,sole_collector=None,
        current_segment_sole_collector=None,training_live=False,production_closed=False,
        current_segment_closed=False,current_segment_final=None,current_segment_evaluation=None,
        current_segment_training_completed=False,current_segment_evaluation_completed=False,
        source_checkpoint=plan['source_checkpoint'],same_source_checkpoint=plan['source_checkpoint'],
        FIRST=None,FIRST_pending=True,actual_GO=None,original_GO=None,original_save_deadline=None,original_nominal_end_epoch=None,
        local_deadlines=None,source_frozen=False,production_launch_consumed=False,newwindow_INDEX=False,newwindow_LAUNCH=False,newwindow_GO=False,
        next=next_text,pending_human_additional_hour=False,trained_jump_skill=False,
        final_and_independent80_pending=True,previous_training_root=str(P),previous_complete_log_pending=True,
        previous_collector70820_exited=True,postround_wait_resolved=True,postround_waiting_external_controller=False,
        closed_retry_ascent_final376_review=closed,
        current_source_index=str(A/'SOURCE_ONLY_PREPARED.json'),
        current_repair=dict(modules=['config.py','rewards.py','target_limits.py','sdk.py'],
            description=plan['repair'],CPU_tests=19,oldstairs_regression_tests=8),
        resource_wait=dict(mode='FreshLOCAL wait for trueSSH39496; then exactknownSCUT32release, originalcanonical/locks/budget/freshfour',
            context=str(A/'reports/CONTINUATION_PEER_CONTEXT.json'),
            no_current_resource_ready_claim=True,no_new_GO=True),
        human_continuation_authorization=plan['human_authorization'])
    value['archive'].update(ordinary_supplement_in_progress=True,
        current_supplement_scope='Final376/full80/all4nativevisual/fullstate1decode/targetprojectionreward19+8CPU/foursmallmodules/sole16444queue/stateautomation',
        supplement_status='Pending ordinarysupplement actualGitpush; no record or retag')
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')

summary=('2026-11-05 04:44实际覆盖：retry-ascent已完整保存113新PPO/54.24M样本/final376/17Adam7520，03:16:14原owner ownwait/settled/released；正式回传03:48:39。'
    '独立80全部7.98s timeout，69局2–6次请求/共300次，push平均world-vz .449606m/s，但0真实向上离地/越沿/台顶/稳定落地；全部4图已当前模型审看，0closure/mimic/数值异常。'
    '两hip目标持续+.5rad。已加奖励项`jump200_target_projection=-2`，按真实actionterm scale/offset和原CAD→motorlimits/CAD投影惩罚不可执行请求；动作/限位/D4/物理/完整学习状态保持。'
    '19项jump200＋8项旧阶梯CPU检查通过，4module/59sharedrefs候选准备完成。唯一local16444/create04:40:09.633017已排队，当前仅等待真SSH读者39496；其W10仍PREGO，当前known canonicalowner为SCUT32/1633096，SAVE05:11:31.777429/NOMINAL05:16:31.777429。'
    'sole16444负责补齐final376完整日志、核actualrelease/原余额/四卡、唯一新launch→FIRST377→postround。尚无新INDEX/LAUNCH/GO，健康只本地，不第二SSH/rebind/重训。100h授权持续。详见`JUMP200_FINAL376_AND_TARGET_PROJECTION.md`。下文早期等待/未返回均为历史。')
for path in (CODE if False else G/'project/isaac/mod4v1_scut/README.md',D/'JUMP200_FINAL263_AND_RETRY_ASCENT.md'):
    text=path.read_text(encoding='utf8');first,tail=text.split('\n',1)
    path.write_text(first+'\n\n'+summary+'\n'+tail,encoding='utf8',newline='\n')
todo=D/'TODO_JUMP200.md';text=todo.read_text(encoding='utf8')
start='- [ ] 当前原窗SAVE03:14:24.739725/NOMINAL03:19:24.739725已到，唯一collector70820在网络前等待真实SSH读者68888退出后正式回传；FINAL/原owner关闭/独立80尚未返回，不重启生产或评测。回传后立即all80和新actualpose原生评审再接续。'
assert start in text
text=text.replace(start,'- [x] retry-ascent原窗完整关闭/正式回传/fullfinal376/17Adam7520；独立80、全部4新图已审：69requestenvs/300requests，0flight/wholeclear/top/landing，原70820退出。')
text=text.replace('\n当前证据：','\n- [x] 针对两hip持续上限增加不可执行leg请求投影奖励惩罚，保留原scale/offset/动作/限位/CAD/D4；19jump200＋8旧阶梯CPU通过，4module/59refs候选已准备。\n- [x] 唯一16444/create04:40:09.633017本地接续已绑定；100h授权下等待真SSH39496，不第二SSH/重bind。\n- [ ] 原sole16444补齐final376完整日志并核actual0errors/ownerrelease；再核knownSCUT32 exactrelease/原canonical余额和四卡，唯一launch/FIRST377，原owner保存安全退出后立即独立80和全部实际图评审。新GO仍未发生。\n\n当前证据：',1)
todo.write_text(text,encoding='utf8',newline='\n')
report=D/'JUMP200_FINAL376_AND_TARGET_PROJECTION.md'
assert not report.exists()
report.write_text('''# 单200mm跳跃：final376与动作请求投影修复

2026-11-05 04:44。本轮原生训练与独立80已关闭、回传并审完4幅实际保存姿态图，跳跃尚未成功。当前仅有一个本地接续程序16444，尚未新GO。

- 原窗GO02:14:24.739725、SAVE03:14:24.739725/NOMINAL03:19:24.739725。final03:13:22.567798、TRAIN_CLOSED03:13:48.348311；独立80完成03:16:14.138422、owner03:16:14.949629完整等待/结算/释放。03:48:39正式回传延迟不延长原窗。
- 113新PPO/54,240,000样本/21,696physicscallbacks/2,260新Adam，source263→376。FULL_V4 40,717,335B SHA `132a74d7aea78274e611b6295ea7c7c9b30f91d2c46304d65a4cf4e33937472a`。
- 必要完整模型诊断仅1次：17Adam均7520，LR.00038443359375000017，actor35/critic78/STD/7组件/RNG/队列/globalcounter9024齐全，actor/critic/Adam有限。3个原SCUTpermission未设置NaN哨兵保留，非模型损坏，不为Git再次decode。
- 80局全7.98s timeout，无contacttermination/closure/mimic/numerical/rawoutlier。69局请求、共300次，4局2次/6局3次/25局4次/30局5次/4局6次；11局无请求。0groundupwardflight/wholeclear/topcontact/landing/success。
- push/tuck20.15%端点，push平均world-vz从前轮.1303升到.4496m/s，但仍无双轮真离地。rootmaxx.54016<edge.8。env0/40停近出生处，env1/41抵近.53m后反复上下推蹬，早期spawn下落不算起跳。四幅early/late side/top均已当前模型原生视觉审看；savedpose为wxyz。
- 两hip目标上限命中100%/99.9937%，mean raw action分别1.9613/1.7545。现有目标投影按设计执行，不把D4延迟或物理跟踪差当映射错误，不放宽限位或重置输出层/STD/Adam。

新增奖励`jump200_target_projection`：当前clip6 leg请求乘实际actionterm._scale加._offset，依次复现原CAD投影与contract限位/CAD投影；残差除actualscale，四项平方均值，权重-2，dt仅一次。可执行请求代价0，不使用motor当前姿态或D4延时目标计算。源mod4_task.py为.5rad/defaultoffset；生产直接读取constructor实例，不假设默认角为0。既有接近/重试/上升/真落台奖励保持。

首18项CPU报告保留；补齐原CAD→限位执行顺序后19项jump200通过，8项旧阶梯回归通过。0生产PT读取/0physics的CPU检查不等于新技能。候选4个module＋owner/entry/plan，共59sharedSHArefs，不复制模型/资产/整树。完整续final376/17Adam7520/LR/STD/组件/RNG/队列/counter，新constructor nominal保护后一次fresh physical reset。

唯一接续16444/parent59852/create04:40:09.633017，`jump200_training_control.py continue_segment --root env20000_jump200_target_projection_1h_20261105`。先本地等待真SSH读者39496/parent40340/create04:19:29.490276，E3W10本地metadata仍PREGO Errno11，无GO，不把它当canonicalowner。known actualcanonicalowner是SCUT32/1633096/create1793823091.1，GO04:11:31.777429、SAVE05:11:31.777429/NOMINAL05:16:31.777429。

原controller已支持本次SCUT owner原生`OWNER_STARTED/OWNER_EXIT all_own_waited`释放回执；E3仍使用原parent/exit/outerreaped。下一步先补final376完整WORKER/EVAL全文核0errors，再核exactpeer释放、canonicalNone/原锁、fresh四卡与原reserve之上3900s，才消耗唯一新launch。若新canonicalowner不同，保留false不抢锁。FIRST须377/480k样本/20新Adam/restore37617entries7520/非零actorcriticgrad/FULL_V4/完整首轮日志0errors；FIRST不是技能。当前无INDEX/LAUNCH/GO。

最终完整日志尚待上述sole16444有限读回，不冒称当前已完成全文0error核验。后续原owner完整保存安全退出后立即独立80，再savedpose回放和当前模型审图；不重放旧once。人类100h持续授权，不逐小时再问；同一原canonical余额与严格reserve86412.86069250107，无grant/refund/复制/延长旧窗。历史余额仅快照，准入取fresh实际。

原件在F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102/runs/mod4v1_scut_step270_2h_20261103/。完整returned、formaltransfers、review、全部renderreports、新源码/CPU/control/once和状态进入本阶段普通supplement，既有trial/tag/peel不改。Git是否已push以工具为准。
''',encoding='utf8',newline='\n')
print(json.dumps(dict(state_updated=True,status=status,sole=controller['row'],new_production_GO=False,report=str(report))))
