# V18 — 单一低位正tracking高度门控，N20000有限25新窗已提交原父

## 当前目标与冻结项

当前goal `goal-c490e4cc-b28b-440e-bde6-30ee956813f0` revision3 active/armed，round2/14；质量目标未完成，不complete/pause/blocked。仅E3；H1、其它专家、Registryv12和1cd母版保持。前轮[closed25实测](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_FRESH1CD_CLOSED25_QUALITY_RESULTS_V1.md>)原qualified0/74、名义五姿0/5且候选漂移差，保留246ac完整候选但不晋升。[V17](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/CURRENT_PROGRESS_V17_FRESH1CD_CLOSED25_ORIGINAL_NOT_IMPROVED.md>)的postreset和critic核对补记均按下一阶段一并归档，不重跑旧模型/评测。

## 唯一新训练行为

[计划与源码证据](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/NEXT_SINGLE_INTERVENTION_LOW_POSITIVE_TRACK_HEIGHTGATE_V1.md>)：只在recipe>=13将3个既有正tracking项乘clip((root_height-.1781)/(.23-.1781),0,1)，weights/params不改且实际构造时要求>0；旧fall/normal原值、负误差项、height/potential/动作代价、命令、五低姿、8s/400timeout、PPO/core、物理/fullDR、接受条件全不改。不将此假设写成已证明因果根因。

[新overlay](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/source_task_runtime_v3_lowheightgate/e3_fudan_task_runtime_v1.py>)156行/12723B/SHA `a89ff5487e76a5d7256b4cf9e60d5c7292047e3d70ca681f02d8c9900f0c4c35`。仅加常量内存的pre-reset高度采样和episode峰值统计，复用phase.update已有height/low；typed state保留基类字段并加n向量与float64[6]，version `fudan_legal_lowrise_lowheightgate_v3`；额外summary只读实际constructed term weights/functions/params，不用defaults冒实际。没有新CPU fixture/物理seal农场。

[source-only适配器](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/prepare_fudan_heightgate_native_sources_and_helpers_once.py>)已消费，7新源/一次AST，worker和owner逆元数据归一后AST完全相同。新worker `source_fudan_native_worker_v6_lowheightgate`46537B/SHA `13da06004b93c0c561bbc638e27bbfe0b93556690b91076625b06c600f17dc32`，Root/schema5、branch `FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_HEIGHTGATE`、source_kind `fdn_fresh_mlp_warm_1cd_n20000_timeout8_heightgate`；依旧1cd 8+8 MLP warm、encoder随机fresh/latent列0/STD.5/两Adam-LR-private-generator-计数fresh，base四0，不继承246ac/205/43090。

## 实际W9准入与唯一观察者

- [stage入口](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/prepare_stage_fudan_heightgate_w9_once.py>)已一次成功，450非PT原runtime/lib/assets/staticNPZ全依赖、原owner source-only preflight0。stage PT/SDK/GPU/GO/C操作0，原invalidescape\\S source warning保持，并非Native failure。不得重跑该入口。
- Root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_HEIGHTGATE_W9_20261105_024613_1793817973423106300`。
- [原父dispatcher](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/dispatch_fudan_heightgate_w9_original_owner_once.py>)已一次提交，epoch1793818002.803464，outer controller1629746。原1800preGO resource wait，不是新GO或PPO证明。
- **唯一host observer `pwsh-4bc96b66ac5f4c39`**，运行[6000s/15s自有metadata collector](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/collect_fudan_heightgate_w9_window_once.py>)。首snapshot1793818014.9966257仍worker/null、INITfalse、UPDATE/null、errorfalse、原Err11资源等待；最近一次job_output无新phase。尚无本新窗已观测GO/SDK/模型读取/PPO/质量值，不将它当0%技能。只继续此观察者，不开重复worker/watch/查询模型。
- PREFIX `FDN_N20000_W9_LOWHEIGHTGATE_`，派生pointer/报告都在D；实际报告目录由collector路径指针读取，不能猜新closed时间。若原父自然超时，先等真实inner/outer wait/结清释放再决定下一新purpose；不重放旧Root/延长旧父。

## 准备好的独立评测（尚未实际执行）

新`source_fudan_frozen_native_eval_v5_lowheightgate`7源+`source_fudan_frozen_parent_v5_lowheightgate`3源，仅3模块metadata变化；其余7 BYTE相同包括合法CRLF AppV6。mean26746/SHA `83673fd3838ad36d87ae25cef9537371e8b4909ec1582bcd783a35a6d0addff4`；safe22097/`560b95f916f9750be507beea71578b4591943851ce572ff7ccde528c2505bb9a`；parent30415/`2451a5e3c17624d729d9bbd2749e056d219917610b1d92d2c4e6727b923b051a`。全部14pi/82505/35x5/history/clip6/wholeCPU未知根/原Appclose与actualwait/资源/原74+6保持；source schema5/新overlay pin、词法排除旧1cd/47937/8af4/3e64/246ac BEFORE input read。训练heightgate不安装进评测。

原生成器误要求继承AppV6必须LF，在首输入read261失败，输出mkdir313尚未到；[错误](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_HEIGHTGATE_FROZEN_BUILDER_V1_NEWLINE_ERRATUM.json>)与旧源保留。新`prepare_fudan_heightgate_frozen_eval_sources_v2_once.py`仅接受UTF8原CRLF roundtrip，原3SHA/逆差异/7byte检查完整，实际一次生成+10 AST/compile成功，0模型/SDK/SSH/GPU/C/fixture，未改native。

[五入口生成器](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/prepare_fudan_heightgate_eval_entries_once.py>)已消费/一次AST+remoteAST+实际import名静态核对。所有下列入口**尚未执行**：

1. `stage_fudan_heightgate_frozen_original_once.py --closed ACTUAL_W9_CLOSED`：实际inner/outer/error-free/settle/release+新Root5/currentpositive25/constructed正tracking门控+pre-reset覆盖才允许stage；全原445依赖，N80/160/seed20260928/74firstepisode+6normal/fullDR/一reset/0优化。
2. `dispatch_fudan_heightgate_frozen_original_once.py`和`collect_fudan_heightgate_frozen_original_once.py`：PREFIX `FDNHEIGHTGATE_FROZEN_`，collector EXACT `FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V5_HEIGHTGATE`，qualification从实际TERMINAL_ROWS/FINAL.rows、skill从真实Case FINAL读取，不造Case qualification文件。
3. `export_fudan_heightgate_pi_for_mujoco_once.py --closed ...`：同一closed前门，正确实际EXCLUDED四组导入，移除旧V2仅为ImportError重试的前提，独立新purpose `FDNHEIGHTGATE_PI_ONLY_EXPORT_`；整文件CPU一次物理/hash/decode，14pi小派生非fullresume，不下载完整源，不造critic/Adam/env。
4. `evaluate_fudan_heightgate_pi_mujoco31_lowrise_once.py --pi-export ...`：PREFIX `FDN_HEIGHTGATE_MUJOCO31_`，五合法姿×8s，四个case物理函数AST BYTE语义不改；同31体/50-100-.0025/PD/gas，clean-noDR，与原native/hardware/视频exact pose区别明确。

所有原canonical/charge_values/authority2EX/privateGPU_EX/trainSH-evalEX、reserve86412.86069250107、3900/3600/300、1800preGO不变；无foreign signal/清锁/改账/扩预算/退款。每真实模型用途一次physical/hash/CPUdecode/immutable缓存，无模型/raw状态或Git读取。评测execution pass不是技能pass；候选晋升由真实质量证据而非25计数。

## Git状态与下一步

最新已核验feature `eca5890fef23d1fc9ad35e2e99362024dabc0124`、tag `trial-20261105-e3-fudan-fresh1cd-closed25-quality-keep-mother`，main只读。此后新计划/overlay/source/格式错误与修复/W9准入/本handoff待下一有意义阶段同归档；不重跑旧record或GPU补档。下一步继续唯一observer，实际GO后读同collector已发布准入/INIT/UPDATE；真实complete后执行上述独立评测与候选/母版决定，归档全部新成功失败并远端核验。goal保持active。


## Archive boundary
Actual450-source new low-positive-tracking-heightgate stage and original bounded-parent submission only. No actual GO/native update or improvement claimed by this point-time title. Reward change only recipe>=13 three positive tracking terms times clip((height-.1781)/(.23-.1781),0,1); old falls/normal, all negative errors/height/potential/commands/acceptance/physics/fullDR/Fudan PPO unchanged. Fresh1cd8+8MLP seed/settings/cap25 match the previous failed pilot, base0/no246ac resume. Passive existing pre-reset height+episode peaks use fixed-size typed buffers, constructed real positive weights are reported. Preserve initial original resource wait/null worker phase. New frozen V5 metadata and exact reader kind prepared, old AppV6 CRLF byte-preserving source-builder correction+error preserved before output/SDK; all7 unmodified modules byte-identical. Original full-runtime/static-bank closure, original wait/charge/locks/reserve remain. Previous V17 postarchive critic-order hypothesis falsification and postreset caveat captured, no unproved permutation. All text point-in-time, model/raw suffixes skipped before stat/read/hash; original recorder validation/redaction/hashes/unique annotated tag retained with only2 exact git pathspecs/full staged-set check. Feature only/main read-only; no record/physical replay.
