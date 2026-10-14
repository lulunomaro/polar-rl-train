from pathlib import Path
import json,hashlib,time
D=Path(__file__).resolve().parent
base=D/'MONITOR_S4_FIRST_SUPPORTED_GATE45M_DISPATCHED_ACTUAL_20261015.txt'
old=base.read_text(encoding='utf8')
prefix='最新transport actual优先：首S4窗口已唯一dispatch后，本轮第一次状态只读在TCP连接10.24.4.210时TimeoutError，尚未运行remote read。不是GPU/PhysX故障证明，也不能说父子仍active、已positive或已failed。L/reports/S4_FIRST_GATE_FIRST_READ_CONNECT_TIMEOUT_ACTUAL.json原样保留；不密集retry/ping、不凭未知状态再dispatch/kill/hotpatch/改预算。当前第一自己的完整PPO保存尚未独立核；实际ownstartup、gate/critic和14Adam变化、全source、完整cost/exit/locks以后续真读取为准。根本机此次reader已结束，无额外foregroundcollector或finite coordinator；下一只在独立工作/原1hheartbeat后有界读，不创建额外watcher。\n\n'
p=D/'MONITOR_S4_FIRST_GATE_TRANSPORT_PENDING_ACTUAL_20261015.txt';assert not p.exists();p.write_bytes((prefix+old).rstrip('\r\n').encode('utf8'))
print(json.dumps(dict(prompt=p.read_text(encoding='utf8'),prompt_SHA=hashlib.sha256(p.read_bytes()).hexdigest())))
