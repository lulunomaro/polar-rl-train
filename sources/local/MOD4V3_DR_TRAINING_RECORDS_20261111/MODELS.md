# Git中的完整PPO检查点

2026-11-11。61个模型ID对应61份不同字节的完整`.pt`。本表链接到Git内的实体；原始本地/目标机路径、父关系、完整recipe与选择依据见 [MODEL_REGISTRY.json](MODEL_REGISTRY.json)。

| 模型ID | iteration | 字节数 | SHA256 | 角色 |
|---|---:|---:|---|---|
| [base_partial_75m](weights/base_partial_75m.pt) | 17133 | 5,072,171 | `1c65583ca187837cc48dd389041afb25ce1f94b0897bd6d1aa4e56f8fb253047` | 历史保留/后续实际父 |
| [base_partial_101m](weights/base_partial_101m.pt) | 17556 | 5,072,171 | `6528b190d686ad4f82c78fb37e30ba1b417754d20fdca55fc032fa878c915f31` | 历史对照 |
| [stage1_joint_friction_25m](weights/stage1_joint_friction_25m.pt) | 17575 | 5,072,171 | `54fa91096ca62ea9bfdb1d64082b7b8b8a2c72d04f746bec9ae4798430b83712` | 历史对照 |
| [stage1_joint_friction_final](weights/stage1_joint_friction_final.pt) | 18166 | 5,072,235 | `c2b5299d132e41c6c02bb1a4713286640c8c79b3f4dd94272734a2bb797683e4` | 历史保留/后续实际父 |
| [stage2_spring_damping_25m](weights/stage2_spring_damping_25m.pt) | 18607 | 5,072,171 | `a4e5b2330a81cbbf087efc5df5cdc9dd79e2a6044872039fea347047dbebf06d` | 历史对照 |
| [stage2_spring_damping_cont10m_final](weights/stage2_spring_damping_cont10m_final.pt) | 18784 | 5,072,171 | `d10729cc6f86908a9b0b388c9df3ddfb8066bb52005a553290f482b34f116ebf` | 历史对照 |
| [stage2_spring_damping_cont20m_final](weights/stage2_spring_damping_cont20m_final.pt) | 19152 | 5,072,171 | `ffbabfe51ca9656d5807d667c4a94065d2cdeefd833b366b97c213c00c779d80` | 历史保留/后续实际父 |
| [stage2_spring_damping_cont30m_final](weights/stage2_spring_damping_cont30m_final.pt) | 19338 | 5,072,171 | `4343848b7bbb85f37f64c7bc2563f357ffa6b8ff7e5251bcbdf693bda9e001a8` | 历史对照 |
| [stage2b_speed_preserve_10m_final](weights/stage2b_speed_preserve_10m_final.pt) | 19336 | 5,088,873 | `a58f8923826288413b1b9197333aa3ecb2ab66f81b684ba60c66098b6d966c70` | 历史对照 |
| [stage3_external_dr_20m_final](weights/stage3_external_dr_20m_final.pt) | 19438 | 5,072,171 | `6ccdfebc0b1ec0c171d007164feeb4c3215276fe16f938531879e12835bc5314` | 历史对照 |
| [stage4_obs_noise_40m_final](../MOD4V3_SCUT_INCREMENTAL_DR_20261109/weights/stage4_obs_noise_40m_final.pt) | 20285 | 5,072,171 | `74d65e189cb496f0298d08d966329da902147f440b01c78209fda1a9c1136ca8` | 历史冻结 |
| [stage5_obs_delay_40m_final](../MOD4V3_SCUT_INCREMENTAL_DR_20261109/weights/stage5_obs_delay_40m_final.pt) | 20838 | 5,072,171 | `884cd07b3942df9c8484b905994e302906c84151f6f9c5d079a417ec98158f24` | 原7a父/谱系基线 |
| [stage3_external_cont10m_r1](weights/stage3_external_cont10m_r1.pt) | 19581 | 5,072,171 | `5d1b4013189ef93ebb27284ee478cc0f609f75997a29185185b4e128c1f8eea9` | 历史实际父 |
| [stage3_external_cont10m_r2](weights/stage3_external_cont10m_r2.pt) | 19724 | 5,072,171 | `f25cc7a71bb56576abdab7def87a91a67b3c8cc7ba369f15b4bf2b5b81acebe4` | 历史实际父 |
| [stage4_obs_noise_first_segment](weights/stage4_obs_noise_first_segment.pt) | 20000 | 5,072,171 | `845bf1cba9e89772da0710375317619a657174c2d8911700d5b01d43e291c403` | 历史实际父 |
| [flat_action_delay_stage6_40m](weights/flat_action_delay_stage6_40m.pt) | 21361 | 5,072,171 | `c3345a4e71be1e533c89b7073bd977bcc5dcc5fc51710e8147dff49f74ccdf0c` | 旧失败试验对照；不重定Step6冻结身份 |
| [flat_action_delay50_stage6b_60m](weights/flat_action_delay50_stage6b_60m.pt) | 21642 | 5,072,235 | `04e07949750eace05ed1100db7418775e3bd0cd721563c2e85a4ff5998ebdad0` | 旧失败试验对照；不重定Step6冻结身份 |
| [flat_action_delay25_stage6c_40m](weights/flat_action_delay25_stage6c_40m.pt) | 21390 | 5,072,171 | `6505500c1d2c0c158bf60236e2c9ccc251ee3b4d4f7c347b61df089a8e930a77` | 旧失败试验对照；不重定Step6冻结身份 |
| [flat_scut_delay_stage7a_20m](weights/flat_scut_delay_stage7a_20m.pt) | 21103 | 5,072,171 | `0da8f78e30cae952a9712234bd32f75d0093b3e43344007b7fa1b0395fb37fb2` | 旧失败试验对照；不重定Step6冻结身份 |
| [legacy7a_005m](weights/legacy7a_005m.pt) | 20904 | 5,072,171 | `cf5a89affea2ef8b1ebd0887e9c8276243455a56809e9cdf20a00182c6d77b7d` | 旧7a退化时间线 |
| [legacy7a_010m](weights/legacy7a_010m.pt) | 20971 | 5,072,171 | `c2c29d7b940a0198d30e67295cb482c8bd1260effa3d0f2c6ec5b7bc8fd09533` | 旧7a退化时间线 |
| [legacy7a_015m](weights/legacy7a_015m.pt) | 21038 | 5,072,171 | `a52746b64afe0502a5ec8d93a1db3ff6b116f53eac5b68472854515b03832f3d` | 旧7a退化时间线 |
| [physical_delay_adapt_005m](weights/physical_delay_adapt_005m.pt) | 20905 | 5,072,171 | `bc22ea7a34c7310f56baeb676ca40bdc0a26da00cf1f0f21a7b124f0a490698f` | 5m试验，未接主线 |
| [square_005m](weights/square_005m.pt) | 20904 | 5,072,939 | `5099d622531430bddf0f63f6f450177111952fe15f4923136823eb525e8de475` | 5m检查点 |
| [square_010m](weights/square_010m.pt) | 20970 | 5,072,939 | `cdfcfe6da10642de58149952e7c88326a65f5ac835ee39b0c61bc480e1b78048` | 5m检查点 |
| [square_015m](weights/square_015m.pt) | 21036 | 5,072,939 | `f4960781490a4de9e45fc97a477d890ab4b3a717edbd39c43581fa059278e483` | 实际续训父 |
| [rangefix_005m](weights/rangefix_005m.pt) | 21102 | 5,072,939 | `b30d3fbab1adc1d14d68a9d551034899137380c5f7ee7d049e4a5f50653541eb` | 5m检查点 |
| [rangefix_010m](weights/rangefix_010m.pt) | 21168 | 5,072,939 | `3dab58d00d5044e4e46fafd3c339c7c81c962240c2f8a5203f42421e020a1630` | 5m检查点 |
| [rangefix_015m](weights/rangefix_015m.pt) | 21234 | 5,072,939 | `74c25dd19708148808d1928fc4d6eb1278239fcdc6ab97598d866cf477dc561f` | 实际续训父 |
| [mass_005m](weights/mass_005m.pt) | 21301 | 5,581,161 | `a1133ccf49af5c975f2f2fbe1e0db983815f7cde78c349ae9e2e8ab8c4d60cd1` | 5m检查点 |
| [mass_010m](weights/mass_010m.pt) | 21366 | 5,581,161 | `c0f312a91997e6859e58477d05cba6cfc8d068d45eb372cb06f2d4b1f5fef5c7` | 5m检查点 |
| [mass_015m](weights/mass_015m.pt) | 21431 | 5,581,161 | `94d8baa1671538170283d427852dccd426c7d281f6ab24e212d7187c84f644f3` | 5m检查点 |
| [mass_020m](weights/mass_020m.pt) | 21497 | 5,581,161 | `e9e6480dd18d397632d3b5c6552d3053436afb7dba326c7b58cd3c8e689c3e11` | 5m检查点 |
| [mass_025m](weights/mass_025m.pt) | 21561 | 5,581,161 | `8d3b110dcb0fc336706fa5991113bfc446292490a36c3c69c05c154a7bdbb436` | 5m检查点 |
| [mass_030m](weights/mass_030m.pt) | 21626 | 5,581,161 | `7fb235249b899bb177c398cd8594b952fd1edae690fddc47f60790d329d9692e` | 5m检查点 |
| [mass_035m](weights/mass_035m.pt) | 21690 | 5,581,161 | `8bcdd0b4fb13dd241108d10ed73bb302bcf8ed7f132ea5b7912aa9c0ba6210c3` | 5m检查点 |
| [mass_040m](weights/mass_040m.pt) | 21754 | 5,581,161 | `23c112b16e9629215c7265124925daaf0f9b6bbbb62be61689c714ba1fc7a772` | Step7主冻结 |
| [effort_005m](weights/effort_005m.pt) | 21821 | 5,746,209 | `82b5e1e84ae425c693585629080a8fbbbd291993214ddffaf0485d9bba1aa17d` | 5m检查点 |
| [effort_010m](weights/effort_010m.pt) | 21886 | 5,746,209 | `5808839cabee9c9350aa36f74497bb2e0f8c733591d2216537b429ccf27d6f75` | 5m检查点 |
| [effort_015m](weights/effort_015m.pt) | 21952 | 5,746,209 | `01cbebc04852710ea3a287f9f454ec74fbf4a065ac063d941f1e7d6615debc13` | 5m检查点 |
| [effort_020m](weights/effort_020m.pt) | 22017 | 5,746,209 | `0a1a8ccb5d1f5cec1582e071798597baa55e43dfb13e4eba6472a7fd82f3b22c` | 本轮选中的训练候选 |
| [effort_025m](weights/effort_025m.pt) | 22082 | 5,746,209 | `891278fde7face8b2d21145c6d7fa32c78a76847b82dba440c15880269e515d0` | 5m检查点 |
| [effort_030m](weights/effort_030m.pt) | 22146 | 5,746,209 | `16750c67f32db5e6d3a9b0825eb269bfafe6a6511395c7908599d2611603eb7b` | 5m检查点 |
| [effort_035m](weights/effort_035m.pt) | 22210 | 5,746,209 | `5c9582742713e7551e8e8b3ab16ea0f67b1a8e6b6d88e2d795d7a0d33741cc91` | 5m检查点 |
| [effort_040m](weights/effort_040m.pt) | 22274 | 5,746,209 | `e56f6d4888ab1fcb02523c89d435732a3c77a78bdf750b35e77ea3e1f03495a1` | 末检查点，退化对照未选 |
| [material_005m](weights/material_005m.pt) | 21818 | 5,746,209 | `0262be5af09410397b08ba330e98f6f1462ce93206952fa452cf7a3f9b496fe8` | 5m检查点 |
| [material_010m](weights/material_010m.pt) | 21882 | 5,746,209 | `49a2bb7b53d3d88b7d47dfc3d5eb15999c5fd8fcfd3a1cf3f0a67d96030c71a1` | 本轮选中的训练候选 |
| [material_015m](weights/material_015m.pt) | 21946 | 5,746,209 | `ed6809ea6d1be0d2aee36e0817d4481f6462c6dec7a1e2321880e2e202e86c5e` | 5m检查点 |
| [material_020m](weights/material_020m.pt) | 22010 | 5,746,209 | `f095b9ad437ee732fb1053fcfedae150a33fe7b32b3f564923cb50b477f7818f` | 5m检查点 |
| [material_025m](weights/material_025m.pt) | 22073 | 5,746,209 | `c9f104505eca73dd593093092d861749dc82fbb8d27caf96b58ffa1a4851a268` | 5m检查点 |
| [material_030m](weights/material_030m.pt) | 22136 | 5,746,209 | `d89bdbf5f8e57d77e13d824a3eba32d717fe00464903b8a67b54806324e72941` | 5m检查点 |
| [material_035m](weights/material_035m.pt) | 22198 | 5,746,209 | `d10ebb4b7b2f3ff9aa6bf226fec35de434654d6cf81b828ea3730ae0bc08b1fa` | 5m检查点 |
| [material_040m](weights/material_040m.pt) | 22260 | 5,746,209 | `6f9a95802f235fd15c647b0979323ad5b79ee28f6c5609976703b5764a983104` | 末检查点，退化对照未选 |
| [push_005m](weights/push_005m.pt) | 21948 | 5,746,273 | `02c169b6de583846ae47bfbf5a3546aae1a408649617131842cac649d88a4d28` | 5m检查点 |
| [push_010m](weights/push_010m.pt) | 22013 | 5,746,273 | `c998a8de29d70974ad826cc2de1d54451a6428f495ebe94091710a20a9a64de6` | 5m检查点 |
| [push_015m](weights/push_015m.pt) | 22077 | 5,746,273 | `96fedcccdf905e41e29aa00f37592d5f9fe47eb87f3ddd55494220bbb27e73c1` | 5m检查点 |
| [push_020m](weights/push_020m.pt) | 22141 | 5,746,273 | `b3eec7bae3045b24a95ea7cd2940a3e1f0b062841cc47ab1785a627bea36408a` | 本轮选中的训练候选 |
| [push_025m](weights/push_025m.pt) | 22205 | 5,746,273 | `28131a35c9d5c3320f2b4e4475187ee2916672d6e38c2befdebc8f042771ec02` | 5m检查点 |
| [push_030m](weights/push_030m.pt) | 22269 | 5,746,273 | `1cbe4ae5e34423aa2ca298db06ee57904b3c18bfa39758da361bbd0cbdc9b805` | 5m检查点 |
| [push_035m](weights/push_035m.pt) | 22332 | 5,746,273 | `93485c8fc9881513f177db76930f05a56b220e1bd8c5519cee700b67c7e466cc` | 5m检查点 |
| [push_040m](weights/push_040m.pt) | 22395 | 5,746,273 | `46fa51e6b8ccaf1ad49c4263c189a1be7c394ff1300b8af264083831af6e8d3f` | 末检查点，退化对照未选 |


## 后续合并DR轮：完整PT实体

以下模型在独立本轮目录保存；首次61份档案仍按原tag固定。

| 模型ID | iteration | 字节数 | SHA256 | 角色 |
|---|---:|---:|---|---|
| [remaining_first](../MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_first_complete.pt) | 22142 | 11,044,601 | `d95c25c0504c2c1e39bc6ba20c980b7043ab071b0d43ce90237b34276a1446f2` | 检查点/原始回归证据 |
| [remaining_005m](../MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_005m.pt) | 22203 | 11,044,601 | `71df98c5d5c50f1407175cd60b7c4760618287cf5477a760884061494ec71594` | 检查点/原始回归证据 |
| [remaining_010m](../MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_010m.pt) | 22265 | 11,044,601 | `978994b2614f4454f96bfd0ac264f00cbe3ffd219a5372487c558435503dbd15` | 本轮保留候选 |
| [remaining_015m](../MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_015m.pt) | 22324 | 11,044,601 | `e925f176c74e375e79c5f6fc75ebacea6c7ebdac6976b4d08284fb915a8585ba` | 检查点/原始回归证据 |
| [remaining_020m](../MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_020m.pt) | 22384 | 11,044,601 | `4290fe3973d5e4e9c9659b46e7fd3aa08dd3fd7c4fef9963cb8b2eb2fd9f558e` | 检查点/原始回归证据 |
| [remaining_025m](../MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_025m.pt) | 22443 | 11,044,601 | `bf2d70f3b0be58e45ed0049d3eead802b8658761a255f5551c072ba70f2f36f3` | 检查点/原始回归证据 |
| [remaining_030m](../MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_030m.pt) | 22501 | 11,044,601 | `0c0941adee768f54b3a6ee48ca08f266d06a9109553bee4c03f864bdb2e797ca` | 检查点/原始回归证据 |
| [remaining_035m](../MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_035m.pt) | 22560 | 11,044,601 | `cb5ac70c5d6f65fc2a02e76695f32e6dfaa13d62791dbf5eb12bffec1637082f` | 检查点/原始回归证据 |
| [remaining_040m](../MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_040m.pt) | 22618 | 11,044,601 | `957653bfaf2c699ef888225ee747fb48563ffaad62bc0f46276e995ba708dfb7` | 检查点/原始回归证据 |


## 第二轮混合采样：完整PT

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [mixed2_first](../MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/model_first_complete.pt) | 22266 | 11,048,951 | `dc3809423e707ff665c285590112a73b39854a487c9e0a8d0a439c9bee896516` |
| [mixed2_005m](../MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/model_005m.pt) | 22326 | 11,048,951 | `627c1d9f5458b78655034a8ddb457548d3fe37c100bbec604d17bb7861ce749c` |
| [mixed2_010m](../MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/model_010m.pt) | 22386 | 11,048,951 | `dcbc1421061a73a8a1c4b2d936737178d58eb4d999239938c40653f5ac76a05e` |
| [mixed2_015m](../MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/model_015m.pt) | 22444 | 11,048,951 | `3dd0aac8b562b4c2a93ac7fd4afb1af53c5a83daad7681ea44ebce9e47ff4532` |
| [mixed2_020m](../MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/model_020m.pt) | 22502 | 11,048,951 | `15775671f430cda69b1f268a230d85c5d1a74878760d26625afefb759e792c20` |
| [mixed2_025m](../MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/model_025m.pt) | 22560 | 11,048,951 | `709cac39846c0eb61225cdf967d56aa145e1e6957ccdf9faab43cb7aeeae87b9` |
| [mixed2_030m](../MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/model_030m.pt) | 22617 | 11,048,951 | `87eb672cfee8885eaae2ef51b0698efb12919a14042555ce98dfec98dee26908` |
| [mixed2_035m](../MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/model_035m.pt) | 22674 | 11,048,951 | `d303f044e99119d8753f13dc47df2eb0a8ecbb8c8ce3a35b14bfbc0380e07f80` |
| [mixed2_040m](../MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/model_040m.pt) | 22731 | 11,048,951 | `81ed3fbb27152f68c2c5f19a1c2f0c74197f12a957ae5be6f33333f63ef3d0a0` |


2026-11-11回放复核：同一mixed2_020m在MuJoCo名义超速、PhysX名义欠速；0/5ms复测保留方向，原训练actor观测与paired包装逐帧最大差0。尚无新确认的输入回放bug，物理/执行差异未定位，不能只凭跨引擎差异定为策略退化。完整DR同时有欠速和超速样本。详见`sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/replay_environment_check/REPORT.md`；未启动第三轮训练。


## 双侧平方惩罚加倍：运行中

仅首完整检查点，尚不代表完成轮次或达标。

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [square1_first](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_first_complete.pt) | 22266 | 11,048,951 | `f8384096a14d2942c688abfa8090b14ce09e6189f03786b671dfe861c39ce384` |


## 双侧平方惩罚加倍：完整40分钟检查点

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [square1_first](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_first_complete.pt) | 22266 | 11,048,951 | `f8384096a14d2942c688abfa8090b14ce09e6189f03786b671dfe861c39ce384` |
| [square1_005m](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_005m.pt) | 22327 | 11,048,951 | `32313574de5b11b136529bda6d055286bad0558db0df271ec1f4b1a1d0e06e6e` |
| [square1_010m](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_010m.pt) | 22386 | 11,048,951 | `3c07572a3c7fef8325486d33ff1c99fa5aa2331769f5c8669d3af37ea9573bb8` |
| [square1_015m](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_015m.pt) | 22445 | 11,048,951 | `ab8f268f5352c747a06d73404415dd53ca13f6839b37bc1a3bebf834384b2914` |
| [square1_020m](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_020m.pt) | 22503 | 11,048,951 | `6aafe9ed4b88e0d27d0380bbc83b2f6d1b31a471ef284f74bb758f83467740fc` |
| [square1_025m](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_025m.pt) | 22561 | 11,048,951 | `d5027e61196517f2e88e7b91a80fb56639d0baeb7b123355438396abfbc5dc16` |
| [square1_030m](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_030m.pt) | 22618 | 11,048,951 | `d5e176401c20dd1b88a74003f7d4993aadc9a9cda301f042953de08fb6108851` |
| [square1_035m](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_035m.pt) | 22676 | 11,048,951 | `67a87a00faf53eed4dae0877832e8f72128b82c810aee342fd8dab0ddf66e801` |
| [square1_040m](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_040m.pt) | 22732 | 11,048,951 | `d86f21e2aa730e77d687ecf009a915a485a67b3bfd6c2d3be489bfee2556a52a` |


## MOD4 R0浅地形：完整40分钟检查点

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [rough_r0_005m](../MOD4V3_ROUGH_R0_20261111/weights/model_005m.pt) | 22660 | 11,324,633 | `b914bd2a29898b6270350d20ec3ec6e9086c31795ab12f3c93e41c64a84e3531` |
| [rough_r0_010m](../MOD4V3_ROUGH_R0_20261111/weights/model_010m.pt) | 22702 | 11,324,633 | `87925dd405b84c2a54aecc927f25bbc2db8247a2769fcaa43f5768f9f1db6b43` |
| [rough_r0_015m](../MOD4V3_ROUGH_R0_20261111/weights/model_015m.pt) | 22743 | 11,324,633 | `21af8bd84d57e22db1e7ccf5ca0eb721989432b71bfaa721f5bec2792621e095` |
| [rough_r0_020m](../MOD4V3_ROUGH_R0_20261111/weights/model_020m.pt) | 22785 | 11,324,633 | `64affb5794f5518f2b84611ab7d3904aef95b7e1ea660e1efd87820102cc14d6` |
| [rough_r0_025m](../MOD4V3_ROUGH_R0_20261111/weights/model_025m.pt) | 22826 | 11,324,633 | `3ad4a74b5df670bc2828e13d8b4ca2e73fcee53d0cf1087c979df61e9654601c` |
| [rough_r0_030m](../MOD4V3_ROUGH_R0_20261111/weights/model_030m.pt) | 22868 | 11,324,633 | `9316106bb24142475aaf3566bf836001d347a1077e7f2566c9377a0fa6231d4f` |
| [rough_r0_035m](../MOD4V3_ROUGH_R0_20261111/weights/model_035m.pt) | 22910 | 11,324,633 | `0cbe8edc81986f3d5bd40bb00dd6423f284d8151e2af95847eb0fd64a2464ce8` |
| [rough_r0_040m](../MOD4V3_ROUGH_R0_20261111/weights/model_040m.pt) | 22952 | 11,324,633 | `501fc89f254937527beaa893ffab2f0e8f2e15862b22ef963a683ed1f170483a` |
| [rough_r0_first](../MOD4V3_ROUGH_R0_20261111/weights/model_first_complete.pt) | 22619 | 11,324,633 | `e8235ef8443de1a7b49904e1676039c6a7f02c267105388313fb49c1ed1a4374` |


## Flat速度平方项1.5实验

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [flat15_005m](../MOD4V3_FLAT_SQUARE15_20261111/weights/model_005m.pt) | 22679 | 11,048,951 | `7605ead60c65004a41a29f0b2c8ce4bb8f22ecd9326b737708a29d454b978632` |
| [flat15_010m](../MOD4V3_FLAT_SQUARE15_20261111/weights/model_010m.pt) | 22739 | 11,048,951 | `e5999df2b04d93db31f26c3ef1570286c6b769ae32346f98ce59bf64375125e7` |
| [flat15_015m](../MOD4V3_FLAT_SQUARE15_20261111/weights/model_015m.pt) | 22797 | 11,048,951 | `99038325c169217e92289ce7feec3c43f629f145097eea356eb1d956161a186e` |
| [flat15_020m](../MOD4V3_FLAT_SQUARE15_20261111/weights/model_020m.pt) | 22856 | 11,048,951 | `a5102af62938f6bf472855edba34c5f10efce061eecaeb3aebee34815fe7cf87` |
| [flat15_first](../MOD4V3_FLAT_SQUARE15_20261111/weights/model_first_complete.pt) | 22619 | 11,048,951 | `865cd88a45a41c64904e69350f38176bdf3ae5aded1185dac0924b96e3190a58` |


## RoughR0接续速度平方项1.5实验

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [rough15_005m](../MOD4V3_ROUGH_R0_SQUARE15_20261111/weights/model_005m.pt) | 22899 | 11,324,633 | `457f604a9bb140a0957d59ad2649f6aa1693e3b0783ba89ccb5b8b1d3b14e51c` |
| [rough15_010m](../MOD4V3_ROUGH_R0_SQUARE15_20261111/weights/model_010m.pt) | 22941 | 11,324,633 | `ece8c41163da29b37a3d1072f942427196db596b22b2813ae7c93b21b34bee89` |
| [rough15_015m](../MOD4V3_ROUGH_R0_SQUARE15_20261111/weights/model_015m.pt) | 22983 | 11,324,633 | `081a5f96e029075ea27f462d8d123d84edaca49643b94dffa9d5e11d40b9d280` |
| [rough15_020m](../MOD4V3_ROUGH_R0_SQUARE15_20261111/weights/model_020m.pt) | 23025 | 11,324,633 | `44ef796fdc92b37ccefa024c688b856df2a178e2d350e79cd2cb4ec94518c9a0` |
| [rough15_first](../MOD4V3_ROUGH_R0_SQUARE15_20261111/weights/model_first_complete.pt) | 22857 | 11,324,633 | `d46d5b7a4a4e6c8fb087dfdcdd1000daa080f4f8c36ec381663e2acd4ebbba41` |


## RoughR1首轮40分钟

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [r1_005m](../MOD4V3_ROUGH_R1_20261111/weights/model_005m.pt) | 22891 | 11,324,889 | `71af95ae3c3282d6dd8bbacbb59d3972d2db0ea623ff7290cd2b004aa94fcaf8` |
| [r1_010m](../MOD4V3_ROUGH_R1_20261111/weights/model_010m.pt) | 22925 | 11,324,889 | `959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022` |
| [r1_first](../MOD4V3_ROUGH_R1_20261111/weights/model_first_complete.pt) | 22857 | 11,324,889 | `1c318faf8f9cca8a7884333603b9a98855dc96e05bb738b9b28fee5e4c68e4c5` |


## RoughR1平方惩罚2.0接续

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [r1sq2_005m](../MOD4V3_ROUGH_R1_SQUARE2_20261111/weights/model_005m.pt) | 22959 | 11,324,889 | `fb7ed1f7c46990b15b7a258c4318f6587430568f4ce9ef57bccd98dfefb4b90d` |
| [r1sq2_010m](../MOD4V3_ROUGH_R1_SQUARE2_20261111/weights/model_010m.pt) | 22993 | 11,324,889 | `53256d1d09e6b6e0244591820bff455557021968e4937f31921005bb5ac764e4` |
| [r1sq2_015m](../MOD4V3_ROUGH_R1_SQUARE2_20261111/weights/model_015m.pt) | 23027 | 11,324,889 | `22513a6e935f1c2ab6204561ef2c81ab6ae0d8974436c7438cbfd8f5ba764c7a` |
| [r1sq2_first](../MOD4V3_ROUGH_R1_SQUARE2_20261111/weights/model_first_complete.pt) | 22926 | 11,324,889 | `e32e17ad887417025cc4834b9d850d455ce6e0ee69de5a619394593c6b19308e` |


## RoughR1平方加绝对三次项接续

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [r1cubic_005m](../MOD4V3_ROUGH_R1_ABSCUBIC_20261111/weights/model_005m.pt) | 23061 | 11,325,017 | `4d0976cf1e7995e50d4084926701209982f26c2606a3c3e8c896f2df0de1efd8` |
| [r1cubic_010m](../MOD4V3_ROUGH_R1_ABSCUBIC_20261111/weights/model_010m.pt) | 23095 | 11,325,017 | `581870601676c62f250057fcfc33c8498c0355c9109bc1e7d1997d9384c34b94` |
| [r1cubic_final](../MOD4V3_ROUGH_R1_ABSCUBIC_20261111/weights/model_final.pt) | 23110 | 11,325,017 | `ab079de2569a7acef19fa0fa31d557fa0ee2669bb1c4fab69172ea3de230d2b6` |
| [r1cubic_first](../MOD4V3_ROUGH_R1_ABSCUBIC_20261111/weights/model_first_complete.pt) | 23028 | 11,325,017 | `34bb4a5b8566b22496811df586bfe1fb9e263b7e9c11592ef24b80f1f548af39` |


## RoughR1原奖励第二轮40分钟

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [r1round2_005m](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_005m.pt) | 22959 | 11,324,953 | `0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f` |
| [r1round2_010m](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_010m.pt) | 22993 | 11,324,953 | `c25f95867ada903e59ab0289c857d1038900e1e1f962783bbb536a24faaac9b5` |
| [r1round2_015m](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_015m.pt) | 23027 | 11,324,953 | `9b0af25593b7b4399af470c91ec6f2e0e7d83bba3a025379493aa17c0d40fbef` |
| [r1round2_020m](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_020m.pt) | 23061 | 11,324,953 | `5e40cc62d26aa6c6c3a6cddeec81a01b9086e98d0a1d9045febedafaae9bc826` |
| [r1round2_025m](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_025m.pt) | 23095 | 11,324,953 | `493501ca0d651431fadaec833a34868505034bd2656c6f25cbed91f486a77f1e` |
| [r1round2_030m](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_030m.pt) | 23129 | 11,324,953 | `81d214520c97b004b94bef8abf4b4bde041ff1573e3a6f99192fc6c3137c1c20` |
| [r1round2_035m](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_035m.pt) | 23163 | 11,324,953 | `94ed1094ea63816bd0a80cde78ce3dc63844513735a0893873245ccdcbeff992` |
| [r1round2_040m](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_040m.pt) | 23197 | 11,324,953 | `28300a51e237011bf7c455143d684351723f6b769e807d14f69341fa4b21bd9a` |
| [r1round2_final](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_final.pt) | 23197 | 11,324,953 | `28300a51e237011bf7c455143d684351723f6b769e807d14f69341fa4b21bd9a` |
| [r1round2_first](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_first_complete.pt) | 22926 | 11,324,953 | `ac5f022954f844e8fff6dffbd0177f5bda51585a06ca268ff115f52718e7bb7c` |


## RoughR2低落高腾空落地40分钟

本轮新权重未综合晋升，继续保留r1round2_005m；r2_005m仅实验备选。[选择与同批结果](../MOD4V3_ROUGH_R2_20261112/DECISION.md)。

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [r2_005m](../MOD4V3_ROUGH_R2_20261112/weights/model_005m.pt) | 22993 | 11,626,993 | `2fec0707f53e3f1b65440b3e27c59fe958dffbcb951cc0bc588593d715ef4680` |
| [r2_010m](../MOD4V3_ROUGH_R2_20261112/weights/model_010m.pt) | 23027 | 11,626,993 | `fc77def49d310477ae59af77bf74a51f87d584ad0534e9f36fc23a4818a8cc54` |
| [r2_015m](../MOD4V3_ROUGH_R2_20261112/weights/model_015m.pt) | 23061 | 11,626,993 | `9dd06c35a612f23b38160b1c5dae42f8411d718a24704271f7cb6c77f563d746` |
| [r2_020m](../MOD4V3_ROUGH_R2_20261112/weights/model_020m.pt) | 23095 | 11,626,993 | `293c8604a36440958ffba555412defea00496cfc0fc70e68e146185fcb194b7d` |
| [r2_025m](../MOD4V3_ROUGH_R2_20261112/weights/model_025m.pt) | 23129 | 11,626,993 | `0a6ff95e80e7d626b7c7196d9bd33325c063fb3a956c333404d01ae2de538fff` |
| [r2_030m](../MOD4V3_ROUGH_R2_20261112/weights/model_030m.pt) | 23162 | 11,626,993 | `dcb9fd7a6f11b3915c93bc5275741665d949bd5da27306c5106029e68931d71a` |
| [r2_035m](../MOD4V3_ROUGH_R2_20261112/weights/model_035m.pt) | 23196 | 11,626,993 | `fb398a04c2c0b42c5a8d3abc00f93d3738a1402c6936e8b3b7616f79ce220171` |
| [r2_040m](../MOD4V3_ROUGH_R2_20261112/weights/model_040m.pt) | 23230 | 11,626,993 | `76325bb137e4e15acb2930dc543e5bf0c9893913b8598cf938ca1b45f50eddfa` |
| [r2_final](../MOD4V3_ROUGH_R2_20261112/weights/model_final.pt) | 23230 | 11,626,993 | `76325bb137e4e15acb2930dc543e5bf0c9893913b8598cf938ca1b45f50eddfa` |
| [r2_first](../MOD4V3_ROUGH_R2_20261112/weights/model_first_complete.pt) | 22960 | 11,626,993 | `32ded960cf1a2aee2b5d50d5de4f1c23439b70946028be635117088a01917a91` |


## SCUT Rough-v0统一科目2小时

| 模型ID | iteration | bytes | SHA256 |
|---|---:|---:|---|
| [roughv0_005m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_005m.pt) | 22994 | 11,327,321 | `3a3fc98861c827a01812cdc9d3bf375362a6400c39d3bded48123dc0bc2e168c` |
| [roughv0_010m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_010m.pt) | 23029 | 11,327,321 | `8cde6b9d685ef9e6aeb4b1dc67d106058dc052e80347f82ae52406f908fd7feb` |
| [roughv0_015m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_015m.pt) | 23065 | 11,327,321 | `2583cde4e30b73bedfa08b7ca5afc8fa7565a82d4a6a3985aad81e3638ecddcb` |
| [roughv0_020m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_020m.pt) | 23100 | 11,327,321 | `599e26c2dd6c0570fab75f3506e7105dd4e6110be5435c902eca84942b465e39` |
| [roughv0_025m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_025m.pt) | 23135 | 11,327,321 | `544846b94eb3c2b6c64c3aaa66538c8ecf6e7876e5d30423a434cf4c6aed71b1` |
| [roughv0_030m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_030m.pt) | 23170 | 11,327,321 | `e82d7f38ef0c777820d864a02383177cd99a3537c26d753379231d227fc0c1c8` |
| [roughv0_035m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_035m.pt) | 23206 | 11,327,321 | `d4f00fff74bacb04f3036cd7e44515e0c736d25025f79e0a314ecfa6de7e0c68` |
| [roughv0_040m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_040m.pt) | 23241 | 11,327,321 | `7be48994088536eb250d3e6a9acd09011fd6d8a1db895a2cc8811f40aa84febb` |
| [roughv0_045m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_045m.pt) | 23276 | 11,327,321 | `a4aa4537a60be2b4231c73084dd8fce7084f070b5e6e85585831e47af1439610` |
| [roughv0_050m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_050m.pt) | 23311 | 11,327,321 | `e79c923635201c6cbed0bcb4662d56c3c2ea1055de14c39ea044575b1b2dbc0a` |
| [roughv0_055m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_055m.pt) | 23347 | 11,327,385 | `3b3c5f5657bbab948809f642f1b9e77f0384a05dcfd93a66fc2cbe214435d097` |
| [roughv0_060m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_060m.pt) | 23382 | 11,327,385 | `924f773003e1ed812fa58128c7b72b2322bd1146fd12ffb28f43eaffafc0d216` |
| [roughv0_065m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_065m.pt) | 23417 | 11,327,385 | `a88276df262fd956db8b6bf260f9d949096f3cb954ddccc2c69089fb4a82257b` |
| [roughv0_070m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_070m.pt) | 23453 | 11,327,385 | `116af7f85b8016aa59c52629de3e3854f1050310cf2d1e94e66dfe2928f685c0` |
| [roughv0_075m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_075m.pt) | 23488 | 11,327,385 | `28d0e3aedbaccc96e5925b2314585b1ff2f69f2285d04fa5501ce570433c8bf4` |
| [roughv0_080m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_080m.pt) | 23523 | 11,327,385 | `85085978eaff334a6702d1ecb251cdb4a69cfff00eb891558dcd70cc11caac5e` |
| [roughv0_085m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_085m.pt) | 23559 | 11,327,385 | `701bd5c8e7cf9c80854a869871c449c59b2c3a792561d7de0fe30aba98d608ea` |
| [roughv0_090m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_090m.pt) | 23594 | 11,327,385 | `89db8bf19041a7954f12cf43dc58caded32c8562a0f088f763d4be0baf5ae1a1` |
| [roughv0_095m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_095m.pt) | 23629 | 11,327,385 | `3914c8b59401aa2ee5e3447ed60fc0e1eb788fe477859da94d8a9a22f6c01cf8` |
| [roughv0_100m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_100m.pt) | 23665 | 11,327,385 | `001028396205e7d44d69ac5af36cdbb638cc26b97daeea29439f84952a58f6e9` |
| [roughv0_105m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_105m.pt) | 23700 | 11,327,385 | `719a28b8c751dacf82539b6316e4394658ab740ba7bea9a40131ee6a65ae9cf5` |
| [roughv0_110m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_110m.pt) | 23736 | 11,327,385 | `16a338f1400171121877dabbd50e7367e2edff792fadbf150b89ec7eb4698724` |
| [roughv0_115m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_115m.pt) | 23771 | 11,327,385 | `d03510eb7dbc933db59a4e6399ff0ab4be7d4d94a519dc29dc8a3c85d618a2f8` |
| [roughv0_120m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_120m.pt) | 23807 | 11,327,385 | `87537baddfbecef424db219e7b86ea140ec4e767c67668b8c7a2cc0849995c09` |
| [roughv0_final](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_final.pt) | 23807 | 11,327,385 | `87537baddfbecef424db219e7b86ea140ec4e767c67668b8c7a2cc0849995c09` |
| [roughv0_first](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_first_complete.pt) | 22960 | 11,327,321 | `c550caacc364882302376bcc15679589c0df72d97e08441a1c661bfddf5d4674` |


统一SCUT Rough-v0两小时与8组验收已完成；本轮26份完整PT均归档，综合接续保留r1round2_005m，100m/120m未晋升。[本轮模型选择](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/DECISION.md)。当前29阶段/164完整训练PT记录。
