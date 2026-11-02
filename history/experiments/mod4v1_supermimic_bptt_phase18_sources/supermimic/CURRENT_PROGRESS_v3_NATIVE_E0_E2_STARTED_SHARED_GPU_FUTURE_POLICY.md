# 已实际启动：E0/E2各20次真实H16 BPTT固定快照；用户新增低占用共享GPU准入

2026-11-02 18:52。当前Goal **goal-1c14ef7d-c888-4287-83bf-c008d54545fb revision9 active/armed/max48**，后续get_goal取实际revision。H1冻结。八条非H1每条>=3000 verified BPTT和各自原技能>=90%依然未完成；80%仅中间底线，不能混入站立/平均/无跌倒代理。

## 最新直接人类指令（18:48:07）

“如果gpu占用不是很高，有其他人占用但是占用不高，可以直接使用”。已edit Goal：两张有足够余量的授权卡，低占用/显存充足即使有其他人compute进程也可共享；后续不用compute-app非空一票阻挡。原项目GPU私EX/finite环境锁/唯一canonical计费writer/原budget+reserve仍保持，不清他人锁/停他人任务。新指令没有要求终止或热改已准入窗口。

已构建仅future unused owner使用的新源：
- `source_runtime/shared_gpu_admission_v1.py` SHA **0ed3ca0e1f449a4c63deb1d6ba4f9037672438e1def74ffbb654efa3a7c3c42d**。
- `source_runtime/supermimic_original_owner_shared_v2.py` 12017B SHA **5e4e77d86ed993236bfc09dee8d264db6b23989ff52c3bff5cbb279b11b3bf54**。
- `reports/FUTURE_SHARED_GPU_ADMISSION_SOURCE_V2.json` 8项stdlib fixture/AST检查全过：空卡/低占用有他人进程均可；util>30/free<=15669MiB/RAM<=64GiB/disk<=50GiB仍等；所有非gpu函数AST逐一与原source相同，原锁/account/main完全未变。
- **新future源尚未上传/执行**，当前live owner/worker/manifest源未动。后续新unused窗口才启用。当前运行不是共享卡实验，别把后续policy回填成当前运行协议。

## 原等待自然结束，真实GPU启动

在原1800秒preGO结束前，外部原LQR owner正常释放；已存在的parent **1475630 creation1793614676.22** 自然取得原twoauthority EX/每卡privateEX/finiteSH和原C唯一计费，无新parent/无重跑stager/无抢锁。

- GPU0 UUID16828f91：E0 worker **1477022 creation1793616448.81（18:47:28）**。
- GPU1 UUIDc27eecbd：E2 worker **1477031 creation1793616449.50（18:47:29）**。
- root仍 `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_SUPERMIMIC_BPTT8_V1_20261102_181251_1793614371303119100`。
- N1024 fresh原Isaacconstructor，全原D0–D7，新MOD4v1 USD2c/contractbae、原400/k2000/d3/50-100Hz/.0025/TGS32,4/.01m-.01rad；一次fresh reset；原teacher35->6冻结，分别E0当前best6cdac1e4.../E2母本b3ae94df...，无20k history投影/伪PPOoptimizer恢复。
- 源与实际startup/DR审计/teacher一次物理读取receipt已保存 **`reports/FIRST_NATIVE_START_AND_SHARED_GPU_REQUEST_V1.json`**（纯producer metadata加工，未再开模型/raw/远端C）。其固定producer epoch1793616613.362（18:50:13）每条iteration120、actual pi optimizer20、verified H16 BPTT20、WM480/aux480/critic80、unverified0/nonfinite0/zero0。
- 每条actual_controls364、transitions372736、physics_callbacks2912、feedback_samples728。H16 temporal+WM-path VJP finite/nonzero、参数probe实际改变：E0 temporal.00807845/WMpath.00494526/paramdelta.00140906，E2 temporal.00907836/WMpath.00406976/paramdelta.00196735。
- **这些是实际原生MOD4采样+WM imagination上的policy BPTT，不是CPU合成3；也不是技能90%证据。** 后续更大计数读唯一observer当前producer发布，别停留在固定20快照或假推算到3000。

## 当前唯一相关后台观察器

**pwsh-0628d778d2fa4b85**，原 `collect_actual_supermimic_run_metadata_once.py`，pointer `SUPERMIMIC_EIGHT_V1_LATEST_METADATA_WATCH.json` -> reports/ACTUAL_SUPERMIMIC_EIGHT_V1_20261102_184527/CURRENT_METADATA.json。20秒纯publishedmetadata，不开模型/raw/SDK/C，36000s有限cap，原parent闭合后收ownstderr/GO/closewait一次并落CLOSED_RESULT。

特别注意：原PREGO_RESOURCE_WAIT文件不会在GO后删除，observer输出original_wait:true只是历史文件存在；**live OWNER_CURRENT workers + startup/progress优先，已经在实际训练，不是继续等锁。** 当前未final/未closewait/未结算解锁，不能声称本窗口完成。

此前CPU软件job pwsh-971753d1767d49a1 RC0、readonly实际资源诊断pwsh-331b559ff24d46e5 RC0均输出已收，不重跑once。旧hostobserver本地进程已确认不在才恢复新observer；不能重复启动观察器或worker。

## 测量agent与归档

源专项agent **d9af2e50-3e24-4eb6-8177-72271f9d0ac2** 在 source_measurement_review_v1 准备E2/W35 getter/frame/UID/episode observer+CPU合成测试。初步重要纠偏：本地root_pos_w基类alias actor frame root_link_pos_w，root_state_w注释是link pose+COM velocity，不得凭名称认定COM位置；实际后端getter/cache仍缺，runtime状态null。E2 begin/terminal同读root_pos_w/heading；W35 begin getter/terminal frame root+xyzw，需future配对插桩。新NativeBridge训练xi没有原world_direction/signed_yaw/is_standing完整cohort标签，不从训练transition猜验收标签。不得热patch当前worker或读旧JSONL补标签。

phase18 `archive_phase18.py` 已准备，**尚未执行/提交/推送**；待纳入当前固定快照/共享新指令和已有全部源失败/CPU检查/资源报告/交接。仅feature mod4v1-experts-fulldr-rm70 + 唯一trial；remote main只读随时独立变化，不能硬绑旧main。旧phase17 finalPPO已完成，所有新活动为新BPTT Goal。

下一步：持续实际nativeBPTT、等500iter完整保存receipt；归档phase18并验证远端；源agent封版后待独立原接受谓词多seed评估。E0/S50 binary谓词未证，E2/W35 frame/cohort原缺口待测；不假80/90达标、不完成Goal。
