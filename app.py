import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AI炒股助手 MVP", page_icon="📈", layout="wide")
st.title("📈 AI 炒股助手 · MVP 1.0")
st.caption("A股研究辅助｜透明规则｜风险优先")

st.warning("演示模式不含实时行情。示例股票和财务数据均为虚构，仅用于测试软件流程，不代表真实公司或投资建议。")

columns = ["代码","名称","行业","营收增长率_pct","净利润增长率_pct","扣非净利润增长率_pct",
"经营现金流净利润比","资产负债率_pct","ROE_pct","PE","应收账款增长率_pct",
"商誉净资产比_pct","风险警示","审计意见异常","重大监管风险","数据报告期"]

demo = pd.DataFrame([
["600001","演示样本甲","制造业",18,22,19,1.25,42,14,18,10,3,"否","否","否","2025年报（虚构）"],
["600002","演示样本乙","消费业",8,6,4,0.65,58,8,35,31,18,"否","否","否","2025年报（虚构）"],
["300001","演示样本丙","科技业",35,42,38,0.30,67,11,80,48,35,"否","否","否","2025年报（虚构）"],
["600003","演示样本丁","周期行业",-8,-25,-32,-0.45,76,-4,12,55,8,"是","是","是","2025年报（虚构）"],
["000001","演示样本戊","医药业",12,15,12,1.05,38,13,26,15,6,"否","否","否","2025年报（虚构）"],
], columns=columns)

with st.sidebar:
    st.header("数据")
    mode = st.radio("选择方式", ["体验虚构演示数据", "上传自己的CSV"])
    st.caption("百分比填数字：12代表12%；现金流/净利润比填倍数。风险字段填“是/否”。")
    st.code(",".join(columns), language="text")

if mode == "上传自己的CSV":
    file = st.file_uploader("上传 CSV", type=["csv"])
    if file is None:
        st.info("请上传CSV，或切换到演示数据体验。")
        st.stop()
    try:
        df = pd.read_csv(file, dtype={"代码": str})
    except Exception as exc:
        st.error(f"读取失败：{exc}")
        st.stop()
else:
    df = demo.copy()
    st.info("当前为虚构演示数据。请勿据此交易。")

missing = [c for c in columns if c not in df.columns]
if missing:
    st.error("CSV缺少字段：" + "、".join(missing))
    st.stop()

num_cols = ["营收增长率_pct","净利润增长率_pct","扣非净利润增长率_pct",
"经营现金流净利润比","资产负债率_pct","ROE_pct","PE","应收账款增长率_pct","商誉净资产比_pct"]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

def is_yes(x):
    return str(x).strip().lower() in ["是","yes","true","1","y"]

def score_row(r):
    score, risks, reasons, hard = 0, [], [], []
    def val(k):
        return r[k] if pd.notna(r[k]) else None

    g, p, roe = val("营收增长率_pct"), val("扣非净利润增长率_pct"), val("ROE_pct")
    cash, debt, pe = val("经营现金流净利润比"), val("资产负债率_pct"), val("PE")
    ar, goodwill = val("应收账款增长率_pct"), val("商誉净资产比_pct")

    if g is not None:
        score += 10 if g >= 15 else 7 if g >= 5 else 3 if g >= 0 else 0
        if g < 0: risks.append("营收下降")
        elif g >= 5: reasons.append("营收保持正增长")
    else: risks.append("营收增长率缺失")

    if p is not None:
        score += 12 if p >= 15 else 8 if p >= 0 else 0
        if p < 0: risks.append("扣非净利润下降")
        else: reasons.append("扣非净利润未同比下降")
    else: risks.append("扣非净利润增长率缺失")

    if roe is not None:
        score += 8 if roe >= 15 else 5 if roe >= 8 else 2 if roe >= 0 else 0
        if roe < 0: risks.append("ROE为负")
        elif roe >= 8: reasons.append("ROE达到初筛参考水平")
    else: risks.append("ROE缺失")

    if cash is not None:
        score += 15 if cash >= 1 else 9 if cash >= .7 else 3 if cash >= 0 else 0
        if cash < .7: risks.append("现金流对利润覆盖偏弱")
        else: reasons.append("现金流覆盖达到初筛参考水平")
    else: risks.append("现金流指标缺失")

    if debt is not None:
        score += 10 if debt <= 40 else 7 if debt <= 60 else 3 if debt <= 75 else 0
        if debt > 75: risks.append("资产负债率偏高，需结合行业核实")
    else: risks.append("资产负债率缺失")

    if pe is not None and pe > 0:
        score += 20 if pe <= 15 else 16 if pe <= 25 else 10 if pe <= 40 else 4
        if pe > 40: risks.append("PE较高，需核实估值与增长预期")
        elif pe <= 25: reasons.append("PE处于初筛区间，不代表低估")
    else: risks.append("PE缺失、为负或不适用")

    if ar is not None:
        score += 8 if ar <= 10 else 5 if ar <= 25 else 1
        if ar > 25: risks.append("应收账款增速偏高，需与营收增速对比")
    else: risks.append("应收账款增长率缺失")

    if goodwill is not None:
        score += 7 if goodwill <= 10 else 4 if goodwill <= 30 else 1
        if goodwill > 30: risks.append("商誉占净资产比例偏高")
    else: risks.append("商誉指标缺失")

    for field, label in [("风险警示","风险警示标记"),("审计意见异常","审计意见异常"),("重大监管风险","重大监管风险")]:
        if is_yes(r[field]):
            hard.append(label)
            risks.append(label)

    missing_n = int(r[num_cols].isna().sum())
    if hard: status = "风险门槛触发"
    elif missing_n >= 3: status = "数据不足"
    elif score >= 75 and not risks: status = "优先研究"
    elif score >= 60: status = "持续观察"
    else: status = "谨慎研究"
    if not reasons: reasons = ["暂未发现足够的正面筛选信号"]
    if not risks: risks = ["未触发本模型预设阈值，不代表没有风险"]
    return pd.Series([min(100, int(round(score))), status, "；".join(reasons), "；".join(risks),
                      "是" if hard else "否", missing_n],
                     index=["研究评分","初筛分类","主要筛选理由","风险提示","风险门槛","缺失数值字段数"])

out = pd.concat([df, df.apply(score_row, axis=1)], axis=1)
st.subheader("一、股票初筛")
a,b,c = st.columns(3)
a.metric("分析数量", len(out))
b.metric("风险门槛触发", int((out["风险门槛"]=="是").sum()))
c.metric("数据不足", int((out["初筛分类"]=="数据不足").sum()))
choices = ["优先研究","持续观察","谨慎研究","风险门槛触发","数据不足"]
selected_status = st.multiselect("显示分类", choices, default=choices)
view = out[out["初筛分类"].isin(selected_status)].sort_values(["风险门槛","研究评分"], ascending=[True,False])
show = ["代码","名称","行业","研究评分","初筛分类","数据报告期","主要筛选理由","风险提示"]
st.dataframe(view[show], use_container_width=True, hide_index=True)
st.download_button("下载筛选结果CSV", out.to_csv(index=False).encode("utf-8-sig"),
                   "筛选结果.csv", "text/csv")

st.subheader("二、个股研究卡")
opts = [f"{x['代码']} - {x['名称']}" for _,x in out.iterrows()]
chosen = st.selectbox("选择股票", opts)
r = out.iloc[opts.index(chosen)]
x,y,z = st.columns(3)
x.metric("研究评分", f"{r['研究评分']}/100")
y.metric("初筛分类", r["初筛分类"])
z.metric("风险门槛", r["风险门槛"])
st.markdown("**筛选理由**")
st.write(r["主要筛选理由"])
st.markdown("**风险提示**")
st.write(r["风险提示"])
st.markdown("**财务数据**")
st.dataframe(pd.DataFrame({"指标": num_cols, "数值": [r[k] for k in num_cols]}),
             use_container_width=True, hide_index=True)

st.subheader("三、买入前自查")
for i, item in enumerate([
"已核实最新财报、公告和数据报告期","已理解主营业务与盈利模式",
"已核对经营现金流与利润是否匹配","已核实估值指标适用于该行业",
"已检查风险警示、审计意见、诉讼和监管事项",
"已明确投资逻辑失效条件和可承受损失","不会仅因模型评分高就直接买入"]):
    st.checkbox(item, key=f"check_{i}")

st.subheader("四、模型与限制")
st.markdown("""
- 初始评分：盈利增长与ROE最高30分；现金流与负债最高25分；PE初筛最高20分；应收账款与商誉最高15分。
- 重大风险标记单独触发风险门槛，不能用高分抵消。
- 这是可解释的初始规则，不是经验证的盈利策略，也不是买卖信号。
- PE和资产负债率需按行业调整；银行、保险、券商、房地产等不能简单套用同一标准。
- 正式使用前需做历史回测、样本外检验，并处理退市股票、交易成本、停牌、涨跌停和财报披露时间。
""")
st.caption("免责声明：本工具仅用于学习和研究辅助，不构成个性化证券投资建议。投资有风险。")
st.caption("分析生成时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
