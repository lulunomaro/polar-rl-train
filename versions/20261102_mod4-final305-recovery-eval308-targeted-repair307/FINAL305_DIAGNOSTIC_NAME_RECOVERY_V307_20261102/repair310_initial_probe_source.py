"""Preserve309localgenerationindentationfailure; independent310source repair."""
from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;old=N/'prepare309_reference_start_probe.py'
s=old.read_text('utf8').replace('V309_20261102','V310_20261102').replace("'309'","'310'").replace('evaluate309','evaluate310').replace('contract309','contract310').replace('probe309','probe310').replace('PROBE309','PROBE310').replace('TASK309','TASK310').replace('SOURCE309','SOURCE310')
s=s.replace(" '''+s[start:]", "'''+s[start:]")
s=s.replace("(E/'run309_probe_once.py')", "(E/'run310_probe_once.py')")
s=s.replace("ast.parse(runner);", "runner=runner.replace(\"patterns='\",\"patterns='run310_probe|\",1)\n+ast.parse(runner);".replace('\n+','\n'))
ast.parse(s)
p=N/'prepare310_reference_start_probe.py';p.write_bytes(s.encode())
with(N/'reports/LOCAL309_PRODUCER_INDENT_FALSE_310_REPAIR.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),original309='localgenerationIndentationErrorbeforeSDK/model/network/GO',repair310='correct extraleading space in generatedreal.reset; preserve309tree andsource',model_reads=0,SDK=0,network=0),f,indent=2)
exec(compile(s,str(p),'exec'),dict(__name__='__main__',__file__=str(p)))
