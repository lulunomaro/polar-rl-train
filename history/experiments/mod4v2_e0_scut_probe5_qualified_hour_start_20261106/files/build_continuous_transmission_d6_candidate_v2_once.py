"""Compare all USD spec values while ignoring child-list insertion order of the reverse copy."""
from pathlib import Path
D=Path(__file__).resolve().parent;s=(D/'build_continuous_transmission_d6_candidate_once.py').read_text(encoding='utf8');a="assert check.ExportToString()==original.GetRootLayer().ExportToString(), 'Undeclared USD content changed'";assert s.count(a)==1
b='''def semantic_specs(layer):
 result={}
 def visit(path):
  obj=layer.GetObjectAtPath(path)
  if obj is not None:
   result[str(path)]={key:obj.GetInfo(key) for key in obj.ListInfoKeys() if key not in ('primChildren','properties')}
 layer.Traverse(Sdf.Path.absoluteRootPath,visit)
 return result
left=semantic_specs(check);right=semantic_specs(original.GetRootLayer());assert set(left)==set(right),'Undeclared USD spec paths changed'
for path in left:
 assert set(left[path])==set(right[path]),('Undeclared USD metadata keys changed',path)
 for key in left[path]:assert left[path][key]==right[path][key],('Undeclared USD value changed',path,key)
'''
s=s.replace(a,b);exec(compile(s,str(Path(__file__)),'exec'),{'__name__':'__main__','__file__':str(Path(__file__))})
