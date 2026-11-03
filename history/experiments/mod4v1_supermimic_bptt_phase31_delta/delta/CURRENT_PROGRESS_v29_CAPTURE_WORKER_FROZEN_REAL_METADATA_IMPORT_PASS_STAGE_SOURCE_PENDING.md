# v29：具体worker封件／63父复验／Linux真实metadata闭包通过；materializer收尾

2026-11-03 20:06 +08:00。最新实际get Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` 仍**rev15 / active / armed / 9/48**；[v28](<CURRENT_PROGRESS_v28_ACTUAL_ACTION_QUEUE_CPU_PASS_NEW_CAPTURE_WORKER_SOURCE_PENDING.md>)的原queue CPU通过、原物理/DR/H1/母本/原接受/预算/锁边界保持。当前阶段1，80/90原技能未达，不complete/blocked、不放行阶段2native。

## 真正NEW worker SOURCE已收件并父独立复验

[source_phase1_capture_worker_v1](<source_phase1_capture_worker_v1/README.md>) 13成员、root `d792dce3f110fe5fdfe30ded8840da657c22c72eaac42f60093cbe814c095028`，seal2537B / `3f713457c5d66c44ad1fe962ff954e6f65f87afedfef1d6e5bb7fa608e76bea7`；index57198 / `234f8a3d0baf2a84338e9a0bf2170510f99d33c416654bf23b47bc3b5b5aa5ad`。

- worker12146B / `662add4a539577074d22abbc9e8a7a3ee6846075e2d17caa535aa922996d107d`；runtime19063 / `2e148e7261aecf2b6de3a5e87a2e458ce06c503956479fb3a95c14fb407b1ed8`；parent9336 / `d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41`。
- 父已read worker/contract/observer/runtime全部核心源码及final修改，独立复跑**63/63 stdlib fake/AST PASS**。原parent17–44/46–78资源/readiness/actualchildwait/finallyEX块逐行相同，45仅单E3guard；完整AppV6→Base及canonical7a092、poseV4/bridge8211保持原17closure。
- 默认E3-only/N80/64，可128，syntheticzero6/PT0，原formal53reset→55fall/publish→66既有compute。原66作为original actor buffer，不宣fresh clean；现存initial cache/FIFO实际进入trace，clean0未知，不改tick/抽噪声/reset。
- 父在封件前发现并修正：initial snapshot变量遗漏export；global100Hz call-slots与per-row episode fresh混称；`group != HERE`误挡正常staged安装（现同remote root group==HERE）；原预SDK GPU/CUDA/deadline门缺失（现恢复GPU==admission.resource.GPU_UUID==CUDA_VISIBLE_DEVICES、deadline>now、两唯一非负fd/fstat-only）。不新增kernel锁检查/审批bool；原FD本来仅existence/fstat。
- SDK execution与coverage不足分离，NEW FINAL/fastcloseintent不借旧quality/training predicate。C→B→bridge→env→原App一次关闭；真正child和outer parent Popen.wait、EX释放证据以后才有。

## NEW实际remote CPU：真实模块/alias/root检查PASS

[run_phase1_capture_metadata_import_cpu_v1_once.py](<run_phase1_capture_metadata_import_cpu_v1_once.py>)已消费，marker存在。job `pwsh-78e709c376294eb3` RC0/已收取；[actual回执](<reports/PHASE1_CAPTURE_METADATA_IMPORT_CPU_V1.json>)：

- 原17+new5+dependency5 **27个真实安装alias**复制到独立CPU源码root并逐bytes/SHA核验；source测试不用dummy模块。
- Linux实际`group==runtime.HERE`正例、foreign/misinstalled/root负例通过；metadata imports worker但**不调用main**。
- 真正导入whole canonical37927/7a092、AppV6 27769/3d2d、完整Base22337/dc4、B/C metadata API，无stub；forbidden torch/SDK模块列表为空。
- 没有创建fake GROUP_PLAN/ACTUAL_GROUP_ADMISSION/FD，不读取模型/raw/canonical、不SDK/Popen/GPU/锁；是**真实metadata import，不是actual SDK／资源准入／Gate1**。
- 本用途已执行一次，不能重放。源码与完整receipt保留；后续新native stage另独立purpose。

[v28](<CURRENT_PROGRESS_v28_ACTUAL_ACTION_QUEUE_CPU_PASS_NEW_CAPTURE_WORKER_SOURCE_PENDING.md>)原queue+tap真实CPU N2/N3，各604全state/privateRNG检查、432正常apply、432ownedTensor、18partialreset、8sameTick组，仍为已通过独立CPU证据；不追写任何旧SOURCE seal。

## 外层actual parent wait controller SOURCE也已冻结

[source_phase1_capture_controller_v1](<source_phase1_capture_controller_v1/README.md>) 5成员，9个纯metadata/AST测试通过。controller3824B / `95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831`；seal SHA `0f8f7ecb86bdd9d45433eec6dd7b1d120ed41479487b2cf155a9dcff79cd8f22`，root `3166b4e9a97e97bb596a56dd68162e73f5c357e279ca4c0f47779e47c4a40292`。

源自真实执行的bound parent controller3456/818e…：identity/atomic put AST完全相同、main Try/Popen/wait/finally AST仅metadata strings改变。新root prefix `MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_`；固定stage receipt `STAGE_COMPLETE_PHASE1_CAPTURE_V1.json`要求materialized=true/parent_launches0/purpose新kind及bytesSHA；不是staged/native_enabled含混flag。实际main/Popen/parentwait尚未运行，SOURCE不冒现场proof。

## 当前active child与接续

`d66482f4-bbf6-4ad6-a2b4-231a32e6bf8a` NEW [source_phase1_capture_materializer_v1](<source_phase1_capture_materializer_v1/>)：主CLI381行、原17helper214行+derive33行父均已read；初步22/22 fake/AST passed，最后usage/manifest/seal仍待收，不直接执行浮动文件。

CLI参数：`--original-group-root --source-root --native-root --new-root --group-id --gpu-uuid [--controls 64|128]`与exactone `--preflight-only/--stage`。source-root是R的**source-only完整引用镜像，不是flat27**；需要original17及27全部映射、worker13+4依赖seal40成员、182 C原sources。sourceWindows路径只provenance，显式mirror做映射。

完整原V8 static/8 runtimes/银行/assets/worker_sources + Admission2 vendor7全部保留。发现3个original17会覆盖原V8同alias：保留冲突原bytes到`worker_sources/phase1_retained_original/<原alias>`，源logical完整tree digest/真正input_path/read bytes/一一relocation独立记录；实际stage stream-copy/hash重建installed后再比独立origin，不靠两相等列表自证。实际消费aliases按新index，原内容不丢；相同bytes不多copy。模型/operational/raw在classification/stat前排除；不是AST82模块裁剪。

父已转发worker13最终seal，D664确认实际verify后固定；已对齐controller receipt字段。**本CLI截至此交接实际prepare/真实input preflight/stage/SDK/Popen均0**，只有SOURCE tests。后续先收seal→父full diff/inputs检查→独立source-mirror/source payload→NEW真实preflight→NEWroot文件materialize→实际原parent资源门/外层wait controller→最小E3接口capture；每个失败/root/once保留，不重放。

当前job_list全completed且所有相关hostjob已收取，无自己的GPU/native/resourceobserver。565/cffddedf/0ad source任务已完成inactive，仅D664 materializer在工作。Goalactive。

## Git

Phase30仍最新已远端核验 `2d16bf1e1dbf55cd72120c761481b446cbd78622` /annotated `8fd5c6723c784895c44533366eb735c563b89304`，main仅读；详[v27](<CURRENT_PROGRESS_v27_PHASE30_VERIFIED_PHASE1_CPU_PASS_NATIVE_WORKER_SOURCE_ACTIVE.md>)。

[archive31](<archive_phase31_action_queue_cpu_worker_source_delta.py>)**已prepare但尚未执行record/commit**，当前额外加入actual metadata-import/worker63/controller9 guard与NOTE；pre-exec source delta待写元数据/复验，不冒称已Git。此v29、v28/晚review、全部late封件/真实queue CPU/metadata import/worker/controller及materializer point-in-time均待Phase31。捕获后后续final seal/stage/SDK/交接再如实pending下次append。绝不为Git重跑模型/raw/CPU/native/旧once。
