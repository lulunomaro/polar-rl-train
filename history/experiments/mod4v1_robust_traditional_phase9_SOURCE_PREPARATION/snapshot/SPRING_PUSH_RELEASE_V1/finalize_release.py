"""Saved-result/source-only close. Does not import core/test/model or rerun QA."""
from pathlib import Path
import ast,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent

def load(n):return json.loads((O/n).read_bytes())
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(n,x):
 with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
U=load('UNIT_RESULT.json');E=load('ENTRY_RESULT.json');P=load('ENTRY_REPAIR_PARSE.json');S=load('SOURCE_LOCK.json')
assert U['status']=='PASS_NEW_500X3_SYNTHETIC_NOT_PHY'and U['checks']==9129 and U['error']is None
assert U['Geometry_wheel_kinematics_calls']==84 and U['NominalModel_FK']==0 and U['frames_each']==500
assert E['status']=='PASS_ACTUAL_ENTRY_HELP_AND_FAKE_PRELOOP_ONLY_NOT_MODEL_ADMISSION'and E['checks']==26 and E['error']is None
assert E['counts']['Geometry_wheel_kinematics']==0 and E['typed_binding_cases']+U['typed_cases']==14
refs=[]
for r in S['files']:
 actual=rec(R/r['relative']);assert actual['SHA']==r['SHA']and actual['bytes']==r['bytes'];refs.append(actual)
assert rec(O/'controller.py')['SHA']==U['core_SHA']==P['core_SHA']=='8d59143b961e1ff93e284cd81be8070508d580509985aa41e3d26db7ab4e8765'
assert rec(O/'run_unit_once.py')['SHA']==U['source_SHA']
assert rec(O/'run_manual_spring_push_v1.py')['SHA']==E['entry_SHA']==P['entry_SHA']
assert rec(O/'run_entry_once_v2.py')['SHA']==E['harness_SHA']==P['new_SHA']
assert rec(O/'run_entry_once.py')['SHA']==P['old_SHA']==rec(O/'entry_parse_attempt_001/run_entry_once.py')['SHA']
assert (O/'run_entry_once_v2.py').read_bytes().replace(b'__code__ and',b'__code__and',1)==(O/'run_entry_once.py').read_bytes()
old=ast.parse((R/'run_manual_position_v4.py').read_text(encoding='utf-8'));new=ast.parse((O/'run_manual_spring_push_v1.py').read_text(encoding='utf-8'))
def main(t):return next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='main')
a,b=main(old),main(new);oldfor=next(n for n in ast.walk(a)if isinstance(n,ast.For));newfor=next(n for n in ast.walk(b)if isinstance(n,ast.For));assert ast.dump(oldfor)==ast.dump(newfor)
protected=('plant','dr','drmeta','complete','hard','guide','peak','final','progress','main_pass','crossed','next_free','local_pass')
def selected(t):return{n.targets[0].id:ast.dump(n)for n in ast.walk(t)if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in protected}
assert selected(a)==selected(b)
put('ENTRY_AST_FINAL.json',dict(status='PASS_CURRENT_ENTRY_STATIC_AST',entry=rec(O/'run_manual_spring_push_v1.py'),original=rec(R/'run_manual_position_v4.py'),loop_AST_identical=True,original_constructor_DR_and_grade_gate_expressions_identical=list(protected),core_unchanged=True,result_schema_actual_hop_enabled=True))
report='''# Spring push release：新synthetic与受控entry零步结果

**已完成新数学/源码/受控preloop验证；不是full-model、DR、驱动或PHY准入，不自动物理。**

## 实际功能与API
- 父core只在实际trigger后的push窗口临时以新dict/新tau副本加正tauGas，super一次，finally还原g/end；不修改物理spring、原gain、air h、轮/事件策略。
- 数据是已封SPRING_PUSH_DECOMPOSITION_V1/ENDPOINTS.json：SHA 1b47bb7d75205c907f9116cb658adbb2922e82decee2c9b19c2fab8d86db762e。FF_new=old+tauGas；不是负counter，静态端点近似不等实际DR去弹簧。
- 新entry在真实plant构造前核data/helper SHA、public/gain来源、实际loaded q/tau/absolute pose；默认off不读取补偿table，enabled构造参数为start_gas_tau6/end_gas_tau6。

## 一次新unit事实（不重放旧600/436k或数学27FK）
- BasePosition/NewDefaultDisabled/NewEnabled各500同样sensor-only帧；9129 checks/0；实际phase为101 supported approach、14 push、25 predicted flight、360 capture，没有硬编码push帧数。
- 500默认off的旧tau、legacy log、ground ref/state与observer flags逐bit相同。True模式目标、phase/guards/observer不变；只push按原FF+PD/32clip/roll/yaw/wheel/final40原式对照，最大误差0Nm，push轮同输入bit一致。
- 非push enabled结果在这组相同固定输入下也bit一致；这不表示不同真实闭环trajectory的flight/capture输出相同。原方程相同与闭环状态相同分开。
- 首push1.01s此前launched=False但已applied；g/end identity、所有原gain array bytes不变，ground tau_eq未被overlay alias污染；原trigger guard和inner exception的finally恢复均核过。
- 实际旧Geometry.wheel_kinematics84次≤128，内部planar pose420另记；NominalModel FK0、MuJoCo0。oracle复用已有J，没有增加geometry查询。nondiagnostic wall timer固定0，仅比较math，不作WCET结论。

## actual entry与失败如实保留
- ENTRY首次harness在解析期因第67行__code__and连写失败，尚无main/help/ctor/model执行；原source/log/ENTRY_FIRST_FAILURE与快照保留。
- 父明确批准仅一空格修复，另存run_entry_once_v2.py；先AST parse并验证逆向逐字节=原失败源码，再一次启动原预算，没有重跑unit/数学/core。
- 实际执行new main --help一次、default-off/on两个真实新controller构造与preloop；26 checks/0，5绑定失败案例。fake plant/DR各2，loop/packet/actuator/geometry/SDK/NominalFK全0。
- 真实loaders/geometry/controller/estimate构造/StreamedRows已走；plant/DR/Bounds与large-asset manifest明确fake，trace在首for-loop前停止。EXPECTED ERROR与空trace/physics producer prefix保留，不制造result.json trial。
- Manifest实际写入完整cfg、kind/requested/dataSHA与source records；off dataSHA=None，on为实际缓存SHA。result的actual-hop enabled字段只作AST验证，本轮未运行result结算。
- 所有kind固定NEW_NOMINAL_SPRING_RELEASE_PUSH_ONLY_TRAIN；relative_V3_push_flight_capture_equations_unchanged=False，only_push_nominal_spring_ff_changed=True，flight_and_capture_equations_unchanged=True；后两者仅说方程范围。

## 交父边界
- loop、good/main/local与plant/DR构造表达式最终AST相同；22个锁定source字节未变。新core/entry/binding/unit SHA见RECEIPT.json，输入配置仅synthetic覆盖，不是父将冻结的物理协议。
- 数学cache、core与本次source/results转只读；等待父独立review、sourcefreeze和真正名义准入。没有PHY、旧QA、Git、新agent或goal操作。
'''
def linkdocs(text):
 refs={'SPRING_PUSH_DECOMPOSITION_V1/ENDPOINTS.json':R/'SPRING_PUSH_DECOMPOSITION_V1/ENDPOINTS.json'}
 refs.update({n:O/n for n in('run_entry_once_v2.py','run_entry_once.py','ENTRY_FIRST_FAILURE.json','ENTRY_REPAIR_PARSE.json','ENTRY_AST_FINAL.json','ENTRY_AST.json','ENTRY_RESULT.json','RECEIPT.json','READ_ERRORS.json','entry_001.log','entry_002.log')})
 text=text.replace('ENTRY_FIRST_FAILURE与','ENTRY_FIRST_FAILURE.json与')
 for label,p in sorted(refs.items(),key=lambda x:-len(x[0])):text=text.replace(label,'['+label+'](<'+p.resolve().as_posix()+'>)')
 return text
with(O/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write(linkdocs(report))
errors='''# 原始错误/修订记录
- READ_ERRORS.json保留两次误猜旧文件名not-found，后按真实import定位；不是已执行单测失败。
- entry_pretest_metadata_01保留生成后的metadata草稿；第一次entry运行前补显式manifest.config=cfg，并同步生成器。未改core/loop/控制数学。
- entry_001.log与entry_parse_attempt_001保留原harness SyntaxError；没有任何main/help/ctor/模型调用，unit PASS未改。
- 父批准仅增加一个空格，新v2源码可逆字节证明存ENTRY_REPAIR_PARSE.json；原失败源码不覆盖。v2执行PASS，日志entry_002.log。
- 复制后的v2首次edit被文件观察规则要求先read，未改文件；read后执行完全相同的空格替换。不是sandbox异常或测试执行。
- ENTRY_AST.json为最初metadata草稿的静态记录；当前最终entry的SHA与静态证明以ENTRY_AST_FINAL.json/RECEIPT为准，不冒称草稿已执行。
'''
with(O/'ERROR_REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write(linkdocs(errors))
primary=[rec(O/n)for n in('controller.py','binding.py','run_manual_spring_push_v1.py','PREEXEC_UNIT_PLAN.json','SOURCE_LOCK.json','UNIT_RESULT.json','ENTRY_RESULT.json','ENTRY_AST_FINAL.json','ENTRY_FIRST_FAILURE.json','ENTRY_REPAIR_PARSE.json','run_unit_once.py','run_entry_once.py','run_entry_once_v2.py','REPORT.md','ERROR_REPORT.md')]
receipt=dict(status='SEALED_NEW_RELEASE_SYNTHETIC_AND_ACTUAL_FAKE_PRELOOP_ONLY_NOT_PHY_ADMISSION',unit_checks=9129,entry_checks=26,main_frames_each=500,phase_counts=U['phase_counts'],Geometry_calls_total=84,NominalModel_FK=0,MuJoCo_boot_forward_RNE_integrator=0,typed_cases_total=14,inner_exception_extra_case=1,first_entry_parser_failure_retained=True,only_one_approved_space_repair=True,original_22_sources_unchanged=refs,primaries=primary,data=rec(R/'SPRING_PUSH_DECOMPOSITION_V1/ENDPOINTS.json'),real_model_admission=False,real_DR_samples=0,automatic_PHY=False,independent_parent_review_required=True)
put('RECEIPT.json',receipt)
print(json.dumps(dict(status=receipt['status'],core=rec(O/'controller.py'),entry=rec(O/'run_manual_spring_push_v1.py'),binding=rec(O/'binding.py'),unit=rec(O/'UNIT_RESULT.json'),entry_result=rec(O/'ENTRY_RESULT.json'),report=rec(O/'REPORT.md'),receipt=rec(O/'RECEIPT.json'),old_sources_unchanged=len(refs)),indent=2))
