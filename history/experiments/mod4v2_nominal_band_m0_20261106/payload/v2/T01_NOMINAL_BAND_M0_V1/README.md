# R27：原M0在新名义地面带的实际单例通过——非鲁棒通廊资格

**520180已实际完成并通过原单例门槛。它没有修改M0、旧接触门，也没有推翻R26的最坏姿态/横偏通廊无候选结论。** 当前是名义实验，不是整个T01、95%可靠性、T36或实机资格；全36仍0/36。

## 冻结场景与必要区别

原[公开带实验定义](<../PUBLIC_NOMINAL_BAND_EXPERIMENT_V1/PLAN.json>)从R26已取得的无障碍源地面带[−1.7343287145,−0.9725199427]m取**几何中线Y=−1.353424328589362m**，不是按控制分数搜索路线。X沿原公开区间−9→−5.5m，原倾斜源floor3553，初始化地面Z约−.03542065646m（真实源平面，不是z0假板）。完整原CAD/P0、圆柱主胎.0625/.01、guide.015/.9、300N/60mm和未实测k2000/d3不改。

名义全311几何盒配每侧4cm可放入该带；但R26所声明±.1rad姿态和原±.2m横偏等的1.298668442m需求仍大于.761808772m带宽，**该鲁棒几何前置证明仍失败**。本轮明确停止把该先验最坏通廊当所有名义仿真的前置要求，另做名义实际实验；不是重新运行R26规划器、缩余量宣告其过筛或掩盖旧路失败。实验真实足迹单独旁观，不能上升为所有可能姿态的证明。

[协议](<PROTOCOL.json>)冻结后只运行唯一seed520180：0–2s站立、2–8s+.3m/s、8–12s停，yaw0；控制100Hz/物理.5ms implicitfast/Newton100，原逆名义PD→目标投影/D4→当前PD→signedDC→gain→同DC。新v2 K/trim、原coord_soft+C1/C2/120–4差分PD/整形/功率限制不变，未叠加失败的M1/M2/M3，不是M4。原T01 gates/windows逐项保留，scope字段明确nominal-only。先验站姿初始化不是自然摊卧起立。

## 实际结果

[完整小结果](<runs/v2_t01_nominal_band_m0_520180_001/result.json>)；job pwsh-778ad795bdb74774已收exit0，case及准备/归约不重开。

- complete=true，1200控制、24000真实物理步、fresh simulation model/FullDR各1，12s仿真/45.5548418s墙钟。rc0不单独作通过标准，实际16个check均true，case_screen_pass=true。
- **接触/姿态评分窗2–12s、20000物理点**：左右主轮>1N支持99.82%/99.85%，即19964/19970点；whole all-positive-normal-sum≤1N点0，guide支持0、hard接触0。不是“每轮100%”、成功概率或实机力标定。
- pitch峰.01264144559rad/RMS.00426183577，roll峰.00614466377rad/RMS.00448897088；closure最大4.06978319e−6m、mimic9.84828721e−6rad。
- 稳态速度RMSE.01038095999m/s，行程1.832455916m、最大横偏.01016064988m，末段9–12s停止vx RMS.01286890088m/s。结果中的stand_xy_drift/stand_vx是统一记录的全运动统计，本slow profile不使用站立专属门，不能把它们解释为停车窗口漂移。
- 全12s私有两阶段DC旁观24000行/1200完整窗口：原两次clip六轴改写计数全0，第二clip到保持输出变化0。真实仿真d.ctrl不是测得硬件输出扭矩，也不是轨限占用/电流/热/物理送达证明；不回填早期未记录case。
- 全12s **100Hz** 私有311几何缓存XY检查在观察带内，最大超量0；姿态观察界内，full-run RPY峰[.0301327282,.0126414456,.0203799030]rad。几何缓存为末PRE、age.5ms，root RPY为POST；无额外forward/step，**不是2kHz全扫掠或动态全域证明**。
- 公共时间观察1198实际插值帧/2启动未知；alpha、误差界、输出扭矩标定、硬件同步资格仍未制造，force_input_ready=false，controller/proxy连接0。

不同Y/地面路径、真实初始化地面高度及新增私有观察意味着这不是旧正向失败的严格单因素因果对照。它提供同一未改M0在**新声明名义场景**可达原单例门的证据；旧路/M1–M3的失败全部保留。

## 原中心岛候选为何未执行

[首次源筛选](<../PUBLIC_UPPERDECK_CORRIDOR_V1/RESULT.json>)返回NO_PUBLIC_ANCHOR_HORIZONTAL_SOURCE_FACE，6个候选凸包/LP0/物理0。其锚点要求1µm内匹配公开level，比源碰撞棱柱约20µm外扩更严格；原结果/源码保留。

[唯一有界源datum核对](<../PUBLIC_UPPERDECK_CORRIDOR_V1/DATUM_INSPECT001/RESULT.json>)只查公开锚点(−1.5,0)与原候选中点(0,0)，一遍源解析/24凸包/LP0/模型物理0：前者rm_col_46841顶面.40002m，比公开.40000000596高19.994µm；后者最高顶面仅.19002m（另有.15002、.00002、−.29998），**不是连贯.4m台面**。因此不作坐标/容差搜索凑过，不执行中心岛520170；其准备器只是源码、无派生协议目录。520160同样保持未用。

## 软件prefix与数据预算

[原准备器](<../prepare_nominal_band_case_once.py>)复用未执行R26准备器时，硬编码meta续行17空格、真实源16空格，派生compile在目录/模型/物理之前失败；[原日志](<../prepare_nominal_band_case_001.log>)与[回执](<../NOMINAL_BAND_PREP_ATTEMPT001.json>)保留。[唯一恢复](<../prepare_nominal_band_case_recovery001.py>)只把2个literal的3条meta续行对齐真实语义行，未改模型/逻辑/数字/门槛；[DERIVATION](<DERIVATION.json>)与[成功log](<../prepare_nominal_band_case_recovery001.log>)记录后才运行上述唯一case。

三个大raw的SHA/bytes/行数均由producer边写边记，见结果收据。**本新raw尚未额外归约/读取，禁止为归档或例行QA重读/hash；所有旧once预算仍已消费。** 本轮无新代理、SDK静态查询、硬件/刷写/GPU/SSH/PPO/旧QA。

## 下一步

保持同一M0/场景/原门槛，另立冻结协议，先一个新seed名义站立，再有界新seed TRAIN DR站立/低速筛选；原旧路DR520112–115继续未消费/暂停，不当作新场景已验证。新TRAIN也不构成独立可靠性/T36资格。R27后累计7个v2名义例、8400控制/168000真实物理步；总体0/36、Goal保持active。
