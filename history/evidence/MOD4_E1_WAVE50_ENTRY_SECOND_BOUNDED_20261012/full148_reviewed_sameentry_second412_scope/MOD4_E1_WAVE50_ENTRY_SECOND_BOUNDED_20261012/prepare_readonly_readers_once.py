"""Read-only source412 readers; preparation does not claim future outcomes."""
from entry_second_io import *
def main():
 prior=W/'MOD4_E1_WAVE50_SECOND_BOUNDED_20261012'
 for src,dest in [('read_second50_actual.py','read_entry_second_actual.py'),('verify_second50_startup_contract_actual.py','verify_entry_second_startup_contract_actual.py'),('verify_second50_startup_save_cpu_actual.py','verify_entry_second_startup_save_cpu_actual.py')]:
  text=(prior/src).read_text().replace('from second50_io import *','from entry_second_io import *').replace('supervise_wave50_second_bounded_once','supervise_wave50_entry_second_bounded_once').replace('e1_WAVE50_second_bounded_observation','e1_WAVE50_entry_second_bounded_observation').replace('==386','==412').replace('source_count=386','source_count=412').replace('actual_source_count=386','actual_source_count=412').replace('SECOND50_','ENTRY_SECOND_')
  if src.startswith('verify'):
   text=text.replace("'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json')","'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json')")
   anchor="assert c['predecessor_command_state_restored_exact']"
   text=text.replace(anchor,"ep=j(root/'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json');assert ep['passed'] and ep['same_entry_identity_restored_exact'] and not ep['explicit_new_entry_scope'] and ep['actual_entry_terrain_command_CUDA_disk_roundtrip_exact']\n"+anchor)
  compile(text,dest,'exec');p=D/dest;assert not p.exists();p.write_text(text,encoding='utf8',newline='\n')
 print(json.dumps(dict(readers_prepared=True,no_future_pass_claim=True)))
if __name__=='__main__':main()
