# V9：TU40一次结构header诊断（非属性重试）

- 当前物件58720B；一次payload open/read，snapshot SHA与V8 producer pin相同。ELF32LE、ET_REL=1、EM_ARM=40。
- e_shnum=304，e_shoff=46560，e_shentsize=40，e_shstrndx=301；table_end=58720 ≤ file_size=58720。
- extended flags={'section_count': False, 'shstr_index': False, 'program_count': False}；有效section count=304，shstr header类型STRTAB；这一区分普通有效N>256与原reader合并报错中的extended/invalid。
- 全304个section header已核；非NOBITS payload边界错0，name offset边界错0。整物件仅opaque取数/hash，未遍历或解释string/symbol entry/attribute/code payload。
- symbol-table header计数（含NULL entry）=[459]；attribute section数=1，总大小=203B。详见[最小JSON](<HEADER_DIAG_01.json>)。
- 最小有界提案仅MAX_SECTIONS：256→304；64KiB与其余caps、conditional1024symbol、全部type/non-type gates原封不动。仅提案，未写新reader/改旧reader/解释属性；其他payload limits足够与否仍UNKNOWN。
- [提案](<CAPACITY_PROPOSAL_01.json>)必须由父另批new reader study；该TU40 ABI仍UNKNOWN，122C+ASM1原样未启动。
- 旧V8仍39成功编译/38scope认可/容量停止；失败prep与唯一suffix修订原件不变，无重新计账。
- 小source/metadata before-after SHA一致；对象post SHA为同一owned snapshot再hash，file侧只核size/mtime，不冒充第二次独立file-side hash。
- sealed V7 reader无import/调用，38个已认可物件无读取；ARM/compile/ASM/fromelf/probe/link/version/IO/oldQA/PHY/Git/agent/root-goal均0。
- 全部V9在PH10 cutoff外；structural validity不是ABI/link/固件/runtime/板级资格。
