# MOD4v1 D0限位：最初产出溯源与截图姿态事实核查

## 结论

1. **当前资产确实带着继承的有限operating ranges；最初MOD4v1增强没有重新核定机械全可达域。** 当时static PASS验证的是“与旧资产限位相同”，不是“CAD/实体机械限位正确”。
2. **存在明确收紧层：400N wrapper把左右gas_slide上界从底层约+35.203334mm覆盖成+20.639440mm，收紧14.563894mm；11月1日enhancement原样继承。**
3. **按当前joint坐标，这张图对应右gas_slide超上界约8.153909mm，不是超下界。** 当前MOD4v1的右rocker/knee仍在range内；更早旧MJCF的两个上界更窄，确实也会挡这幅姿态。两代模型需要区分。
4. 用户明确说明图示姿态在实体机械上可达；本轮证据独立确认的是软件约束/代数姿态/生成谱系。没有运行实体测量或CAD全装配碰撞/行程验收；也未定位截图确切UI程序，因此不把低闭链残差、勾选框或静态圆交点当作全机械认证。
5. 本轮**未改任何运行资产、关节range、训练source、checkpoint、Registry或预算，未启动训练/动力学/GUI/IsaacSDK/GPU**。下一修复应在新版本中区分真实机械界与训练操作窗，并让MJCF/USD/contract/重置IK一致，不通过扩大所有关节或关掉被动限位处理。

## A. 最初MOD4v1产出时发生了什么

本session可恢复开头是“将已产出的MOD4v1适配所有冻结专家”的归一化任务。更早增强产出情况从原构建回执、保留baseline、源代码和归档说明恢复；不把这些摘要冒称逐字用户对话。项目文档记忆也有旧静态对齐检查，其边界说明与原产物一致。

- [BUILD_RECEIPT:3–8](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/BUILD_RECEIPT.json#L3-L8>)：开始UTC `2026-11-01T13:52:22.236219Z`，即北京时间 **2026-11-01 21:52:22**。输入是qualified240 400N50包的assets；wrapper SHA **bce9a7740fd9a2e2252d34a09c1fef7dab70e2a65f9d0ee2e422cec5f12c60e4**，底层source_700N SHA **694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87**，旧contract SHA **517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49**。
- [最初README:16–32](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/README.md#L16-L32>)：修独立层米/千克/Z-up元数据、已知电机质量与对应COM/惯量、solver默认32/4、封装独立USD；**所有关节端点/轴/限位/驱动/armature、气弹簧行程明确保留**。实际mass14.29414kg仍非整车实称，组级CAD标定当时未全完成。
- [build_enhanced_usd.py:33–41](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/build_enhanced_usd.py#L33-L41>)复制baseline并deepcopy契约，随后flatten；没有重算上述限位。
- [VALIDATION:36–39](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/VALIDATION.json#L36-L39>)为`all36_joint_types_frames_limits_drives_armatures_unchanged=true`；[最初README:56–58](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/README.md#L56-L58>)也限定18项为静态检查、target PhysX/实机未验证。
- [BUILD_RECEIPT:24–30](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/BUILD_RECEIPT.json#L24-L30>)产出USD **2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3**、contract **bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755**。后续归一化沿用这一对，不意味着限位已独立机械认证。

## B. 当前MJCF/USD具体边界

左右相同；当前contract是SI，USD转动边界是degree、v1长度单位m。

| joint | 当前下界 | 当前上界 | 当前启用语义 |
|---|---:|---:|---|
| rocker_pin | −0.782777718496 rad | +0.705741736495 rad | USD有限lower/upper、jointEnabled默认true；MJCF limited=true |
| knee | −0.761328703012 rad | +0.720233100662 rad | 同上 |
| gas_slide | −0.0267046843609 m | +0.020639440248416612 m | 同上 |

证据：[当前contract:1008–1173及1368–1533](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets/import_contract.json#L1008-L1533>)；[当前31体MuJoCo scene:324–510](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/contract_parity_mujoco_v1/scene.xml#L324-L510>)。既有pxr LoadNone只读属性栈给USD rocker约[−44.849861145,+40.436023712]deg、knee[−43.620922089,+41.266315460]deg；gas float边界[−.026704683899879456,+.020639440044760704]。无独立limitEnabled author值。这六处不是把原USD disabled/unbounded重新有限化。

**直接的gas上界覆盖证据：** [baseline/robot.usd:10–18](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/baseline/robot.usd#L10-L18>)同时写`stiffness=2000`和`physics:upperLimit=.020639440248416612`。其source_700N层原upper为+.03520333394408226，lower沿用。数值上界内收 **14.5638936957mm**；不能把这一层归因于后来11月1日enhancement。当前gas目标位置[contract:8718–8727](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets/import_contract.json#L8718-L8727>)约.22063944109、k2000/d3，是力学配置，不能独立证明物理行程。

## C. 截图输入条件重建：究竟挡在哪里

用户截图显示hip_L=0、crank_L=.108050，hip_R=−.33050、crank_R=.357203 rad；按[同源kinematics:21–36](<F:/RMPOLAR-RL/traditional_control_20261101/kinematics.py#L21-L36>)，difference=crank−hip，故左右difference=.108050/.687703。只提取纯代数函数与[neutral骨架:120–205](<F:/RMPOLAR-RL/traditional_control_20261101/reports/model_manifest.json#L120-L205>)进行一次静态NumPy反解，未import MuJoCo或运行forward/step。

| 右侧量 | 图示输入反解 | 当前MOD4v1上界 | 对比 |
|---|---:|---:|---|
| rocker_pin | +.575610178081 rad | +.705741736495 rad | 未到上界 |
| knee | +.584232486030 rad | +.720233100662 rad | 未到上界 |
| gas_slide | +.0287933493553 m | +.0206394400448 m（USDfloat） | **超上界8.153909mm** |

左侧rocker=.0907277849563、knee=.0908165340719 rad、gas=+.00438354638115m，均在当前range内。右gas定义是`|T−S|−neutral_eye_length`：中性眼距 **179.360558910mm**，图示右实际眼距 **208.153908265mm**；当前upper映射为约 **200mm**眼距。当前模型因此先在200mm端裁掉这幅姿态，方向是**伸长上限**。

复算L0=290.287719/372.086187mm、theta0=−3.268618/−1.103425deg；假定直立机身/水平地/轮半径62.5mm几何落轮，root434.517188mm、左轮底82.201710/right0、腹底267.517188mm，均吻合截图舍入。滑块396.610mm到root实际434.517mm的37.907mm差与该几何落轮解释相符；这不是已确认UI的碰撞解算流程。

**两代MJCF区别：** 更早[robot_hifi.xml:443–505](<C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4/robot_hifi.xml#L443-L505>)右rocker/knee/gas上界仅.336793828442/.339258885370rad/.0167269302872m，分别挡住图示右姿态.238816349639rad/.244973600660rad/12.066419mm；[当前USD对齐MJCF:446–508](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mod4v1_usd_source_aligned.xml#L446-L508>)则只有右gas超界。**确切截图UI未定位，精确标题窗口查一次无匹配；候选view_joints.py标题不同、没有checkbox且落轮常数64.5mm，不冒认是截图程序。** checkbox究竟改jnt_limited还是range仍未取得源码证据。

## D. 更早约束来源：操作窗、机械止挡、力学候选要分开

- [早期build_mod4.py:19–23](<C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4_work/build_mod4.py#L19-L23>)明确称**operating envelope**；DIFF_RANGE=[−.25,.85]，非完整CAD机械运动界。[98–107](<C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4_work/build_mod4.py#L98-L107>)用151个configuration样本min/max，[213–225](<C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4_work/build_mod4.py#L213-L225>)写rocker/knee/gas的range。这个更早版本数值与当前不同，不能当成当前精确限位重写器。
- [同脚本89–91](<C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4_work/build_mod4.py#L89-L91>)把gas眼距150–200mm、50mm行程明确标为**可调仿真候选，非已验证MOD4硬件弹簧**。当前gas upper=.2−neutral_eye在几何上吻合，不把公式吻合升级为已找到当前生成意图或硬件止挡认证。
- [当前mechanical_stop:8787–8822](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets/import_contract.json#L8787-L8822>)来源署2026-09-12 SolidWorks B-Rep+MuJoCo反解；固定part145、首先接触part124/接近part134，只有低折一侧：rocker min−.7828277184955518、knee min−.7613787030122099rad、gas min−.02675468436086534m。**这里没有rocker/knee上界的CAD依据。** 当前下界相对这些记录内缩rocker/knee各50µrad、gas50µm；训练difference下限−1.0843比低折止挡−1.0863195404360622内缩.00201954rad。这是另一个方向的裕度，不能解释截图8.15mm的伸长上界冲突。
- [HANDOFF_ISAAC_FIX_V2:15–35](<C:/Users/lulu/Desktop/claude/mjcf/HANDOFF_ISAAC_FIX_V2.md#L15-L35>)曾记录统一.03混用rad/m、误放gas30mm的历史问题；建议区分角度与位移软裕度，并以真实B-Rep为机械界。其建议值并非当前50e−6实际写入理由的证据。
- 当前边界在9/12 fixed contract已存在；[9/13 make_rolling_contract.py:114–115与155–156](<C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/sources/remote/incoming/mod4_rolling_20260913/tools/make_rolling_contract.py#L114-L156>)又原样继承`limits_si`、`mechanical_stop/training_window`。当前rocker/knee上界精确采样来源、50e−6具体重写脚本/理由与截图UI身份仍为来源缺口，不填猜测。

## 修复边界与既有结果处置

优先重核真实gas伸长/压缩眼距、装配锚点、rocker/knee两侧真实CAD止挡和连续机构支路，再形成**独立新版本**。把机械硬界、训练操作窗、软裕度与400N力曲线分列；同步MJCF/USD/import_contract/IK校验和部署资产身份，不热换运行文件，不直接取消全部passive limits。

现有九专家/E3试验仍是旧2c/bae限位版本下的真实记录，保留全部模型/失败/成本/原分母，不把这次D0疑点写成旧试验已修好，也不再用旧operating limits冒充真实全机械可达证明。新增训练/大评测应先完成D0修复依据和新版本身份；本次仅事实核查，没有修复或重训。
