from pathlib import Path
import sys,json,base64,time
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'USER_PAUSE_EXECUTED.json').exists(),'Once already executed'
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'))
from eval_remote_io import connect_eval
W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
j='clk2500-closure-episode-d3-94-shallow-bounded-latest-20261003-flat'
w=connect_eval()
try:
 receipt={'epoch':time.time(),'human_instruction':'知到不能大跨步走了，暂停这个吧，我们继续按计划走','scope':'Pause this synthetic shallow zero-shot evaluation only; preserve raw; continue approved main training and normal frozen evaluation.','paused_jobs':json.loads((R/'BOUNDED_TRAVERSAL_PUBLISHED.json').read_text())['jobs'],'not_skill_pass':True,'no_4090_or_canonical_mutation':True}
 with w.open_sftp() as f:
  with f.open(W+'/SHALLOW_EVALUATION_USER_PAUSE.json','w') as q:q.write(json.dumps(receipt,indent=2,ensure_ascii=False))
  with f.open(W+'/jobs/'+j+'/USER_PAUSE_REQUEST.json','w') as q:q.write(json.dumps(receipt,indent=2,ensure_ascii=False))
 ps=r"""$ErrorActionPreference='Stop'
$job='clk2500-closure-episode-d3-94-shallow-bounded-latest-20261003-flat'
$done='D:\MOD4_async_eval\closure_episode_clock2500_v15\jobs\'+$job+'\PHYSICS_COMPLETE.json'
$targets=@(@{pid=34400;creation=1791529315.36;ppid=28836},@{pid=28836;creation=1791529315.343;ppid=19964})
$stopped=@();$ended=@()
foreach($t in $targets){
 if(Test-Path -LiteralPath $done){break}
 $p=Get-CimInstance Win32_Process -Filter ('ProcessId='+$t.pid)
 if(-not $p){$ended+=$t.pid;continue}
 $creation=([DateTimeOffset]$p.CreationDate).ToUnixTimeMilliseconds()/1000
 if([math]::Abs($creation-$t.creation) -gt .002 -or $p.ParentProcessId -ne $t.ppid -or $p.CommandLine -notlike ('*'+$job+'*') -or $p.CommandLine -notlike '*a4e31f49b0ee83fbfbbd33b9d5a178651517ca8c4667ef9211fcdffb010e24f8*frozen_history_flat.py*'){throw 'Identity changed; no signal'}
 Stop-Process -Id $t.pid -ErrorAction Stop
 $stopped+=[pscustomobject]@{pid=$p.ProcessId;ppid=$p.ParentProcessId;creation=$creation;argv=$p.CommandLine}
}
[pscustomobject]@{stopped=$stopped;already_exited=$ended;physics_receipt_present=(Test-Path -LiteralPath $done);scope='Human-authorized own frozen inference only; no training process signal'}|ConvertTo-Json -Compress -Depth 6
"""
 _,o,e=w.exec_command('powershell -NoProfile -EncodedCommand '+base64.b64encode(ps.encode('utf-16-le')).decode(),timeout=40)
 b=o.read();err=e.read();rc=o.channel.recv_exit_status()
 receipt['signal_result']=json.loads(b) if b.strip() and rc==0 else {'returncode':rc,'stdout':b.decode(errors='replace'),'stderr':err.decode(errors='replace')}
 (R/'USER_PAUSE_EXECUTED.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False),encoding='utf8')
 assert rc==0,(b+err).decode(errors='replace')
 print(json.dumps(receipt,ensure_ascii=False))
finally:w.close()
