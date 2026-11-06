# R29：原M0只读观测副路——重力校正可用性与混合时标证据

**本轮没有修控制或换估计器喂actor。** 原估计器先算，原Estimate对象始终给原M0；同包独立审计副路只记录，不作第4个控制力矩候选，不续跑暂停520184/185或旧520112–115，不换seed搜通过。全36仍0/36。

## 原源码与新代码证据

- [副路](<../observer_audit_v1.py>)用原StateEstimator.update的AST生成，仅插入“清审计字段”和“quat_step前快照locals”两条诊断语句。[派生回执](<../OBSERVER_AUDIT_V1/SOURCE_DERIVATION.json>)核验删掉这两条后AST与原方法相同；原共享源码未改。副路单独持有状态/geometry拷贝，无DR参数/root/contact输入。
- [新接口测试](<../OBSERVER_AUDIT_V1/check001/RESULT.json>)128个新stub packet+1held view、1164断言：所有估计字段最大差0，回给caller是原对象，packet数组不变；12次重力权重0。简化geometry stub不是P0 FK，0SDK/model/FK/forward/physics/旧QA/raw；该check001已消费不重跑。
- [独立小源码复核](<../OBSERVER_CONTRACT_REVIEW_V1/NOTE.md>)仅复用原C，已正常停止：前7项预测到arrival，roll/omega/rates等保持source；C1用held roll+pred pitch/关节拼nB，确为混合epoch view/消费近似，并非已证“新回归bug”或既往DR失败唯一因。
- 旧DR held-roll误差本来已对齐sensor真值，故.0266rad RMS不应全部归“10ms内roll没外推”。重复packet从source缓存预测，不递归重积分或增加独立样本。

## 唯一实际新诊断例

[冻结协议](<PROTOCOL.json>)只允许seed520190 fullDR slow，原地面带、场景/机构/P0圆柱胎、300N/60mm、K/PD/整形/100Hz/.5msNewton100/原逆PD-D4-currentPD-twoDC/gates/windows保留；18个小源码身份pin。此新draw是观察原融合内部状态，不是重抽旧seed取得通过；旧失败仍失败，原后组仍暂停。

[完整小结果](<runs/v2_t01_observer_only_dr_520190_001/result.json>)：job pwsh-3db759858d1f4fd2已收exit0，12s/1200控制/24000真实物理/fresh model与FullDR各1，46.411181s墙钟。无额外model/forward/物理；副路有额外纯几何计算，未将其计成episodes或实时性证明。

- **1200原包/1200新fusion，所有副路估计字段相对原输出最大差0，副路错误0、控制连接0，observer_diagnostic_valid=true。** 只证明同包估计输出一致/旁路身份，未双跑主植物或控制器，不冒充独立系统因果复现实验。
- 真实D3抽到**0ms**，未改抽；mass/inertia×1.043692056，mu=.961290323，六motor gain独立。D4仍腿2.5ms/轮0；IMU均值孔径仍存在，所以不是所有延迟/通道异步都为0。
- 原性能门仍**FAIL**：左右主轮98.975%/99.365%（均过95%），whole all-positive-normal-sum≤1N **10个.5ms评分点**，guide/hard0；停车9–12s vx RMS **.053201171m/s > .05**。只有whole0/停车两门false，其他姿态/速度/闭链等原门均true。低速RMSE.060062213、行程2.109248825m、横偏.022901320m；评分窗pitch/roll峰.0355481/.0214061rad。
- 100Hz缓存311几何scope true只对已观察轨迹，R26鲁棒通廊证书仍false。force/标定/HW同步资格未制造。

## 真正新增的内部观测

原姿态互补更新为`quat_step(q, omega+accel_correction*confidence*error,dt)`；这里weight是原重力校正权重，**不是接触概率、独立force confidence或新KF资格**。

| 内部量 | 本例全12s |
|---|---:|
| 重力校正权重均值 | .159871645876 |
| 权重恰为0 | **564/1200 = 47%** |
| 重力创新模长均值 / 最大 | 1.23460271 / 208.82543855 m/s² |
| held-roll→arrival一阶差最大 | **0**（本例D3=0） |
| 速度KF内部加速度bias状态均值 | −.0785912884 m/s²（非独立传感器标定） |

创新最大值含启动过程，不将其当稳态水平。末段9–12s：weight均值.155070149，重力创新均值1.013021914/RMS1.101813099m/s²；原估计vx−command同epoch真值mean+.017929284/RMS.021838163m/s，pitch残差mean−.000338689/RMS.009102653rad，held-roll−sensor同epoch真值mean−.007209098/RMS.007661399rad。

这说明原融合在该真实DR轨迹中经常不给重力校正，同时存在停车缺口；**不证明校正门是唯一原因**，也不把confidence全置1/减掉真值残差。0ms D3下也有同类门失败，说明“10ms shared queue”不是这类失败的必要条件；与旧520183的不同draw不是严格单因素对照。混合epoch表达问题确实存在，但本例age0的roll一阶差为0，不能拿它替代融合/模型/噪声问题的证据。

所有统计随本次运行边走边记，真值只在runner评分诊断，未传入副路/actor；**新三条大raw未额外读/归约**，只用producer边写SHA/bytes/行数归档。所有旧once预算仍消费，暂停seed仍未执行。未发送硬件命令、未新建agent、未GPU/SSH/PPO/安装依赖；旧3控制机制仍冻结。

## 缺口与后续边界

T01名义站立/低速已有通过，但DR仍未正式收口，整体0/36、Goal active。新例后全v2累计8名义+3DR=11例、13200控制/264000真实物理步；不是95%可靠性/ARM WCET/硬件资格。

下一焦点是原重力创新门与现有D1噪声/均值/动态加速度契约的一致性，不再把时间表达缺口当唯一解释。旧M1/M2/M3、K和暂停seed不动；任何后续观测器修复需独立命名、预先冻结并用全新同条件协议验证，明确其会改变系统输入，绝不把有反馈的候选仍标成“只旁观/原系统不变”。禁止为新诊断回执继续微几何预检或重开旧raw/QA。
