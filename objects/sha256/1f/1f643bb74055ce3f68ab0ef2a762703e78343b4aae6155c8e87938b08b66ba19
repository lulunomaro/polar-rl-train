"""Regression: rollback source iteration can be lower than failed DR weights."""
import ast,json,tempfile,types
from pathlib import Path
source=Path(__file__).with_name('supervise_sensor_dr.py').read_text()
node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='training')
with tempfile.TemporaryDirectory() as temp:
    root=Path(temp);(root/'logs/failed').mkdir(parents=True);(root/'logs/current').mkdir()
    failed=root/'logs/failed/model_99999.pt';current=root/'logs/current/model_15000.pt'
    failed.touch();current.touch()
    (failed.parent/'latest_complete.json').write_text(json.dumps(dict(pid=111,checkpoint=str(failed))))
    (current.parent/'latest_complete.json').write_text(json.dumps(dict(pid=222,checkpoint=str(current))))
    base=types.SimpleNamespace(STATE={},latest=lambda folder:failed)
    original_latest=base.latest
    def fake_training(ck,phase,**kw):
        base.STATE['training_pid']=222
        assert base.latest(root/'logs')==current
        base.STATE['training_pid']=None
        assert base.latest(root/'logs')==current,'Trainer exit reverted to higher failed weight'
        return current
    bindings={'Path':Path,'ROOT':root,'base':base,'helpers':types.SimpleNamespace(read=lambda p:json.loads(p.read_text())),
              'ORIGINAL_TRAINING':fake_training}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<save-pin-test>','exec'),bindings)
    assert bindings['training'](current,'rollback')==current
    assert base.latest is original_latest
print('PASS: exact PID receipt wins over higher failed iteration; pin persists after exit; original helper restored')
