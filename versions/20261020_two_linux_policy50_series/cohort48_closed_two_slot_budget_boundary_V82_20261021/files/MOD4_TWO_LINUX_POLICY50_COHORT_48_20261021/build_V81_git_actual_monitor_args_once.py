from pathlib import Path
import json,subprocess
B=Path(__file__).resolve().parent;R=B/'reports';G=B.parent/'polar-rl-train';a=json.loads((R/'V81_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());head=subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip();assert head=='44d0730b73b49fcbe591ada6d77743d6ecd06329'
a['prompt']='V81 Git lateractual：按人类明确两槽预算准入授权的新真实修复/部署阶段已唯一record '+head+'/tagobject56d1d372caf0881d117327eb20c6ff57c38b3026/trial-20261021-e2-e3-scheduled-two-slot-budget-guard-approved-v81/总1417。remote main/tag/peeled及原1416全部tag对象和peels真核；3159完整/引用文本entries、40新Git文件完整Gitblob核过，没有新大日志，旧完整同SHA全文Git路径引用。模型只producer路径大小SHA，不为Git重PT/hash/GPU或改账。record_experiment原main一次运行，仅内存Git add等价stdin NUL pathspec避免Win206，不改源码或重record/tag。该unique archive/helper/record已consume，以后same授权两槽series各新actualrunid只ordinary补档，pushfail续已有objects。此后appreceipt/monitor精确readback只一次ordinary追加，不无限补HEAD。旧V80预算候选未批准/pending仅历史事实；现在明确已批准并在新48 root实际GO/PPO及owner远端全SHA核过，47失败根保留不重用。\n'+a['prompt']
with (R/'V81_GIT_ACTUAL_MONITOR_UPDATE_ARGS.json').open('x',encoding='utf8') as f:json.dump(a,f,ensure_ascii=False,indent=2)
print('Unique approved repair actual Git args prepared')
