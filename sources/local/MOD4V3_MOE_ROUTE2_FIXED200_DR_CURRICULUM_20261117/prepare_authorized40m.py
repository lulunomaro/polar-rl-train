from pathlib import Path
import ast,datetime,difflib,hashlib,json
n=Path(__file__).resolve().parent
e=n/'evidence';archive=e/'budget40_authorization';archive.mkdir(exist_ok=True)
sha=lambda s:hashlib.sha256(s).hexdigest()
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
plan_path=n/'PLAN.json';old_plan=json.loads(plan_path.read_text(encoding='utf8'));put(archive/'PLAN_BEFORE.json',old_plan)
pre=json.loads((e/'zeroDR_curriculum_probe_r3_cache/ROUTE2_NATIVE_PREFLIGHT.json').read_text(encoding='utf8'))
protected=json.loads((e/'PROTECTED_INPUTS.json').read_text(encoding='utf8'))
verified={k:sha(Path(v['path']).read_bytes())==v['sha256'] for k,v in protected.items()}
assert all(verified.values()),verified
train=n/'support/mod4v3_ppo_v1/route2_train.py';before_bytes=train.read_bytes();before=before_bytes.decode('utf8').replace('\r\n','\n');(archive/'route2_train.before.py').write_bytes(before_bytes)
train_key='mod4v3_ppo_v1/route2_train.py';assert sha(before_bytes)==pre['source_sha256'][train_key]
changes=[
 ('within a strict7200s budget.','within the explicitly authorized2400s budget.'),
 ("    assert plan.get('PPO_training_authorized') and plan.get('human_restart_authorized'), 'Human restart authorization required before native app or job creation'", "    assert plan.get('PPO_training_authorized') and plan.get('human_restart_authorized'), 'Human restart authorization required before native app or job creation'\n    assert args.seconds == plan['authorized_PPO_seconds'] == plan['strict_timing']['maximum_seconds'] == 2400"),
 ("        original_deadline=datetime.datetime.fromisoformat(plan['restart_policy']['original_absolute_deadline']).timestamp()\n        remaining_compute=7200.-plan['restart_policy']['previous_elapsed_seconds']\n        effective_seconds=min(float(args.seconds),remaining_compute,original_deadline-start_epoch)\n        assert effective_seconds>2460.,'Less than40m plus safe-close reserve remains before original deadline'", "        original_deadline=datetime.datetime.fromisoformat(plan['restart_policy']['superseded_original_absolute_deadline']).timestamp()\n        effective_seconds=float(args.seconds)\n        assert effective_seconds == 2400., 'Explicit fresh40m authorization required'"),
 ("args.seconds==plan['authorized_PPO_seconds']==7200","args.seconds==plan['authorized_PPO_seconds']==2400"),
 ('requested_seconds=7200,','requested_seconds=args.seconds,'),
 ('strict_max_seconds=7200,original_absolute_deadline_epoch=original_deadline,','strict_max_seconds=args.seconds,superseded_original_absolute_deadline_epoch=original_deadline,'),
 ('deadline_epoch=start_epoch+7200','deadline_epoch=start_epoch+effective_seconds')]
after=before
for old,new in changes:
 assert after.count(old)==1,(old,after.count(old));after=after.replace(old,new)
ast.parse(after);train.write_text(after,encoding='utf8')
(archive/'timing_only.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='prechecked/route2_train.py',tofile='authorized40m/route2_train.py')),encoding='utf8')
unchanged={k:sha((n/'support'/k).read_bytes())==v for k,v in pre['source_sha256'].items() if k!=train_key}
assert all(unchanged.values()),unchanged
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
auth=dict(approved_at_recorded=now,human_message='开始40分钟ppo训练',authorized_seconds=2400,clock_basis='fresh actual PPO start; supersedes previous absolute deadline for this round only',work_seconds=2340,save_close_reserve_seconds=60,automatic_extension=False,automatic_restart=False,automatic_promotion=False,previous_attempt_seconds_historical_only=old_plan['restart_policy']['previous_elapsed_seconds'])
put(e/'HUMAN_40M_AUTHORIZATION.json',auth)
p=old_plan.copy()
for k in ['authorized_PPO_seconds','proposed_training_seconds','alternative_only_if_human_approves_seconds','authorized_total_seconds','budget_total_training_seconds','budget_cap_seconds']:p[k]=2400
p.update(PPO_training_authorized=True,human_restart_authorized=True,training_job='train_fixed200_dr_curriculum_40m',training_round='human_authorized_zeroDR_to_DR_40m_20261117',strict_timing=dict(maximum_seconds=2400,work_cutoff_seconds=2340,save_close_reserve_seconds=60,clock='monotonic from actual PPO start',finish_iteration_after_deadline=False),human_40m_authorization=auth)
p['evaluation']={**p['evaluation'],'midrun_minutes':[5,10,20],'final_at_authorized_budget':True}
p['native_probe']={**p['native_probe'],'job':'native_zeroDR_curriculum_probe_r3_cache'}
p['restart_policy']={**p['restart_policy'],'authorized':True,'awaiting_explicit_clock_rebase':False,'reason':'Human explicitly authorized a fresh40m PPO run after completed zero-update precheck','superseded_original_absolute_deadline':p['restart_policy']['original_absolute_deadline'],'deadline_basis':'actual PPO start +2400s; no absolute limit inherited from superseded round','prior_elapsed_is_historical_not_deducted_from_new40m':True,'human_authorization_message':'开始40分钟ppo训练'}
put(plan_path,p)
v=dict(passed=True,recorded_at=now,authorized_seconds=2400,train_source_key=train_key,prechecked_sha256=sha(before_bytes),authorized_sha256=sha(train.read_bytes()),all_other_prechecked_sources_exact=all(unchanged.values()),unchanged_source_checks=unchanged,protected_inputs_exact=verified,only_timing_and_receipt_fields_changed=True,diff_path=str(archive/'timing_only.patch'),new_deadline_from_actual_start=True,work_cutoff_seconds=2340,no_new_PPO_in_validation=True)
put(e/'BUDGET40_VERIFICATION.json',v)
launcher=n/'remote_control.py';s=launcher.read_text(encoding='utf8');(archive/'remote_control.before.py').write_bytes(launcher.read_bytes())
old="files=[(T/'startup_sweep_poses.json'";assert s.count(old)==1
s=s.replace(old,"files=[(T/'evidence/BUDGET40_VERIFICATION.json','BUDGET40_VERIFICATION.json'),(T/'evidence/HUMAN_40M_AUTHORIZATION.json','HUMAN_40M_AUTHORIZATION.json'),(T/'startup_sweep_poses.json'")
old=" assert all(hashlib.sha256((r/'support'/k).read_bytes()).hexdigest()==v for k,v in pre['source_sha256'].items())"
new=" timing=json.loads((r/'BUDGET40_VERIFICATION.json').read_text());assert timing['passed'] and timing['authorized_seconds']==2400 and timing['all_other_prechecked_sources_exact']\n for k,v in pre['source_sha256'].items():\n  if k==timing['train_source_key']:\n   assert v==timing['prechecked_sha256'];v=timing['authorized_sha256']\n  assert hashlib.sha256((r/'support'/k).read_bytes()).hexdigest()==v,k"
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace("assert p['authorized_PPO_seconds']==7200", "assert p['authorized_PPO_seconds']==2400")
s=s.replace("'--seconds','0'if probe else'7200'", "'--seconds','0'if probe else str(p['authorized_PPO_seconds'])")
ast.parse(s);launcher.write_text(s,encoding='utf8')
(n/'LAUNCH_PLAN_40M.md').write_text('# 2026-11-17 人类授权40分钟PPO\n\n人类最新指令：开始40分钟ppo训练。实际PPO起点起算2400秒，2340秒停算预留60秒保存关闭；不自动延长、重启或晋升。原22:30:31绝对截止由本次明确40分钟授权覆盖，原326.837秒短轮仅作历史记录。\n\n沿用已通过的2048环境600步0更新预检及同一v1权重、课程、奖励、物理和架构，仅更改计时与审计字段。完整保留预检原哈希、原代码及逐行差异，不重写预检结论。E0冻结真c874，E1先0DR center，再五点速度泛化，再按成功逐步增加原fullDR环境占比。每5分钟完整保存，5/10/20分钟独立抽检，最终冻结全回归与1x视频。预检成绩不冒充正式或fullDR毕业。\n',encoding='utf8')
print(json.dumps(dict(prepared=True,authorized_seconds=2400,work_cutoff_seconds=2340,protected=verified,all_other_prechecked_sources_exact=all(unchanged.values()),train_sha256=v['authorized_sha256']),ensure_ascii=False))
