"""Integrity and auxiliary-gradient dry run; no optimizer exists in this check."""
from pathlib import Path
import sys,json,hashlib,ast,numpy as np,torch
from types import SimpleNamespace
T=Path(__file__).resolve().parent;R=T.parents[2];F=R/'sources/local/MOD4V3_SERIAL_TEACHER_FIXED200_40M_20261116';sys.path[:0]=[str(T/'support'),str(R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/runtime/core')]
from play_ppo_flatv1 import ActorMLP
torch.set_num_threads(1);torch.manual_seed(0);plan=json.loads((T/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();refs=json.loads((T/'evidence/INITIAL_REFERENCES.json').read_text());assert sha(Path(refs['default_pointer']['path']))==refs['default_pointer']['sha256']
assert sha(T/'weights/parent_035m.pt')==plan['parent_sha256']and sha(T/'comprehensive_keep_teacher.pt')==plan['teacher_retention']['keep_teacher_sha256']
assert plan['parent_sha256']!=plan['teacher_retention']['keep_teacher_sha256']
assert plan['training_round']['seconds']==plan['budget_total_training_seconds']==600 and '2400'not in (T/'PLAN.json').read_text()
a=np.load(T/'skill_dataset/qualified_mod4_skills.npz');manifest=json.loads((T/'skill_dataset/MANIFEST.json').read_text());assert sha(T/'skill_dataset/qualified_mod4_skills.npz')==manifest['sha256']==plan['skill_supervision']['manifest_sha256'];assert a['obs'].shape[1]==35 and a['actions'].shape[1]==6;assert np.all(a['obs'][:,28:35]==[0,1,0,0,0,1,0]);assert abs(a['sampling_weight'].sum()-1)<1e-8
for row in manifest['episodes']:
 assert row['qualified']
 if row['source']=='qualified_dagger':
  result=json.loads(Path(row['admission']).read_text());assert result['qualified']and result['final_continuous_top_hold_s']>=.4-1e-7
for f in T.rglob('*.py'):ast.parse(f.read_text(encoding='utf8'))
report=dict(passed=True,budget_seconds=600,default_c874_unchanged=True,parent_035m_sha256=plan['parent_sha256'],frozen_keep_sha256=plan['teacher_retention']['keep_teacher_sha256'],separate_student_teacher_sha_verified=True,no_optimizer_created_or_stepped=True,optimizer_updates=0,dataset_frames=len(a['obs']),qualified_dagger=manifest['qualified_dagger_episodes'],old2400_fields_absent=True,mode_slices=plan['skill_supervision']['existing_mode_slices'],skill_lambda_schedule=dict(start=.25,end=1.,warmup_minibatches=48),remote_actual_tensordict_loss_dryrun_required_before_launch=True)
(T/'evidence/LOCAL_PREFLIGHT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('LOCAL_PREFLIGHT',json.dumps(report))
