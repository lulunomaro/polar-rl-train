# V5元数据脚本首次失败（保留）

- 首次 `static_plan_01.log`：AttributeError，保存的 lexical 图某些 `resolved.member` 是 JSON null（例：stdlib.h），字符串比较前未处理 null。
- 此时尚未写候选计划；0 ZIP/header/source payload、0 native toolchain/compile。
- 原脚本和日志已复制保留在 [首attempt](<revisions/static_plan_attempt_01/plan_headers_once.py>)、[原log](<revisions/static_plan_attempt_01/static_plan_01.log>)；原脚本SHA `6d65c040cd1f8fc166b9e0f4706001e986ecd5ffd965ec50b9bc1176e35770e2`。
- 唯一代码修正：把 `get('member','').casefold()` 改为 `(get('member') or '').casefold()`；null仅表示无该project member，不宣称已解析系统头。
- 未改候选reason、目录、后缀、数量/bytes界限、图、163 argv、原输入或警告；后续只允许重做同四个JSON元数据计算，不运行项目/编译器。
