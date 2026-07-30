# Copyright (c) 2026 Samuel Gobbi (Ezpeon). Licensed under the MIT License (see LICENSE).

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATASETS_FOLDER = Path(__file__).resolve().parent / "datasets"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
GRAY = "#52514e"
FONT = "sans-serif"
SEC3_SERIES = {
    "S&P 500": ("sp500_monthly.csv", "^GSPC"),
    "Bitcoin": ("btc_monthly.csv", "BTC-USD"),
    "Ethereum": ("eth_monthly.csv", "ETH-USD"),
    "Gold": ("au_monthly.csv", "GC=F"),
    "Fine Wine": ("Cult_Wines_Global_Index_01-07-2025.csv", "Global"),
    "Magic the Gathering Cards": ("RESERVED_LIST.csv", "PaperPrice"),
    "Pokemon Cards": ("pokemon.csv", "UngradedPrice"),
    "Luxury Watches": ("watches.csv", "ValueinUSD"),
}
SEC3_COLORS = [
    BLUE,  # S&P 500
    ORANGE,  # Bitcoin
    "#1baf7a",  # Ethereum
    "#eda100",  # Gold
    "#e87ba4",  # Fine Wine
    "#008300",  # Magic the Gathering Cards
    "#4a3aa7",  # Pokemon Cards
    "#e34948",  # Luxury Watches
]


def get_sec_1_data(narrow: bool) -> pd.DataFrame:
    filename = ""
    if narrow:
        filename = "mini_scf_nq.csv"
    else:
        filename = "mini_scf.csv"
    df = pd.read_csv(DATASETS_FOLDER / "Sec1" / filename)
    df["PCT_ALTERNATIVE"] = df["ALL_ALTERNATIVE"] / df["TOTAL_INVESTED"] * 100
    df["PCT_TRADITIONAL"] = 100 - df["PCT_ALTERNATIVE"]
    return df


def get_sec_2_data() -> pd.DataFrame:
    allocation = pd.read_csv(DATASETS_FOLDER / "Sec2" / "allocation.csv")
    aum = pd.read_csv(DATASETS_FOLDER / "Sec2" / "aum.csv")
    merged = pd.merge(allocation, aum, on="Year", how="outer").sort_values("Year")
    merged["ALLOC_INDEXED"] = (
        merged["Alloc_Perc"] / merged["Alloc_Perc"].dropna().iloc[0] * 100
    )
    merged["AUM_INDEXED"] = merged["AUM_T"] / merged["AUM_T"].dropna().iloc[0] * 100
    return merged


def get_sec_3_data() -> pd.DataFrame:
    indexed = {}
    for label, (filename, column) in SEC3_SERIES.items():
        df = pd.read_csv(DATASETS_FOLDER / "Sec3" / filename, parse_dates=["Date"])
        series = df.set_index("Date")[column].sort_index()
        indexed[label] = series / series.iloc[0] * 100
    return pd.DataFrame(indexed)


st.set_page_config(
    page_title="How Alternative Investments Diverged Between Institutions and Households",
    layout="wide",
)
st.title("How Alternative Investments Diverged Between Institutions and Households")
st.markdown(
    "Alternative investments - assets like private equity, hedge funds, real estate, commodities, collectibles, and crypto that sit outside traditional stocks and bonds - have grown steadily among institutions while remaining nearly flat for households."
)

st.divider()  ################################################################

col_g, col_t = st.columns([3, 2])

with col_g:
    narrow = st.toggle(
        'Narrow "financial alternatives" definition',
        value=True,
        help=(
            'choose whether to include private business equity, non-residential real estate, and vehicles in the alternative category. These usually represent small family businesses which do not necessarily qualify as "alternative investments"'
        ),
    )
    house_df = get_sec_1_data(narrow)

    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(
            x=house_df["YEAR"],
            y=house_df["PCT_ALTERNATIVE"],
            name="Alternative",
            marker_color=BLUE,
            hovertemplate="Year %{x}<br>Alternative: %{y:.1f}%<extra></extra>",
        )
    )
    fig1.add_trace(
        go.Bar(
            x=house_df["YEAR"],
            y=house_df["PCT_TRADITIONAL"],
            name="Traditional",
            marker_color=GRAY,
            hovertemplate="Year %{x}<br>Traditional: %{y:.1f}%<extra></extra>",
        )
    )
    fig1.update_layout(
        barmode="stack",
        xaxis_title="Year",
        yaxis_title="% of portfolio",
        yaxis=dict(range=[0, 100], ticksuffix="%"),
        legend_title="Holding",
        hovermode="x unified",
        font=dict(family=FONT),
    )
    st.plotly_chart(fig1, width="stretch")
    st.caption(
        "Note that some alternative investments may be missed in these numbers, especially assets that are difficult to track or value, or that are perceived as collectibles or personal possessions rather than investments."
    )

with col_t:
    st.header("1. Household Participation")
    st.write(
        "The share of household portfolios held in alternative assets has stayed roughly flat or declining over the past three decades¹."
    )

st.divider()  ################################################################


col_t, col_g = st.columns([2, 3])

with col_t:
    st.header("2. Institutional Participation")
    st.write(
        "Institutional investors have steadily increased both their allocation and total assets under management in alternative investments²."
    )

with col_g:
    inst_df = get_sec_2_data()

    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=inst_df["Year"],
            y=inst_df["ALLOC_INDEXED"],
            name="Allocation to alternatives",
            mode="lines+markers",
            connectgaps=True,
            line=dict(color=BLUE, width=2),
            marker=dict(size=8),
            customdata=inst_df["Alloc_Perc"],
            hovertemplate="Year %{x}<br>Allocation: %{customdata:.1f}%<br>Indexed: %{y:.0f}<extra></extra>",
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=inst_df["Year"],
            y=inst_df["AUM_INDEXED"],
            name="Alternatives AUM",
            mode="lines+markers",
            connectgaps=True,
            line=dict(color=ORANGE, width=2),
            marker=dict(size=8),
            customdata=inst_df["AUM_T"],
            hovertemplate="Year %{x}<br>AUM: $%{customdata:.1f}T<br>Indexed: %{y:.0f}<extra></extra>",
        )
    )
    for _, row in inst_df.dropna(subset=["Alloc_Perc"]).iterrows():
        fig2.add_annotation(
            x=row["Year"],
            y=row["ALLOC_INDEXED"],
            text="{:.1f}%".format(row["Alloc_Perc"]),
            showarrow=False,
            yshift=16,
            font=dict(color=BLUE, size=13),
            bgcolor=GRAY,
            borderpad=2,
        )
    for _, row in inst_df.dropna(subset=["AUM_T"]).iterrows():
        fig2.add_annotation(
            x=row["Year"],
            y=row["AUM_INDEXED"],
            text="${:.1f}T".format(row["AUM_T"]),
            showarrow=False,
            yshift=-16,
            font=dict(color=ORANGE, size=13),
            bgcolor=GRAY,
            borderpad=2,
        )

    fig2.update_layout(
        xaxis_title="Year",
        yaxis=dict(visible=False),
        legend_title="Series",
        margin=dict(t=60, b=60),
        font=dict(family=FONT),
    )
    st.plotly_chart(fig2, width="stretch")
    st.caption(
        "Note: data points are drawn from separate reports and are not a continuous time series."
    )

st.divider()  ################################################################

st.subheader("The divergence in numbers")
st.write(
    "Households have held roughly 3-7% of their portfolios in alternatives since 1992, while institutional allocations climbed from 15% in 2019 to 31% in 2025."
)

st.divider()  ################################################################

col_g, col_t = st.columns([3, 2])

with col_g:
    perf_df = get_sec_3_data()

    selected = st.multiselect(
        "Assets to show",
        options=list(SEC3_SERIES.keys()),
        default=["S&P 500", "Bitcoin", "Luxury Watches"],
    )

    fig3 = go.Figure()
    label_points = []
    for i, label in enumerate(SEC3_SERIES.keys()):
        if label not in selected:
            continue
        is_baseline = label == "S&P 500"
        fig3.add_trace(
            go.Scatter(
                x=perf_df.index,
                y=perf_df[label],
                mode="lines",
                name=label,
                connectgaps=True,
                line=dict(
                    color=SEC3_COLORS[i],
                    width=4 if is_baseline else 2,
                    dash="solid" if is_baseline else "dash",
                ),
            )
        )
        last = perf_df[label].dropna()
        label_points.append(
            (
                label,
                last.index[-1].to_pydatetime(),
                last.iloc[-1],
                SEC3_COLORS[i],
            )
        )

    if len(label_points) > 0:
        y_span = perf_df[selected].max().max() - perf_df[selected].min().min()
        label_points.sort(key=lambda p: p[2])
        p_y = [label_points[0][2]]
        for _, _, y, _ in label_points[1:]:
            p_y.append(max(y, p_y[-1] + (y_span or 1) * 0.05))
        for (label, x, _, color), y in zip(label_points, p_y):
            fig3.add_annotation(
                x=x,
                y=y,
                text=f"  {label}",
                showarrow=False,
                xanchor="left",
                align="left",
                font=dict(color=color, size=12),
            )

    fig3.update_layout(
        xaxis_title="Date",
        yaxis_title="Value of €100 invested",
        legend_title="Asset",
        margin=dict(r=140),
        font=dict(family=FONT),
    )
    st.plotly_chart(fig3, width="stretch")

with col_t:
    st.header("3. If I invested €100 in 2021 ...")
    st.write(
        "Some alternatives have beaten the S&P 500 over this period, others have lagged behind³."
    )


st.divider()  #################################################################

st.caption(
    "1: Household data: Federal Reserve Survey of Consumer Finances (SCF), via the Berkeley SDA archive."
)
st.caption(
    "2: Institutional data: compiled from industry reports published by McKinsey, Preqin, Quintet, BAI, and CAIS."
)
st.caption(
    "3: Performance data: Yahoo Finance (S&P 500, Bitcoin, Ethereum, Gold); Cult Wines (Global Index); MTGGoldfish (MTG Reserved List); PriceCharting (Pokémon Base Set Box); WatchCharts (Luxury Watches Index)."
)
