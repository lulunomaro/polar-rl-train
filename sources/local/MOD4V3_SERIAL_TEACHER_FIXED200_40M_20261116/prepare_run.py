from pathlib import Path
import json, shutil, hashlib, ast, datetime
R=Path(__file__).resolve().parents[3];T=Path(__file__).resolve().parent
C=R/'sources/local/MOD4V3_LOW_SPEED_STAIR_CURRICULUM_2H_20261116'
E=R/'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1'
S=E/'forward_capture_repair_20261116';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def put(f,d):f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
shutil.copytree(C/'support',T/'support',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ['remote_run.py','launch.py','fixed_single_step_eval.py','fixed_pitch_eval.py','fixed_60_eval.py','fixed_stair_eval.py','descent_eval.py','matched_pitch_metrics.py']:
 shutil.copy2(C/name,T/name)
shutil.copytree(C/'manual_replay',T/'manual_replay',ignore=shutil.ignore_patterns('__pycache__','*.log','runtime'))
p=json.loads((C/'PLAN.json').read_text());old=p['root'];remote='/home/egde/rl_candidates/mod4v3_serial_teacher_fixed200_40m_20261116_r1'
for k in ['root','support','parent','training_job','probe_job']:
 if isinstance(p.get(k),str):p[k]=p[k].replace(old,remote)
p.update(root=remote,support=remote+'/support',parent=remote+'/parent_comprehensive.pt',training_job='train_serial_teacher_fixed200_40m',probe_job='probe_fixed200_contract',source_experiment=str(C.relative_to(R)),budget_total_training_seconds=2400,cumulative_training_seconds_before=0,resume_mode='Complete c874 PPO actor/critic/STD/17 Adam; new independent fixed200 task; no separate warmstart')
p['training_round']['seconds']=2400;p['teacher_retention']['keep_teacher']=remote+'/comprehensive_keep_teacher.pt';p['teacher_retention']['keep_domain']='1229 retained flat/rough including pitch targets; stair uses current native LQR demonstrations'
p['teacher_retention']['stair_fraction']=0.;p['continuous_stair'].update(course='fixed_200mm_serial_teacher_v1',heights_m=[.2],easy_review_fraction=0.,one_success_advances_one_env_at_next_reset=False,failures_before_demotion=None,curriculum_enabled=False,teacher_on_curriculum=True,commanded_root_height_m=.3466+.0625)
p['skill_supervision']=dict(enabled=True,dataset=remote+'/skill_dataset',lambda_bc=1.,batch_size=192,teacher_profile=str(S/'CANDIDATE_PROFILE.json'),teacher_profile_sha256=sha(S/'CANDIDATE_PROFILE.json'),qualified_starts_mm=[-60,-30,0,30,60],task='stair200_only',modes=[0,1,0,0,0,1,0],action_order=['left_front1_joint','left_rear1_joint','right_front1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint'],frozen_current_native_teacher=True,teacher_assistance_in_student_rollout=False)
p['GPU_sharing']['observed_additional_owner']=dict(pid=2898583,command_contains=['train_lift.py','baseline_loaded','--livestream 0'],allow_shared_gpu_without_killing_or_modifying=True)
p['authority_update']='2026-11-16 latest human approved current native teacher and requested original recipe, fixed200mm without height curriculum,40min';p['authorization_status']='authorized_by_latest_human';p['startup_probe']='Integrated native contract assertions and dry loss; no separate matrix; first update receipt required'
put(T/'PLAN.json',p)
weights=T/'weights';weights.mkdir();parent=R/'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt';assert sha(parent)==p['parent_sha256'];shutil.copy2(parent,weights/'parent_comprehensive.pt');shutil.copy2(parent,T/'comprehensive_keep_teacher.pt')
put(T/'evidence/DEFAULT_BEFORE.json',dict(path=str(R/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json'),sha256=sha(R/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json')))
# Freeze the actual native teacher source/profile without changing its live files.
files=[f for f in E.rglob('*')if f.is_file()and f.parent in [E,E/'sim',E/'data',E/'config']and f.suffix in ['.py','.yaml','.npz']]
source=[]
for f in files:
 dest=T/'teacher_snapshot'/f.relative_to(E);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest);source.append(dict(path=str(f),snapshot=str(dest.relative_to(T)),sha256=sha(f),bytes=f.stat().st_size))
shutil.copy2(S/'CANDIDATE_PROFILE.json',T/'teacher_snapshot/CANDIDATE_PROFILE.json');put(T/'teacher_snapshot/SOURCE_INDEX.json',dict(files=source,profile_sha256=sha(S/'CANDIDATE_PROFILE.json'),source_commit='ec9c7f66365cb4196b513fdcb1e1cb11a233a853',known_oblique_qualification='1/4; failed angles excluded from positive demonstrations'))
# Eliminate progression at both the task-state and cooked-geometry definitions.
f=T/'support/mod4v3_ppo_v1/single_step_math.py';s=f.read_text();s=s.replace('(.05,.07,.09,.11,.13,.15,.17,.19,.20)','(.20,)').replace('review_fraction: float = .15','review_fraction: float = 0.').replace("COURSE='single_step_low_speed_per_env_v1'","COURSE='fixed_200mm_serial_teacher_v1'");start=s.index('    # Review success');end=s.index('\ndef supported_upper',start);s=s[:start]+'''    zeros=torch.zeros_like(mastered)
    flags=torch.zeros_like(success,dtype=torch.bool)
    return zeros,zeros,flags,flags
'''+s[end:];f.write_text(s,encoding='utf8')
f=T/'support/single_step_geometry.py';s=f.read_text().replace('(.05,.07,.09,.11,.13,.15,.17,.19,.20)','(.20,)').replace('row=min(8,max(0,int(float(difficulty)*10)))','row=0');f.write_text(s,encoding='utf8')
f=T/'support/mod4v3_ppo_v1/continuous_stair_env.py';s=f.read_text().replace('minlength=9','minlength=len(SPEC.heights)').replace('self.stair_height[picked]=(.28+.4*h).clamp_max(.38)','self.stair_height[picked]=.4091');old_obs='        return ScutUnifiedRoughV1Env._get_observations(self)';new_obs='''        raw=ScutUnifiedRoughV1Env._get_observations(self)
        if getattr(self,'_course_ready',False):
            mask=self.continuous_stair_mask
            for key in ('policy','critic'):
                raw[key]=raw[key].clone()
                raw[key][mask,-7:]=raw[key].new_tensor([0.,1.,0.,0.,0.,1.,0.])
        return raw''';assert s.count(old_obs)==1;s=s.replace(old_obs,new_obs);f.write_text(s,encoding='utf8')
# Original finite PPO owner and full-DR settings retained; add focused startup assertions.
f=T/'support/mod4v3_ppo_v1/continuous_stair_train.py';s=f.read_text();marker="        checkpoint_format=(";pos=s.index(marker);check='''        if plan.get('skill_supervision',{}).get('enabled'):
            from .single_step_math import SPEC,advance
            mask=env.continuous_stair_mask;raw=env._get_observations()
            assert SPEC.heights==(.2,) and SPEC.review_fraction==0.
            assert bool(env.course_level[mask].eq(0).all())
            assert raw['policy'].shape==(env.num_envs,35) and raw['critic'].shape==(env.num_envs,78)
            for key in ('policy','critic'):
                assert torch.allclose(raw[key][mask,-7:],raw[key].new_tensor([0,1,0,0,0,1,0]).expand(int(mask.sum()),-1))
                assert torch.allclose(raw[key][~mask,-7:],raw[key].new_tensor([1,0,0,0,0,0,0]).expand(int((~mask).sum()),-1))
            assert not env.enforce_closure_reset
            from isaaclab.utils.warp import raycast_mesh
            terrain=env.terrain;ids=mask.nonzero().flatten();column=int(terrain.terrain_types[ids[0]])
            centers=terrain.terrain_origins[:2,column];starts=centers.repeat_interleave(2,0).clone();starts[:,2]+=2.;starts[1::2,0]+=2.
            directions=torch.zeros_like(starts);directions[:,2]=-1.
            hits=raycast_mesh(starts,directions,terrain.r1_wp_mesh,max_dist=5.)[0];heights=hits[::2,2]-hits[1::2,2]
            assert torch.allclose(heights,heights.new_full(heights.shape,.2),atol=1e-5)
            put(job/'FIXED200_CONTRACT.json',dict(passed=True,actual_cooked_heights_m=heights.tolist(),curriculum_enabled=False,stair_envs=int(mask.sum()),retained_envs=int((~mask).sum()),command_root_height_m=.4091,policy35_critic78_action6=True,stair_mode=[0,1,0,0,0,1,0],normal_mode=[1,0,0,0,0,0,0],teacher_assisted_rollouts=False,closure_2mm_diagnostic_only=True))
''';s=s[:pos]+check+s[pos:];s=s.replace("independent per-env low-speed single-step curriculum; same current-model teacher only on1229 retained flat/rough environments","fixed200mm skill BC plus c874 retention on1229 flat/rough; no progression");f.write_text(s,encoding='utf8')
# Record authorization before any optimizer starts; old prohibitions are historical.
text='''## 2026-11-16 21:00 最新人类授权：当前教师，固定200mm，40分钟

用户已认可当前native LQR+VMC教师用于训练，明确放弃高度进阶，直接200mm，40分钟。此授权覆盖下方旧“未验收前不开训”限制。实验目录sources/local/MOD4V3_SERIAL_TEACHER_FIXED200_40M_20261116；从c874完整PPO续训、当前五起点教师成功示范加技能监督、1229保留环境冻结c874约束，2048/full-DR/35/78/6和原物理电机不变。台阶仅200mm，不升降、不低级复习。默认c874指针不变；斜向失败不作为合格示范；实际开训以FIRST_UPDATE/TRAINING_CLOCK为准，当前准备中。

'''
for f in [R/'AGENTS.md',R.parent/'AGENTS.md',E.parent/'README.md',E.parent/'MEMORY_ENTRY.md']:
 f.write_text(text+f.read_text(encoding='utf8'),encoding='utf8')
(T/'README.md').write_text(text+'本轮只授权2400秒PPO时钟；每300秒完整PT和独立学生回放，无自动延长或晋升。保留原配方lr3e-5/clip0.1/epochs3/rollout24/TGS32/4。技能监督lambda1、batch192来自既有SkillSupervision默认配方；与保留lambda1共同进入同一PPO优化器。\n',encoding='utf8')
for f in (T/'support').rglob('*.py'):ast.parse(f.read_text(encoding='utf8'))
put(T/'evidence/PREPARATION.json',dict(prepared_at=datetime.datetime.now().astimezone().isoformat(),source_support=str(C/'support'),student_sha256=sha(parent),default_unchanged=True,requested_training_seconds=2400,optimizer_updates=0))
print('Prepared fixed200 isolated run',len(source),'teacher source files')
