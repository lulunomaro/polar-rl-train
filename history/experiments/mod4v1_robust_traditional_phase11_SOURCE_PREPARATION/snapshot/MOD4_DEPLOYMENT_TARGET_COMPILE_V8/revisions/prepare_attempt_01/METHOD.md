# V8：原UNSTARTED C-only的一次独立续编前缀

1. 本轮catalog只有Office/ACL类，无当前ARM/ELF任务匹配skill；采用文件工具与现有Python标准库、已知安装ARMCC5u6。仅本新目录写入，旧V1/V2/V3/V4/V5/V6/V7全部只读。
2. 先核父scope和四项sealed V7 SHA、V6 literal/result pin；从V6 execution_order与原unstarted交集精确提取161 C，保持顺序。排除已消费main(id1)，原ASM(id0)仅保存原计划与UNSTARTED，不启动。不开旧project parser、不跑version/help/旧QA/40。
3. 一次冻结所有161 C原argv及源：唯一argv差异为原-o物件路径改到V8；stdout/stderr仅V8日志路径变化。实际CWD、trusted armcc.exe、相对源名、所有include（含两个既有overlay）、宏/重复宏、CPU/C99/-O1/-Otime/interwork/split_sections/diag_error全部原样。逐TU逆变换必须精确等于V6。
4. 新plan冻结前fresh pin恰好161个所选C源并比原saved source_pin；两个已批准raw header overlay比V6既有pin。不是423全树重hash，也不是所有间接头依赖已穷尽。执行前及返回后核当前源/header pins，漂移即止。
5. 新executor、sealed V7 reader、原ABI expected、所有计划和小input pins在首个TU前固定到PREEXEC。编译只direct subprocess argv、cwd和独占stdio文件，不用shell/管道/UV/hooks；每TU最多一次。任何既有账本/结果阻止重启执行。
6. 先写并flush ledger的attempt/native-begin，再启动可信armcc。native-return后立即保存最低COMPILE_RESULT/checkpoint，再作一次该新物件的sealed V7 inspect_elf。新成功compile与scope认可prefix分列；编译成功而reader容量或ABI停止，不抹掉compile成功。每次返回/stop先落最低结果，再报告。
7. 保留sealed V7所有容量（64KiB物件、256 sections等）不变；ParseError中明确cap/bound容量项分类READER_CAPACITY_STOP；真正截断/错误格式、same-scope冲突及不支持格式分别保存后停止。无fromelf fallback、cap扩张、新probe或重编。每个有输出的成功物件最多一次reader调用。
8. 原V6非type gate逐项不改：ELF32/LE/ET_REL/EM_ARM与FILE CPU13/profile77/Thumb2=2/FP6/HardFP1/VFPargs1/denormal1或2；缺项为UNKNOWN并停，不借本次类型规则放宽其他字段。
9. 对每个SHF_EXECINSTR section和真实SYMBOL override，18只接受2或有官方来源的0/UNUSED，26只接受1或有官方来源的0/UNUSED。规范0是类型禁止使用契约（显式或规范省略经继承），不是猜宽度。UNKNOWN、reserved/other值、scope冲突均停；输出完整provenance。实际没有SYMBOL不能声称真实SYMTAB路径覆盖。
10. 首次编译错、退出0但缺/空输出、源漂移、格式/容量/ABI未知或冲突、executor异常即停全部后缀。保留物件、原始日志、accepted prefix和未启动IDs；没有自动补header、改flags、删输出或再试。原ASM始终0，fromelf/version/probe/link/flash/CAN/SPI/PHY/Git/agent/root-goal均0。
11. 原V6历史compile1/postABI认可0/gate=false与V7单物件静态解释单列，本次C8不重编main。所有本V8内容在PH10 cutoff外；compile-only通过不等于库ABI、link容量、固件/运行时/FPSCR/WCET或MOD4实际硬件校准。
