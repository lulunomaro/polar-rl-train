# V15 — W7零GO自然超时并收口；释放已观察；新W8原父提交

## 当前目标与质量底线

只做E3 Fudan起身质量，goal `goal-c490e4cc-b28b-440e-bde6-30ee956813f0` revision3 active/armed/max14，尚未取得改善；不以计数/RC0/完整保存替代质量。H1/其它专家/Registryv12/1cd保持。W6真实closed72之后的独立原N80执行资格true但0/74、名义同五姿0/5且body高度/漂移更差；3e64/8af4完整候选保留，不晋升。最新已核验Git为7ee034128525a83dc3a33284bfe219eece934e26、trial-20261105-e3-fudan-fresh1cd25-original-admission；那是W7原提交点时记录，不是本次训练成功。

## W7实际终态（不是技能失败率）

- [完整closed证据](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W7_FRESH1CD_20261105_005713/CLOSED_RESULT.json>)58行；root `MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_W7_20261105_005638_1793811398919144400`。
- 原parent1625509在epoch1793813220.6316745 / 2026-11-05 01:27:00 因`b.LOCKS`原authority EX仍忙，原1800s preGO自然超时；`Original preGOresourcewait1800expired`完整错误保留。outer controller1625502实际wait于1793813220.6404047，RC0/reapedtrue；inner/all own children waited、cost settled、leases released均true。**RC0不是合格训练。**
- COHORT_FINAL及全部FDN字段为null：没有GO/worker/SDK/selected PT读取/新PPO/候选/技能分数。新25只是上限，尚未跑一轮；与旧205完全分开。原stage450/preflight0为source-only，不算实训。
- 原observer **pwsh-8166db58c67945b0 已completed0/output collected**。W7 stage/dispatch/collector/root全部消费，不重放，不延长已退出的原parent。

## 唯一活跃释放观察

- [只读释放observer](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/watch_original_authority_after_fresh1cd_w7_once.py>)先核W7实际closed/所有wait结清释放/精确parent与controller/全部FDN null/preGO错误，再启动一次30s×1800s canonical只读观察。**job pwsh-ddb393298cab4501已completed0/output collected**；epoch1793814056.4740443确实观察ownerNone，reader_gaps0，remaining216974.77313899994（只读历史值），没有GPU/锁/SDK/model/C写操作。此时并未证明原GPU/锁可用，不另开重复C观察器。
- 首次实际canonical读epoch1793813334.117258：owner_run_id `MOD4V1_JUMP200_APPROACH_PUSH_REPAIR_PREPARED_1793809808600122700`、owner_parent_pid1624598、started1793810450.0693789；remaining217673.22818255424、charged2050326.7718174458。这是历史只读账本视图，绝不写回/推算改账。
- 仅等该原owner自然释放，不signal/清锁/触碰外国worker或模型；C ownerNone也不是GPU/锁资格证明，后续原parent仍完整重检。

## W8 Admission2来源stage完成，原parent已提交但尚无GO证据

- 同一worker/core/owner/overlay/25上限，**只新namespace及新增W7 closed-zeroGO前置条件**，没有物理故障重试或learner变化。[三薄入口builder](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/prepare_fudan_fresh1cd_w8_admission2_helpers_once.py>)单次AST/compile，通过后只执行新stage；生成时dispatcher未执行，后续一次实际提交见下。
- 新root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_W8_ADMISSION2_20261105_013118_1793813478778262400`，prefix `FDN_N20000_W8_FRESH1CD_ADMISSION2_`，payload `native_payload_v8_n20000_fresh1cd25_admission2`。
- [新stage入口](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/prepare_stage_fudan_fresh1cd_w8_admission2_once.py>)已消费，450完整nonPT/runtime/lib/assets/staticNPZ，原owner source-only preflight0；selected model/SDK/GPU/GO/C操作0；旧invalid escape warning保留。未source剪枝，未动原budget/physics/DR。
- watch实际ownerNone后，[W8原父dispatcher](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/dispatch_fudan_fresh1cd_w8_admission2_original_owner_once.py>)已一次执行（epoch1793814087.6205213/controller1626919），不重放。随后一次启动[W8 collector](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/collect_fudan_fresh1cd_w8_admission2_window_once.py>)，唯一活跃job **pwsh-91f1d23a513944ec**，6000s/15s只看own metadata。首次epoch1793814106.3936956仍是原resource preGO Errno11、worker/init/update为null/false；ownerNone不等于资源资格，原父正在原1800s上限内重新检查。原authority2EX/privateGPU_EX/finiteSH/3900-3600-300/1800preGO/charge_values/实际wait全部保留；当前尚无W8实际训练/质量证据。

## 实际开训后动作

fresh1cd MLP8+8，encoder fresh随机/latent列0/STD.5/两Adam与计数全0，N20000/T48/max25，不接坏候选；相同386107/8571低位8s timeout/fullDR/全部硬件物理。已备妥Root4的7+3冻结源及stage/export/dispatcher/collector/同五姿MuJoCo入口，collector明确匹配`FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V4_FRESH1CD`。待真正GO/INIT/正更新后只冻结一次首个实训proof，待完整保存+inner/outer实际wait+cost结清+leases释放后再原N80/160/seed20260928/74+6及名义MuJoCo；不要提前运行已消费的旧版本。

7ee0341之后的W7真实timeout、W8 namespace/stage、只读watch与本handoff暂待下个有意义合并archive（实际新admission/正实训或watch终态），不为每个健康轮询造trial。所有Git只feature+唯一annotated tag，main只读；模型/raw/JSONL/geometry在stat/read/hash前跳过，不为同步重跑物理或旧once。
