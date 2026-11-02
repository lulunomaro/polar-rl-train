# SPR SRC_ONLY 审计错误与操作记录

## 原样错误留存

- ZIP 中央索引/所选文本提取异常原样日志：[ERRORS.jsonl](<ERRORS.jsonl>)。当前文件为 **0 bytes**，本轮无 ZIP 读取、CRC、解码或路径校验异常。
- Python 算术检查：15 项通过、0 项失败，见[向量结果](<codec_vectors_spr.json>)。没有产生额外异常traceback文件。
- 文件哈希/证据行区间校验全部通过，见[验证结果](<validation_results.json>)。没有产生额外异常traceback文件。
- 本轮命令未出现非零退出；没有重复同参数失败、权限重试、安装、构建、固件执行或硬件IO。

## 非错误的发现/局限

1. 定向glob没有在本工作目录或父根的指定repo-lqr位置找到AGENTS文档；未扩展搜索无关目录，也未进行Git归档/commit/push。
2. 初次嵌套底盘候选输出过长，工具显示了截断；完整中央索引已写入[底盘中央索引](<chassis_central_index.json>)，后续通过read/grep使用本地UTF-8数据。终端对部分中文名称的显示编码与JSON文件显示不同；磁盘索引和选中文本已用read读取确认。
3. 所选GB18030源码转UTF-8供read审阅，原始字节SHA与副本SHA均保留，换行/行号结构未重排。
4. 已装工具探测仅在PATH查询，见[清单](<toolchain_inventory.json>)；MinGW GCC 6.3.0仅查询[版本](<gcc_version.txt>)，不作为ARM固件构建通过证据。
5. 静态源码缺陷不是本轮工具错误，其原文完整留在引用副本，逐项见[部署审计](<SPR_DEPLOYMENT_AUDIT.md>)与[证据索引](<SPR_SOURCE_INDEX.json>)。
