from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'DEPTH_STUDENT_RETENTION_REPAIR_V292_20261101';R=N/'reports';D=N/'normal297';D.mkdir(exist_ok=False)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.write_bytes(s.encode());ast.parse(s,filename=str(p))
collector=(O/'normal292/collect292_teacher_student_formal_cost_normal900_UNUSED_once.py').read_text('utf8').replace('292','297')
write(D/'collect297_tracking_formal_cost_normal900_UNUSED_once.py',collector)
common=(O/'normal292/normal292_common.py').read_text('utf8').replace('292','297');write(D/'normal297_common.py',common)
for name in('normal297_common.py','collect297_tracking_formal_cost_normal900_UNUSED_once.py'):
    text=(D/name).read_text('utf8').replace('INDEX297_NORMAL_SOURCE_FROZEN.json','INDEX297_NORMAL_SOURCE_FROZEN.json');write(D/name,text)
files=(D/'normal297_common.py',D/'collect297_tracking_formal_cost_normal900_UNUSED_once.py',N/'teacher_task297.py')
with(D/'INDEX297_NORMAL_SOURCE_FROZEN.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]),f,indent=2)
print(json.dumps(dict(passed=True,normal_index_SHA=H(D/'INDEX297_NORMAL_SOURCE_FROZEN.json'))))
