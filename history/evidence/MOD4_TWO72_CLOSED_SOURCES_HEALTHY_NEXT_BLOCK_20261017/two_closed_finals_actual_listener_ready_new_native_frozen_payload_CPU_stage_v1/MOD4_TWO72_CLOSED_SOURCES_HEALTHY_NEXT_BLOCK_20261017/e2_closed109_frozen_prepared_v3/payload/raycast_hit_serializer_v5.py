"""Read-only Mapping / installed110 RaycastHit object serialization.

The exact property names below come from the actual installed _physx.pyi.
No field is inferred from geometry and no encoded path is rounded through float.
"""
from collections.abc import Mapping
import numbers,traceback
DECLARED_FIELDS=('distance','face_index','material','material_encoded','normal','position','collision','collision_encoded','protoIndex','rigid_body','rigid_body_encoded')
ACTUAL_PRIMARY_STUB_SHA256='49430e3d566a559253408948bae508a174f633cee2359d9b61c91b9cb426d73f'
def plain(value):
 if value is None or isinstance(value,(bool,str)):return value
 if isinstance(value,numbers.Integral):return int(value)
 if isinstance(value,numbers.Real):return float(value)
 if isinstance(value,Mapping):return {str(k):plain(v) for k,v in value.items()}
 try:return [plain(v) for v in value]
 except TypeError:return dict(unsupported_type=type(value).__module__+'.'+type(value).__qualname__,actual_repr=repr(value))

def serialize_raycast_hit(hit):
 klass=type(hit).__module__+'.'+type(hit).__qualname__
 row=dict(_actual_hit_qualified_class=klass,_declared_API_fields=list(DECLARED_FIELDS),_primary_stub_sha256=ACTUAL_PRIMARY_STUB_SHA256,_public_field_names=[],_field_read_errors={},_skipped_callable_fields=[])
 try:
  if isinstance(hit,Mapping):
   row['_adapter']='Mapping_actual_keys';row['_public_field_names']=[str(k) for k in hit]
   for key,value in hit.items():row[str(key)]=plain(value)
  else:
   row['_adapter']='typed_RaycastHit_readonly_attributes'
   public=sorted(set(DECLARED_FIELDS)|{n for n in dir(hit) if not n.startswith('_')});row['_public_field_names']=public
   for name in public:
    try:
     value=getattr(hit,name)
     if callable(value):row['_skipped_callable_fields'].append(name);continue
     row[name]=plain(value)
    except BaseException as error:row['_field_read_errors'][name]=type(error).__name__+': '+str(error)
  required=('position','normal','distance','collision')
  missing=[name for name in required if name not in row]
  if row['_adapter']=='typed_RaycastHit_readonly_attributes':missing+=list(set(DECLARED_FIELDS)-set(row))
  if missing:row['_serializer_error']='Actual declared hit fields missing: '+repr(sorted(set(missing)))
  if not isinstance(row.get('collision'),str):row['_serializer_error']='Actual collision field is not the declared str path'
 except BaseException:
  row['_serializer_error']=traceback.format_exc()
 return row
