from pathlib import Path
import shutil,json,hashlib
R=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106');S=R/'sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112';T=R/'sources/local/MOD4V3_SCUT_STAIR_LIFT_20M_20261112'
assert not T.exists();T.mkdir()
shutil.copytree(S/'support',T/'support',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ['launch.py','inspect_checkpoint.py','CHECKPOINT_EVAL_TEMPLATE.json','checkpoint_unified_replay.py']:
 shutil.copy2(S/name,T/name)
(T/'evidence').mkdir();(T/'weights').mkdir()
shutil.copy2(Path(__file__).parent/'TRAIN_STORAGE_RESTORE_20261112.json',T/'evidence/STORAGE_RESTORE.json')
plan=json.loads((S/'EFFECTIVE_RECIPE.json').read_text(encoding='utf8'));old=plan['support'].rsplit('/support',1)[0];remote=plan['root']+'/scut_stair_lift_20m_20261112_r1'
plan['support']=remote+'/support';plan['parent']=old+'/train120m_scut_rough_v1_r1/model_120m.pt';plan['parent_sha256']='7cc1fc6deeee3d3aba8ae8d2da31dce200079fb229a145f1cbb1cd3bfabea103';plan['parent_iteration']=24482
plan['execution_scope']='User2026-11-12: continue selected120m full checkpoint; one1200s stair-height-guidance trial, full PT every300s; no automatic further training.'
plan['training_round'].update(job='train020m_stair_lift_r1',seconds=1200,parent_sha256=plan['parent_sha256'],state='Full actor/critic/STD/Adam/RNG from selected Rough-v1 120m iter24482; new stair-lift episode sampling',budget='One1200s actual PPO window; native no-optimizer probe separate; no further training',post_training='Compare parent and trial checkpoints: raised-height ascent, original-height ascent/descent and flat retention')
plan['reward']['profile']='rough_scut_v1_stair_lift';plan['stair_lift']=dict(families=['low_speed_stair_for_rm','high_speed_stair_for_rm'],approach_fraction_of_wide_stair_resets=.5,spawn_abs_x_m=3.75,spawn_y_m=[-.3,.3],height_initial_m=.28,height_target_m=[.365,.4],height_slew_mps=.06,settle_before_forward_s=3.,approach_forward_command_mps=[1.5,2.2],progress_weight=1.,height_gate_sigma_m=.05,per_step_bonus=.5,terrain_grade_reference='Existing static-terrain ground ray hits; relative body height, no world-z lift reward',existing_height_rewards='Kept unchanged; new command height uses existing35-D actor slot',other_distributions='All11families/all10rows, fullDR, nominal20%/flat20% and original airborne modes retained; original reset/commands for nonselected episodes')
(T/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(T/'EFFECTIVE_RECIPE.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=T/'launch.py';s=p.read_text();s=s.replace('default=7200','default=1200');p.write_text(s,encoding='utf8')
p=T/'support/mod4v3_ppo_v1/scut_flat_train.py';s=p.read_text();s=s.replace('from .scut_rough_scut_v1_env import ScutUnifiedRoughV1Env as EnvClass','from .scut_rough_stair_lift_env import ScutRoughV1StairLiftEnv as EnvClass')
s=s.replace("if args.profile=='rough_r1':from .rough_r1_checks import run_probe", "if args.profile=='rough_scut_v1':from .stair_lift_checks import run_probe\n            elif args.profile=='rough_r1':from .rough_r1_checks import run_probe")
p.write_text(s,encoding='utf8')
print(json.dumps(dict(stage=str(T),remote=remote,parent=plan['parent'],seconds=1200)),flush=True)
