# V10：新有界容量版本静态study（非ABI放宽/非后缀编译）

- 状态：STATIC_STUDY_PASS_TU40_NEW_GATE_PASS_NOT_COMPILE_CONTINUATION。最小数字先保存在[结果](<STUDY_RESULT_MIN_01.json>)；任何首错保prefix且无修订重跑。
- 父另选HOST结构预算16×：MAX_OBJECT=1048576B、MAX_SECTIONS=4096、条件SYMTAB entries=16384；不是V9仅需304的最小提案推断。
- [独立派生](<DERIVATION_01.json>)仅3个literal；字节inverse与AST inverse精确还原sealed V7，其他caps与全部范围/语义检查不变。
- 六个NEW fixture每cap正/负边界、完整backing，实际6 parse、已过6/6、22 assertions；public SYMBOL路径显式测试16384/16385，未重放旧19/64QA。
- 只有fixture全部通过后读TU40：open/read=1，新完整parse=1；58720B producer pin及同snapshot post SHA，file侧只核size/mtime。
- TU40新gate=True；summary={'section_count': 304, 'code_sections': 82, 'public_symbol_ids': [], 'symbol_index_metadata_read': False, 'public_blocks': 3, 'type_checks': 164, 'non_type_checks': 11, 'unknown_type_cells': 0, 'failed_type_cells': 0, 'failed_non_type_checks': 0, 'type_histogram': {'tag18/UNUSED/0': 3, 'tag26/UNUSED/0': 3, 'tag18/VALUE/2': 79, 'tag26/VALUE/1': 79}}。完整[scope与provenance](<TU40_SCOPE_RESULT_01.json>)仅在实际返回后保存。
- Non-type gate仍ELF1/1/1/40、FILE CPU13/profile77/Thumb2/FP6/HardFP1/VFPargs1/denorm1或2；纯gate定义AST与V8原件一致，未import executor。
- 每EXEC/SYMBOL 18=2或规范UNUSED0，26=1或规范UNUSED0；继承/override/nodefaults/冲突/UNKNOWN STOP全部原样，不把0解释为width0或强填2/1。
- 旧V8仍39成功编译/38scope认可/TU40容量停止；旧V6 gate历史不变。新TU40静态认可若PASS也不是旧账重写或新增C编译。
- 122C+ASM1仍未启动；ARM/ASM/fromelf/probe/link/version/UV/hooks/IO/flash/oldQA/FK/PHY/Git/agent/root-goal均0，38accepted/main读取0。
- source小输入before-after SHA一致=True; reader/resource limits仅HOST预算，不是库/固件/MCU/FPSCR/gradual/WCET或实机资格。
- 全部PH10 cutoff外；父actual read后另批C-only scope才可继续122C，ASM仍排除。
