from pathlib import Path
import hashlib,json,os,subprocess,time,tomllib
D=Path(__file__).resolve().parent;R=D/'reports'
q=D/'actual_target72/OWNED72_FINAL_CLOSURE_V1/audit/ZONGLIN2_DEPLOYMENT_CLOSURE_V1_ACTUAL.json'
v=json.loads(q.read_bytes());assert v['both_CUDA_and_headless_Lab_GPU_PhysX_actual_passed'] and v['actual_validation_fcntl_free']
assert not v['actual_compute_snapshot'].strip() and not v['source_old_absolute_home_exists_on_target']
pids=sorted({x['pid'] for p in R.glob('*STARTED.json') for x in [json.loads(p.read_bytes())] if isinstance(x.get('pid'),int)})
filter_text=' OR '.join('ProcessId = '+str(p) for p in pids)
cmd='$p=Get-CimInstance Win32_Process -Filter '+"'"+filter_text+"'"+';@($p)|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'
p=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,encoding='utf8',check=True)
cim=json.loads(p.stdout) if p.stdout.strip() else [];cim=cim if isinstance(cim,list) else [cim]
assert all(D.name not in str(x.get('CommandLine','')) for x in cim)
value=dict(epoch=time.time(),status=v['status'],target='lc01@10.24.0.72',root=v['root'],
 source4090_readonly_archive=json.loads((R/'SOURCE4090_TO_ZONGLIN2_TRANSFER_V2_COMPLETE.json').read_bytes())['archive'],
 extraction=dict(files=192821,bytes=43355115027),actual_closure_source=str(q),actual_closure_SHA=hashlib.sha256(q.read_bytes()).hexdigest(),
 both_GPU_CUDA_arithmetic_and_Lab_PhysX24_steps_finite_UUID_exact_natural_exit0=True,
 actual_recorded_local_coordinator_PID_snapshots=cim,actual_own_remote_validation_processes_out=v['actual_process_exit_snapshots'],
 actual_fcntl_free=True,no_own_compute_jobs_at_closure=True,
 original_base_entries_present=v['original_base_entries_still_present'],private_libc_not_system_replacement=True,
 no_manual_deletion_or_outside_target_root_installation_source_driver_profile_mutation=True,
 original_all_failures_false_and_unused_source_retained=True,
 previous_crashreporter_absolute_paths_historical_and_absent_on_target=True,
 no_training_budget_change_MOD4_fullstate_rendering_GUI_camera_or_deadline_admission=True,
 existing_unique_stage_commit='4205677b5f41519429e5c975f8e880bf4a4c3502',
 ordinary_Git_append_pending_at_this_report_capture=True,
 human_three_host_coordination_discussion='Proposed role-based scheduling:210 main training/recovery;72 two-GPU expansion candidate;249 frozen eval only. Not one machine permanently per expert. Human question does not launch72 learning or authorize parallel GPU workers, extra budget, new gatePPO or S8.')
with (R/'ZONGLIN2_HUMAN_DEPLOYMENT_FINAL_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
cfg=tomllib.loads((Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml').read_text(encoding='utf8'))
assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1'
prefix='''最新 human/actual优先：10.24.0.72双4090环境部署已实际闭合。人类明确只在 /home/lc01/Zonglin Li/ 下新建zonglin2、不要删任何东西、可从原4090复制。真实root=/home/lc01/Zonglin Li/zonglin2，无symlink。原210只读source环境+selected项目，21GB archive SHA77b823a63570fd5f0acfa7b1ce935cd61b914e9a5727e1e3333b39a95be7e184/20988865638B完整target核，192821 regularfiles/43355115027B安全解包，371仅新副本prefix迁移。所有原包/失败/unused源保留，原目录entries仍在，无manual delete、系统glibc/driver/旧env/profile或source更改。

新部署D=C:/Users/lulu/Desktop/claude/mjcf/MOD4_HOST72_ZONGLIN2_ENV_DEPLOY_20261015，优先reports/ZONGLIN2_HUMAN_DEPLOYMENT_FINAL_ACTUAL.json与actual_target72/OWNED72_FINAL_CLOSURE_V1/audit/ZONGLIN2_DEPLOYMENT_CLOSURE_V1_ACTUAL.json。Python3.12.14/Torch2.10cu128/TD.14.1/RSL5.0.1/Sim6.0.1metadata/Lab6.1.14metadata，actualLab仍copied3beta路径。native SDK原GLIBC2.33缺失保留，私有compat/glibc240 loader后CPU全import passed，不改targetUbuntu20/glibc2.31/driver535。两物理4090各tiny CUDA exact；原V3默认图形/legacyWorld startup失败、V4 Warp reader、V5 parentmodule metadata、V6早Carb settings错误均原件保留，不能称原PASS。最终V7用实际LabAppLauncher/headless与原SimulationContext，Warp转Torch只读，source进口/各24 physicssteps/.0025s/CUDA view-pose-velocity finite/UUID exact，两GPU naturalEXIT0、SimulationContext cleared、所有原父子实际/proc out/真实fcntlFree/nvidia无compute闭合。新run-python.sh引导private loader；README.md和tools/zonglin2_app_launcher.py已保存，owned subclass只supported launch-config关crashreporter/保留旧dump/不渲染，不改SDK源或driverguard。旧复制crash metadata引用/home/egde在target实际不存在，不是新target训练故障。此仅headless环境准入，非MOD4 robot-query-contact-hardware-DR/fullstate/PPO/RTX/GUI/camera/deadline通过。自己的所有local transport sessions已自然结束，PID不是永久idle/active，以以后creationargv/root/save/EXIT/实际锁优先。

人类随后问三机协同/是否一机一expert，已说明建议按职责：210主线训练恢复；72双4090作新增训练候选容量，后按具体批准任务分配；249/3060冻结评测与retention/fair suite only。不是三台永久各绑expert，也不是72两个PPO已发。部署及问句无新72学习/双GPUworker/第二gatePPO/S8或预算批准。LaptopGPU仍暂停。新72仅在具体新task/source/native/fullrestore/resources/locks/原账边界准入并具备授权后安排学习，不凭此prompt自动开训。

此D unique stage4205677/tagtrial-20261015-host72-zonglin2-isolated-environment-deploy-started/object12989d73a473ece6d071752fff5ef57c82c82976已actualremote/all1348oldtags/tracked25核。后来copy/runtime/全部reader errors/source/closure/本monitor需ordinarysupplement，当前以之后actualHEAD/remote main/all1349tag originalpeels/trackedSHA为准，不能再record/tag/重造commit；pushfail只续existingobjects，不为Git重GPU/删除/改账。大tar/dumps/JSONL实际path-size-SHA索引原件保留，凭据不输出Git。后面的旧copy37248/extract active字段仅历史。

同mod4-10 ACTIVE/hourly/target01a07a2d-9036-7531-a012-692df9f56353不第二monitor/额外watcher或自动预算。健康unchanged/pending DONT_NOTIFY静默，不重复部署/双GPU passed通知。人类部署目标已闭合，原S5总plan仍未完，可继续原批准缺失scope准备；72不因此自动纳入学习。保留旧solecanonical1188000s/七extensions和原全部source/failure/预算/安全边界。后来的actual/newhuman优先。

以下旧完整prompt只追溯：
'''
dest=D/'MONITOR_ZONGLIN2_TWO_GPU_HEADLESS_DEPLOY_COMPLETE_AND_THREE_HOST_ROLES_ACTUAL_20261015.txt'
with dest.open('x',encoding='utf8',newline='\n') as f:f.write(prefix+cfg['prompt'])
print(json.dumps(dict(report=str(R/'ZONGLIN2_HUMAN_DEPLOYMENT_FINAL_ACTUAL.json'),monitor_prompt=str(dest),prompt_SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),known_local_owners_actual_CIM=cim)),flush=True)
