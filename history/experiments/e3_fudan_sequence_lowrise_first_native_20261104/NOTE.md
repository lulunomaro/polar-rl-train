# E3复旦历史编码PPO：首窗关闭、Mapping修复、新窗原资源等待

## 当前目标与状态

- 目标 `goal-c490e4cc-b28b-440e-bde6-30ee956813f0`，revision 2，仍在推进。只训练E3；H1、其它专家、Registry v12和已选E3母本1cd/43090保持原状。
- 用户要求是实际起身能力与复旦训练方法对齐；更新数、CPU功能测试、进程RC0都不代表技能通过。
- 截至18:03–18:12这组实际观察：新分支尚无有效原生PPO更新；W1已关闭，W2尚在原父进程的1800秒准入等待中。禁止把派发、SDK创建、暖启动或CPU测试写成开训成功。

## 已落地的训练方法与模型

复旦参考固定commit `8204e853dfd2ed06d85a322e1a998c3d20a3be2c`：PPO加5帧监督速度编码器，不是SuperMimic/RNN/VAE。本地改编沿用raw35与critic38，历史175→速度latent3，actor38、critic41，PPO和encoder两个独立Adam；5×4更新、KL自适应、独立梯度裁剪。1cd仅完整MLP暖启动，新latent输入列为0，探索标准差重新初始化.5，旧Adam/迭代/DR不冒充完整续训。

旧MuJoCo模型实际23体/22坐标，和原生31体/30坐标不同。新独立场景已补足8导向滚轮、对齐31体质量/质心/惯量与原生关节行程；原场景未覆盖。归一化主轴四元数后的静态核对误差2.78e-17；这不是接触后端或实物一致性证明。

原行程内扫描得到469个机身与双轮着地的有限网格初态，未得到膝、轮全在机身同一端的姿态。当前训练采用合法低趴起身子目标，**没有声称覆盖视频整个腿后置翻身目标**。无私自扩大髋、曲柄、被动关节或气簧行程。

新增低趴任务与原12个跌倒+正常案例混合：低趴请求8秒，要求起到至少.23m、原重力/速度/角速度连续.5秒条件、双轮接触且机身卸载。该新增训练判据明确是工程子目标；原74案例3.2秒冻结grader不变。接下来还需独立原74例和新增低趴评测，训练奖励与事件数不替代验收。

## W1真实失败：已关闭、未学习

```text
root /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_SEQ_PPO_LOWRise_W1_20261104_174732_1793785652300963500
controller 1608668 / original_owner 1608677 / worker 1608709
GO 1793785727.498113
terminal_owner_received 1793785822.506934
outer_actual_wait 1793785823.309611
```

[原始关闭记录](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_W1_20261104_175106/CLOSED_RESULT.json>)保留：完整保存false，更新0、PPO优化器步0、编码器步0、原生策略控制0。所有内外等待完成、原计账结清、租约释放。GO至terminal约95.008821专家秒为源元数据推导，不另造账、不退款。

错误是 `MotherCache._freeze` 仅识别exact dict，而实际RSL权重为OrderedDict；暖启动后的检查进入标量相等分支，触发多元素Tensor布尔值歧义。最终source receipt也因同一检查失败而null，原null保留。不是物理/奖励失败。

W1每行original_error已为true，但全局errors数组仍采用RC-only条件而为空；这也保留为旧读者/聚合缺陷，不能把RC0和errors[]当成功。

## W2修复与实际准入等待

新worker只把exact-dict识别改为Mapping，保留嵌套Tensor对象/版本/形状/dtype检查；新owner将全局错误传播条件改为实际qualified。小型CPU回归复现旧OrderedDict错误，新Mapping检查通过，原位修改与替换Tensor均被检测；无真实PT、SDK、GPU、原生学习或旧core测试重跑。

```text
root /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_SEQ_PPO_LOWRise_W2_MAPPING_20261104_180245_1793786565596043500
role_key e3_fudan_seq_lowrise_w2_mapping_72
controller 1610275
collector job pwsh-43cf684a498c4a05
```

新450文件完整非PT源克隆与原owner source-only预检通过。旧W1源、根、once、成本、失败报告均保留，未热改运行源、未重放旧once。W2派发18:03:44；首个实际collector观察为未有worker、未有GO，原准入报Errno11 Resource temporarily unavailable，部分锁均释放。18:12一次只读显卡查询：GPU0 free24203MiB/util0，GPU1 free4613MiB/util57；空闲显存不等于原authority/finite锁可用，未干扰外部进程或清锁。

一次诊断的canonical字段白名单用了旧字段名，结果为空对象；它不证明canonical无owner。随后依据原owner源码实际字段做了一次只读精化：18:22的active_segment确为另一个任务 `MOD4V1_SCUT_RIGHT_ANGLE_STAIRS_FULLSTATE_20000ENV_1H_1793785460959945700`，owner PID 1609081，开始epoch1793785968.4116793。当次remaining_training_seconds为237782.75914430618，仅为读到时快照，未写回。详细见[原schema精化回执](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_W2_CANONICAL_OWNER_SCHEMA_REFINEMENT_V2.json>)。原W2 owner继续等原authority准入；GPU0空闲也未绕过既有canonical owner，不延长1800秒等待、不共享私有EX租约。

只保留一个W2元数据observer，15秒轮询、6000秒总界，读本任务JSON及最终新日志尾，不读模型/旧轨迹/canonical、不重复派发。W1 observer `pwsh-1a157295bc014600` 已completed且输出已收取。

## 下一步与归档

1. 继续由唯一W2 observer确认实际GO、首次真正PPO/encoder更新、完整保存与原关闭计账。等待结束亦须忠实记录，未GO不是0%技能。
2. 唯一子agent `3b92c2b6-8850-4ad3-857f-77fc0e518590` 已交付定稿pi-only冻结actor+encoder，严格initialize→act→observe混合reset历史；实际一次新N80×9步CPU合成结果为PASS，与同权重core逐步均值误差全0，14权重张量、82,505参数，无critic/Adam活体，默认校验会排除零原生更新。该测试没有真实模型/SDK/SSH/GPU/Git访问，所有训练计数为0；不代表技能验收。[推理API](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/source_fudan_frozen_mean_v1/README.md>)和[唯一CPU结果](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/source_fudan_frozen_mean_v1/CPU_RESULT.json>)已保存，旧core测试及新适配器测试均不再重跑。
3. 有实际完整候选且原窗口关闭后，才执行原74例及新增低趴独立评测；禁止为了到更新数盲目接续或替换母本。
4. 将新E3/Fudan阶段、W1失败/W2修复/实际运行、前两个用户纠正的本地演示及相关普通关闭文本，合并有意义的阶段归档。当前仍Git pending；最新已核验feature HEAD `cf86e9105c970e5456e53380901c49648bd2666f`。仅既有feature+唯一annotated trial，不push/reset main，不为归档重读PT/大轨迹/视频。


## Archive scope
This snapshot preserves both earlier user-corrected local demos, all current Fudan/history-PPO implementation and functional-only CPU checks, native W1 zero-update failure and original charge/wait/release truth, Mapping and global semantic-error propagation fixes, W2 original admission metadata, and the newly scoped frozen pi-only adapter. Dynamic W2 metadata is only true at each captured timestamp; pending learning/evaluation is not completion. The reference video whole-leg-same-end target remains uncovered by the constrained low-rise subtask. Source parity is not backend/hardware proof. Earlier models, all original 74-case grading, physics/DR/limits, H1 and Registryv12 remain preserved. Physical traces, weights and original media are path references, not reopened or copied for this archive. Later actual reports require a later meaningful stage, not replay of this archive.
