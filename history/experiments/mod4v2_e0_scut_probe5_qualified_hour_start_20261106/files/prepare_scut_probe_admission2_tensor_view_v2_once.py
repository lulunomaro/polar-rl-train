"""Use the observed fields-dictionary ABI; first preparer failed before all output publication."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;tree=ast.parse((D/'prepare_scut_probe_admission2_tensor_view_once.py').read_text(encoding='utf8'));fixes={
'value = _need(data, key)\n            if not isinstance(value, t.Tensor) or tuple(value.shape) != shape:':'fields = {k: _need(data, k) for k in (',
'value = _tensor_view(_need(data, key), t, key)\n            if tuple(value.shape) != shape:':'fields = {k: _tensor_view(_need(data, k), t, k) for k in (',
'raise Unknown("Unexpected robot tensor shape: " + key + " observed=" + str(tuple(value.shape)) + " expected=" + str(shape))':'raise Unknown("Unexpected robot tensor shape: " + key + " observed=" + str(tuple(value.shape)) + " expected=" + str(shapes[key]))'};counts={k:0 for k in fixes}
class Fix(ast.NodeTransformer):
 def visit_Constant(self,n):
  if isinstance(n.value,str)and n.value in fixes:counts[n.value]+=1;n.value=fixes[n.value]
  return n
Fix().visit(tree);assert all(v==1 for v in counts.values()),counts;ast.fix_missing_locations(tree);exec(compile(tree,str(Path(__file__)),'exec'),dict(globals(),__name__='__main__',__file__=str(Path(__file__))))
