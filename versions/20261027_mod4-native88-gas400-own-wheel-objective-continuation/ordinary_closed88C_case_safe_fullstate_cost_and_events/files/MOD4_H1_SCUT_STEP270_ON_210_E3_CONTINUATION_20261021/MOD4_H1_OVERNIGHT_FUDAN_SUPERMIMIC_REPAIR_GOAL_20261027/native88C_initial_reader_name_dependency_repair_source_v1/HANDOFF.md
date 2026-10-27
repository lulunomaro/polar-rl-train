Frozen SOURCE ONLY dependency repair. Only merge the new
native88_initial_CPU_reader_primitives_v1.py from this directory. No actual CPU
qualification main, wrapper or runtime/weight modification was created here.

New primitives SHA:
da0c81ae801c768578f199f280d86c73c2fd69a86ed16c56d31b7560d991a63f

Only two definitions were inserted after SOURCE_SHA:

    def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    def read(p):return json.loads(Path(p).read_bytes())

All original classes/functions, imports/module assignments and source paths are
AST identical. Exact unified diff is saved. Complete-source symbol-table audit
finds only H/read unresolved before the repair and none afterward, including
method/nested-function scopes. torch remains locally imported where needed;
stdlib names and imported BOOTSTRAP_SHA/require are bound. This is a source-name
audit, not a claim that every future decoded model/schema/path was exercised.

Nine NEW tiny source/JSON CPU checks passed. They execute the real repaired
PinnedSource init/raw/extract on tiny reviewed fixture files, and reject wrong
manifest SHA, changed Python bytes, extra Python and raw path escape. Original
validator definitions remain exact. No model/PT was statted/read/hashed, no Torch,
actor/WM, SDK, GPU, remote or old reviewer/fixture was executed. Intentional
negative fixtures and source pins are retained; no CPU fixture failures occurred.

External pure dependency remains the original C
native88_closing_protocol_v1.py SHA
5391889c771e453291af03806cb46e3d6a48b75dcbf41e2b1fbbdc55066bdec8.
The root's new-purpose qualification must import this NEW primitives module,
not a cached old module with the same basename. Verify imported __file__/SHA or
load the new source explicitly. No monkeypatch/global namespace injection is
needed. All existing guards, model counters, numerical criteria and training
semantics are untouched. No model-path fallback was introduced.

Actual load history must remain truthful: the consumed old initial reviewer
loaded the shared normal86 witness ONCE, then failed at PinnedSource before
either NEW FINAL initial load. That process has exited and its witness tensor
cache is gone. Next actual new-purpose qualification therefore needs ONE MORE
shared normal86 witness read for literal frozen actor9/critic8/STD6/all17Adam832460
comparison with the two NEW FINALs. It must not claim zero old-model rereads.
Each new FINAL has not yet been loaded; its next read is its first initial CPU
load. Native R5 input models do not need reloading. Retain the old false/errors,
intent/consumed marker and completed witness record as references. The inherited
pool's historical role label mentioning native87R5 is unchanged; new main must
state the actual new-purpose88C qualification and prior consumed attempt clearly.

Root may front-load metadata/PinnedSource/actualCPU-ready validation before any
new model reads. Root alone owns the new actual main/output markers, mandatory
reference to previous errors, actual qualification and ordinary Git supplement.
This source fix does not classify the two new models as CPU-qualified or as
physical270mm skill: actual events still have zero crossing/landing/recovery.
Imagined reward ratios remain diagnostic and do not supply physical success.
