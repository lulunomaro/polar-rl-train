"""Preserve failed generic decision reader; select actual147 collection/review fields."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'review_entry_direct147_prefix_actual.py').read_text()
anchor="exec(compile(s, '<entry-candidate-direct147-readonly>'"
assert s.count(anchor)==1
s=s.replace(anchor,"s=s.replace(\"before['collection']\",\"before['actual_collection']\").replace(\"before['review']\",\"before['full_actual_review']\")\n"+anchor)
exec(compile(s,'<actual147-decision-schema-readonly>','exec'),{'__file__':str(D/'review_entry_direct147_prefix_actual.py'),'__name__':'__main__'})
