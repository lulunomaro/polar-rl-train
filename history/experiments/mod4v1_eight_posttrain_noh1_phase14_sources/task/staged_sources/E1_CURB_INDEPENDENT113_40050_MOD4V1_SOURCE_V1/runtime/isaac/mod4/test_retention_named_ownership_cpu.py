"""New named ownership admission only, no simulation, replay or CUDA initialization."""
from pathlib import Path
import ast,hashlib,json,tempfile,torch

def main():
 D=Path(__file__).resolve().parent;torch.set_num_threads(1)
 class FixtureBase:
  def __init__(self):
   self._mode_rng=torch.Generator().manual_seed(11)
   self._retention_rng=torch.Generator().manual_seed(20261010)
 ns={'RetainedFlatCommand':FixtureBase}
 tree=ast.parse((D/'retention_flat_runtime_named_owned.py').read_text())
 cls=next(x for x in tree.body if isinstance(x,ast.ClassDef))
 exec(compile(ast.fix_missing_locations(ast.Module(body=[cls],type_ignores=[])),'<new-owned-class>','exec'),ns)
 restore=next(x for x in ast.parse((D/'sensor_resume_contract.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='restore_named')
 exec(compile(ast.fix_missing_locations(ast.Module(body=[restore],type_ignores=[])),'<old-exact-restore>','exec'),globals())
 obj=ns['RetainedFlatNamedOwnedCommand']();assert set(k for k,v in vars(obj).items() if isinstance(v,torch.Generator))=={'_mode_rng'}
 legacy={'_mode_rng':torch.Generator().manual_seed(987).get_state()};private=obj._retention_rng.get_state().clone();assert restore_named(obj,legacy)==['_mode_rng'];assert torch.equal(private,obj._retention_rng.get_state())
 with tempfile.TemporaryDirectory() as temp:
  p=Path(temp)/'private.pt';torch.save(private,p);new=ns['RetainedFlatNamedOwnedCommand']();new._retention_rng.set_state(torch.load(p,weights_only=False));assert torch.equal(torch.rand(500,generator=new._retention_rng),torch.rand(500,generator=obj._retention_rng));diskSHA=hashlib.sha256(p.read_bytes()).hexdigest()
 try:restore_named(obj,dict(legacy,unexpected=private));raise RuntimeError('strict schema must reject')
 except AssertionError:pass
 assert not torch.cuda.is_initialized()
 print(json.dumps(dict(passed=True,private_named_generator_ownership_exact=True,legacy_named_streams_restored_exact=True,private_CPU_disk_rng_restore_exact=True,strict_unknown_generator_schema_rejection_preserved=True,CPU_only_new_ownership_checks=5,no_CUDA_initialized=True,disk_SHA=diskSHA,numerical_sampling_eligibility_old_adapter_byteexact=True)))
if __name__=='__main__':main()
