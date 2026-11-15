# 首个5分钟检查点：同时间窗启停比较

完整检查点 model_005m.pt，iter25361，SHA82a9448cf39f38c6488b627a224b339d8a161b6297cbc185d40fc69205eee104。冻结db6父模型作对照；同8个nominal MuJoCo0ms情形，每例截到双方共同结束时间。

|地形|指标|父|5m|
|---|---|---:|---:|
|random_uniform_for_rm|startup_pitch_peak_deg|12.2865|12.3623|
|random_uniform_for_rm|braking_pitch_peak_deg|22.6446|20.2248|
|random_uniform_for_rm|startup_rate_peak_rad_s|2.7201|2.6003|
|random_uniform_for_rm|braking_rate_peak_rad_s|3.1430|2.9889|
|random_uniform_for_rm|pitch_RMS_deg|5.6770|5.4998|
|random_uniform_for_rm|moving_vx_MAE|0.8598|0.8528|
|plane_for_rm|startup_pitch_peak_deg|12.2066|12.1094|
|plane_for_rm|braking_pitch_peak_deg|18.6731|18.0876|
|plane_for_rm|startup_rate_peak_rad_s|2.6849|2.5839|
|plane_for_rm|braking_rate_peak_rad_s|3.0049|2.8770|
|plane_for_rm|pitch_RMS_deg|5.5490|5.4733|
|plane_for_rm|moving_vx_MAE|0.8460|0.8512|

粗糙地形急停角度峰值下降约10.69%，平地下降约3.13%；粗糙地形启动角度仍12.36°，尚未解决。运动期MAE是硬启停短窗口，不能当平地稳态速度误差。

8个启停情形仍有两个高度0.40/速度2.2情形因地图越界提前结束（与父同为6/8完整）；不是摔倒。其余平地60/台阶/下阶结果见本检查点EVALUATION.json，未完成前不声称保留通过。训练继续原40分钟上限，不追加预算。
