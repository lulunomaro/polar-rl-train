# Method / CPU / weights 阶段 helper 交接

**仅追加可审查源码；没有执行transport或连接72/210。** root继续唯一串行远端owner；source/bootstrap/torch/requirements均不在本helper的action集合，绝不重跑已consumed阶段。已只读看到torch实际rc0；requirements/check必须等待root实际成功收据，不根据进程活跃或pip输出猜pass。本轮完成后人类暂禁子代理；本子代理完成交付后不自动续task、不spawn，后续由root直接处理。

不覆盖冻结engineering_agent或method_agent。新源在 `root_preparation_sources/weights_and_method_stage_v1/`，目标root固定：

`/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025`

## 71文件精确staging

最终method V2 index包含70条且明确不索引自身；故完整包是**71文件/690537bytes**。`METHOD_TRANSFER_PAYLOAD.json`包含全部71原字节的base64、每文件bytes/SHA，排除__pycache__，不含旧H1目录。payload本地934341bytes，SHA256 `f716fe37a2cc66e7d1726b3f165a658ec36f4523527eaaa4933e985b5b8695d5`；最终method index SHA256 `7f9c18f93b3bef98b664f0c0416e4579258dacd61884cf8ee1d8883f456cea49`。

stage-method在root/staging新唯一目录逐文件open-x、SHA验证，再验证完整71集合后rename到独立`method_bundle`；既存target只接受逐文件完全相同，不覆盖。上传CPU runner到`preparation_helpers/weights_and_method_stage_v1/cpu_method_runner.py`，也按source SHA绑定；方法71原文件始终不改。

root可复用现有受控`d.code`的stdin JSON传参，示意如下。以下只是接入形状，不含连接/credential获取或调用transport：

```python
import base64, hashlib, json
from pathlib import Path
helper_dir = Z / 'root_preparation_sources/weights_and_method_stage_v1'
remote_source = (helper_dir / 'remote_stage_helper.py').read_text('utf-8')
runner_bytes = (helper_dir / 'cpu_method_runner.py').read_bytes()
request = {
    'root': '/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025',
    'action': 'stage-method', 'phase_id': 'METHOD_STAGE_EXACT71_V1',
    'method_payload': json.loads((helper_dir / 'METHOD_TRANSFER_PAYLOAD.json').read_text('utf-8')),
    'cpu_runner': {'bytes': len(runner_bytes),
                   'sha256': hashlib.sha256(runner_bytes).hexdigest(),
                   'base64': base64.b64encode(runner_bytes).decode()},
}
# root自行审查后接入既有finite transport；helper自身不提供网络连接：
remote_code = "import json;ns={'__name__':'reviewed_stage_helper'};exec(v['helper_source'],ns);print(json.dumps(ns['run_request'](v['request'])))"
transport_payload = {'helper_source': remote_source, 'request': request}
```

root的remote wrapper需要先`import json`（如现有d.code已提供也可显式加入）。传参不进shell argv，不打印base64或payload正文。staging可在CPU依赖齐前单独做；其余action严格检查远端receipts下`ROOT_TORCH_ACTUAL.json`、`ROOT_REQUIREMENTS_ACTUAL.json`、`ROOT_CHECK_ACTUAL.json`的root/actual_returncode0/phase_passed=true。若requirements真实失败，先保留失败，再由root设计missing-only新phase；helper不会重新pip或以修改旧成功状态绕过。

## 有限CPU检查

每个action使用新的唯一phase_id，均有`<id>_STARTED.json`与`<id>_FINAL.json`。相同ID返回REFUSED_ALREADY_CONSUMED；自己`staging/WEIGHTS_AND_METHOD_ACTIVE.lock`阻止helper内并发，异常残留锁需root按实际helper进程/回执核清，不自动删他人锁或signal进程。

- `action='cpu-imports', phase_id='CPU_IMPORT_REGISTRY_V1'`：检查冻结engineering脚本/manifest SHA，独立venv经只读glibc240 loader执行官方CPU imports/tinyencoder与纯JSON registry检查；180+60秒有限子调用。
- `action='method-tests', phase_id='METHOD_CPU_TESTS_AND_BIND_V1', method_stage_binding='<root>/receipts/METHOD_STAGE_EXACT71_V1_METHOD_SOURCE_BINDING.json'`：runner最多600秒，12个CPU tests、原4CLI行为和第5个真实installed-upstream CPU import/bind。没有main、Wan构造、pretrained load或policy inference。

method测试原本`OLD_SOURCES`指旧H1源码快照；本runner不传旧目录，而是从已安装固定source读取3份已固定SHA源码，存到本次`receipts/<id>/fixed_upstream_text_views`，**仅在检查进程内**给`test_moe_cpu.OLD_SOURCES`赋新views路径。原71文件不改。test/CLI严格隐藏设备、stub is_available/device_count、拒绝CUDA init；每个CLI通过新venv相同loader，不绕回旧env或裸sys.executable。

CPU错误保留stdout/stderr与RESULT，无自动缺依赖安装。`PASS_CPU_ONLY`仍`training_ready=false`：没有真实RGB数据、VAE/DiT模型构造/真实keyaudit/完整save-resume/冻结共享模型z梯度检查或4090 fit证据。预训练仅数据下载，也不等于模型load。

## 13文件匿名有限下载

依赖实际成功后，root每次单独请求：

```python
request = {'root': ROOT_STRING, 'action': 'download-batch',
           'phase_id': 'WEIGHTS_BATCH_0001',
           'max_seconds': 180, 'max_files': 1,
           'max_new_bytes': 2 * 1024**3}
```

每批新ID；helper不内部循环反复续批。上界seconds10..900、files1..13、新字节1..8GiB，subprocess最多seconds+120秒。复用已冻结并SHA验证的download_required.py及44,253,006,084bytes/13files pinned manifest；匿名标准库urllib，不token/cookie/login，不下载数据集，不生成HF完整重复cache。`.part`原地续传，新完成文件立刻大小+官方hash校验；已完成文件在后续批次不反复读hash。每批精确收一个downloader JSON receipt，保留部分下载/HTTP错误；stdout仅安全状态/receipt路径，不signedURL/凭据/文件内容。

`action='verify-weights', phase_id='WEIGHTS_FINAL_FULL_SHA_V1'`：先只stat确认13个完整文件大小均齐，再执行一次verify-only全13文件fullSHA，最多1800+120秒；仅当`all_required_verified_in_this_receipt=true`才标`PASS_ALL13_FULL_SHA_VERIFIED`。未齐时拒绝，不先扫描已有巨型文件。最终校验不是训练GO。

原25GiB guard保持，每个阶段和下载块检查目标free；不升级driver/syslibs/compat、不写旧mod4环境、预算/canonical、不碰unknownpeer。root决定外层finite transport timeout：staging约60秒；cpu-imports约300秒；method-tests约660秒；download约seconds+180；finalverify约1980秒（内部有界I/O，可用root现有轮询而不阻塞用户沟通）。

## 回执与Git

此本地新helper、payload、QA与index均pending root Git；不是已部署或已运行的远端报告。root需把所有新remote receipts取回，包括STARTED/FINAL、METHOD_SOURCE_BINDING、子命令logs、`receipts/<CPUphase>/`全部合成数据/源码view/测试日志和RESULT、engineering CPU检查与download新JSON；模型/part原件留真实72路径，Git仅真实path/bytes/SHA索引。没有为收据归档增加任何新训练、data rollout或预算授权。
