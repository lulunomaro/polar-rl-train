"""Preserve failed fixture/reader source; fix only nested local metadata locator."""
from pathlib import Path
import json,runpy,time
HERE=Path(__file__).resolve().parent
def main():
 p=HERE/'finalize_frozen_E0_single72_V2_LR_source_after_fixture_path_fix_once.py';assert not p.exists()
 s=(HERE/'finalize_frozen_E0_single72_V2_LR_source_once.py').read_text('utf8')
 s=s.replace('assert not proof.exists();shutil.copy2(source,proof)','assert proof.exists() and H(proof)==H(source)')
 before="fixture=fixture.replace('E0_SINGLE72_READY_GO_SPAWN_CHARGE_SOURCE_FIXTURE_ACTUAL_V3.json'"
 after="fixture=fixture.replace('T=HERE.parents[1]','T=HERE.parents[2]')\n fixture=fixture.replace('E0_SINGLE72_READY_GO_SPAWN_CHARGE_SOURCE_FIXTURE_ACTUAL_V3.json'"
 assert s.count(before)==1;s=s.replace(before,after)
 s=s.replace('test_E0_single72_V2_LR_source_fixture_once.py','test_E0_single72_V2_LR_source_fixture_path_fixed_once.py')
 p.write_bytes(s.encode())
 (HERE/'E0_V2_LR_FIXTURE_LOCATOR_AND_COMMAND_ERRORS_RETAINED.json').write_text(json.dumps(dict(epoch=time.time(),
  original_fixture_error='Nested V2_LR fixture inherited T=HERE.parents[1] instead of new depth2; FileNotFound before reading actual small source-extension JSON.',
  actual_model_or_GPU_failure=False,old_fixture_and_error_report_retained=True,
  command_errors=[dict(tool_chunk='3e22c9',kind='PowerShell python-c quote ParserError before Python execution'),dict(tool_chunk='a84824',kind='Follow-on invocation found absent repair script because preceding shell parse failed')],
  correction='This standalone script creates a new repaired finalizer, reuses already-copied immutable CPU return proof, and fixes only local metadata root depth.',
  no_PT_or_SDK_GPU_or_ledger_IO=True),indent=2),encoding='utf8')
 runpy.run_path(str(p),run_name='__main__')
if __name__=='__main__':main()
