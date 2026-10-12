"""Preserve observer equality error; independently handle complete nested CPU trees."""
from pathlib import Path
D=Path(__file__).resolve().parent
original=D/'review_route_second_component_and_storage_actual.py'
s=original.read_text(encoding='utf8')
old=' assert same(clone,ck)'
assert s.count(old)==1
new=''' import numpy as np
 def full_cpu_tree_equal(a,b):
  if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
  if isinstance(a,np.ndarray):return isinstance(b,np.ndarray) and a.dtype==b.dtype and a.shape==b.shape and np.array_equal(a,b)
  if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(full_cpu_tree_equal(a[k],b[k]) for k in a)
  if isinstance(a,(list,tuple)):return type(a) is type(b) and len(a)==len(b) and all(full_cpu_tree_equal(x,y) for x,y in zip(a,b))
  return type(a) is type(b) and a==b
 assert full_cpu_tree_equal(clone,ck)'''
s=s.replace(old,new).replace('ROUTE_SECOND_COMPONENT_READER_ERROR_','ROUTE_SECOND_CPU_TREE_REVIEWED_READER_ERROR_')
exec(compile(s,str(__file__)+'#independent-full-CPU-tree-comparator','exec'),dict(__file__=__file__,__name__='__main__'))
