"""Append actual CPU preparation to the one existing heartbeat; no new monitor/runtime."""
from pathlib import Path
import json,time,hashlib,subprocess
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,value):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2))
def main():
 assert subprocess.check_output(['git','-C',str(W/'polar-rl-train'),'rev-parse','HEAD'],text=True).strip()=='6a5ab9d756f005b559ba718cecf95cdaf23d2c2e'
 p=R/'LATEST_H1_CLOSED24_FROZEN_PUBLIC04_SOURCE_COMPONENTS_CPU_PREPARED_ACTUAL.json';r=json.loads(p.read_bytes())
 assert r['passed_source_actor_and_original_clock_components_CPU'] and len(r['source_negative_cases'])==10 and len(r['adapter_negative_cases'])==18
 original=B/'NEXT_ACTUAL_H1_FINAL_NATIVE180_E3_FULL0OF96_SOURCE_RESIDUAL_V2_WORK_ORDER.json'
 wo=dict(epoch=time.time(),latest_component_report=dict(path=str(p),SHA=H(p)),previous_full_closed_source_residual_work_order=dict(path=str(original),SHA=H(original)),
   next_priority='Finish independent latest H1 closed24/644660 frozen package from exact original H1 environment, external zero twist, reward masks and phase source; actual resource/identity/lock/SDK/source CPU, unused own frozen native and full allrow CPU required. CPU components do not grant new paid production.',
   components_only_no_new_H1_frozen_target_package_or_dispatch=True,no_new_GPU_worker_GO_canonical_or_charge=True,
   original_source_negative_cases=r['source_negative_cases'],adapter_negative_cases=r['adapter_negative_cases'],fixture_302_controls_8env_only_not_physics=True,
   phase_module_sources_byteexact=True,source_GPU937_label_and_121update_label_historical_not_actual_current_owned24=True,
   E2_paid_behavior_hold_E3_paid_review_hold_unchanged=True,original_all_physical_guards_and_budget_unchanged=True,
   Git_before_this_CPU_supplement='6a5ab9d756f005b559ba718cecf95cdaf23d2c2e',prior_all_A_unique_and_ordinary_helpers_consumed=True,current_supplement_pending_until_actual_tools=True)
 put(B/'NEXT_LATEST_H1_PUBLIC04_FROZEN_SOURCE_COMPONENTS_CPU_ACTUAL_WORK_ORDER.json',wo)
 old=B/'MONITOR_H1_FINAL_E3_FULL_SOURCE_ACTUAL_ORDINARY_ONCE_V3.txt'
 prefix='''最新actual（本轮CPU准备，非新冻结或PPO）优先：A/reports/LATEST_H1_CLOSED24_FROZEN_PUBLIC04_SOURCE_COMPONENTS_CPU_PREPARED_ACTUAL.json与A/NEXT_LATEST_H1_PUBLIC04_FROZEN_SOURCE_COMPONENTS_CPU_ACTUAL_WORK_ORDER.json为新交接。A/h1_latest_closed24_frozen_public04_components_CPU_v1已实际用最新fe1709/全17Adam644660/owned24完整源通过sourceguard、10错phase/update/kind/Adam/profile/critic/shape/STD/runtimefinite/dtype负例；FrozenMean35类AST与既有原件exact、actor9含STD初末literalexact、无critic/optimizer/gate加载。原H1_public_request_phase_v1和takeoff_progress_phase_v2两文件byteSHA exact；8环境302control纯CPU fixture完整检100normal→80mode4→normal、selectedreset只同列phase和previousactual6、一次provider/whole6clip6、实际发布perenv0/4向量/onehot、18个tick/mode/device/shape/NaN/previousaction/reentrant/actualaction负例，CPU RNG不变0CUDA0optimizer。此是组件和源审，不是机器人轨迹/20krestore/3060完整包或新Task/native/full/技能资格。原源GPU210和121旧标签照留，真实当前owned24与Adam644660分列，未改原checkpoint。全部本机查找miss/权限拒绝/聚合输出截断和inline JSON Tensor序列化TypeError-V2 shape/dtype读取修复已在新报告保留，不冒GPU故障。
下一立即可做的是完成此最新H1的独立冻结完整target包，使用原takeoff_progress_environment_v2+原external_operator零twist+原h1_takeoff_progress_reward_v2七mask和原phase/readback/每callback contact-query-COM-hardware-source审查；fresh小环境不是20k源状态强塞。之后按实际249资源/当前签名desktop身份/MSVCRT/sourceSDKmanifestCPU、自己的unused frozen native→全rowCPU→unused full与严格flight/landing/recovery，不能复用旧20knative作新冻结技能或自动开paid窗。E2/E3 paid reviewhold不变，三4090本scope未新发paid，不说永久idle或全3PPO。
本轮开始实际GitHEAD6a5ab9d756f005b559ba718cecf95cdaf23d2c2e已remote/main/all1371旧tagobject-peel与全部文本/两个非UTF8日志完整bytes核；旧unique0001、ordinary7d82及6a5日志修复、全部旧archive/append helper已consume，绝不重run/record/tag/同commit。此新CPU组件/工作单/monitor/appreceipt用新的ordinary supplement helper append_latest_H1_public04_CPU_components_ordinary_once.py仅一次，lateractualHEAD若不再6a5不得重run/重commit，pushfail只已有objects。以后Git工具回执优先，不为把最终HEAD写回prompt无限补档。正常CPUprepared/健康pending静默DONT_NOTIFY，不把此CPU准备重复冒新物理结果通知；仅原约定的新完整FINAL/新冻结/实质修复/重大退化/新增人类必要动作通知。同一mod4-10 ACTIVE/hourly/原target不变，无新增watcher/预算。
以下原完整合同和已通知结果保留，所有pending和Git字段以lateractual优先：
'''
 prompt=prefix+old.read_text('utf8');q=B/'MONITOR_LATEST_H1_PUBLIC04_COMPONENTS_CPU_ACTUAL_V4.txt';put(q,prompt)
 args=json.loads((B/'AUTOMATION_UPDATE_H1_FINAL_E3_FULL_SOURCE_ORDINARY_ONCE_V3_ARGS.json').read_bytes());args['prompt']=prompt
 put(B/'AUTOMATION_UPDATE_LATEST_H1_PUBLIC04_COMPONENTS_CPU_ACTUAL_V4_ARGS.json',args)
 print(json.dumps(dict(work_order_prepared=True,one_existing_monitor_update_args_only=True,prompt_SHA=H(q),no_app_update_yet=True)),flush=True)
if __name__=='__main__':main()
