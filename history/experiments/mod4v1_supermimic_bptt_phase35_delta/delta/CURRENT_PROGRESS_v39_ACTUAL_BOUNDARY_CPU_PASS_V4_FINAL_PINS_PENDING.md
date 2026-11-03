# v39：真实TorchCPU合同通过；仅设备表示的一行V4候选待最后pins

2026-11-03（具体CPU epoch/远端own purpose见[实际回执](<reports/PHASE1_BOUNDARY_DEVICE_ACTUAL_CPU_V1.json>)）。Goal最新实际rev15/active/armed/9/48不变；当前阶段1，Stage2/exact/技能结论未升级。继续[v38 Git34与活动SOURCE](<CURRENT_PROGRESS_v38_PHASE34_VERIFIED_V3_CLOSED_V4_CONTRACT_SOURCE_ACTIVE.md>)，原物理/DR/速度/阈值/预算/锁/期限/H1/母本/Registryv12均不变。

## NEW实际CPU结果

[source_phase1_boundary_device_contract_v1](<source_phase1_boundary_device_contract_v1/README.md>) source seal1570/c9fae49e96b7042863372e7fb681c7c93fd8ce733646908222c9af6f7d306bdc，8members root5b4d0134e8ec0d828adef1fae8156d195ede032eacea2476457a403162e9e106。父read完整fixture115/API98/seal51；CLI两完整PY6289/cb09e…与5380/93d8b…不含本地provenance依赖。

父[一次CPU runner](<run_phase1_boundary_device_cpu_v1_once.py>)实际执行于新CPU purpose，job `pwsh-9ff34c1f81bc47a3` **RC0且已收取**。只实际TorchCPU、source、synthetic80 flags，无SDK/env/bridge实例、PT/raw/原账本/锁或GPU操作。使用真实已物化V3 root完整canonical37927/7a092的全模块/类，原bool/N80/设备/step-order predicate原样，没有抽AST替代或放松门。

- `OriginalEpisodeBoundary(torch,'cpu',80)`遇bool CPU flags，精确重现原 `separate original bool term/trunc N80 required`。
- 使用模拟既有规范`torch.device('cpu')`，2actions→2synthetic original_steps，首次all-fresh、以后term|trunc、pending=False均通过。
- 11负例：两侧shape79、80×1、float32/int32，step-before-action、doubleaction/noStep、N79均被原predicate阻挡。
- 原两个Tensor对象身份与值不变；全局TorchCPU/Python RNG均不变。
- **实际V3 env.device类型/实际flags.shape/dtype/device仍null，actual_V3_root_cause_confirmed=False。** 这是明确synthetic合同路径的实证，不是现场flags测量或Stage1通过。

此源fixture、CPU runner和报告均once消费，不因格式或归档重复物理执行。父已将结果发565与D664；CPU实际报告不加入worker或source镜像硬依赖，不改原sealed SOURCE receipt的child-scope false声明。

## 最窄V4计划与当前状态

565正在NEW workerV4仅将原worker126的boundary构造实参从`env.device`改为**已经存在的`bridge.device`**。原bridge86构造早已`torch.device(env.device)`，原bridge144分别`.bool()`；不改state.flags/predicate/boundary原类，不加SDKgetter、不改原step/reset/时钟/RNG/close/physics/DR/accepted/资源协议。其余4candidate目标逐字节同V3；13seal/index最终pins**待收**。不把候选方案冒已native修复。

D664 materializerV4、CFF collectorV4仅待固定pins的未封模板，不能用于任何preflight或native。CFF模板40/40明确exclude7个final-pin tests（完整suite声明47，不能算已跑）；D664仅3PY AST，均NOT_READY。原17/fullAppV6-Base/canonical、原完整static/banks/vendor7、B2全部164source、4routingJSON/435/155/diag/root-normalize、origin-retained-stream、same bootstrap、typed V1/parentd557/controller9595必须保持。

仍在并行SOURCE：A194纯capture application（已own20synthetic但未封），BAC good-holdoutV2父只读来源review。均不读actual trace/模型/SDK或发起新parent。V3已经实际closed20.37s/doublewait/EXrelease、countsnull/error保留，没有自己的live scene。

真实下一步：收到565final13/index→父核实唯一一行diff/Source回归与完整派生来源→D664/CFF固定最终refs/seals→父复核与NEW实际source preflight/fullstage/root/原准入/一次最小capture→成功才对原wholeworker+group FINAL新scientific用途一次read/hash/decode缓存做证据application。旧三次root/once不重放，缺数据不补0或投影。

## Git与报告

Phase34已remoteexact HEAD9f2891dd380b2e76fd93103766a4f337cb23dbe9、annotated35fb29b7bf40dc9a02a1896359449b66e8ce238d、peeled同；main只读359505569da8dddb7d4ffb5ba25962cad60a23ab。6997entries/6463refs/79texts；所有job已收。

**v38/v39、小fixture/本次CPU、V4 final源/未来实际窗口、application/good-holdout新SOURCE review等均在Phase34捕获后，待Phase35补入。** 不为Git重开模型/raw或重放任何试验/record，main不写。Goal继续active；有实质工作未complete/blocked。
