from pathlib import Path
import json,shutil
R=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106');S=R/'sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112';T=R/'sources/local/MOD4V3_SCUT_STAIR_LIFT_20M_20261112'
s=(S/'remote_ops.py').read_text();s=s.replace('MOD4V3_SCUT_ROUGH_V1_2H_20261112','MOD4V3_SCUT_STAIR_LIFT_20M_20261112');s=s.replace("name='smoke4096_unified_r2' if act=='smoke'", "name='probe4096_stair_lift_r1' if act=='smoke'");s=s.replace("'--kind',act,'--num-envs','4096','--seconds','30' if act=='smoke' else '7200'", "'--kind','probe' if act=='smoke' else 'train','--num-envs','4096','--seconds','10' if act=='smoke' else '1200'")
(T/'remote_ops.py').write_text(s,encoding='utf8')
s=(S/'monitor_round.py').read_text();s=s.replace('MOD4V3_SCUT_ROUGH_V1_2H_20261112','MOD4V3_SCUT_STAIR_LIFT_20M_20261112').replace("JOB=REMOTE+'/train120m_scut_rough_v1_r1'","JOB=REMOTE+'/'+PLAN['training_round']['job']").replace('tmp/scut_rough_v1_2h_20261112_r1','tmp/scut_stair_lift_20m_20261112_r1');s=s.replace('two-hour unified SCUT Rough-v1 course','twenty-minute stair-lift continuation');(T/'monitor_round.py').write_text(s,encoding='utf8')
(T/'README.md').write_text('''# 从11月12日选定120m权重接续：台阶抬高底盘20分钟试验

父：Rough-v1 120m/iter24482，SHA7cc1fc6deeee3d3aba8ae8d2da31dce200079fb229a145f1cbb1cd3bfabea103。单开1200秒PPO，每300秒完整PT；不自动追加训练。开始前短原生探针无优化器更新。

保留完整DR、11类地形全部10档、20%名义/20%平地、35/78/6接口、2.5/10/20ms时序、TGS32/4、2mm单环境保护、原−1.5e²速度项与指数1.2、LR3e-5/clip0.1/3epochs/rollout24。

修改限于宽台阶上行示范：两类宽阶的50% reset从外侧平地x±3.75m、y±0.3m以可行站姿出发，面向中央；站立高度指令从0.28m按0.06m/s缓慢升至0.365～0.40m，3秒后给1.5～2.2m/s前进指令。其他reset、下行与其他地形的原指令保持。高度用原35维观测槽，既有高度奖励保留。

额外奖励：真正向中央推进到新的最远位置，并保持相对地面高度接近指令，给每米1.0的进展奖励（速率clip2.2，按step_dt积分）；从真实地形射线地面高度识别新台阶，每级一次0.5奖励。高度是相对地面，不把站上高台的世界z当成抬高底盘。来回摆动不重复领取同一段进展。原摔倒、闭链和数值保护保留。

本轮训练统计不是固定验收；轮末与父权重比较上阶、下阶和原平地能力，所有保存点和失败原件保留。配方见PLAN.json/EFFECTIVE_RECIPE.json，执行实现为support/mod4v3_ppo_v1/scut_rough_stair_lift_env.py。
''',encoding='utf8')
shutil.copy2(Path(r'D:/claude2/fangzhen/tmp/rough_v1_local_showcase_20261112/prepare_stair_lift_trial.py'),T/'prepare_trial.py')
print('TRIAL_READY_FOR_NATIVE_PROBE')
