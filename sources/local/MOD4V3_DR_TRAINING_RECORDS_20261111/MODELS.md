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
