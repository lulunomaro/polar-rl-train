"""Preserve the initial export and declare its already verified fixed six output."""
from pathlib import Path
import hashlib, json, shutil, sys
import onnx, onnxruntime as ort, numpy as np

W = Path(__file__).resolve().parent
P = W.parent/'mod4-onnx-mujoco-launcher/policies/imported/mod4_latest_moe_20261018.onnx'
def H(p): return hashlib.sha256(p.read_bytes()).hexdigest()
M = P.with_suffix('.json')
meta = json.loads(M.read_text(encoding='utf-8'))
assert H(P) == meta['onnx_sha256']
old = W/'large_originals'
old.mkdir(exist_ok=True)
original = old/'initial_symbolic_output.onnx'
assert not original.exists()
shutil.copy2(P, original)
shutil.copy2(M, W/'reports/INITIAL_EXPORT_SYMBOLIC_OUTPUT_METADATA.json')
session = ort.InferenceSession(str(P), providers=['CPUExecutionProvider'])
for n in (1, 2, 7):
    assert session.run(None, {'observation': np.zeros((n,35),np.float32)})[0].shape == (n,6)
graph = onnx.load(str(P))
nodes_before = [n.SerializeToString() for n in graph.graph.node]
weights_before = [n.SerializeToString() for n in graph.graph.initializer]
graph.graph.output[0].type.tensor_type.shape.dim[1].dim_value = 6
assert nodes_before == [n.SerializeToString() for n in graph.graph.node]
assert weights_before == [n.SerializeToString() for n in graph.graph.initializer]
onnx.checker.check_model(graph)
onnx.save(graph, str(P))
meta['onnx_sha256'] = H(P)
meta['fixed_output_shape_declaration_only_no_graph_math_change'] = True
M.write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
report = dict(original=dict(path=str(original), bytes=original.stat().st_size, sha256=H(original)),
    corrected=dict(path=str(P), bytes=P.stat().st_size, sha256=H(P)),
    only_static_output_declaration_changed=True, no_reexport_or_model_changes=True,
    actual_batch_shapes_verified=[1,2,7])
(W/'reports/LOCAL_ONNX_SYMBOLIC_SHAPE_FIXED_ACTUAL.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
