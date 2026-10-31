"""Narrow ROOT before-use caller repair; original frozen219 caller stays unused."""
from pathlib import Path
import hashlib,inspect,json,time,paramiko,ast
N=Path(__file__).resolve().parent
p=N/'launch219_install_original_solo_W35_FIRST_UNUSED_once.py'
b=p.read_bytes();assert hashlib.sha256(b).hexdigest()=='bc92b56ed9549dabbeb1c2d4e0166dfde54958cd2d793100fab2a8e9ef1a1b3d'
s=b.decode('utf8');assert s.count("sf.file(remote,'xb')")==1
s=s.replace("sf.file(remote,'xb')","sf.file(remote,'wx')").replace("'launch219_|","'launch219V2_|launch219_|")
s=s.replace("index=read(N/'INDEX219_FROZEN.json')","assert H(N/'INDEX219_FROZEN.json')=='dfc17386feee6ebdeabd73a27e927d4d00a933c30a7e1c8ca9e34ae970bf0043'\n index=read(N/'INDEX219_FROZEN.json')")
ast.parse(s)
o=N/'launch219V2_install_original_solo_W35_FIRST_UNUSED_once.py'
with o.open('x',encoding='utf8',newline='')as f:f.write(s)
v=dict(epoch=time.time(),source_only_before_any_execution=True,
 original_frozen_caller=str(p),original_SHA=hashlib.sha256(b).hexdigest(),original_stays_UNUSED=True,
 selected_new_caller=str(o),selected_SHA=hashlib.sha256(o.read_bytes()).hexdigest(),
 original_frozen219_index='dfc17386feee6ebdeabd73a27e927d4d00a933c30a7e1c8ca9e34ae970bf0043',
 changes=['Paramiko stage exclusive write mode xb to wx','Include V2 basename in fresh LOCAL CIM','Pin unchanged original219 INDEX'],
 reason='Installed Paramiko sets WRITE for w/a/+; x only sets CREATE+EXCL. xb has no write flag; wx preserves exclusive creation and adds WRITE.',
 installed_API_source=inspect.getsource(paramiko.SFTPClient.open),
 source_model_or_physics_or_reward_changed=False,model_raw_NPZ_USD_SDK_GPU_network_calls=0,
 prior_inline_generator_shell_refusal='PowerShell ParserError before Python/no source file or network action; corrected with this structured source file')
with(N/'reports/ROOT219V2_SFTP_MODE_BEFORE_USE_REPAIR_FROZEN.json').open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(selected=str(o),SHA=v['selected_SHA'],source_repair_only=True)))
