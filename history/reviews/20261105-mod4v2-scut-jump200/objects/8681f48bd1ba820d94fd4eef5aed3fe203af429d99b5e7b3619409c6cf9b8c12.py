from pathlib import Path
import json,time

N=Path(__file__).resolve().parent
S=N.parents[1]
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200'
quote='看看能否把supermimic的那套bptt加进去，让这一套加速方案兼容supermimc，这个等到一小时ppo训练开始后开始做，然后设置定时任务，两个交叉着做，30分钟定制任务提醒，如果在训练就处理这个，如果没训练就去处理评测和训，如果评测达标就进入下一阶段，换issica lab台阶地图，如果supermimic处理完就换supermimic，你设个定时任务记得把我说的给记明白了'
interleave=dict(epoch=time.time(),human_quote=quote,automation_id='mod4-10',interval_minutes=30,
    target='current_chat',status='ACTIVE',legacy_mod4_200_rl_bptt='PAUSED',
    sequence=['Start actual one-hour Newton/MuJoCo-Warp PPO, validate update/fullsave',
              'While PPO runs, implement and test SuperMimic BPTT compatibility',
              'When no training, prioritize fullsave/safeexit/independent80/actual playback and next training',
              'After genuine single200mm jump acceptance, advance to Isaac Lab stairs map',
              'After actual SuperMimic gradient/update/fullsave compatibility, switch at fullsave boundary'],
    new_chat_goal_or_duplicate_automation=False,implementation_started=False,
    not_started_reason='Production Newton PPO must start first; native4env PPO is only a migration test')
migration=dict(epoch=time.time(),status='NATIVE_PPO_TEST_PASSED_PRODUCTION_PENDING',
    backend='Newton 1.7.0 SolverMuJoCo / MuJoCo-Warp 3.15.0',
    source_root=str(N/'fudan_warp_final461_1h'),source_iteration=620,
    source_SHA='3da87af137a5244a56a8cfb6ecb4df7636fef7bc23cde62eb3eff2e04648a544',
    source_Adam_step=12400,source_lr=.0005766503906250003,
    old_train_closed=True,old_independent80_recovered=True,old_successes=0,
    original_owner_zombie_error_preserved=True,production_running=False,
    direct_free_gpu_no_ledger=True,full_IsaacLab3_manager_migration=False)
for path in [S/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
    obj=json.loads(path.read_bytes())
    obj['newton_migration']=migration
    obj['supermimic_interleaving']=interleave
    obj['current_training']='NEWTON_MIGRATION_PRODUCTION_PENDING_FINAL620_CLOSED'
    obj['next']='Finish Newton production resume and full FIRST621; only then develop SuperMimic BPTT. Existing 30-minute same-chat automation is ACTIVE.'
    obj['human_latest_request']=quote
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
note='''
## 2026-11-06 Newton迁移与SuperMimic交叉推进

人类要求实际使用Newton/MuJoCo-Warp，并明确先开始一小时PPO，再在训练期间做SuperMimic BPTT兼容。mod4-10复用当前聊天ACTIVE，每30分钟交叉推进：训练中做兼容；无训练优先保存退出、独立80、实际回放、据证据修复接续。单200mm真实跳跃验收达标后进入Isaac Lab台阶地图；SuperMimic有实际梯度/更新/完整保存证据后在保存边界切换。不得将Warp加速等同可微物理。旧mod4-200-rl-bptt保持PAUSED，不新建聊天/Goal/重复任务。直接空闲GPU/noledger最高指令、累计100h上限及所有失败Git记录保持。见v2工作单与NEWTON_MIGRATION_AND_SUPERMIMIC.md。
'''
for path in [G/'AGENTS.md',G.parent/'AGENTS.md']:
    text=path.read_text(encoding='utf8')
    if '## 2026-11-06 Newton迁移与SuperMimic交叉推进' not in text:
        path.write_text(text.rstrip()+'\n'+note,encoding='utf8')
print(json.dumps(dict(saved=True,production_running=False,automation='mod4-10 ACTIVE 30 minutes')))
