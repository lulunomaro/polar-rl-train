Dispatcher V2已冻结，解决72 run-python.sh实际exec为ld-loader的确定接线错误。h1仍精确原python argv/exe；72只接受既有LD/libpath/envPython/-B前缀+原逻辑argv，不使用endswith或放宽解释器匹配。

fresh分支启动同一CPU子进程后，最多5s等待wrapper exec稳定，要求同pid/create/exe/argv/cwd两次精确一致，再保存实际identity并等待EXIT0。cache使用相同expected recipe及精确root验证，绝不重CPU/model load。原Proof/schema与manifest/script/report/source/STARTED/WAITED/externalSHA绑定保持，旧冻结11文件目录未改。

本机10项source/metadata检查通过：使用已保存86B三路实际process文本核对recipe，fake psutil+fakeclock模拟exec稳定/timeout/create变化，没有真实进程、SDK、网络或模型。root应在新controllers和3payload复制本同名dispatcher后全部重pin，旧SHA87f...不再用于新manifest。观察器可复用expected_exec_identity(spec,logicalargv)核对worker或node。
