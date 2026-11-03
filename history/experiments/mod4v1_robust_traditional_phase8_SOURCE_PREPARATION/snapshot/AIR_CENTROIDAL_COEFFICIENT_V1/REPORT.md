# AIR_CENTROIDAL_COEFFICIENT_V1 — 一次public nominal代数prototype

3个旧public pose；全31body COM转动+轨道动量，不调用旧terms，不删wheel rotational；phase0只是synthetic fixture，2wheel/8guide独立rate列按axis/tree解析。

|pose|I_locked yy kg·m²|Ac_y kg·m²|Adelta_y kg·m²|−Adelta_y/Ac_y|
|---|---:|---:|---:|---:|
|crouch|0.272437640747|0.0800775352365|0.0323268911662|-0.40369488234989054|
|pushend_delta_plus_0p2|0.331253334464|0.149398709074|0.0689811651886|-0.4617253095184038|
|landing_delta0|0.310768782773|0.126125922692|0.0576689374228|-0.45723302705724317|

所有pose I_locked对称/SPD、zero、17basis/directsum、固定mixed及同mixed常坐标旋转协变均通过预锁1e−8abs+1e−10rel（各自SI单位）代数自洽预算，非实际物理误差界。
实际27top-level FK、0recursive、27all-FK；60whole-body momentum evaluations，每pose20，zero同一遍历组装I/A，无额外coefficient sweep；另外每pose2次COM/JCOM聚合如预锁。0SDK modelboot/forward/RNE/step/runtime。
完整逐pose I_locked3x3/Aq3x4/Awheel3x2/Aguide3x8/Ac/Adelta、Y行ratio/guard、basis/mixed/残差见[RESULT](<RESULT.json>)；[预执行锁](<SOURCE_PREEXEC.json>)、[固定方法预算](<METHOD.json>)和[receipt](<RECEIPT.json>)。
unknownH0/guide及wheel实际自旋/phase、外接触、softpassive、physicalrotor/armature仍缺绑；未加armature/DR，不代表全plant总动量或实际反作用可消。ratio不是路径/gain，不选h第三range。
零积分器自洽≠独立plant/dynamic验证、未知接触/landing稳定性/驱动可达性/wholeRM/270/hardware资格。未控制、未改旧source或oldscore，PH8pending。
