# AI炒股助手 MVP 1.0

## 文件
- `app.py`：应用程序
- `requirements.txt`：依赖
- `sample_fictitious_data.csv`：虚构示例数据，可用来测试上传
- 本应用不是实时行情软件；示例数据全部虚构。

## 运行
安装 Python 3.11+ 后，在本目录运行：
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 手机上使用
先在电脑或云端启动应用，再用安卓浏览器访问部署地址。它是适配手机的网页应用，不是 APK。后续可再考虑封装原生安卓应用。

## CSV字段
代码,名称,行业,营收增长率_pct,净利润增长率_pct,扣非净利润增长率_pct,经营现金流净利润比,资产负债率_pct,ROE_pct,PE,应收账款增长率_pct,商誉净资产比_pct,风险警示,审计意见异常,重大监管风险,数据报告期

百分比填数字（12代表12%）；现金流/净利润比填倍数（1.2代表1.2倍）；风险字段使用“是”或“否”。

## 免费部署参考
Streamlit Community Cloud官方文档：https://docs.streamlit.io/deploy/streamlit-community-cloud
部署免费额度和政策可能变化。不要上传证券账户密码或其他敏感信息。

## 合规和数据提醒
商业化提供个性化荐股、投资建议或自动交易功能前，应先评估中国证券监管和相关资质要求。数据接入需核实授权、稳定性、更新频率和使用条款。
