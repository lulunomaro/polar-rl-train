from pathlib import Path
from datetime import datetime, timezone, timedelta
import json, hashlib, shutil
ROOT=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106')
T=ROOT/'sources/local/MOD4V3_SCUT_PITCH_BRAKE_2H_20261116'
D=ROOT/'deliveries/MOD4V3_LOW_PITCH_20261116'
A=ROOT/'sources/local/MOD4V3_LOW_PITCH_ADOPTION_AUDIT_20261116'
NOW=datetime.now(timezone(timedelta(hours=8))).isoformat()
MODEL='scut_pitch_brake_2h_20261116_005m'
NAME='11月16日俯仰较低模型'
SHA='c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617'
PARENT='db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283'
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(ROOT).as_posix()
assert not D.exists(), 'Use existing adoption rather than overwrite'
selected=json.loads((T/'weights/SELECTED_STUDENT.json').read_text())
meta=json.loads((T/'evidence/training/PERIODIC_005M.json').read_text())
source=T/'weights/model_005m.pt'
assert selected['sha256']==SHA==hashlib.sha256(source.read_bytes()).hexdigest()==meta['SHA']
assert meta['iteration']==25362 and meta['optimizer_entries']==17
D.mkdir(parents=True);A.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,D/'model_full_ppo.pt')
assert hashlib.sha256((D/'model_full_ppo.pt').read_bytes()).hexdigest()==SHA
for src,dst in [('PLAN.json','TRAINING_RECIPE.json'),('weights/SELECTED_STUDENT.json','SELECTION_SNAPSHOT.json'),('evidence/checkpoint_evals/model_005m/EVALUATION.json','EVALUATION_SNAPSHOT.json'),('FINAL_REPORT.md','TRAINING_FINAL_REPORT.md')]:shutil.copy2(T/src,D/dst)
identity=dict(display_name=NAME,model_date='2026-11-16',adopted_at=NOW,designation_authority='User explicitly requested adoption and Git archive named 11月16日俯仰较低模型',model_id=MODEL,iteration=meta['iteration'],sha256=SHA,bytes=source.stat().st_size,weight_file='model_full_ppo.pt',git_path=rel(D/'model_full_ppo.pt'),ordinary_full_PT=True,complete_PPO=True,actor_input=35,critic_input=78,action_output=6,source_checkpoint=rel(source),training_seconds_to_checkpoint=meta['training_elapsed_seconds'],parent_sha256=PARENT,role='User-adopted current comprehensive default and next comprehensive continuation model; old db6 preserved as rollback baseline',git_label=NAME,ascii_git_label='best-20261116-low-pitch-c874a1af',weights_changed=False,new_training_run=False,real_robot_certified=False,full_DR_graduation=False)
dump(D/'MODEL_IDENTITY.json',identity)
adoption=dict(adopted=True,adopted_at=NOW,display_name=NAME,model_id=MODEL,sha256=SHA,old_default_model_id='stairs200_max_height_40m_20261113_005m',old_default_sha256=PARENT,old_default_rollback_path='deliveries/MOD4V3_BEST_COMPREHENSIVE_20261113/model_full_ppo.pt',scope='User-approved comprehensive default/reference adoption; full-DR graduation and deployment not inferred',authority='采用一下git归档叫11月16日俯仰较低模型',evidence=rel(T/'FINAL_REPORT.md'),fixed_results=dict(flat60=60,straight5=5,actual_oblique20=1,descent5=5,rough_braking_peak_deg=13.561968469231244,flat_braking_peak_deg=13.370204023521898),historical_experiment_reports='Existing non-promotion decisions describe the earlier automatic selection stage and remain unchanged; this file records the later explicit user adoption')
dump(D/'ADOPTION.json',adoption)
dump(ROOT/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json',dict(model_id=MODEL,display_name=NAME,sha256=SHA,iteration=25362,full_PT_git_path=rel(D/'model_full_ppo.pt'),identity_git_path=rel(D/'MODEL_IDENTITY.json'),adoption_git_path=rel(D/'ADOPTION.json'),updated_at=NOW,rollback_sha256=PARENT,rollback_full_PT_git_path=adoption['old_default_rollback_path']))
reg_path=ROOT/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json'
reg=json.loads(reg_path.read_text(encoding='utf8'));assert reg['current_comprehensive_default_model_id']=='stairs200_max_height_40m_20261113_005m'
reg['as_of_date']='2026-11-16';reg['updated_at_epoch']=datetime.now().timestamp();reg['current_comprehensive_default_model_id']=MODEL;reg['selected_comprehensive_continuation_model_id']=MODEL
reg['current_comprehensive_default_git_path']=rel(D/'model_full_ppo.pt');reg['current_comprehensive_default_sha256']=SHA
reg['user_adopted_low_pitch_20261116']=identity
reg['latest_pitch_repair_training_20261116']=dict(status='completed',PPO_seconds=7209.351270437241,final_iteration=26036,selected_model_id=MODEL,adopted_by_user=True,report=rel(T/'FINAL_REPORT.md'))
assert not any(m.get('id')==MODEL for m in reg['models'])
reg['models'].append(dict(id=MODEL,display_name=NAME,file='model_full_ppo.pt',git_path=rel(D/'model_full_ppo.pt'),sha256=SHA,bytes=source.stat().st_size,complete_PPO=True,iteration=25362,actor_input=35,critic_input=78,action_output=6,root_parent_sha256=PARENT,recipe_files=[rel(D/'TRAINING_RECIPE.json')],role='User-adopted current comprehensive default and comprehensive continuation reference',git_storage='ordinary full PT blob',evaluation=rel(D/'EVALUATION_SNAPSHOT.json'),full_DR_graduation=False))
dump(reg_path,reg)
update=f'''## 2026-11-16 最新采用：{NAME}\n\n用户已明确采用两小时俯仰训练的5分钟检查点：`{MODEL}` / iteration25362 / SHA256 `{SHA}`。当前综合默认及后续综合续训入口改为`deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt`，统一指针为`deliveries/CURRENT_COMPREHENSIVE_MODEL.json`。旧11月13日db6保留回退基线；历史“不自动晋升”记录是本次用户采用前的状态。\n\n两小时PPO已于2026-11-16T03:30:17+08:00结束，实际7209.351秒，全部25组检查点评估及原轮次归档已完成。选中5m的名义MuJoCo固定评测：崎岖急停13.562°、平地13.370°，平地60/60、正向两阶5/5、实际斜向1/20、下阶5/5。尚无此新SHA的原生完整DR毕业证据，不继承旧db6的分数；没有新增训练或部署。MOD4v3、35/78/6接口与硬件合同保持。详见`deliveries/MOD4V3_LOW_PITCH_20261116/README.md`。\n\n'''
for p in [ROOT/'AGENTS.md',ROOT.parent/'AGENTS.md']:
 text=p.read_text(encoding='utf8');old='当前冻结综合默认仍为11月13日iteration25331、权重SHA256 `'+PARENT+'`；之后未晋升试验不能覆盖它。'
 text=text.replace(old,'原11月13日iteration25331/db6保留为历史冻结基线；当前综合默认已按2026-11-16用户指令采用本页顶部的5分钟低俯仰模型。')
 p.write_text(update+text,encoding='utf8')
idx=ROOT/'docs/DR_TRAINING_INDEX_20261111.md';text=idx.read_text(encoding='utf8');text=text.replace('当前综合默认固定使用这份权重。','该权重在2026-11-16用户采用低俯仰模型后保留作回退基线。');idx.write_text(update+text,encoding='utf8')
old_readme=ROOT/'deliveries/MOD4V3_BEST_COMPREHENSIVE_20261113/README.md';text=old_readme.read_text(encoding='utf8');old_readme.write_text('> 2026-11-16状态更新：用户已采用[11月16日俯仰较低模型](../MOD4V3_LOW_PITCH_20261116/README.md)作为当前综合默认。本目录保留11月13日原命名权重与历史证据，作为回退基线。以下正文描述原命名时的状态。\n\n'+text,encoding='utf8')
readme=f'''# {NAME}\n\n用户于2026-11-16明确采用的当前综合默认模型。后续综合回放和续训从本目录完整PT进入；统一指针见[CURRENT_COMPREHENSIVE_MODEL.json](../CURRENT_COMPREHENSIVE_MODEL.json)。\n\n- 模型：`{MODEL}`，iteration **25362**；两小时轮次第5分钟完整检查点，实际305.428秒。\n- 完整权重：[model_full_ppo.pt](model_full_ppo.pt)，{source.stat().st_size:,}字节，普通Git二进制；SHA256 `{SHA}`。\n- 名称固定指向上述SHA，不随最后检查点变化。actor35、critic78、6动作；完整PPO与17项优化器状态。\n- Git名称：`{NAME}`；ASCII别名：`best-20261116-low-pitch-c874a1af`。\n- 原机体：MOD4V3_HW300N60_R3；MJCF77904c00、USDe057969b；不替换资产、电机或控制时序。\n\n| 固定MuJoCo名义回放 | 11月13日父db6 | 本模型 |\n|---|---:|---:|\n| 难度9崎岖急停俯仰峰值 |22.645°|13.562°|\n| 平地急停俯仰峰值 |18.673°|13.370°|\n| 平地综合 |60/60|60/60|\n| 正向连续两阶 |4/5|5/5|\n| 实际斜向 |1/20|1/20|\n| 下阶 |5/5|5/5|\n\n采用依据是已完成的固定协议改善与用户明确指令。完整DR训练不等于此SHA已通过完整DR验收；父模型的原生成绩不能直接记入本模型。原[11月13日db6](../MOD4V3_BEST_COMPREHENSIVE_20261113/README.md)权重保留回退。\n\n[身份](MODEL_IDENTITY.json) · [采用记录](ADOPTION.json) · [训练配方](TRAINING_RECIPE.json) · [评测快照](EVALUATION_SNAPSHOT.json) · [两小时报告](TRAINING_FINAL_REPORT.md) · [华南虎奖励差距分析](../../sources/local/MOD4V3_LOW_PITCH_ADOPTION_AUDIT_20261116/REPORT.md)\n\n快照中的实验候选/未晋升措辞记录自动筛选时刻；本目录ADOPTION.json记录用户随后明确采用。此次采用没有进行PPO更新、ONNX导出或真机部署。\n'''
(D/'README.md').write_text(readme,encoding='utf8')
dump(A/'ADOPTION_SNAPSHOT.json',adoption)
print(json.dumps(dict(adopted=NAME,sha256=SHA,iteration=25362,default=rel(D/'model_full_ppo.pt'),git_pending=True),ensure_ascii=False,indent=2))
