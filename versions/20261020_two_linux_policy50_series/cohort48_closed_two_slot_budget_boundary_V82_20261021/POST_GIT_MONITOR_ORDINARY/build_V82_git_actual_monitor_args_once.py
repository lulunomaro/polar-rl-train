from pathlib import Path
import json,subprocess
B=Path(__file__).resolve().parent;R=B/'reports';G=B.parent/'polar-rl-train';a=json.loads((R/'V82_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());head=subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip();assert head=='f79f2b199481dcaf256b5209d6844f2dbe3006e5'
a['prompt']='V82 Git lateractual：cohort48完整闭合/两新完整模型wholeCPU/原各真实interval结清/全部ownout与原锁free/保留余量后的预算准入边界，已同系列ordinary '+head+'，remote main及全部1417原tag对象/peels真核；4290完整/引用文本entries、85新Git文件与1份大日志完整orderedUTF8parts和全重组SHA真核；模型只producer pathsizeSHA，没有下一PPO或49 dispatch。unique44d0730b/tag56d1d372/1417已consume不重record/tag，所有closing/review/V82 archivehelpers已consume；pushfail只续已有objects。此后appreceipt与精确monitor readback只一次ordinary补档，不无限补HEAD/连训练host/PT重hash/GPU/改账。当前只是保留明确safety/legacy后的续训准入边界，非总budget耗尽；same ACTIVE monitor保留，unchanged pending静默。\n'+a['prompt']
with (R/'V82_GIT_ACTUAL_MONITOR_UPDATE_ARGS.json').open('x',encoding='utf8') as f:json.dump(a,f,ensure_ascii=False,indent=2)
print('Budget boundary actual Git monitor args prepared')
