from pathlib import Path
import json,ast,shutil
R=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106');T=R/'sources/local/MOD4V3_CONTINUOUS_STAIRS_OWN_REPAIR_20261113'
# Keep the already proven archive transport; avoid re-archiving earlier trials as new results.
f=T/'archive_run.py';s=f.read_text();a=s.find('# Include every immutable original-segment model/source/report, including failed probes.');b=s.find("files += [R/'README.md'",max(0,a));s=s[:a]+s[b:] if a>=0 else s;s=s.replace('Fresh SCUT-method7200s from iter24692 network/STD weights with newAdam/seed/iteration0;13.33wide/66.67otherRough/20flat; wide uses saved successful-stair reward and no-air mask; shaping diagnostics only; new2048env native functional probe; original plant/controller/perenvguards; no graduation claim','Own50stairs30rough20flat; half-flat6task coverage; complete parent PPO; restored stair shaping and symmetric speed penalty; native2048env probe; no graduation claim');s=s.replace('Fresh bounded7200s round','Own bounded2400s round');f.write_text(s,encoding='utf8')
f=T/'finalize_run.py';s=f.read_text().replace('continuous_stairs200_parent_mixed_2h_20261113','continuous_stairs200_own_repair_40m_20261113').replace('CONTINUOUS_STAIRS_PARENT_MIXED_2H_20261113','CONTINUOUS_STAIRS_OWN_REPAIR_40M_20261113').replace('selected_parent_mixed_candidate.pt','selected_own_repair_candidate.pt').replace('7200','2400').replace('两小时','40分钟').replace('父模型起步混训','自有配方平地保留修复').replace('从健康父模型重新完整训练','从健康父模型恢复自有配方训练')
s=s.replace("records=[];evaluations=[]","records=[];evaluations=[]")
s=s.replace('PPO为3e-5 fixed/clip.1/3epochs/value4','PPO为3e-5 fixed/clip.1/3epochs/value4；平地一半固定原六项目标、地面reset，实际覆盖见flat_preservation')
s=s.replace("(T/'FINAL_REPORT.md').write_text(report,encoding='utf8')","report+='\\n\\n此次恢复自有收腿/落轮/接续奖励；平地保留组的一半固定练原六项目标并用地面reset，余下平地和原rough采样保留；真实terrain_family用于奖励过滤。实际配方、探针和启动核验见PLAN.json及evidence。\\n'.replace('\\\\n','\\n')\n (T/'FINAL_REPORT.md').write_text(report,encoding='utf8')")
ast.parse(s);f.write_text(s,encoding='utf8')
# Real retained-task exposure is checked throughout the existing native functional probe.
f=T/'support/mod4v3_ppo_v1/continuous_stair_checks.py';s=f.read_text();needle=' for k in range(600):';assert needle in s
s=s.replace(needle,""" fixed=env.flat_preservation_mask;task=env.flat_preservation_task[fixed]
 assert int(fixed.sum())==205 and not bool((fixed&~env.flat_terrain_mask).any())
 assert set(task.tolist())==set(range(6))
 assert int((fixed&env.full_dr.nominal_env_mask).sum())==41
 expected=env.command.new_tensor([[2.,0.,0.],[2.2,0.,0.],[-1.5,0.,0.],[0.,0.,4.5*3.141592653589793],[0.,0.,0.],[0.,0.,0.]])
 heights=env.height.new_tensor([.28,.28,.28,.28,.20,.40])
 assert env.reward.cfg.rewards['track_lin_vel_xy_square']==-1.5
 assert env.reward.cfg.lin_vel_xy_square_sigma==1.
 assert env.reward.cfg.rewards['track_lin_vel_xy']==1.2
 assert not bool(env.reward.get_terrain_name_mask('mod4_step270').any())
 for k in range(600):""")
needle="  assert not bool(env.stair_up[~stairs].any())";s=s.replace(needle,"  assert torch.allclose(env.command[fixed],expected[task]) and torch.allclose(env.height[fixed],heights[task]), 'Fixed six-task targets were overwritten'\n  assert not bool(env.r2_air_reset[fixed].any()), 'Preservation ground task became an airborne reset'\n"+needle,1)
s=s.replace('geometry_verified=True,samples=samples','geometry_verified=True,flat_six_tasks_verified=True,own_stair_shaping_enabled=True,terrain_name_filter_verified=True,samples=samples');ast.parse(s);f.write_text(s,encoding='utf8')
# Record baseline data directly from immutable existing replays.
base=R/'sources/local/MOD4V3_CONTINUOUS_STAIRS_200MM_2H_20261113/evidence/checkpoint_evals/model_035m'
fdata=json.loads((base/'flat60/RESULT.json').read_text());ev=json.loads((base/'EVALUATION.json').read_text());groups={}
for row in fdata['rows']:groups.setdefault(row['task'],[]).append(row)
summary={name:{'n':len(rows),'passed':sum(r['passed'] for r in rows),'vx_mean':sum(r['vx_mean'] for r in rows)/len(rows)} for name,rows in groups.items()}
(T/'evidence/OWN_RECIPE_BASELINE.json').write_text(json.dumps({'source':base.relative_to(R).as_posix(),'sha256':ev['sha256'],'stairs10':ev['whole_stair_passed'],'flat60':ev['flat60_passed'],'flat_by_task':summary,'interpretation':'Existing own recipe acquired nominal stair skill but forward overspeed; fixed task coverage is a hypothesis to test, not a proven root cause'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Include the actual preparation code for source ancestry; no credentials.
shutil.copy2(R.parent/'tmp/prepare_own_stair_repair_20261113.py',T/'prepare_source.py')
for f in T.rglob('*.py'):ast.parse(f.read_text(encoding='utf8'),filename=str(f))
print('Own recipe source and lifecycle parsed; native probe pending')

