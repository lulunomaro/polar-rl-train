"""Record completed R25 evidence once; preserve all36 rows and prior stages."""
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'TERRAIN_ADAPTATION_TASKS_V2.md'
text=p.read_text(encoding='utf-8');lines=text.splitlines()
if '| Round25新增M3 |'in text:raise RuntimeError('R25 ledger already updated,do not replay')
updates={
'当前动作':'**Round25唯一M3完成，原接触门仍失败；M1/M2/M3=3/3冻结、不采用、不追加第4机制。** [M3代码与实际结果](<T01_REFERENCE_FULL_STATIC_FF_V1/README.md>)保留完整reference名义静力共同项；共同LQR反馈/K/PD/整形/执行链/gate均未改。新[公开路线宏观源证据](<PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1/README.md>)显示flat_run双胎带并非均匀平面：公开x=-7.5m时名义胎中心地面高差89.45mm。先核计划/测试任务域，不再在未核双胎带走廊上堆参数。默认runtime/UI/BSP不变，四TRAIN DR暂停',
'当前物理job':'**无；M3 pwsh-ab134f8e920a4117已收exit0，不重收完成通知。** 六个v2名义例累计7200控制/144000实际物理，520151已消费，不重开case/准备；M2新1200行一次归约已消费。无硬件/GPU/旧QA；M3大raw只保留producer收据、未额外归约',
'下一实质动作':'**3/3控制机制已冻结，先审公开CAD的双胎带/车体走廊，纠正把flat_run标签当均匀平面的任务域假设。** 新源核查只24个宏观计划点/26候选凸包，非接触微隙探针。若更正计划，另立明确场景协议、保留旧路全部失败，不将换路线成绩冒充同条件控制器改善，不把机制计数清零或追加M4。未改路/模型/gate；Fn/alpha/标定/预算仍不闭环，全36仍0/36',
'v2失败驱动机制计数':'**M1/M2/M3已实测3/最多3，全部原接触筛选失败、均未采用，暂停同类参数尝试。** M1支持91.640/98.160%、whole84；M2差分静力92.210/98.715%、43；M3完整静力92.545/98.425%、59且roll RMS .0209362仍比原.00941665差。C的9.51%对角化设计未物理跑，不作为另一机制；默认控制保留。rc0/低支持减少不等于通过',
'子代理':'Round25仅复用原C完成[实际API同名义点核对](<PUBLIC_CONTROL_GEOMETRY_API_V1/RESULT.json>)，真实factory1/左右wheel API各1(内部pose共10)，与已保存P0 XZ/J/T0差≤2.88e-13m/1.81e-11m·rad⁻¹/6.57e-11，0模型/MjData/forward/积分/静力DARE/旧QA；Y/Jy无旧参考仍unknown。此前Round24因SDK约束跳过的核对现在明确单独完成，不扩全域/动态结论。C/E4均已正常停止，新agent0；旧CONTACT三姿态/14stub/83断言/设计计算不重开'
}
seen={k:0 for k in updates};out=[]
for line in lines:
 for k,v in updates.items():
  if line.startswith('| '+k+' |'):
   line='| '+k+' | '+v+' |';seen[k]+=1;break
 if line.startswith('| 本轮FF代价/归档边界 |'):
  line=line.replace('本M2新trace尚未额外归约','Round25已完成[本M2新控制trace唯一归约](<T01_REFERENCE_STATIC_FF_V1/REDUCTION001/RESULT.json>)：1200行、0重放/FK/物理、q与packet差5.55e-17rad、reference髋峰.220769rad，matched roll误差RMS.000740743rad，7–8s集中37/43低支持点；不再读该raw')
 if line.startswith('| T01 |'):
  line=line.replace('进行中：v2站立过；低速承载未过，DR暂停','进行中：站立过/低速承载未过；3/3冻结，先核实际双胎带计划，DR暂停')
 out.append(line)
 if line.startswith('| 当前动作 |'):
  out += [
   '| Round25新增M3 | [520151结果](<T01_REFERENCE_FULL_STATIC_FF_V1/runs/v2_t01_reference_full_static_ff_nominal_slow_520151_001/result.json>)：12s/1200控制/24000物理/63.5082s墙钟/fresh模型与FullDR各1。非接触全true，左/右92.545/98.425%、whole59个孤立.5ms点、guide/hard0，两个原接触gate false/case_screen_pass=false；未采用。全12s两DC改写0，完整FF额外四关节峰[2.5381,2.7495,1.3833,1.2819]Nm，保留共同项峰.577386/.733815Nm，映射差0；FK10809/terms1201非独立例，FF平均13.7063ms/max28.6465ms未获墙钟实时/ARM WCET。M3尚未raw额外归约 |',
   '| Round25路线源证据 | [宏观高度结果](<PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1/RETRY001/RESULT.json>)：只读真实47282源凸碰撞体，24公开计划胎带点、26候选凸包/无unknown、0模型/物理/raw，无改图或actor回流；root x=-9/-8/-7.5/-5.5的左右胎中心源表面差11.459/25.194/89.450/11.459mm。x=-7.5左z+.0575542、右-.0318954m；不是实际轨迹或动态低支持唯一原因，却说明该中心线未保证均匀平面。首次6顶点假设失败在0高度查询，原prefix保留；一次结构根因诊断证实6..420顶点，再唯一恢复到现有SciPy凸包，未盲重试 |',
   '| Round25局部几何 | [6次纯pose](<T01_REFERENCE_STATIC_FF_V1/COMMON_REFERENCE_GEOMETRY001/RESULT.json>)仅用新M2已归约小记录765/1199，0原raw/模型/物理。平均关节不变但平均轮X漂2.970/2.608mm、Z-.187/-.154mm；不足以单凭此上CartIK，未增加该控制机制 |',
   '| Round25 Git状态 | 本实际代码/M3失败/路线源软件prefix与确定恢复/一次M2归约待唯一trial收口；下方533为上轮已完成cutoff，不将当前文件冒充已推送 |'
  ]
assert all(v==1 for v in seen.values()),seen
p.write_text('\n'.join(out)+'\n',encoding='utf-8')
print('R25_LEDGER_UPDATED_0_OF36_3OF3_FROZEN_SOURCE_ROUTE_SCOPE_FIRST')
