from pathlib import Path
import json,time,tomllib,hashlib,ast
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
p=D/'read_entry_seed_reuse_aware_actual.py';assert not p.exists();text=(D/'read_entry_seed_actual.py').read_text(encoding='utf8')
text=text.replace("small_passed='entry_discard128_PASSED.json' in v['reports']","small_passed='entry_discard128_PASSED.json' in v['reports'] or bool(v['reports'].get('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',{}).get('small'))")
text=text.replace("big_passed='entry_discard20k_PASSED.json' in v['reports']","big_passed='entry_discard20k_PASSED.json' in v['reports'] or bool(v['reports'].get('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',{}).get('big'))")
ast.parse(text);p.write_text(text,encoding='utf8')
a=max(R.glob('ENTRY_SEED_ACTUAL_*.json'),key=lambda p:int(p.stem.removeprefix('ENTRY_SEED_ACTUAL_')));v=json.loads(a.read_bytes());assert v['reports']['ENTRY_FRESH_SAME_SCOPE_PASSED.json']['passed'] and v['reports']['E1_COMPLETE_PPO_PREFLIGHT_PASSED.json']['old_actual_valid_scope_exact_reused']
stage=json.loads((R/'STAGE_GIT_RECORDED.json').read_bytes());assert stage['remote_main_tag_peeled_verified']
t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert t['status']=='ACTIVE' and t['rrule']=='FREQ=MINUTELY;INTERVAL=30'
old=t['prompt'];(D/'MONITOR_PREVIOUS_410_FRESH_PROMPT.md').write_text(old,encoding='utf8')
prefix='''最新2026-10-11 source410自己的fresh strict恢复已经actualPASSED，首300s正式CURB20入口复训已实际启动；旧410freshpending/409freshactive/未部署均历史，之后自己的final/139actual优先。

新root=/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_SEED_REVIEWED_20261011，source410/唯一supervise_curb20_entry_seed_reviewed_once.py已执行，不重main/resume/stage/SDK/native/preflight/PPO/fresh/once。parent2746349-start86012358/guardian2746422-start86012472/formal2748108-start86034491仅定位；actual/proc argv/cwd/start/自己的manifest/latestcomplete/sourcefreeze/snapshot/rollingfreeze/ownPIDreceipt/PASSED/实际phase优先。run=e1_CURB20_entry_repair_observation_1791705166118561568，首deadline1791705466.118295约Oct11 16:17:46+08仅定位。目标300s包含load-learn-save-exit/save25/15s本机guardian，由原父同canonical真实扣；当前startup/save/health未生成可合法pending，不把预检save当formal自己的final，不假永久父活跃。

fresh20k新进程0control0PPO实际全actorcriticstdoptimizer/D0D7/globalnamed/dictprivateCPUCUDA/terraincommand/CUDAroundtrip/savedsourceepisode+1通过，sameCURB+sameentry exact/新entryscopefalse；原409fresh默认seed42被严格20260928拒绝的false/error保持，410只明确seed、不放宽validator。409新SDK10真实10CURB起点/1200callbacks和128x2/20kx4 fullPPO/PASSED/CPU102/unique段均exactSHA复用，native398/clock/DR/geometry复用，无任何预检重做。正式仍从完整129source3643c97加载，明确G3→CURB+newentry迁移，terrainentryexactfalse是新范围披露，非漏恢复/PhysXexactresume。今后同geometryentry恢复须严格exact。

积极复用本机MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011/read_entry_seed_reuse_aware_actual.py(410默认/复用small-big判读)及read_entry_seed_own_formal_cpu_actual.py仅读。旧409reader仅历史；410旧direct小大PASSED文件不存在只表示标签在409原root，实际E1_COMPLETE_PPO_PREFLIGHT_PASSED内的原ownPASSED/unique段仍有效，不是再预检许可。正式ownfullsave/PIDreceipt/PASSED/source410/CPU102/实际snapshot数/独立outputs/unique结清后才能自动发139四case并自然reviewready/noactive/父guardian退出；合法单课审查边界非监督故障或全课程finished，不复活旧入口/重结账。

必须actual139 complete/errorfree后新collector/reviewer收两hostprobe/result JSON byteexact/fullNPZ SHA，132原同20mm竖直150mm条带接平台/9m镜像/approach.4/200mm后支撑/80env15s/20260928white3初始化配对与115合同/1293c97旧三skill直接比较。所有root30q参数recipesassignment/6000callbacks/ground-contact积分COMlinkhardware/两轮真实ground符号方向/1N支撑与位置完成分列/ordinary和declaredtruncation coverage/fullsignedcircle alongcross/dedrift/两signed4pi/直线误差及originalstrictfalse/有效未完成prefix保持，resetteleport不计。139发布之前无result正常pending，不占新号/重发旧complete；未完整自身决定不更多PPO/升高度/qualifiedCURB/MoE毕业，不无限hold/只队列。

本新stage唯一trial-20261011-curb20-entry-origin-sdk-and-seed-reviewed-fullstate commitf54c19095a2618c4c88b6a427485dd1975a9abab/tagobjectbf258eba8df9b97c7b43379b49784cb2a5b8ff4b已actualremote main/tag/peeled核验，59捕获文件/原1288tagobjects保持。首次超长ID在record/commit/tag前拒绝，原untrackedcapture和错误保留，较短ID仅续未执行record，不能重复record/tag/commit。此stage后新freshPASSED/正式dispatch/reader/monitor/中央sync/Gitreceipt及未来final/139仍须ordinarysupplement，actualtracked/remote最终工具证明优先。weights/rawNPZ/USD/ZIP仅actualpath-size-SHA，凭据临时授权env不输出不Git。

solecanonical005总1188000s330h/七扩展，第七100h已唯一登记，futureactive/accounted未accounted真实尾段优先；formal原父load-learn-save-exit唯一扣账，无扩展/复制/clearactive/重tail/重结。E0/Wave/SLOPE/本地WASD播放器不触碰，gate未训/硬件未标定/S8后续具体批准/93-94paused；原master/RM003002001/004005/clock/DR/reward/LR/hardware/地形五族/healthv3/fullsignedcircle原容差与其它expert/gate修复规划保持，不hotpatch/kill/dual20k/干预其它AI。

mod4-10同一heartbeatACTIVE每30分钟，healthy pendingDONT_NOTIFY静默，仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY，无5minSSH/ping/Rich/额外驻守；reviewready不删monitor，仅预算真正结束且actualfinal全完成才停止。以下旧snapshot历史保留：

'''
prompt=prefix+old;(D/'MONITOR_CURRENT_410_FORMAL_PROMPT.md').write_text(prompt,encoding='utf8')
(R/'ENTRY_FORMAL_MONITOR_REQUEST.json').write_text(json.dumps(dict(epoch=time.time(),id=t['id'],name=t['name'],kind=t['kind'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],prior_prompt_SHA=H(old.encode()),new_prompt_SHA=H(prompt.encode()),actual_formal_current_report=str(a.resolve()),same_existing_heartbeat=True,stage_Git=stage),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(mode='update',id=t['id'],name=t['name'],kind=t['kind'],status=t['status'],rrule=t['rrule'],targetThreadId=t['target_thread_id'],prompt=prompt),ensure_ascii=True))
