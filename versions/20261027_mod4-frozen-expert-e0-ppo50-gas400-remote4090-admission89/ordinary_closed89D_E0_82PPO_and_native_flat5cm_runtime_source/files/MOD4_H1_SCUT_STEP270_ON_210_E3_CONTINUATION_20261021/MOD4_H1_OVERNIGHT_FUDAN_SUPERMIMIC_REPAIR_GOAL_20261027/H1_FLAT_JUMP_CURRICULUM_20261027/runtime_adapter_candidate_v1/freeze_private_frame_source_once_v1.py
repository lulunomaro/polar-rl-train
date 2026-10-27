from pathlib import Path
import ast,hashlib,json,time
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=HERE/'INDEX.json';assert not out.exists()
 assert json.loads((HERE/'PRIVATE_PHASE_FRAME_TINY_CPU_ACTUAL_V1.json').read_bytes())['passed']
 for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
 rows=[dict(relative=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(HERE.rglob('*')) if p.is_file()]
 with out.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_frozen=True,files=rows,
  actual_runtime_integration_pending=True,no_learner_replay_public_age_reset_or_RNG_changes=True,
  Git_status='ordinary_supplement_pending_root'),f,indent=2)
 print(json.dumps(dict(index_SHA=H(out),source_SHA=H(HERE/'private_phase_frame_v1.py'),files=len(rows),source_only=True)))
if __name__=='__main__':main()
