"""Only producer JSON index content + JSONL stat; never reads/hashes JSONL data."""
from pathlib import Path
import json,re
def metadata_indexes(J,F,source_SHA):
 J=Path(J).resolve();F=Path(F).resolve();assert F.is_relative_to(J)
 expected=[F/'E2_OBSERVED_COMMAND_INSTANCE_RECORDS_ACTUAL.jsonl',F/'early_original_resample/E2_REAL_INITIAL_SAMPLED_COMMANDS_ACTUAL.jsonl'];result=[];missing=[]
 for path in expected:
  index=Path(str(path)+'.PRODUCER_INDEX_ACTUAL.json')
  if not index.exists():missing.append(str(index));continue
  assert index.resolve().is_relative_to(F) and not index.is_symlink()
  value=json.loads(index.read_bytes());assert value['path']==str(path) and value['source_SHA']==source_SHA
  assert value['producer_stream_SHA_no_reread'] is True and value['content_transfer_default'] is False and value['collector_mode']=='producer_path_bytes_SHA_metadata_only'
  assert isinstance(value['rows'],int) and 0<=value['rows']<=80000 and isinstance(value['bytes'],int) and 0<=value['bytes']<=256*1024**2
  assert re.fullmatch('[0-9a-f]{64}',value['SHA']) and path.resolve().is_relative_to(F) and not path.is_symlink() and path.is_file() and path.stat().st_size==value['bytes']
  result.append(dict(value,producer_index=str(index),contents_not_read_rehashed_or_transferred=True))
 return dict(indexes=result,missing=missing,both_expected_producer_indexes_present=len(result)==2,raw_JSONL_content_read=False)
