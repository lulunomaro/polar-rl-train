# T01 M3：完整参考静力偏置；3/3候选均未过接触门

## 本轮实际改动

- [控制器](<../controller_reference_full_static_ff_v1.py>)只撤销M2的“关节共同项删除”：完整保留名义静力reference变化的4关节偏置，轮前馈为0。原共同LQR**反馈**、120/4差分PD、C1/C2参考、K、整形、执行链及碰撞/评分数值不变；共同模型**前馈**明确新增。
- [单次准备](<../prepare_reference_full_static_ff_v1.py>)导出[独立runtime](<../runtime_reference_full_static_ff_v1.py>)和[唯一runner](<run_reference_full_static_ff_v1.py>)、[冻结协议](<PROTOCOL.json>)；源检查后创建新prefix，准备exit0、0模型/FK/物理，旧源与默认UI/runtime/BSP未改。
- M2最新[一次归约](<../T01_REFERENCE_STATIC_FF_V1/REDUCTION001/RESULT.json>)读新控制trace1200行、无物理/重放/FK；reference髋偏移峰0.220769rad，而最初静态设计仅±0.02rad。M2删去共同项峰0.575/0.731Nm。M3是恢复完整reference模型平衡变化，不是扫FF系数或K；动态收益未预先保证。
- [参考几何核对](<../T01_REFERENCE_STATIC_FF_V1/COMMON_REFERENCE_GEOMETRY001/RESULT.json>)只算6次纯pose：765点平均轮X偏2.970mm、Z偏-0.187mm；1199点X偏2.608mm、Z偏-0.154mm。证据不足以把“共同轮位漂移”列成新控制机制，未改CartIK。
- [实际API窄核对](<../PUBLIC_CONTROL_GEOMETRY_API_V1/RESULT.json>)真实geometry工厂1次、左右wheel API各1（内部pose共10）；与已存同名义点XZ/J/T0误差≤2.88e-13m/1.81e-11m·rad⁻¹/6.57e-11，0SDK模型/forward/积分。Y/Jy旧参考未存仍unknown；不是全域资格，也没重跑旧QA。

## 唯一M3物理结果

[520151完整结果](<runs/v2_t01_reference_full_static_ff_nominal_slow_520151_001/result.json>)：12s、1200控制、24000实际物理步，fresh模型与FullDR各1，wall63.5082s，完整结束/exit0。公开原正向起点-9,-1，2–8s为+.3m/s，其他时段站立/停车，非旧例重跑。

|指标|原基线|M2差分静力FF|M3完整静力FF|
|---|---:|---:|---:|
|左/右主轮>1N支持|91.570% / 98.035%|92.210% / 98.715%|92.545% / 98.425%|
|全机法向和≤1N评分点|92|43|59|
|roll RMS rad|0.00941665|0.0210572|0.0209362|
|速度RMSE m/s|0.0406789|0.0420189|0.0411387|
|guide / hard|0 / 0|0 / 0|0 / 0|

M3的pitch峰0.0165086rad、roll峰0.0337912rad、行程1.65901m、横偏0.0383346m、最终停车vx RMS0.0135737m/s；所有非接触检查true。**EACH主轮≥95%与全机低支持零次两门仍false，case_screen_pass=false，未采用。** 59点全为孤立0.5ms，不称59次宏观腾空。

全12s/24000物理tick两级原DC改写6轴计数全0，第二DC到held值差0；这是本新例观测，不转填早期未记录例或硬件电流/温度/送达事实。实际d.ctrl不是实测输出轴力矩。

完整额外关节峰[2.53810,2.74951,1.38333,1.28188]Nm，轮0；共同项峰0.577386/0.733815Nm，实际共同和峰1.46763Nm。整体余量缩放1次/min0，完整reference映射差0。模型terms1201（含init）/内部纯FK10809不是独立物理case。FF累计16.4475s/平均13.7063ms/最大28.6465ms；未具100Hz墙钟或ARM WCET资格。

1198个公开信号实际插值观测，alpha/真实输出力矩标定/噪声与时钟误差预算仍缺，force_input_ready=false，没有回接力代理、FSM或控制器。300N/60mm气弹簧k2000/d3未实测，P0为原生圆柱胎版本，不称v1网格胎/PhysX/HIL通过。

## 阶段冻结与新发现

M1/M2/M3均失败，**3/3已消费**；不再第四个同类候选、不加尾段、不扩DR或扫系数。默认控制器保持原选择。六个v2名义例共7200控制/144000实际物理；总体仍0/36、T01进行中。

冻结后的[公开路径宏观源核查](<../PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1/README.md>)发现：名为flat_run的中心线并不保证双胎带等高。只读47282个真实源凸碰撞体，24个公开计划点、26个候选凸包计算、0物理/模型/raw。公开root x=-7.5m时，两名义胎中心下方源表面高差**89.45mm**（左+57.55mm、右-31.90mm）；-9/-5.5处仍有11.46mm横坡差。这不是接触微隙、实际走线或动力学唯一根因证明，但足以停止把该路线直接当“均匀平面”调参。

下一步先审公开CAD上双胎带/车体走廊是否适合T01。若更正计划，另建明确场景协议并保留旧失败，勿把换路线成绩称同路线控制器改善；3/3机制冻结不重置。

三份新大raw只用原producer边写bytes/lines/SHA收据；本M3尚无额外raw归约，不为归档读/hash。M2新trace的一次预算已消费；旧baseline/M1/reverse一次预算均继续封存。
