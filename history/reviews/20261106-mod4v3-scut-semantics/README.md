# MOD4v3 HW300N60：华南虎 V14_2 语义包

用户2026-11-06明确要求制作 MOD4v3 MJCF/USD 包，将语义与华南虎一一对应。本阶段完成独立语义资产交付，不替换其它聊天运行资产，不启动训练。

交付 ZIP：F:/RMPOLAR-RL/mod4v3_scut_semantics_20261106/MOD4v3_HW300N60_SCUT_semantics.zip
SHA256：08b09b75d1b7d4688434eafd2bbd1cbcdbf1a7c7076bf60b2248a57a12b0e57d；20831173 bytes。

来源：不可变 MOD4v2 HW300N60 MJCF c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125；华南虎 Git b8ff79f3df855faf9dc92f4a282bd80c42649466 的 V14_2 USD48f2d53ac589391a37f3df550e8e537af3ecb5bdb6ebb632fb8c7b83fa9af325。该华南虎仓库无MJCF，不冒用复旦或旧步兵模型。

最终 MJCF SHA77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f；USD SHAc0e45c305ac91cefabb83709dc9b12fa78eda615a4a5fd7a5866263ed1f539a1。原质量14.294140288606286kg、31刚体/6执行器/10等式、六杆闭链、mimic、实体滚轮、300N60mm气簧及CAD止挡保持。

机构对应：crank→front1，coupler→front2，rocker→front3，distal→front4，hip/thigh→rear1，knee/shin→rear2，gas_inner/barrel→spring1/2，wheel_spin/wheel→wheel。此前“MOD4没有rear2”的判断被真实拓扑推翻；原错误记录不回写。

连杆参考方向由对应销轴连线推导。参考坐标帧/原点变化通过 mesh/collider/COM/惯量反变换抵消，MJCF使用ref，USD使用joint局部帧，保留物理世界几何。全部37个参考刚体、42个关节/闭链轴逐项有记录；27刚体/32轴有物理同源角色，2云台及8华南虎专有导轮不存在，不创建假质量/零值替代。额外4个MOD4传动follower保留。

原front3树切口保留；SCUT front2→front3标量由qrear1+qf3r1−qfront1−qfront2计算。ScutRobotView提供严格名字/数据访问，位置/速度/加速度和保持功率的力矩变换。不能宣称无需适配的原生关节树完全相同。尝试华南虎同树重排因MuJoCo3.15跨分支fixed-tendon armature编译缺交叉项而拒绝；原候选和失败验证04/05保留，不入交付ZIP。

华南虎投影腿长/腿角与MOD4三维L0/theta独立命名。raw action=default+scale*action，轮控mode与scale显式；不复制SCUT连杆长度、硬件限位或额外弹簧。新增strict奖励汇总禁止非零缺项静默零，终止项读取最终pre-reset terminated；未改运行训练环境/奖励权重。86个原奖励项的源码依赖清单附包。

实际验证：最终VALIDATION10 1659项通过。多姿态原几何/COM误差约2.22e-16m、惯量tensor误差2.04e-17kgm2；USD变换误差约3.36e-9，最大锚点gap7.0e-9m。0.2秒有重力CPU同源响应差约1.85e-15m，闭链1.1795mm<原10mm。

Newton实际验证：host72 pinned Newton1.7/SolverMuJoCo CPU运行20×2.5ms，通过，保留31刚体/10等式；初始误差.000122mm，最大闭链.138331mm；50ms与直接MJCF位置差1.0757mm，仅为短时CPU诊断。Newton joint_q为q_MJCF-ref，适配必须显式newton_displacement。错误绝对角输入导致CPU04闭链62.819mm失败，修正后CPU05通过。旧Newton1.2.1探针出现QACC warning，不算通过；CPU03只有finite不足以证明动力，CPU04/05补实际几何/闭链检查。未执行本版Warp GPU/PhysX GPU或策略训练，不声称收敛/硬件认证。

其它失败：validator01语法括号、BUILD02闭链prim实际路径/Robot/closures解析、validator06腿解算输出误含导轮；全部原报告/源码或SHA索引保留。最终PhysX数值wrapper只将46个无界角端表达为1e20deg，原有限CAD边界保持；静态检查通过，native动态未测。

全部源与报告见ALL_FILES_INDEX；大型USD/mesh/ZIP/图像只真实路径/bytes/SHA索引，原件保留。阶段新trial使用record_experiment一次，不重录本站高V42或其它聊天trial。
