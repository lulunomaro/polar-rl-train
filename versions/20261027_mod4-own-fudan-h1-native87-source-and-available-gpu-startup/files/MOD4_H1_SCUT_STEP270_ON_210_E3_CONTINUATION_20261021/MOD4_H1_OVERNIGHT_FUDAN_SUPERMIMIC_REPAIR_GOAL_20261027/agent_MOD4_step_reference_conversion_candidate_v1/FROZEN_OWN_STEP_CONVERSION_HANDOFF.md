源码/CPU候选已冻结；没有任何模型、actor、物理或训练执行。

原V3自己的root+q通过原OwnUsdKinematics.forward(enforce_transmission=False)与已提取轮碰撞点计算。joint帧来自既存import_contract.json，axisX由旧export/audit源码明确，未重读USD/mesh资产。与旧USD-derived9个选点共18个wheel中心核对，最大差4.996e-16m。此核对只覆盖wheel链；不升级为全body collision/实际joint readback资格。旧261帧IK资格没有重跑。

双轮>=.27的下降窗口：[[137, 144]]。原.8m/s理想跟踪从age100、X0出发，没有在下降净空窗内完整footprint越缘的交集。窗口所需最小恒速到达下界约0.949244m/s；原command并非物理硬速度上限，因此这只拒绝该理想跟踪参考，不能证明机器人永远无法越台。

已实现bounded new own task forward goal，物理command仍.8、request100..179和原source时钟不改：age141到达root位移0.420336m，可用0.41s，平均vx1.025210、目标峰vx1.379688m/s，比.8理想跟踪多位移0.092336m。X用从静止到末速.8的Hermite，随后保持原command目标速度直到180。完整目标的差分峰ax40m/s²包含request结束的停止边界；到达前加速度另列解释JSON。它是待审核的参考目标，不是强制动作或力。

严格转换器generate_candidate先检查下降净空与完整平台footprint，再尝试截去外来平地返回段，下降Hermite接own neutral支撑q/root，不在空中+270mm。原.8轨迹被拒绝；新forward goal虽找到窗口，落地截接仍被拒绝：['ENTRY_ORIENTATION_NOT_NEUTRAL_ROTATION_SPLICE_REQUIRES_REVIEW', 'SPLICE_WHEEL_PENETRATES_PLATFORM_GEOMETRY']。没有导出可准入的step reference；原错误和数值全保留。不能将FK拟合或目标曲线称为动态可行/学习成功。90%excursion attenuation未改。

代码交付：mod4_step_reference_conversion_v1.py提供recorded-frame FK构造、wheel底/footprint分析、严格生成器、bounded own前进参数、OwnStepReference.target_bundle/future10_goal/objective_error。own_step_reference_tables_v1.py提供标准tables ages/control_dt_s/packed73/mask73/phase/joint_names/metadata.phase_contract，to_named_tables拒绝None，query_numpy支持future10并拒绝越界/非整数。新tiny schema fixture通过正例+4负例，不是实际converted动作。根可以接Torch provider与同义tracking terms，但实际source仍应因几何拒绝而不能准入。

后续明确工作是合适的own支撑orientation/q/root截接与全碰撞/驱动/真实接触验证；不能仅把外来后段整体抬高.27m。保留原callback成功/物理/动作/clock；source contact从未被当own contact。无USD/mesh资产/PT/raw/NPZ/SSH/GPU/Git/账本读写。归档由根负责。
