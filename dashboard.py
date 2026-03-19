
# dashboard.py — BTC + ETH + Free USD Dashboard
# pip install streamlit plotly requests

import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

INVESTED_USD = 3768.79
INVESTED_RUB = 319000.0
INVEST_DATE  = "18.08.2025"

st.set_page_config(page_title="Portfolio Dashboard", page_icon="₿", layout="wide")
st.markdown("""
<style>
.stApp { background-color:#0d1117!important; color:white!important; }
section[data-testid="stSidebar"] { background-color:#161b22!important; border-right:1px solid #21262d; }
div[data-testid="metric-container"] {
    background:#161b22; border:1px solid #21262d;
    border-radius:10px; padding:16px 20px; margin-bottom:8px;
}
div[data-testid="metric-container"] label { color:#8b949e!important; font-size:13px!important; }
div[data-testid="stMetricValue"] { font-size:26px!important; color:white!important; }
.stButton>button { background:#21262d; color:white; border:1px solid #30363d; border-radius:8px; width:100%; }
.stButton>button:hover { background:#30363d; }
.block-title { color:#8b949e; font-size:11px; text-transform:uppercase; letter-spacing:1.5px; margin:18px 0 6px 0; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_prices():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
            timeout=8
        )
        d = r.json()
        return float(d["bitcoin"]["usd"]), float(d["ethereum"]["usd"])
    except:
        return 85000.0, 2000.0

@st.cache_data(ttl=300)
def get_usd_rub():
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        return float(r.json()["rates"]["RUB"])
    except:
        try:
            r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
            return float(r.json()["rates"]["RUB"])
        except:
            return 82.59

# ═══════════════════════════════
# БОКОВАЯ ПАНЕЛЬ
# ═══════════════════════════════
with st.sidebar:
    st.markdown("## ✏️ Мои данные")
    st.divider()

    st.markdown("### ₿ BTC")
    btc_amount         = st.number_input("Кол-во BTC",              min_value=0.0, value=0.0, step=0.0001, format="%.4f")
    btc_loan_orig      = st.number_input("Займ под BTC ($)",        min_value=0.0, value=0.0, step=1.0,    format="%.2f")
    btc_loan_interest  = st.number_input("Займ под BTC + % ($)",    min_value=0.0, value=0.0, step=0.01,   format="%.4f")
    btc_loan_income    = st.number_input("Займ BTC + доход ($)",    min_value=0.0, value=0.0, step=0.01,   format="%.4f")

    st.divider()
    st.markdown("### ⟠ ETH")
    eth_amount         = st.number_input("Кол-во ETH",              min_value=0.0, value=0.0, step=0.001,  format="%.3f")
    eth_loan_orig      = st.number_input("Займ под ETH ($)",        min_value=0.0, value=0.0, step=1.0,    format="%.2f")
    eth_loan_interest  = st.number_input("Займ под ETH + % ($)",    min_value=0.0, value=0.0, step=0.01,   format="%.4f")
    eth_loan_income    = st.number_input("Займ ETH + доход ($)",    min_value=0.0, value=0.0, step=0.01,   format="%.4f")

    st.divider()
    st.markdown("### 💵 Свободные $")
    free_usd           = st.number_input("Свободные USDT/USDC ($)", min_value=0.0, value=0.0, step=1.0,    format="%.2f")

    st.divider()
    if st.button("🔄 Обновить цены"):
        st.cache_data.clear()
        st.rerun()

# ═══════════════════════════════
# РАСЧЁТЫ
# ═══════════════════════════════
btc_price, eth_price = get_prices()
usd_rub = get_usd_rub()

def calc_asset(amount, price, loan_orig, loan_interest, loan_income):
    usd          = amount * price
    rub          = usd * usd_rub
    interest_usd = loan_interest - loan_orig
    interest_pct = (interest_usd / loan_orig * 100) if loan_orig > 0 else 0.0
    profit_usd   = loan_income - loan_interest
    roi_pct      = (profit_usd / loan_orig * 100) if loan_orig > 0 else 0.0
    profit_asset = profit_usd / price if price > 0 else 0.0
    asset_inc_pct= (profit_asset / amount * 100) if amount > 0 else 0.0
    ltv          = (loan_interest / usd * 100) if usd > 0 else 0.0
    return dict(usd=usd, rub=rub,
                interest_usd=interest_usd, interest_pct=interest_pct,
                profit_usd=profit_usd, roi_pct=roi_pct,
                profit_asset=profit_asset, asset_inc_pct=asset_inc_pct,
                ltv=ltv)

btc = calc_asset(btc_amount, btc_price, btc_loan_orig, btc_loan_interest, btc_loan_income)
eth = calc_asset(eth_amount, eth_price, eth_loan_orig, eth_loan_interest, eth_loan_income)

total_assets_usd = btc["usd"] + eth["usd"] + free_usd
total_profit_usd = btc["profit_usd"] + eth["profit_usd"]
total_loan_orig  = btc_loan_orig + eth_loan_orig
total_interest   = (btc["interest_usd"] + eth["interest_usd"])
total_pnl_usd    = total_assets_usd - INVESTED_USD
total_pnl_rub    = (total_assets_usd * usd_rub) - INVESTED_RUB
total_pnl_pct_usd= (total_pnl_usd / INVESTED_USD * 100) if INVESTED_USD > 0 else 0
total_pnl_pct_rub= (total_pnl_rub / INVESTED_RUB * 100) if INVESTED_RUB > 0 else 0

def sign(v): return "+" if v > 0 else ""
def clr(v):  return "normal" if v >= 0 else "inverse"
def m(label, value, delta="", dc="normal"): st.metric(label, value, delta, delta_color=dc)

# ═══════════════════════════════
# ЗАГОЛОВОК
# ═══════════════════════════════
st.markdown(f"""
## 📊 Portfolio Dashboard
<span style='color:#8b949e;font-size:13px'>
⏰ {datetime.now().strftime("%H:%M:%S")} &nbsp;|&nbsp;
₿ <b style='color:#f0883e'>${btc_price:,.0f}</b> &nbsp;|&nbsp;
⟠ <b style='color:#58a6ff'>${eth_price:,.0f}</b> &nbsp;|&nbsp;
💱 <b style='color:#3fb950'>{usd_rub:.2f} ₽/$</b> &nbsp;|&nbsp;
📅 Старт: {INVEST_DATE}
</span>
""", unsafe_allow_html=True)
st.divider()

# ═══════════════════════════════
# ИТОГОВЫЙ БЛОК
# ═══════════════════════════════
st.markdown('<p class="block-title">💼 Итог портфеля</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: m("💼 Всего активов ($)", f"${total_assets_usd:,.2f}", f"BTC+ETH+Free: {total_assets_usd*usd_rub:,.0f} ₽")
with c2: m("📈 P&L в $", f"{sign(total_pnl_usd)}${total_pnl_usd:,.2f}",
           f"{sign(total_pnl_pct_usd)}{total_pnl_pct_usd:.2f}% | вложено ${INVESTED_USD:,}", dc=clr(total_pnl_usd))
with c3: m("🇷🇺 P&L в ₽", f"{sign(total_pnl_rub)}{total_pnl_rub:,.0f} ₽",
           f"{sign(total_pnl_pct_rub)}{total_pnl_pct_rub:.2f}% | вложено {INVESTED_RUB:,.0f} ₽", dc=clr(total_pnl_rub))
with c4: m("📊 Доход на займы ($)", f"{sign(total_profit_usd)}${total_profit_usd:,.4f}",
           f"Займов всего: ${total_loan_orig:,.2f} | % уплачено: ${total_interest:,.4f}", dc=clr(total_profit_usd))

st.divider()

# ═══════════════════════════════
# BTC БЛОК
# ═══════════════════════════════
st.markdown('<p class="block-title">₿ BTC</p>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1: m("₿ BTC в $",        f"${btc['usd']:,.2f}",          f"{btc_amount:.4f} BTC × ${btc_price:,.0f}")
with c2: m("⚖️ LTV BTC",       f"{btc['ltv']:.1f}%",           "✅ OK" if btc["ltv"] < 60 else "⚠️ Риск", dc="normal" if btc["ltv"] < 60 else "inverse")
with c3: m("💸 % по займу",    f"${btc['interest_usd']:,.4f}", f"{sign(btc['interest_pct'])}{btc['interest_pct']:.4f}%", dc="inverse" if btc["interest_usd"] > 0 else "normal")
with c4: m("💰 Доход на займ", f"{sign(btc['profit_usd'])}${btc['profit_usd']:,.4f}",
           f"ROI {sign(btc['roi_pct'])}{btc['roi_pct']:.4f}%", dc=clr(btc["profit_usd"]))
with c5: m("₿ Доход в BTC",   f"{sign(btc['profit_asset'])}{btc['profit_asset']:.6f} BTC",
           f"{sign(btc['asset_inc_pct'])}{btc['asset_inc_pct']:.4f}% от BTC", dc=clr(btc["profit_asset"]))

st.divider()

# ═══════════════════════════════
# ETH БЛОК
# ═══════════════════════════════
st.markdown('<p class="block-title">⟠ ETH</p>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1: m("⟠ ETH в $",        f"${eth['usd']:,.2f}",          f"{eth_amount:.3f} ETH × ${eth_price:,.0f}")
with c2: m("⚖️ LTV ETH",       f"{eth['ltv']:.1f}%",           "✅ OK" if eth["ltv"] < 60 else "⚠️ Риск", dc="normal" if eth["ltv"] < 60 else "inverse")
with c3: m("💸 % по займу",    f"${eth['interest_usd']:,.4f}", f"{sign(eth['interest_pct'])}{eth['interest_pct']:.4f}%", dc="inverse" if eth["interest_usd"] > 0 else "normal")
with c4: m("💰 Доход на займ", f"{sign(eth['profit_usd'])}${eth['profit_usd']:,.4f}",
           f"ROI {sign(eth['roi_pct'])}{eth['roi_pct']:.4f}%", dc=clr(eth["profit_usd"]))
with c5: m("⟠ Доход в ETH",   f"{sign(eth['profit_asset'])}{eth['profit_asset']:.6f} ETH",
           f"{sign(eth['asset_inc_pct'])}{eth['asset_inc_pct']:.4f}% от ETH", dc=clr(eth["profit_asset"]))

st.divider()

# ═══════════════════════════════
# СВОБОДНЫЕ $
# ═══════════════════════════════
if free_usd > 0:
    st.markdown('<p class="block-title">💵 Свободные средства</p>', unsafe_allow_html=True)
    c1, c2, _ = st.columns(3)
    with c1: m("💵 USDT/USDC", f"${free_usd:,.2f}", f"≈ {free_usd * usd_rub:,.0f} ₽")
    with c2: m("📊 Доля от портфеля",
               f"{(free_usd/total_assets_usd*100):.1f}%" if total_assets_usd > 0 else "0%", "")
    st.divider()

# ═══════════════════════════════
# ГРАФИК
# ═══════════════════════════════
if total_assets_usd > 0:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<p class="block-title">🪙 Распределение активов</p>', unsafe_allow_html=True)
        pie_labels, pie_values, pie_colors = [], [], []
        if btc["usd"] > 0:
            pie_labels.append("BTC $" + f"{btc['usd']:,.0f}")
            pie_values.append(btc["usd"])
            pie_colors.append("#f0883e")
        if eth["usd"] > 0:
            pie_labels.append("ETH $" + f"{eth['usd']:,.0f}")
            pie_values.append(eth["usd"])
            pie_colors.append("#58a6ff")
        if free_usd > 0:
            pie_labels.append("Free $" + f"{free_usd:,.0f}")
            pie_values.append(free_usd)
            pie_colors.append("#3fb950")

        if pie_values:
            fig = go.Figure(go.Pie(
                labels=pie_labels, values=pie_values, hole=0.42,
                textinfo="label+percent", textfont={"size": 13},
                marker=dict(colors=pie_colors, line=dict(color="#0d1117", width=3)),
            ))
            fig.update_layout(paper_bgcolor="#161b22", font=dict(color="white"),
                              height=300, margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<p class="block-title">📊 Займы и доход</p>', unsafe_allow_html=True)
        bar_x, bar_y, bar_c = [], [], []
        if btc_loan_orig > 0:
            bar_x += ["BTC займ", "BTC+%", "BTC доход"]
            bar_y += [btc_loan_orig, btc_loan_interest, btc_loan_income]
            bar_c += ["#58a6ff", "#f85149", "#3fb950"]
        if eth_loan_orig > 0:
            bar_x += ["ETH займ", "ETH+%", "ETH доход"]
            bar_y += [eth_loan_orig, eth_loan_interest, eth_loan_income]
            bar_c += ["#7c3aed", "#f85149", "#3fb950"]

        if bar_x:
            fig2 = go.Figure(go.Bar(
                x=bar_x, y=bar_y, marker_color=bar_c,
                text=["$" + f"{abs(v):,.2f}" for v in bar_y],
                textposition="outside", textfont=dict(color="white", size=12),
                cliponaxis=False,
            ))
            fig2.update_layout(
                paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                font=dict(color="white"), height=300,
                margin=dict(l=10,r=40,t=20,b=10),
                yaxis=dict(gridcolor="#21262d", zerolinecolor="#8b949e", title_text="USD ($)"),
                xaxis=dict(tickfont=dict(color="white", size=12)),
            )
            st.plotly_chart(fig2, use_container_width=True)

if total_assets_usd == 0:
    st.info("👈  Введите данные в боковой панели слева")

st.caption(f"₿⟠ цены — каждую минуту · ₽/$ — каждые 5 мин · Вложено: ${INVESTED_USD} / {INVESTED_RUB:,.0f} ₽ ({INVEST_DATE})")
