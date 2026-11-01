"""Summarize task-local SolidWorks structured inventory without touching CAD."""
import json,sys
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parent
name=sys.argv[1] if len(sys.argv)>1 else 'before'
d=json.loads((root/f'inventory_{name}.json').read_text(encoding='utf-8-sig'))
parts=d['part_properties'];rows=d['components'];leaves=[r for r in rows if r['is_leaf'] and r['suppression']!=0]
summary={'assembly':d['assembly_path'],'configuration':d['configuration'],'assembly_dirty':d['assembly_dirty_before'],'lightweight':[d['lightweight_before'],d['lightweight_after']],'component_instances':len(rows),'active_leaf_instances':len(leaves),'unique_referenced_models':len(parts),'mass_including_hidden':d['assembly_mass_including_hidden'],'mass_excluding_hidden':d['assembly_mass_excluding_hidden'],'material_databases':d.get('material_databases'),'configuration_mismatches':[{'path':p['path'],'referenced':p['configuration'],'loaded':p['loaded_configuration']} for p in parts.values() if not p['configuration_matches']]}
print(json.dumps({'summary':summary},ensure_ascii=False,indent=2))
bykey={}
for r in rows:bykey.setdefault(r['key'],[]).append(r['name'])
for key,p in parts.items():
 if p['document_type']!=1:continue
 bodies=p.get('bodies',[]);mat=p.get('part_material')
 mirror=[f for f in p.get('features',[]) if f.get('mirror_source_path') or f.get('derived_source_path') or 'Mirror' in f.get('type','') or 'Stock' in f.get('type','')]
 missing=not mat and any(not b.get('material') for b in bodies)
 if missing or mirror or any(p.get('mass_properties_si',{}).get(k) for k in ['override_mass','override_com','override_inertia']):
  print(json.dumps({'path':p['path'],'cfg':p['configuration'],'instances':bykey[key],'material':mat,'database':p.get('part_material_database'),'missing_body_material':missing,'dirty':p['dirty'],'read_only':p['read_only'],'mass':p.get('mass_properties_si'),'bodies':[{'name':b['name'],'material':b.get('material'),'database':b.get('material_database'),'box':b.get('body_box_m'),'geometry_mass_at_density1':b.get('geometry_mass_at_density1')} for b in bodies],'mirror_features':mirror,'all_feature_names':[{'name':f['name'],'type':f['type']} for f in p.get('features',[])] if missing else []},ensure_ascii=False))
print(json.dumps({'top_level':[{'name':r['name'],'path':r['path'],'hidden':r['hidden_by_self_or_ancestor'],'suppression':r['suppression'],'leaf':r['is_leaf']} for r in rows if not r['parent']]},ensure_ascii=False,indent=2))
