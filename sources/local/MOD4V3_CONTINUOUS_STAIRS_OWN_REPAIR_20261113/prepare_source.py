from pathlib import Path
import shutil,json,hashlib,ast
R=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106');B=R/'sources/local'
OLD=B/'MOD4V3_CONTINUOUS_STAIRS_PARENT_MIXED_2H_20261113';SCUT=B/'MOD4V3_SCUT_STAIR_FINETUNE_2H_20261113';T=B/'MOD4V3_CONTINUOUS_STAIRS_OWN_REPAIR_20261113'
assert not T.exists(),str(T)
T.mkdir();(T/'evidence').mkdir();(T/'weights').mkdir()
shutil.copytree(OLD/'support',T/'support',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(SCUT/'retention_eval_terrain',T/'retention_eval_terrain',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ('fixed_stair_eval.py','evaluate_checkpoint.py','monitor_run.py','remote_run.py','rough_retention_replay.py','run_retention_replays.py','native_cache_lifecycle.py','archive_run.py'):
 shutil.copy2(SCUT/name,T/name)
for name in ('launch.py','finalize_run.py'):
 shutil.copy2(OLD/name,T/name)
p=json.loads((OLD/'PLAN.json').read_text());p['root']='/home/egde/rl_candidates/mod4v3_continuous_stairs_own_repair_20261113_r1';p['support']=p['root']+'/support';p['training_round']['seconds']=2400;p['previous_stage']=OLD.relative_to(R).as_posix();p['previous_remote_job']='/home/egde/rl_candidates/mod4v3_scut_stair_finetune_2h_20261113_r1/train120m_scut_stair_r1';p['cumulative_training_seconds_before']=0;p['budget_total_training_seconds']=2400;p['phase']='Own continuous-stair reward repair; fixed flat command coverage; complete parent PPO resume; independent2400s';p['resume_mode']='complete_ppo';p.pop('reference_method',None)
p['flat_preservation']={'fraction_of_flat':0.5,'fraction_of_all_envs':0.1,'expected_num_envs':205,'normal_ground_resets':True,'tasks':[['forward20',2.,0.,.28],['forward22',2.2,0.,.28],['reverse15',-1.5,0.,.28],['yaw14137',0.,14.137166941154069,.28],['height020',0.,0.,.20],['height040',0.,0.,.40]],'command_fixed_for_episode':True,'reward_unchanged':'Original symmetric -1.5e2 plus exponential1.2','other_flat_and_rough_sampling':'Unchanged original tasks including eligible airborne resets'}
p['continuous_stair']['all_other_recipe_settings_unchanged']=True;p['continuous_stair']['terrain_name_filter']='Actual terrain_family; carry verified implementation repair';p['continuous_stair']['custom_stair_shaping_to_PPO']=True;p['continuous_stair']['retained_commands']='Original Rough-v1 elsewhere; half of flat assigned existing6task regression commands; all special stair overrides remain within50% stair subset'
(T/'PLAN.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
shutil.copy2(R/p['root_parent']['git_path'],T/'weights/parent_iter24692.pt')
assert hashlib.sha256((T/'weights/parent_iter24692.pt').read_bytes()).hexdigest()==p['parent_sha256']
f=T/'support/mod4v3_ppo_v1/continuous_stair_env.py';s=f.read_text();s=s.replace('from isaaclab.utils.math import quat_from_euler_xyz','from isaaclab.utils.math import quat_from_euler_xyz\nfrom rough_scut_v1_terrain import FAMILIES')
s=s.replace('  self._continuous_ready=True','''  # Keep the original stair objective; repair only retained-task exposure and terrain lookup.
  self.flat_preservation_mask=torch.zeros(n,device=dev,dtype=torch.bool)
  self.flat_preservation_task=torch.full((n,),-1,device=dev,dtype=torch.long)
  task_offset=0
  for nominal in (False,True):
   ids=(self.flat_terrain_mask&(self.full_dr.nominal_env_mask==nominal)).nonzero().flatten()
   chosen=ids[::2]
   self.flat_preservation_mask[chosen]=True
   self.flat_preservation_task[chosen]=(torch.arange(len(chosen),device=dev)+task_offset)%6
   task_offset+=len(chosen)
  self.reward.get_terrain_name_mask=self._terrain_name_mask
  self._continuous_ready=True''')
anchor=' def _center(self):'
addition=''' def _terrain_name_mask(self,names):
  if isinstance(names,str):names=(names,)
  if not names:return torch.ones(self.num_envs,device=self.device,dtype=torch.bool)
  mask=torch.zeros(self.num_envs,device=self.device,dtype=torch.bool)
  for name in names:
   if name in FAMILIES:mask|=self.terrain_family==FAMILIES.index(name)
  return mask
 def _flat_preservation_commands(self,ids):
  if not getattr(self,'_continuous_ready',False):return
  picked=ids[self.flat_preservation_mask[ids]]
  if not picked.numel():return
  tasks=self.flat_preservation_task[picked]
  table=self.command.new_tensor([[2.,0.,.28],[2.2,0.,.28],[-1.5,0.,.28],[0.,4.5*math.pi,.28],[0.,0.,.20],[0.,0.,.40]])
  self.command[picked]=0.;self.command[picked,0]=table[tasks,0];self.command[picked,2]=table[tasks,1]
  self.height[picked]=table[tasks,2];self.command_timer[picked]=1e9
  self.heading_env[picked]=False;self.standing_env[picked]=tasks>=4
  self.reward.command[picked]=self.command[picked];self.reward.height_cmd[picked]=self.height[picked]
  self.reward._invalidate_step_caches()
'''
assert anchor in s;s=s.replace(anchor,addition+anchor,1)
s=s.replace('  picked=ids[self.continuous_stair_mask[ids]];self.heading_env[picked]=False;self.standing_env[picked]=False','  picked=ids[self.continuous_stair_mask[ids]];self.heading_env[picked]=False;self.standing_env[picked]=False\n  self._flat_preservation_commands(ids)',1)
needle='  picked=ids[self.continuous_stair_mask[ids]]\n  if not picked.numel():return';assert needle in s;s=s.replace(needle,'  self._flat_preservation_commands(ids)\n'+needle,1)
s=s.replace("   out['continuous_stair']=dict(","   out['flat_preservation']=dict(envs=int(self.flat_preservation_mask.sum()),tasks=torch.bincount(self.flat_preservation_task[self.flat_preservation_mask],minlength=6).tolist(),ground_only=True,reward_unchanged=True,nominal=int((self.flat_preservation_mask&self.full_dr.nominal_env_mask).sum()))\n   out['continuous_stair']=dict(",1)
ast.parse(s);f.write_text(s,encoding='utf8')
f=T/'support/mod4v3_ppo_v1/scut_rough_scut_v1_env.py';s=f.read_text();needle='        if self.r2_force_air:\n            selected[:] = True';assert needle in s;s=s.replace(needle,needle+"\n        preservation=getattr(self,'flat_preservation_mask',None)\n        if preservation is not None:selected &= ~preservation[ids]",1);ast.parse(s);f.write_text(s,encoding='utf8')
for name in ('monitor_run.py','run_retention_replays.py','native_cache_lifecycle.py'):
 f=T/name;s=f.read_text().replace('train120m_scut_stair_r1','train040m_own_repair_r1');f.write_text(s,encoding='utf8')
f=T/'archive_run.py';s=f.read_text().replace('mod4-scut-stair-finetune-2h','mod4-continuous-stairs-own-repair-40m').replace('SCUT-method7200s','own-recipe2400s').replace('Fresh SCUT-method7200s from iter24692 network/STD weights with newAdam/seed/iteration0;13.33wide/66.67otherRough/20flat; wide uses saved successful-stair reward and no-air mask; shaping diagnostics only; new2048env native functional probe; original plant/controller/perenvguards; no graduation claim','Own50stairs30rough20flat; half-flat6task coverage; full parent PPO; original stair shaping and speed objective; terrain lookup repaired; native noPPO probe; no graduation claim')
# Already archived prior trials remain referenced; this archive records this distinct trial only.
start=s.index('# Include every immutable original-segment model/source/report, including failed probes.')
end=s.index('for name in ',start) if 'for name in ' in s[start:] else -1
print('ARCHIVE_PREVIOUS_BLOCK',s[start:start+1200])
f.write_text(s,encoding='utf8')
(T/'README.md').write_text('''# 自有连续登阶配方修复（2026-11-13）

用户要求回到我们自己的配方继续修复。保留SCUT失败轮原件；恢复原连续登阶PPO目标，从健康父iter24692完整续接。下一轮2400秒，每300秒保存/检查，独立预算，不自动延长。

## 此次集中改动

- 恢复50%连续200mm双阶、30%原Rough-v1、20%平地，原完整DR继续。
- 原进展0.8/m、越沿抬轮与收腿0.6、首/次落轮各0.5、阶间等待-0.15/s、到顶保持0.3s完成2.0参与PPO。
- 速度指数1.2和对称-1.5e²保持；恢复原3e-5 fixed、clip0.1、3epochs，完整继承父Adam/STD/RNG。
- 平地保留组的一半持续练原六项固定目标；另一半平地与其余rough保留原随机科目。固定保留组用原地面reset，避免变成落地恢复科目；完整DR仍交叉覆盖。
- 真实terrain_family用于奖励状态机的地形过滤；这是已查实的实现修复。

原35m模型连续登阶8/10，但平地40/60，2.0/2.2指令实测约2.936/3.131m/s。它是动作参考，不能称全面改进。当前健康父平地60/60、连续阶2/10；实验从该父开始。

先用无PPO探针检查实际采样/命令/奖励路由，然后开展40分钟修复。每5分钟同协议回放平地60例及连续两阶。以原始结果判断，原成熟模型保留；所有实际PT与失败报告通过7897代理归档。

MOD4资产、35/78/6接口、电机包络、2.5ms物理、400Hz轮/100Hz腿/50Hz策略、TGS32/4、2mm单环境闭链保护保持。华南虎原参考配置不是本轮奖励来源。
''',encoding='utf8')
# Source ancestry records identify this restoration, not a relabel of the SCUT trial.
(T/'evidence/SOURCE_ANCESTRY.json').write_text(json.dumps({'own_recipe_source':OLD.relative_to(R).as_posix(),'failed_reference_trial':SCUT.relative_to(R).as_posix(),'parent_sha256':p['parent_sha256'],'changes':['fixed flat6task exposure on half-flat,ground reset','actual terrain-name filter'],'new_stage':T.relative_to(R).as_posix()},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('CREATED',T)
