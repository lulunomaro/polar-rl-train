# V4 首案：实际起立失效，单次已存传感流诊断

- 193 controls / 3860 physics；complete=False，原门=False；limited startup pitch/roll envelope exceeded。
- phase={'OBSERVE': 31, 'LIFT_WORLD_SUPPORT': 161, 'INHIBIT': 1}；未到CAPTURE/RETURN/VERIFY/BLEND/BALANCE；sensor capture eligible=False。
- 末真实pitch=0.991339657rad；rootZ=0.305914938m，高度增量=0.068776234m；最大XY=0.076305426m。抬高不是站稳。
- 193个控制bin中：双主轮全部20采样承重=193；guide/hard全部20采样≤1N=0；两者同时=0。whole guide=3815，hard=0，仅原private grader。
- request峰值Nm=[13.109112906429308, 20.288575273186552, 0.18883948714355994, 13.092783885279376, 20.289044947036693, 0.1880606303703649]；wheel-rate峰值rad/s=[0.6294649571451998, 0.6268687679012164]；不从request推断actual/DC clipping，不从encoder proxy推断真实路程。
- PRE sensor/command vs POST root以及.5ms collision缓存按原日志时标保留。一次新control读取193行，0physics/旧raw/模型/FK/重仿真/原始流hash。
- 既有静态支撑几何只是构型可行性，尚未成为动态起立策略；本案按原阈值停，门/旧冻结结果不改。本诊断不证明唯一失效原因，也不自动批准后续增益或病例。
