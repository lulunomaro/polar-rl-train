"""Confirm an already running job from native loss arithmetic; never launches PPO."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';P=json.loads((T/'PLAN.json').read_text())
confirmed=json.loads((E/'TRAINING_STARTED_CONFIRMED.json').read_text())
progress=json.loads((E/'training/LATEST_PROGRESS.json').read_text());ret=progress['teacher_retention'];last=ret['last'];spec=ret['spec']
base=float(spec['lambda_bc'])*(float(spec['keep_fraction'])*last['teacher_keep_mse']+float(spec['stair_fraction'])*last['teacher_stair_mse'])+float(spec['lambda_high_stance'])*last['teacher_high_stance_legs_mse']+float(P['rearward_reference']['lambda_legs'])*last['rearward_reference_legs_mse']
residual=last['teacher_aux_loss']-base
assert residual>1e-7,'No observed brake contribution in this completed native PPO update'
(E/'START_CONFIRMATION_PROGRESS_SNAPSHOT.json').write_text(json.dumps(progress,indent=2)+'\n')
record=dict(epoch=time.time(),iteration=progress['iteration'],training_elapsed_seconds=progress['training_elapsed_seconds'],native_teacher_aux_loss=last['teacher_aux_loss'],retained_and_high_stance_aux_loss=base,extra_brake_weighted_loss=residual,brake_lambda=P['brake_distillation']['lambda_brake'],derived_mean_brake_MSE=residual/P['brake_distillation']['lambda_brake'],method='Actual native auxiliary loss minus all other documented loss components; mean over same12minibatches',sampling_count='Not exposed by existing finish_update aggregation; not fabricated',training_restarted=False)
(E/'BRAKE_LOSS_NATIVE_CONFIRMED.json').write_text(json.dumps(record,indent=2)+'\n')
(E/'START_READER_REPAIR.json').write_text(json.dumps(dict(error='Starter queried a cumulative metric discarded when native finish_update rebuilds summary',repair='Stop only the local acknowledgement waiter; confirm nonzero actual brake contribution by exact auxiliary-loss decomposition; remote PPO, source and7200s clock unchanged',native_loss_verified=record,training_restarted=False),indent=2)+'\n')
print('ACTUAL_NATIVE_BRAKE_LOSS_CONFIRMED',json.dumps(record),flush=True)
note='2026-11-16新独立两小时俯仰修复已实际开训：'+confirmed['actual_PPO_start_local']+'，预计完整迭代结束约'+confirmed['planned_end_local']+'；从冻结db6/iter25331完整恢复，新增SCUT稠密姿态、水平速度奖励修复和训练期急停轮协调示范。每5分钟完整PT与固定回放，默认不自动晋升。见sources/local/MOD4V3_SCUT_PITCH_BRAKE_2H_20261116/README.md。'
with(T/'README.md').open('a',encoding='utf8')as f:f.write('\n实际开始：'+confirmed['actual_PPO_start_local']+'；预计结束：'+confirmed['planned_end_local']+'。首迭代actor已改变，17项Adam完整恢复，原生PPO额外轮协调损失已由总辅助损失的正残差核实。\n')
for path in [R/'AGENTS.md',R.parent/'AGENTS.md']:
 text=path.read_text(encoding='utf8');head,sep,rest=text.partition('\n');path.write_text(head+sep+'\n'+note+'\n'+rest,encoding='utf8')
(E/'WORKSPACE_AGENTS_SNAPSHOT.md').write_text((R.parent/'AGENTS.md').read_text(encoding='utf8'),encoding='utf8')
path=R/'docs/DR_TRAINING_INDEX_20261111.md';text=path.read_text(encoding='utf8');head,sep,rest=text.partition('\n');path.write_text(head+sep+'\n## 2026-11-16：SCUT奖励与急停轮协调两小时训练\n\n'+note+'\n'+rest,encoding='utf8')
subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/'archive_run.py'),'--phase','launch'],cwd=R,check=True)
print('START_AND_REPAIR_ARCHIVED',flush=True)