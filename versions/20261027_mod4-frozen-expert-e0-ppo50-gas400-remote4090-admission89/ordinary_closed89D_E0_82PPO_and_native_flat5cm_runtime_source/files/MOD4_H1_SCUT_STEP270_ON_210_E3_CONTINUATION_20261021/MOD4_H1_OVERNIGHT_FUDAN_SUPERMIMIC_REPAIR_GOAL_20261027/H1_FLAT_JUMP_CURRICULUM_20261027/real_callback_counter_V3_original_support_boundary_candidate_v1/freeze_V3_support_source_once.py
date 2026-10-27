from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=HERE/'INDEX.json';assert not out.exists()
 assert json.loads((HERE/'V3_ORIGINAL_SUPPORT_BOUNDARY_TINY_CPU_ACTUAL.json').read_bytes())['passed']
 rows=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(HERE.iterdir()) if p.is_file()]
 with out.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_frozen=True,files=rows,actual_native_pending=True,Git_status='ordinary_supplement_pending_root'),f,indent=2)
 print(json.dumps(dict(index_SHA=H(out),V3_SHA=H(HERE/'flat_real_physics_events_v3_original_support.py'))))
if __name__=='__main__':main()
