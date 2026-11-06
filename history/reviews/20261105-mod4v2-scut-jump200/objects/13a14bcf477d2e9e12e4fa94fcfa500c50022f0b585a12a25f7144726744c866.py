"""Freeze this finite controller evaluation and append its evidence. No PT/physics."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

N=Path(__file__).resolve().parent
T=N/'scut_teacher_verify'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200'
REF=G.parent/'reference_repos/scut_wheeled_legged_RL'
S=N.parents[1]
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
digest=lambda raw:hashlib.sha256(raw).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
summary=read(T/'CONTROLLER_SUMMARY.json')
names=['manual_trigger02','stair_saved01','stair200_01','manual_stair200_01']
for name in names:
    assert read(T/name/'COMPLETE.json')=={'steps':550,'envs':16}
    assert not (T/name/'ERROR.json').exists()
    assert all(r['recorded_root_body_force_finite']for r in read(T/name/'CONTROLLER_RESULT.json')['results'])
revision='1a26356d6f591734d4f6f666f5cead1a6925da67'
delta=subprocess.check_output(['git','diff','--stat',revision,'HEAD','--','source/agent_tasks/agent_tasks/direct/wheelbipe','source/agent_world/agent_world/assets','scripts/rsl_rl/keyboard_controller.py','scripts/rsl_rl/play.py'],cwd=REF,text=True)
assert not delta.strip()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REF,text=True).strip()
successful=read(T/'stair200_01/CONTROLLER_RESULT.json')['results'][13]
assert successful['full_wheels_crossed']and successful['bilateral_top_support_seconds_max']>7
assert successful['side_contact_before_crossing']and not successful['pre_side_ground_takeoff_wholeclear_sequences']
assert not successful['strict_quiet_top_pass']
review=dict(time=stamp,reviewer='current model native vision',
    images=[str(T/name/'ACTUAL_MESH_SIDE.png')for name in ('stair200_01','manual_trigger02','manual_stair200_01')],
    representation='Original SCUT USD projected convex visual silhouettes at saved200Hzbodyposes; no new NN/physics during rendering; saved quaternionwxyz.',
    observations={
        'stair200_01':'env13 reaches vertical200mmface, contacts its side, compresses/tucks wheels, then reaches bilateral top and drives forward; env0 also climbs13cm.',
        'manual_trigger02':'flat and200mm selected cases remain low/oscillate; no200mmwholeclear; request phase is verified by tensors rather than images.',
        'manual_stair200_01':'env3 climbs13cm; selected env9/13 fail200mm and remain by step or retreat; no200mmwholeclear in all8.'},
    physics_replay_operations=0,optimizer_operations=0)
(T/'CONTROLLER_ACTUAL_NATIVE_REVIEW.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=dict(time=stamp,status='COMPLETED_NATIVE_REVIEWED_CONTROLLER200_CLIMB1OF8_NO_STRICT_JUMP',
    human_quote='你去找手动跳跃出发和上台阶状态机去试试',root=str(T),
    source_commit=revision,source_and_assets_delta=delta,
    checkpoint=read(T/'SOURCE_BINDING.json')['artifacts'][0],policy_parity=read(T/'POLICY_PARITY.json'),
    runtime='OriginalSCUTrobot, localIsaacSim5.1PhysX,200Hzphysics/50Hzpolicy,RTX5070TiLaptop,seed66',
    runs=summary,success_example=successful,
    findings=[
        'Unmodified Q callback actually prints unsupported: V14 has no trigger_manual_jump; request_jump_takeoff exists and was exercised.',
        'All12 published saved configs inspected have jump_takeoff and stair state machines disabled. Roughdash uses step_up scan. No matched jump-trained weights found in this inventory.',
        'Public model1000 is the same previouslyverifiedstair checkpoint; explicitly enabling dormant machines is a new controller condition, not evidence of author training with them.',
        'Saved detector0.12<height<0.14 andwall0.14 resets all8single200cases; terminal blocks retained as diagnostic evidence but excluded from skill scores.',
        'Detector-adapted condition changes only detection upper andwall to0.25; stairs0.4-0.43mheightcmd and originalpolicy/plant/DR retained.',
        'Public stair ctrlmode onehot remains zero in current source despite internalstairactive; effectiveheightoverride is verified. This test does not patch that interface.',
        'Manual entry uses public request andballisticphase withtarget0.70, disablestrackingrequirementforoperatorrequest; jumpforce/velocityassist0. Other originalDRintervalpushes andforces remain.',
        'Quick genericanalyze RESULT uses hardcoded0.2mtop fornonflat; preservedraw but CONTROLLER_RESULT corrects13cm and excludes complete terminalcontrolblock.',
        'Physical event snapshots precede commandupdate; manualtrigger pulses are absent there but phases andjumpobservations verify activation. Later runs additionally log post-control events.',
        '200mmclimbenv13contactsstepface2.99s,wholewheelcross/top3.27s,continuousbilateraltop7.39s; quietmax.045s<.5. It is not a ground-pre-face unsupportedjump proof.'
    ],
    policy_training_operations=0,optimizer_operations=0,ssh_operations=0,
    repeated_old_MOD4_final_decodes=0,MOD4_training_running=False,foreign_edits=0,
    previous_MOD4_cumulative_upper_seconds=75088.49385809898,
    timing_scope='Four finite localSCUTevaluationprocesses; log mtime-minus-invocation is elapsed proxy, not trueGPUcost or productionowner cost.',
    report=str(D/'SCUT_MANUAL_JUMP_AND_STAIR_CONTROLLER_20261106.md'))
(T/'CONTROLLER_VERIFICATION.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
markdown='''# 华南虎手动跳跃及上阶状态机实际测试

2026-11-06，北京时间。人类要求“你去找手动跳跃出发和上台阶状态机去试试”。已完成4批、每批16环境×11s首次episode的原SCUT机器人实际物理评测，原公开model1000/导出policy逐tensor误差0，0训练/优化器/SSH。不能再笼统说华南虎上不了台阶：上阶状态机适配200mm检测后，8组中1组真实双轮登顶并连续支撑7.39s；尚无满足MOD4严格200mm自主跳跃验收的教师。

## 实际结果

| 条件 | 13cm直角台阶双轮登顶 | 20cm直角台阶双轮登顶 | 触发证据 |
|---|---:|---:|---|
| manual_trigger02，手动请求 | 未测 | 0/12设置；8组实际触发 | 4/4平地及8/12台阶进入push/tuck和jump观测；其余4组未到触发位置 |
| stair_saved01，原检测范围 | 6/8 | 0/8；8组均触发墙重置 | 13cm7/8进入stair；20cm终止控制块明确wall标记 |
| stair200_01，适配检测到20cm | 7/8 | 1/8 | 13cm8/8、20cm7/8内部stair激活，真实有效高度命令0.40–0.43m |
| manual_stair200_01，两者开启 | 3/8 | 0/8 | 两个高度各8/8手动请求进入jump；20cm7/8进入stair |

表中登顶是双轮整轮越沿并真实台顶支撑，不要求停车，不等于自主跳跃成功。全部20cm测试严格静止0.5s通过数均0。single200成功env13命令vx1.8m/s、基础height.38m，台沿x1.6m，2.99s先接触立面，3.27s整轮越沿并双轮台顶接触，最长连续支撑7.39s；最大全条件静止.045s。它先碰台阶再收腿离开接触并登顶，不是台前地面提前起跳、无立面接触跳过的实证。新原USD保存姿态图已由当前模型原生审阅，0新物理回放。

## 公开接口与配置缺口

固定作者commit `1a26356d6f591734d4f6f666f5cead1a6925da67`。原始Q键回调在实际V14对象上输出“不支持手动跳跃触发”：调用的`trigger_manual_jump`不存在，可用公开方法是`request_jump_takeoff`。此次实际测试后者，不修改作者仓库。

公开保存env.yaml的state machine总开关、jump_takeoff、stair均为false；CPU检查12套保存配置也未找到jump_takeoff或stair启用的对应训练权重，rough_dash仅启用step_up扫描。因此本次在原model1000上启用状态机是新控制条件，不能称已找到作者训练好的手动跳跃专家。35维输入/6动作及原权重不变，jump观测实际置位；当前源stair onehot仍写0，但有效高度命令确实被状态机覆盖。没有偷偷修该观测接口。

原wheel_forward_scan检测范围为0.12–0.14m，wall_height.14m，20cm直接判墙结束。原配置先实测保留，再仅把检测上界/墙阈值改.25m，记录为独立条件；状态机高度范围仍.40–.43m。手动ballistic目标.70m、tracking条件关闭以发出操作者请求，push/tuck真实生效；jump外力/速度注入辅助均关闭，原DR的5–10s区间扰动仍保留。上阶成功发生在3.27s。

## 协议与边界

原SCUT机器人USD、原公开policy、IsaacSim5.1/PhysX200Hz、50Hzpolicy、本地5070TiLaptop、seed66。20cm/13cm用显式竖直阶面和水平台顶，并把实际台阶加入raycast相同地形mesh。原观测噪声、传感/动作延迟、动力学与DR保留。评测仅改场地/初始化/命令和明确列出的控制开关；不是MOD4蒸馏或MOD4已通过。

64组设置中16组13/20cm原检测、16组适配、16组组合、另4平地+12手动200mm；每组11s，首次episode，终止的整个控制块与全部后续episode从技能统计排除。400Hz MOD4验收未改；本次SCUT为200Hz，静止.5s按100实际物理tick计。saved quaternionwxyz不换序。

原快速`RESULT.json`分析器非平地台顶高度写死.2m，不能用于13cm成绩，已保留并由新`CONTROLLER_RESULT.json`按实际阶高重新分析。物理快照发生在控制更新前，单步triggerpulse不可据0值否定触发；阶段/jump观测明确，后两批另记录postcontrol脉冲。没有重跑原评测弥补日志。

首次manual_trigger01传未注册seed参数，在解析阶段退出，0物理；原日志保留，随后显式支持seed并启动02。其它4实际批次完整退出，全部root/body/force有限，保留PhysX警告及原DR扰动。原检查点SHA `d19492be858ffd431a67e5aa40afb4a4c51dc9a1c914c5c92022ed46d5868db7`；policy SHA `7a2ba09cb1d61ae59467bdba12f97f5b0f26f7565a2ad68ea88446da7eadfa15`。作者源/资产对固定commit差异为空。

证据根`N/scut_teacher_verify`：`CONTROLLER_VERIFICATION.json`、`CONTROLLER_SUMMARY.json`、`CONTROLLER_ACTUAL_NATIVE_REVIEW.json`、`CONTROLLER_CHECKPOINT_INVENTORY.json`和4批目录。各批冻结RUNNER_SOURCE、完整有效配置、调用、首次episode轨迹/接触、请求和原始日志保留；PT/NPZ/图片仅真实路径/大小/SHA索引。之前零成功测试按原条件保留，不改成成功。本次支持把它作为接触上阶候选教师继续讨论，不能把它称为已验证200mm自主跳跃专家或无依据自动蒸馏。
'''
(D/'SCUT_MANUAL_JUMP_AND_STAIR_CONTROLLER_20261106.md').write_text(markdown,encoding='utf-8')
brief={k:record[k]for k in ('time','status','human_quote','root','source_commit','runs','report','policy_training_operations','optimizer_operations','ssh_operations')}
brief['success200']=dict(case=13,run='stair200_01',side_contact_seconds=2.99,whole_wheel_cross_seconds=3.27,bilateral_top_support_seconds=7.39,strict_quiet_max_seconds=.045,strict_jump_pass=False)
brief['do_not_repeat_completed_tests']=True
for path in (S/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json'):
    state=read(path)
    state['scut_manual_and_stair_verification']=brief
    state['scut_teacher_actual_verification']['controller_followup']=brief
    state['scut_teacher_actual_verification']['latest_verdict']='Manual/stair followup found1of8contactclimb200mm; previous8failure result preserved; no strict200mmgroundjumpteacher verified.'
    temp=path.with_name(path.name+'.scutcontroller.tmp')
    temp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(path)

sys.path.insert(0,str(G/'archive_tools'))
from capture_history import redact
index=read(D/'EVIDENCE_INDEX.json')
known={(x.get('path'),x.get('SHA'))for x in index['files']}
selected=[T/'native_verify.py',T/'render_actual.py',T/'analyze_controllers.py',Path(__file__),T/'manual_trigger01.log',T/'CONTROLLER_VERIFICATION.json',T/'CONTROLLER_SUMMARY.json',T/'CONTROLLER_ACTUAL_NATIVE_REVIEW.json',T/'CONTROLLER_CHECKPOINT_INVENTORY.json',T/'render_trace.log',S/'admin/CURRENT_STATE.json']
for name in names:
    selected.extend(x for x in (T/name).rglob('*')if x.is_file()and '__pycache__'not in x.parts)
    selected.append(T/(name+'.log'))
for name in ('stair200_01','manual_trigger02','manual_stair200_01'):
    selected.append(T/(name+'_RENDER_REPORT.json'))
selected += [T/'manual_trigger_render01.log',T/'manual_stair_render01.log']
for path in sorted(set(selected)):
    if not path.is_file():continue
    raw=path.read_bytes();sha=digest(raw)
    if(str(path),sha)in known:continue
    row=dict(path=str(path),bytes=len(raw),SHA=sha)
    if path.suffix.lower()in ('.py','.json','.log','.md','.txt')and len(raw)<100_000_000:
        text=raw.decode('utf-8-sig')
        text='\n'.join(line.rstrip()for line in text.splitlines()).rstrip('\n')+'\n'if text else''
        text,count=redact(text);content=text.encode('utf-8')
        dest=D/'objects'/(digest(content)+path.suffix.lower())
        if not dest.exists():dest.write_bytes(content)
        row.update(git_path=dest.relative_to(G).as_posix(),archived_SHA=digest(content),redactions=count,transform='OnlyTextBOMTrailingWhitespaceNormalized; originalpathbytesSHApreserved')
    else:row.update(external_artifact=True,archive_model_reads=0,physics=0)
    index['files'].append(row)
index['captured_epoch']=datetime.datetime.now().timestamp()
(D/'EVIDENCE_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(report=record['report'],archived_refs=len(index['files']),status=record['status']),ensure_ascii=False))
