# 导轮材质属性与有效接触摩擦的分层澄清

这是追加审计，不重写旧模型/旧结果/旧通过标签。

## 实际观测

- [原USD来源](<../../mod4_usd_scut_fudan_20261101/candidates/v1/assets/robot.usd>)对8导轮绑定guide_roller材质，static/dynamic friction均约0.02；本轮未见该材质authored frictionCombineMode。
- [主MJCF](<../MODEL_AUDIT/mod4v1_usd_source_aligned.xml>)导轮geom friction3约[.02,.001,.0001]，step270/ground为[.9,.003,.0001]，二者priority都是0。
- [0step静态接触审计](<../MODEL_AUDIT/GUIDE_EFFECTIVE_MATERIAL_V1/RESULT.json>)在既有真实记录姿态mj_forward，观察到contact.friction5实际[.9,.9,.003,.0001,.0001]。因此“geom authored μ=.02”不等于“该MuJoCo pair有效 μ=.02”。SCUT grid地形面μ=1且平priority，也存在同样max-mixing解释。
- 已知轮D0单独提高main-tire priority以保留frictionbucket；这没有自动给导轮同样的优先级。

## 对旧证据的影响与边界

旧R13–R22跳阶/地形有导轮接触的轨迹，应按照其**实际原接触规则**解读；它们不是effective μ=.02的资格证据。旧角速度/姿态/越沿/结束稳定统计原样保留，未倒填成另一物理模型。无导轮接触的其它轨迹也不以此追加审计代替原复核。

USD属性、PhysX场景combine设置、MuJoCo pair参数、实物摩擦标定是不同层级。本轮未运行实时PhysX对照，也没有实物摩擦标定，所以不把任一推测的combine规则称为源模型的唯一正确动力学。

## 显式替代分支，仅作敏感性

新[guide-priority variant](<../physics_bridge_guide_mu_v1.py>)令guide priority高于terrain、wheelDR随后再升高，保留所有几何/MCI/关节/电机界限/控制器。静态[QA](<../MODEL_AUDIT/GUIDE_PRIORITY_VARIANT_V1/STATIC_QA.json>)验证该分支effective sliding μ≈.02；由于priority还选择其它接触参数，明确不是只改一个标量的完全等价试验。

[R28](<../batches/r28_guide_material8/BATCH_RESULT.json>)用两套固定控制器、nominal+3个已知TRAIN种子，全部8条完成，但μ=.02分支下：原push.34/.11的3条DR结束稳定2s为0/3；push.65/.13为1/3。两个nominal都通过结束稳定2s，仍有导轮/个别硬几何接触。选取样本不是独立成功率，替代分支不当作原模型更高通过率，更不挑容易分支宣称鲁棒完成。

接续应公开区分两种接触语义，验证最坏敏感性；不通过改小摩擦/删导轮/调接触刚度来覆盖原失败。
