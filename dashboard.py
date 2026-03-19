# dashboard.py — Portfolio Dashboard v6
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
    border-radius:10px; padding:14px 18px; margin-bottom:8px;
}
div[data-testid="metric-container"] label { color:#8b949e!important; font-size:12px!important; }
div[data-testid="stMetricValue"] { font-size:22px!important; color:white!important; }
.stButton>button { background:#21262d; color:white; border:1px solid #30363d; border-radius:8px; width:100%; }
.stButton>button:hover { background:#30363d; }
.block-title { color:#8b949e; font-size:11px; text-transform:uppercase; letter-spacing:1.5px; margin:14px 0 4px 0; }
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

params = st.query_params
def qp(key, default=0.0):
    try:
        return float(params.get(key, default))
    except:
        return float(default)

# ═══════════════════════════════
# БОКОВАЯ ПАНЕЛЬ
# ═══════════════════════════════
with st.sidebar:
    st.markdown("## ✏️ Мои данные")
    st.divider()

    st.markdown("### ₿ BTC")
    btc_start     = st.number_input("BTC на начало",           min_value=0.0, value=qp("bs",  0.0), step=0.0001, format="%.4f")
    btc_bought    = st.number_input("BTC куплено на кредит",   min_value=0.0, value=qp("bb",  0.0), step=0.0001, format="%.4f")
    btc_actual    = st.number_input("BTC факт (всего)",        min_value=0.0, value=qp("ba",  0.0), step=0.0001, format="%.4f")
    btc_loan_orig = st.number_input("Займ под BTC ($)",        min_value=0.0, value=qp("blo", 0.0), step=1.0,    format="%.2f")
    btc_loan_int  = st.number_input("Займ BTC + % ($)",        min_value=0.0, value=qp("bli", 0.0), step=0.01,   format="%.4f")

    st.divider()
    st.markdown("### ⟠ ETH")
    eth_start     = st.number_input("ETH на начало",           min_value=0.0, value=qp("es",  0.0), step=0.0001, format="%.4f")
    eth_bought    = st.number_input("ETH куплено на кредит",   min_value=0.0, value=qp("eb",  0.0), step=0.0001, format="%.4f")
    eth_actual    = st.number_input("ETH факт (всего)",        min_value=0.0, value=qp("ea",  0.0), step=0.0001, format="%.4f")
    eth_loan_orig = st.number_input("Займ под ETH ($)",        min_value=0.0, value=qp("elo", 0.0), step=1.0,    format="%.2f")
    eth_loan_int  = st.number_input("Займ ETH + % ($)",        min_value=0.0, value=qp("eli", 0.0), step=0.01,   format="%.4f")

    st.divider()
    st.markdown("### 🏦 Вклад")
    dep_borrowed  = st.number_input("Заёмные $ во вкладе",     min_value=0.0, value=qp("db",  0.0), step=1.0,    format="%.2f",
                                     help="Часть займа, размещённая во вкладе (напр. $150 из ETH-займа)")
    dep_personal  = st.number_input("Личные $ во вкладе",      min_value=0.0, value=qp("dp",  0.0), step=1.0,    format="%.2f",
                                     help="Ваши личные деньги во вкладе (напр. $250)")
    dep_current   = st.number_input("Вклад сейчас + доход ($)", min_value=0.0, value=qp("dc",  0.0), step=0.01,   format="%.2f",
                                     help="Текущая сумма вклада с накопленным доходом")

    st.divider()
    st.markdown("### 💵 Свободные $")
    free_usd      = st.number_input("USDT/USDC ($)",            min_value=0.0, value=qp("fu",  0.0), step=1.0,    format="%.2f")

    st.divider()
    if st.button("💾 Сохранить в ссылку"):
        st.query_params.update({
            "bs": btc_start,  "bb": btc_bought,  "ba": btc_actual,
            "blo": btc_loan_orig, "bli": btc_loan_int,
            "es": eth_start,  "eb": eth_bought,  "ea": eth_actual,
            "elo": eth_loan_orig, "eli": eth_loan_int,
            "db": dep_borrowed, "dp": dep_personal, "dc": dep_current,
            "fu": free_usd,
        })
        st.success("✅ Сохранено! Скопируйте ссылку из адресной строки.")
    if st.button("🔄 Обновить цены"):
        st.cache_data.clear()
        st.rerun()

# ═══════════════════════════════
# РАСЧЁТЫ
# ═══════════════════════════════
btc_price, eth_price = get_prices()
usd_rub = get_usd_rub()

def calc_asset(start, bought, actual, loan_orig, loan_int, price, extra_loan_income=0.0):
    my_coins         = actual - bought
    income_coins     = my_coins - start
    income_pct       = (income_coins / start * 100) if start > 0 else 0.0
    income_usd       = income_coins * price
    income_rub       = income_usd * usd_rub
    interest_paid    = loan_int - loan_orig
    interest_pct     = (interest_paid / loan_orig * 100) if loan_orig > 0 else 0.0
    # Доход на заёмные: ETH часть + доход заёмными во вкладе
    loan_profit_usd  = (bought * price) - loan_int + extra_loan_income
    loan_profit_coins= loan_profit_usd / price if price > 0 else 0.0
    loan_roi_pct     = (loan_profit_usd / loan_orig * 100) if loan_orig > 0 else 0.0
    total_usd        = actual * price
    my_usd           = my_coins * price
    ltv              = (loan_int / total_usd * 100) if total_usd > 0 else 0.0
    return dict(
        my_coins=my_coins, income_coins=income_coins, income_pct=income_pct,
        income_usd=income_usd, income_rub=income_rub,
        interest_paid=interest_paid, interest_pct=interest_pct,
        loan_profit_usd=loan_profit_usd, loan_profit_coins=loan_profit_coins,
        loan_roi_pct=loan_roi_pct, total_usd=total_usd, my_usd=my_usd, ltv=ltv,
    )

# Расчёт вклада
dep_invested      = dep_borrowed + dep_personal
dep_income_total  = dep_current - dep_invested if dep_current > 0 else 0.0
dep_ratio_borrow  = (dep_borrowed / dep_invested) if dep_invested > 0 else 0.0
dep_ratio_personal= (dep_personal / dep_invested) if dep_invested > 0 else 0.0
dep_income_borrow = dep_income_total * dep_ratio_borrow
dep_income_personal = dep_income_total * dep_ratio_personal
dep_income_pct    = (dep_income_total / dep_invested * 100) if dep_invested > 0 else 0.0

# Передаём доход заёмными во вкладе в ETH-расчёт
btc = calc_asset(btc_start, btc_bought, btc_actual, btc_loan_orig, btc_loan_int, btc_price)
eth = calc_asset(eth_start, eth_bought, eth_actual, eth_loan_orig, eth_loan_int, eth_price,
                 extra_loan_income=dep_income_borrow)

total_my_usd      = btc["my_usd"] + eth["my_usd"] + free_usd + dep_current
total_all_usd     = btc["total_usd"] + eth["total_usd"] + free_usd + dep_current
total_loan_profit = btc["loan_profit_usd"] + eth["loan_profit_usd"]
total_income_usd  = btc["income_usd"] + eth["income_usd"]
pnl_usd           = total_my_usd - INVESTED_USD
pnl_rub           = (total_my_usd * usd_rub) - INVESTED_RUB
pnl_pct_usd       = (pnl_usd / INVESTED_USD * 100) if INVESTED_USD > 0 else 0
pnl_pct_rub       = (pnl_rub / INVESTED_RUB * 100) if INVESTED_RUB > 0 else 0

def sign(v): return "+" if v >= 0 else ""
def clr(v):  return "normal" if v >= 0 else "inverse"
def m(label, val, delta="", dc="normal"): st.metric(label, val, delta, delta_color=dc)
def fmt(v, d=4): return f"{sign(v)}{v:,.{d}f}"

# ═══════════════════════════════
# ЗАГОЛОВОК
# ═══════════════════════════════
st.markdown("## 📊 Portfolio Dashboard")
st.markdown(
    f"<span style='color:#8b949e;font-size:13px'>"
    f"⏰ {datetime.now().strftime('%H:%M:%S')} &nbsp;|&nbsp; "
    f"<b style='color:#f0883e'>BTC ${btc_price:,.0f}</b> &nbsp;|&nbsp; "
    f"<b style='color:#58a6ff'>ETH ${eth_price:,.0f}</b> &nbsp;|&nbsp; "
    f"<b style='color:#3fb950'>{usd_rub:.2f} ₽/$</b> &nbsp;|&nbsp; "
    f"Старт: {INVEST_DATE}</span>",
    unsafe_allow_html=True
)
st.divider()

# ═══ ИТОГ ═══
st.markdown('<p class="block-title">💼 Итог портфеля</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: m("💼 Мои активы ($)",   f"${total_my_usd:,.2f}",        f"≈ {total_my_usd*usd_rub:,.0f} ₽")
with c2: m("📈 P&L в $",          f"{fmt(pnl_usd, 2)}$",           f"{fmt(pnl_pct_usd, 2)}% | вложено ${INVESTED_USD:,}", dc=clr(pnl_usd))
with c3: m("🇷🇺 P&L в ₽",         f"{fmt(pnl_rub, 0)} ₽",          f"{fmt(pnl_pct_rub, 2)}% | {INVESTED_RUB:,.0f} ₽", dc=clr(pnl_rub))
with c4: m("📊 Доход на займы",   f"{fmt(total_loan_profit, 2)}$", f"Рост актива: {fmt(total_income_usd, 2)}$", dc=clr(total_loan_profit))
st.divider()

# ═══ BTC ═══
st.markdown('<p class="block-title">₿ BTC — Мой доход</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: m("₿ BTC мой",        f"{btc['my_coins']:.4f} BTC",        f"Факт {btc_actual:.4f} − Кредит {btc_bought:.4f}")
with c2: m("📈 Доход в BTC",    f"{fmt(btc['income_coins'], 6)} BTC", f"Нач. {btc_start:.4f} → Мой {btc['my_coins']:.4f}", dc=clr(btc["income_coins"]))
with c3: m("📊 Доход в %",      f"{fmt(btc['income_pct'], 4)}%",      f"= {fmt(btc['income_usd'], 2)}$", dc=clr(btc["income_pct"]))
with c4: m("🇷🇺 Доход в ₽",     f"{fmt(btc['income_rub'], 0)} ₽",    f"курс {usd_rub:.2f}", dc=clr(btc["income_rub"]))

st.markdown('<p class="block-title">₿ BTC — Займ</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: m("🏦 Займ / долг",       f"${btc_loan_int:,.4f}",               f"изначально ${btc_loan_orig:,.2f}")
with c2: m("💸 % уплачено",        f"${btc['interest_paid']:,.4f}",       f"{fmt(btc['interest_pct'], 4)}%", dc="inverse" if btc["interest_paid"] > 0 else "normal")
with c3: m("💰 Доход на займ ($)",  f"{fmt(btc['loan_profit_usd'], 4)}$",  f"ROI {fmt(btc['loan_roi_pct'], 4)}%", dc=clr(btc["loan_profit_usd"]))
with c4: m("₿ Доход на займ (BTC)",f"{fmt(btc['loan_profit_coins'], 6)} BTC", f"куплено: {btc_bought:.4f} BTC", dc=clr(btc["loan_profit_coins"]))

st.markdown('<p class="block-title">₿ BTC — Статус</p>', unsafe_allow_html=True)
c1, c2, c3, _ = st.columns(4)
with c1: m("₿ Всего BTC в $", f"${btc['total_usd']:,.2f}", f"{btc_actual:.4f} × ${btc_price:,.0f}")
with c2: m("₿ Мои BTC в $",   f"${btc['my_usd']:,.2f}",   f"{btc['my_coins']:.4f} × ${btc_price:,.0f}")
with c3: m("⚖️ LTV", f"{btc['ltv']:.1f}%", "✅ OK" if btc["ltv"] < 60 else ("⚠️ Риск" if btc["ltv"] < 80 else "🚨 Опасно"), dc="normal" if btc["ltv"] < 60 else "inverse")
st.divider()

# ═══ ETH ═══
st.markdown('<p class="block-title">⟠ ETH — Мой доход</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: m("⟠ ETH мой",        f"{eth['my_coins']:.4f} ETH",        f"Факт {eth_actual:.4f} − Кредит {eth_bought:.4f}")
with c2: m("📈 Доход в ETH",    f"{fmt(eth['income_coins'], 6)} ETH", f"Нач. {eth_start:.4f} → Мой {eth['my_coins']:.4f}", dc=clr(eth["income_coins"]))
with c3: m("📊 Доход в %",      f"{fmt(eth['income_pct'], 4)}%",      f"= {fmt(eth['income_usd'], 2)}$", dc=clr(eth["income_pct"]))
with c4: m("🇷🇺 Доход в ₽",     f"{fmt(eth['income_rub'], 0)} ₽",    f"курс {usd_rub:.2f}", dc=clr(eth["income_rub"]))

st.markdown('<p class="block-title">⟠ ETH — Займ (включая вклад)</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: m("🏦 Займ / долг",       f"${eth_loan_int:,.4f}",               f"изначально ${eth_loan_orig:,.2f}")
with c2: m("💸 % уплачено",        f"${eth['interest_paid']:,.4f}",       f"{fmt(eth['interest_pct'], 4)}%", dc="inverse" if eth["interest_paid"] > 0 else "normal")
with c3: m("💰 Доход на займ ($)",  f"{fmt(eth['loan_profit_usd'], 4)}$",
           f"ETH {fmt(eth['loan_profit_usd']-dep_income_borrow, 2)}$ + Вклад {fmt(dep_income_borrow, 2)}$",
           dc=clr(eth["loan_profit_usd"]))
with c4: m("⟠ Доход на займ (ETH)",f"{fmt(eth['loan_profit_coins'], 6)} ETH", f"куплено: {eth_bought:.4f} ETH", dc=clr(eth["loan_profit_coins"]))

st.markdown('<p class="block-title">⟠ ETH — Статус</p>', unsafe_allow_html=True)
c1, c2, c3, _ = st.columns(4)
with c1: m("⟠ Всего ETH в $", f"${eth['total_usd']:,.2f}", f"{eth_actual:.4f} × ${eth_price:,.0f}")
with c2: m("⟠ Мои ETH в $",   f"${eth['my_usd']:,.2f}",   f"{eth['my_coins']:.4f} × ${eth_price:,.0f}")
with c3: m("⚖️ LTV", f"{eth['ltv']:.1f}%", "✅ OK" if eth["ltv"] < 60 else ("⚠️ Риск" if eth["ltv"] < 80 else "🚨 Опасно"), dc="normal" if eth["ltv"] < 60 else "inverse")
st.divider()

# ═══ ВКЛАД ═══
if dep_invested > 0:
    st.markdown('<p class="block-title">🏦 Вклад</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        m("💰 Общий доход вклада",
          f"{fmt(dep_income_total, 2)}$",
          f"{fmt(dep_income_pct, 4)}% от ${dep_invested:,.2f}",
          dc=clr(dep_income_total))
    with c2:
        m("🏦 Доход на заёмные",
          f"{fmt(dep_income_borrow, 2)}$",
          f"${dep_borrowed:,.2f} = {dep_ratio_borrow*100:.1f}% вклада",
          dc=clr(dep_income_borrow))
    with c3:
        m("👤 Доход на личные",
          f"{fmt(dep_income_personal, 2)}$",
          f"${dep_personal:,.2f} = {dep_ratio_personal*100:.1f}% вклада",
          dc=clr(dep_income_personal))
    with c4:
        m("📊 Вклад сейчас",
          f"${dep_current:,.2f}",
          f"вложено: заёмные ${dep_borrowed:,.2f} + личные ${dep_personal:,.2f}")
    st.divider()

# ═══ СВОБОДНЫЕ $ ═══
if free_usd > 0:
    st.markdown('<p class="block-title">💵 Свободные средства</p>', unsafe_allow_html=True)
    c1, c2, _ = st.columns(3)
    with c1: m("💵 USDT/USDC", f"${free_usd:,.2f}", f"≈ {free_usd*usd_rub:,.0f} ₽")
    with c2: m("📊 Доля портфеля", f"{(free_usd/total_my_usd*100):.1f}%" if total_my_usd > 0 else "0%", "")
    st.divider()

# ═══ ГРАФИКИ ═══
if total_all_usd > 0:
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<p class="block-title">🪙 Распределение активов</p>', unsafe_allow_html=True)
        pie_l, pie_v, pie_c = [], [], []
        if btc["my_usd"] > 0:
            pie_l.append("BTC мой"); pie_v.append(btc["my_usd"]); pie_c.append("#f0883e")
        if btc_bought * btc_price > 0:
            pie_l.append("BTC кредит"); pie_v.append(btc_bought * btc_price); pie_c.append("#f0883e55")
        if eth["my_usd"] > 0:
            pie_l.append("ETH мой"); pie_v.append(eth["my_usd"]); pie_c.append("#58a6ff")
        if eth_bought * eth_price > 0:
            pie_l.append("ETH кредит"); pie_v.append(eth_bought * eth_price); pie_c.append("#58a6ff55")
        if dep_current > 0:
            pie_l.append("Вклад"); pie_v.append(dep_current); pie_c.append("#3fb950")
        if free_usd > 0:
            pie_l.append("Free $"); pie_v.append(free_usd); pie_c.append("#a371f7")
        if pie_v:
            fig = go.Figure(go.Pie(labels=pie_l, values=pie_v, hole=0.42,
                textinfo="label+percent", textfont={"size": 11},
                marker=dict(colors=pie_c, line=dict(color="#0d1117", width=2))))
            fig.update_layout(paper_bgcolor="#161b22", font=dict(color="white"),
                height=300, margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<p class="block-title">📊 Весь доход по источникам</p>', unsafe_allow_html=True)
        bx = ["BTC\n(актив)", "BTC\n(займ)", "ETH\n(актив)", "ETH\n(займ)", "Вклад\n(заёмные)", "Вклад\n(личные)"]
        by = [btc["income_usd"], btc["loan_profit_usd"]-0,
              eth["income_usd"], eth["loan_profit_usd"]-dep_income_borrow,
              dep_income_borrow, dep_income_personal]
        bc = ["#3fb950" if v >= 0 else "#f85149" for v in by]
        fig2 = go.Figure(go.Bar(x=bx, y=by, marker_color=bc,
            text=["$" + f"{abs(v):,.2f}" for v in by],
            textposition="outside", textfont=dict(color="white", size=11), cliponaxis=False))
        fig2.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22",
            font=dict(color="white"), height=300, margin=dict(l=10,r=40,t=20,b=10),
            yaxis=dict(gridcolor="#21262d", zerolinecolor="#8b949e", title_text="USD ($)"),
            xaxis=dict(tickfont=dict(color="white", size=11)))
        st.plotly_chart(fig2, use_container_width=True)

if total_all_usd == 0:
    st.info("👈  Введите данные в боковой панели, затем нажмите 💾 Сохранить в ссылку")

st.caption(f"BTC/ETH цены — каждую минуту · ₽/$ — каждые 5 мин · Вложено: ${INVESTED_USD} / {INVESTED_RUB:,.0f} ₽ ({INVEST_DATE})")
