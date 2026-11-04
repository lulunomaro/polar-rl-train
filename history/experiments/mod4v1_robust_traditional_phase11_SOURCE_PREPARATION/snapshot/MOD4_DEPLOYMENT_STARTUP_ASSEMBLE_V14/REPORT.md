# V14：唯一startup首次诊断汇编与新物件元数据
- 实际一次ARMASM rc0；source id0保持原30149B SHA；新object 6880B / 480f8c785deb11c702c437ee81e97ace0e27a24ff0c2b362cd5031cb7cb46134。
- 采用C13已核CPU Cortex-M4.fp.sp、--li、新-o；无APCS/FPUoverride、无__MICROLIB定义、无新-I/宏/source改写。不是旧UV数值selector精确复现。
- ELF32LE/ARM ET_REL；sections=14，code=1，symbols=112，weak=91，relocations=120。
- FILE有效tag值：{"10": 6, "18": 0, "24": 0, "25": 1, "26": 0, "27": 1, "28": 1, "6": 13, "64": 0, "7": 77, "8": 0, "9": 2}；详细scope/provenance另存。
- tag10/27/28/24/25按C13精确含义分别观察；不将0泛作UNUSED或从ET_REL flags推断hardFP。18/26规范0仍为typeUNUSED。
- 未套C浮点gate；当前仅汇编成功及scope原始元数据，C/lib PCS/merge/链接、强IRQ覆盖、地址、stackheap充足、FPSCR/WCET/实机均待核。
- undefined global/weak：SystemInit, __main, __use_two_region_memory；导入不是已解析链接。
- ONE新object文件读snapshot/SHA；sealedV10 inspect1；symbol/relocation均用同ownedbytes。六输入before-after匹配，无162Cobjects/库读取、旧test重放、fromelf/ARMCC/query/link/flash/PHY/Git。
- 旧C11仍保留其当时ASM未启动记录；新V14补独立id0object，163个source已有分段compile/assemble记录不等单次完整firmware。全部PH11pending，不自动link或重跑。
