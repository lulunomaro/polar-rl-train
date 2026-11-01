"""Existing health JSON/log + frozen LOCAL sources; no experiment/model replays."""
from pathlib import Path
import datetime as dt,hashlib,json,re,time
T=Path(__file__).resolve().parent;N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stamp(t):return dt.datetime.fromtimestamp(t,dt.timezone(dt.timedelta(hours=8))).isoformat()
j=read(R/'ROOT241_ACTUAL240_ONE_HUMAN_HEALTH_SNAPSHOT_RETURNED.json');assert j['passed_read'] and not j['authority']['canonical_None']
assert all(x['executing_not_original_zombie']for x in j['process_facts'].values())
assert read(R/'ROOT241_HUMAN_HEALTH_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
small={Path(x['path']).name:x['value']for x in j['files']};progress=small['LATEST_PROGRESS.json'];saved=small['latest_complete.json']
assert progress['new_PPO_updates']==56 and saved['actual_new_PPO_updates']==53 and saved['saved_iteration']==2103
assert saved['Adam_min']==saved['Adam_max']==42300 and saved['full_core_STD_optimizer_and_targetDR_saved']
text=re.sub(r'\x1b\[[0-9;]*m','',j['owned_log_tail']['UTF8']);metrics={}
for label in ('Learning iteration','Mean value loss','Mean surrogate loss','Mean action std','Mean episode length','Mean reward','Steps per second'):
 lines=[x.strip()for x in text.splitlines()if label in x];metrics[label]=lines[-1]if lines else None
V1=T/'W35_LATEST32481_FULL32S_AUTHORITY240_SOURCE_V1_20261101';V2=T/'W35_LATEST32481_FULL32S_AUTHORITY240_SOURCE_V2_20261101'
assert H(V1/'INDEX_AUTH240_V1_REJECTED_CPU_FROZEN.json')=='cb5de27e6c3ce707e20972b310ec6c0332210eaa84931005fbee73ebd15bb683'
assert H(V2/'INDEX_W35_LATEST32481_AUTH240_FROZEN.json')=='8236c3b520b2a79cc1f1f751ffc1982d70ce584ec96fbfc4de1ccfb21f33f704'
order=dict(epoch=time.time(),kind='CURRENT_ACTUAL241_HUMAN_ONE_HEALTH_SNAPSHOT_AND_FROZEN_W35_AUTH240',read_BJT=stamp(j['epoch']),
 run_id=j['run_id'],runtime_progress_and_save_publishing_normal_at_read=True,continuous_health_not_inferred=True,
 exact_known_owner_node_worker_live=True,new_PPO_updates=56,new_own_transitions=26880000,latest_progress_BJT=stamp(progress['epoch']),
 published_full_save=dict(saved,local_checkpoint_content_read=False),published_full_save_BJT=stamp(saved['epoch']),
 selected_stdout_metrics=metrics,selected_log_issue_count=j['selected_log_issue_count'],original_error_or_final_files_present=[x for x in small if 'ERROR'in x or x=='FINAL.json'],
 raw_original_termination_flag_occurrences=progress['original_jump_diagnostic']['terminations'],
 interpretation='Training processes/updates/saves are live and selected bounded log has no error/NaN evidence. Tilt and closure flags are frequent, overlap is possible; not independent population rates or stable-jump proof. 2mm remains per-env reset, not whole-batch halt.',
 flight_flags_and_absolute_root_height_not_geometric_success=True,no_training_model_raw_or_source_changes=True,
 checkpoint_byte_hash_decode_transfer_and_SDK_GPU_calls=0,all_ROOT_SSH_closed_SESSION_restored_lease_FREE=True,
 NEXT='Keep original240 save12:08:19.217688/nominal12:13:19/normal earliest11:58:19. Original normal+NEWformalCPU remain FROZEN_UNUSED; no repeat human241 reader or extra healthwatcher.',
 W35=dict(V1_rejected_frozen=str(V1),V2_frozen=str(V2),V2_INDEX_SHA='8236c3b520b2a79cc1f1f751ffc1982d70ce584ec96fbfc4de1ccfb21f33f704',
  actual_metadata_SDK_GPU_model_raw_remote_or_learning=0,full32s_20k_latest32481_case='SOURCE_READY_NOT_EXECUTED',
  components_byte_identical_to_base=True,V1_KeyError_GPU_UUID_preserved=True,
  actual240_GO_has_no_GPU_UUID=True,actual_GPU168_from_saved_launch_specs_and_public_schedule=True,
  authority_modes='Fresh exact240 owner PID/create/exe/fullargv/globalcwd/taskroot/fullGO/canonical match OR same240 actuallyclosed+freshCNone; old235 disallowed',
  original_model='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b/32481/17Adam651260',
  new_source_CPU='11AST/2authorityJSONcases/12refusals/Taskjoin, oldfixtures0; not skill qualification or SuperMimic',
  actual_case_pending_ROOT=True),ordinary240_supplement_only_no_new_tag=True)
put('CURRENT_ACTUAL241_HUMAN_HEALTH56_AND_W35_AUTH240_FROZEN_SUPPLEMENT.json',order)
note=f'''# 原240的一次人类健康查询与W35 authority240冻结源码补充

人类问“现在训练健康吗”。ROOT只执行一次新的有界只读目的：精确原owner/node/worker身份、当前canonical与完整原GO，既有进度/完整保存JSON、已有错误/结束JSON，原stdout最后64KiB一次。不读/hash/解码checkpoint或raw，不查询GPU空闲或其它PID，不改训练、源、预算或发signal。所有SSH已finally关闭/SESSION恢复/globalleaseFREE。

读取时刻 {stamp(j['epoch'])}：owner/node/worker真实身份均匹配且非Z存活；原240仍active。进度新增56PPO/26,880,000 own transitions，进度记录时刻 {stamp(progress['epoch'])}，读取时年龄14.385s。最近完整发布保存为53新PPO/iter2103/17Adam42300、22099474B、SHA {saved['SHA']}，保存时刻 {stamp(saved['epoch'])}，读取时年龄130.525s；仅使用原producer metadata，未读模型。stdout最新iter2106/value_loss.0959/surrogate-.0010/meanSTD.75，未发现所选异常词/NaN，错误或FINAL文件均无。

这支持运行/更新/保存正常，不等于策略已稳定。原终止标记累计bad_orientation62739、closure57019、time_out18869，其余记录项0。标记项可能重叠，不能当独立机器人成功率；2mm仍为每env重置，不整批停训。flight环境控制累计和绝对root高均不能代替双轮几何腾空、落台或270稳定验收。保留原训练，按12:08:19.217688保存、12:13:19收尾；normal最早11:58:19，原collector/NEWCPU仍未用。

同授权208子代理仅LOCALsource/CPU完成W35最新32481完整32s评测的authority240适配。V1因真实240 GO不含GPU_UUID出现KeyError；源/错误/once/拒绝INDEX全部冻结保留。独立V2从真实launch.specs和public schedule双核GPU168，完整GO继续精确匹配，没有补造或修改GO；owner PID/create/exe/argv/cwd与taskroot分scope核对。11AST、2内存JSON正例、12拒绝与Taskjoin通过，无oldfixture/model/raw/SDK/GPU/SSH/GO/Git调用。六个执行组件与已冻结base逐字相同，模型2d0/32481/651260、20k/32s、原命令奖励CAD70mm峰谷、400N50D0-D7、2mm/.01、3600/3780/3900不改。实际ROOT准入和完整技能评测仍待执行。

本次是已消费240 phase的普通补充，保留1514旧tag对象/peels，不record/retag240或新造241 GPU标签。所有新状态/原stdout选段/源错误和两个冻结目录完整追加，原训练不因Git动作受影响。
'''
with(R/'ACTUAL241_HEALTH_AND_W35_AUTH240_ORDINARY240_NOTE.md').open('x',encoding='utf8')as f:f.write(note)
prior=read(R/'AUTOMATION_ACTUAL240_FIRST_UPDATE_REQUEST.json')
header='''CURRENT_ACTUAL241_ONE_HUMAN_HEALTH56_AND_W35_AUTH240_SOURCE_READY_20261101. FIRST READ N240/reports/CURRENT_ACTUAL241_HUMAN_HEALTH56_AND_W35_AUTH240_FROZEN_SUPPLEMENT.json;N240=T/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101. Human requested onehealthread;ACTUAL241 CONSUMED/RETURNED0,2026-11-01T11:49:52.903888+08 exactowner/node/workerlive/current240canonical+fullGO matched,new56PPO/26880000owntransitions/latestprogress11:49:38.518898;publishedfullsave53updates/2103/17Adam42300/22099474B SHAcb36a97fd93c937ec084cf381734e85b7be14ae865af7424101f0a02fad0cc7a at11:47:42.379266,modelcontent0. Oneownedstdout64KiB:latest2106/value.0959/surrogate-.001/meanSTD.75,no selectedNaN/errorline andnoerrororFINALfiles. Thisishealthsnapshotnotcontinuousalive/skill;tiltflags62739/closure57019/timeout18869 mayoverlap/notpopulationrate,flightflags/rootheightnotjump success. Keephealthy240/nochanges/nohealthwatcher/noreread241forstatsGit. AllSSHfinallyclosed/SESSIONrestored/globalleaseFREE. Original240normal+NEWCPU stillFROZEN_UNUSED/earliest11:58:19.217688/save12:08:19.217688/nominal12:13:19.217688;only originalgates/onefee/1NEWformal+CPU,notoldonce. NewW35authority240V2SOURCE_READY N=T/W35_LATEST32481_FULL32S_AUTHORITY240_SOURCE_V2_20261101/INDEX_W35_LATEST32481_AUTH240_FROZEN.json SHA8236c3b520b2a79cc1f1f751ffc1982d70ce584ec96fbfc4de1ccfb21f33f704/18files. Sixexecutioncomponentsbyteidenticalbase40ede6,latest2d0/32481/651260/20k32s/originalCAD70pp/rewardcommands/400N50D0-D7/2mm.01/3600worker3780parent3900transport unchanged. V1rejectedINDEXcb5de27e6c3ce707e20972b310ec6c0332210eaa84931005fbee73ebd15bb683/siblingSOURCE_V1 KeyError preserved. Actual240 GO lacksGPU_UUID;V2 usesactual launch.specs+publicscheduleGPU168 dualproof without alteringGO,ReadyVALUE50069distinctmodelCPU5ec90. New11AST/2authorityJSON/12reject/TaskjoinPASS;modelrawSDKGPUremoteGO0/SOURCEonly,nophysical32s yet. FutureRootcaller usesactual240binding andfresh exactownerpid/create/exe/argv/globalcwd/taskroot/fullGO/canonical startedepoch,oractualsame240closed+freshCNone;neverold235 orfakeCNone. Newactualtargetmetadata/privateEX/resources/one model read/typedcase stillpendingRoot;nohotadd/secondwriter/newgrant. Same208LOCALsourceonly/no newnestedAstraSol. Git240 actualphase CONSUMED HEAD e75e3db3733d7af949d92b54ffdfede8a03ca54c/tagobjeb71fbfefa78be0572704cb2b812cee0e46154dd/1514tags,actualrefsfirst/neverretag. This241health+bothW35V1V2fullsourceerrors/receipts ORDINARY240appendonly;postGitnoHEADchasingreports. SameautomationACTIVE/hourly/originalchat/meaningfulchangesonly. Alloriginalcurrent240/budget/globalserial/physics/security gates belowretain;oldstatusesnotrerun directives.\n\n'''
request=dict(prior);request['prompt']=header+prior['prompt'];put('AUTOMATION_ACTUAL241_HEALTH_AND_W35_READY_UPDATE_REQUEST.json',request)
files=[T/'human241_240_one_read_health_once.py',Path(__file__).resolve(),R/'ROOT241_HUMAN_HEALTH_FRESH_LOCAL_EXACT_CIM.json',R/'ROOT241_NEW_HUMAN_HEALTH_READ_PURPOSE_ONCE_CONSUMED.json',R/'ROOT241_ACTUAL240_ONE_HUMAN_HEALTH_SNAPSHOT_RETURNED.json',R/'ROOT241_HUMAN_HEALTH_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',R/'CURRENT_ACTUAL241_HUMAN_HEALTH56_AND_W35_AUTH240_FROZEN_SUPPLEMENT.json',R/'ACTUAL241_HEALTH_AND_W35_AUTH240_ORDINARY240_NOTE.md',R/'AUTOMATION_ACTUAL241_HEALTH_AND_W35_READY_UPDATE_REQUEST.json',R/'AUTOMATION_ACTUAL241_HEALTH_AND_W35_READY_UPDATE_RECEIPT.json']
put('CAPTURE241_ORDINARY240_FROZEN_SCOPE.json',dict(epoch=time.time(),files=[str(p)for p in files],roots=[str(V1),str(V2)],
 automation_request_path=str(R/'AUTOMATION_ACTUAL241_HEALTH_AND_W35_READY_UPDATE_REQUEST.json'),
 scope='Ordinary240 supplement, no newtag/experiment replay/modelrawGPU reads',pending=['No W35 actual targetmetadata/SDK/eval/Pi','240normalclosing/fullformalCPU pendingoriginalgate']))
print(json.dumps(dict(passed=True,read_BJT=stamp(j['epoch']),new_PPO_updates=56,new_own_transitions=26880000,model_reads=0,W35_source_ready_only=True)))
