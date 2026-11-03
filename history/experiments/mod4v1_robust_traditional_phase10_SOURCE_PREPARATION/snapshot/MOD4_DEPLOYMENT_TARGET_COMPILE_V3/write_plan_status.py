"""Small saved-plan status only: no native tool, schema search, payload rehash or TU."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
load=lambda n:json.loads((O/n).read_bytes())
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def save(n,v):
 with(O/n).open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
p=load('RAW_TU_PLAN_01.json');g=load('PLAN_GATE_01.json');v=load('ARMASM_QUERY_DEFERRED.json')
assert len(p['translation_units'])==163 and not p['missing_TU_inputs']and not p['missing_declared_source_pins']
assert all(x['state']=='UNSTARTED'and x['effective_argv']is None and x['effective_flags']is None for x in p['translation_units'])
assert g['successful_prefix']==[]and g['failed_TU']is None and g['unstarted_TU_ids']==list(range(163))and not v['executed']
for r in p['source_refs']:
 now=rec(Path(r['path']));assert(now['bytes'],now['SHA'])==(r['bytes'],r['SHA'])
fields=['interw','Optim','oTime','SplitLS','OneElfS','Strict','EnumInt','PlainCh','wLevel','uThumb','uC99']
def vals(x):return{k:x.get(k)for k in fields}
tc=p['profiles']['target']['raw']['TargetArmAds']['Cads'];group_records=[]
for group in p['groups']:
 pr=p['profiles'][group['profile']]['raw']
 if not pr['present']:continue
 record=dict(group=group['name'],TU_count=group['TU_count'],option_profile=group['profile'],Cads_values=vals(pr['Cads']),VariousControls=pr['Cads'].get('VariousControls'))
 examples=[x for x in p['translation_units']if x['group']==group['name']and x['raw_file_profile']is not None]
 if examples:
  ex=examples[0];fp=p['profiles'][ex['raw_file_profile']]['raw']['Cads'];record['first_file_override']=dict(TU_id=ex['id'],name=ex['name'],profile=ex['raw_file_profile'],Cads_values=vals(fp),VariousControls=fp.get('VariousControls'))
 group_records.append(record)
facts=dict(status=g['status'],compiler_variant=p['compiler_variant'],project_declared_compiler=p['project_declared_compiler'],source_refs=p['source_refs'],raw_plan=rec(O/'RAW_TU_PLAN_01.json'),plan_gate=rec(O/'PLAN_GATE_01.json'),actual_target_Cads_values=vals(tc),actual_target_VariousControls=tc['VariousControls'],explicit_groups=group_records,option_profiles=len(p['profiles']),TU_count=163,C_TU=162,ASM_TU=1,all_TU_sources_exist=True,all_saved_source_pins_present=True,source_SHA_basis=p['current_source_SHA_policy'],effective_argv_frozen=False,unresolved=p['unresolved'],successful_prefix=[],failed_TU=None,failed_compile_diagnostic=None,unstarted_TU_ids=g['unstarted_TU_ids'],C_compile_invocations=0,ASM_compile_invocations=0,native_tool_invocations=0,armasm_version_query='DEFERRED_BUDGET_UNCONSUMED',schema_semantics_claim='NONE: parent reported installed XSD ranges only, not authoritative inheritance/selector meaning; child did not read/search it',stage1_or_V2_writes=False,full423_payload_rehash=False,link_UV_hooks_flash_PHY_oldQA_host40_Git_agents=0)
save('FACTS.json',facts)
md=['# V3：首轮compile前门槛停止','', '**状态：STOPPED_BEFORE_ANY_TU_UNRESOLVED_EFFECTIVE_PLAN。** 这是参数计划未决，不是编译器错误、ABI失败或许可证失败。','', '## 已实际保存', '- [原值链计划](<RAW_TU_PLAN_01.json>)：163 TU、71 profiles、target/group/file独立XML值与XPath、每TU来源pin/当前stat、候选隔离object/dependency路径。', '- [小facts](<FACTS.json>)、[门槛状态/163未启动ID](<PLAN_GATE_01.json>)；有效argv/flags全为null，未声称完成可运行argv冻结。', '- C162+ASM1，输入存在性全部通过、保存的来源SHA pin全部有；这些pin继承stage1记录，**不是本轮重新hash163/423 payload**。','', '## 真实覆盖值，不盲套target', '| 层级 | Optim | oTime | wLevel | EnumInt |', '|---|---:|---:|---:|---:|', '| target | '+ ' | '.join(str(tc.get(k))for k in ['Optim','oTime','wLevel','EnumInt'])+' |']
for r in group_records:
 c=r['Cads_values'];md.append('| '+r['group']+'（'+str(r['TU_count'])+' TU） | '+' | '.join(str(c.get(k))for k in ['Optim','oTime','wLevel','EnumInt'])+' |')
for r in group_records:
 if 'first_file_override'in r:
  e=r['first_file_override'];c=e['Cads_values'];md.append('| '+e['name']+' file override | '+' | '.join(str(c.get(k))for k in ['Optim','oTime','wLevel','EnumInt'])+' |')
md+=['', '- [target原文:312–339](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx#L312-L339>)；[HAL group:492–559](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx#L492-L559>)；[first file:565–614](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx#L565-L614>)。', '- 当前armcc短help定义-O0/-O1/-Otime等CLI，不定义这些uVision整数selector及空VariousControls继承；没有把0/1/2凭数字近似转成argv。', '- 父另报已安装XSD只见twoBits/sevenBits值域，尚非映射语义证据；子未额外搜/读schema，不将schema存在当已解决。', '- literal include/defines与RTE component声明分开保存。没有猜加_RTE_或新target RTE路径；direct variant的隐含宏/路径策略仍待明确。','', '## 预算和隔离', '- [163未启动列表](<PLAN_GATE_01.json>)：successful_prefix=[]，failed_TU=null，failed_compile_diagnostic=null；不是失败了163次。', '- C/ASM编译、native工具、link、UV/hook/flash、PHY/FK、host40/旧QA/Git/新agent全部0。', '- [armasm版本查询](<ARMASM_QUERY_DEFERRED.json>)也未执行，原一次预算保持未消耗。', '- 没有安装/生成RTE、补空头/stub、删music或改stage1/V2；没有根goal动作。', '- 父提供可审映射或另定显式diagnostic-override variant前，保持当前停止状态；不得冒称uVision继承exact或u4.422复现。','']
text='\n'.join(md);assert len(text.splitlines())<=70
with(O/'REPORT.md').open('x',encoding='utf-8')as f:f.write(text)
receipt=dict(status=g['status'],report=rec(O/'REPORT.md'),facts=rec(O/'FACTS.json'),raw_plan=rec(O/'RAW_TU_PLAN_01.json'),plan_gate=rec(O/'PLAN_GATE_01.json'),method=rec(O/'METHOD.md'),parser=rec(O/'inspect_plan_once.py'),parser_first_log=rec(O/'inspect_plan_01.log'),status_writer=rec(Path(__file__).resolve()),source_metadata_refs_checked=len(p['source_refs']),source_payload_hashes='STAGE1_SAVED_LINEAGE_ONLY; NOT_FRESH_TU_REHASH',C_compiles=0,ASM_compiles=0,native_tools=0,target_links=0,unstarted_count=163,effective_argv_frozen=False,ready_to_compile=False,old_stage1_and_V2_written=False)
save('RECEIPT.json',receipt)
print(json.dumps(dict(status=receipt['status'],report=receipt['report'],facts=receipt['facts'],receipt=rec(O/'RECEIPT.json'),C_compiles=0,ASM_compiles=0,native_tools=0,unstarted=163),ensure_ascii=False,indent=2))
