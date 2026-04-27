"""
MapBiomas Observer — Cerrado, Amazônia e Mata Atlântica
Coleção 10 | Cultivos temporários e dinâmica de uso do solo
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="MapBiomas Observer",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .metric-card { background: #f8f9fa; border-radius: 8px; padding: 12px 16px; border-left: 4px solid; }
    div[data-testid="stTabs"] button { font-size: 15px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ── Paleta de cores MapBiomas (Coleção 10) ──────────────────────────────────
COLORS = {
    "6. Not Observed":                    "#cccccc",
    "1. Forest":                          "#1f8d49",
    "1.1. Forest Formation":              "#1f8d49",
    "1.2. Savanna Formation":             "#7dc975",
    "1.3. Mangrove":                      "#04381d",
    "1.4 Floodable Forest":               "#026975",
    "1.5. Wooded Sandbank Vegetation":    "#02d659",
    "2. Non Forest Natural Formation":    "#ad975a",
    "2.1. Wetland":                       "#519799",
    "2.2. Grassland":                     "#d6bc74",
    "2.3. Hypersaline Tidal Flat":        "#fc8114",
    "2.4. Rocky Outcrop":                 "#ffaa5f",
    "2.5. Herbaceous Sandbank Vegetation":"#ad5100",
    "3. Farming":                         "#FFFFB2",
    "3.1. Pasture":                       "#edde8e",
    "3.2. Agriculture":                   "#E974ED",
    "3.2.1. Temporary Crop":              "#C27BA0",
    "3.2.1.1. Soybean":                   "#f5b3c8",
    "3.2.1.2. Sugar cane":                "#db7093",
    "3.2.1.3. Rice":                      "#c71585",
    "3.2.1.4. Cotton":                    "#ff69b4",
    "3.2.1.5. Other Temporary Crops":     "#9932cc",
    "3.2.2. Perennial Crop":              "#d082de",
    "3.2.2.1. Coffee":                    "#d68fe2",
    "3.2.2.2. Citrus":                    "#9b59b6",
    "3.2.2.3. Palm Oil":                  "#9065d0",
    "3.2.2.4. Other Perennial Crops":     "#e6ccff",
    "3.3. Forest Plantation":             "#7a5900",
    "3.4. Mosaic of Uses":                "#ffefc3",
    "4. Non vegetated area":              "#d4271e",
    "4.1. Beach, Dune and Sand Spot":     "#ffa07a",
    "4.2. Urban Area":                    "#d4271e",
    "4.3. Mining":                        "#9c0027",
    "4.5. Other non Vegetated Areas":     "#db4d4f",
    "5. Water and Marine Environment":    "#2532e4",
    "5.1. River, Lake and Ocean":         "#2532e4",
    "5.2. Aquaculture":                   "#091077",
}

TEMP_CROP_COLORS = {
    "Soja":                       "#f5b3c8",
    "Cana-de-açúcar":             "#db7093",
    "Arroz":                      "#c71585",
    "Algodão":                    "#ff69b4",
    "Outros Cultivos Temporários":"#9932cc",
}

BIOME_COLORS = {
    "Amazônia":       "#1f8d49",
    "Cerrado":        "#7dc975",
    "Mata Atlântica": "#026975",
}

# ── Classes de cultivos temporários ─────────────────────────────────────────
TEMP_CROP_IDS = {
    39: "Soja",
    20: "Cana-de-açúcar",
    40: "Arroz",
    62: "Algodão",
    41: "Outros Cultivos Temporários",
}

# ── Períodos pré-calculados na planilha Transition ───────────────────────────
PERIODS = {
    "1985–2024 (total)": "p1985_2024",
    "1985–1990":          "p1985_1990",
    "1990–2000":          "p1990_2000",
    "2000–2010":          "p2000_2010",
    "2005–2010":          "p2005_2010",
    "2010–2020":          "p2010_2020",
    "2015–2020":          "p2015_2020",
    "2020–2024":          "p2020_2024",
    "1985–2000":          "p1985_2000",
    "2000–2024":          "p2000_2024",
}

LEVEL_OPTIONS = {
    "Nível 1 — geral":       "class_level_1",
    "Nível 2":               "class_level_2",
    "Nível 3 — detalhado":   "class_level_3",
    "Nível 4 — específico":  "class_level_4",
}

# ── Carregamento de dados ────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "MapBiomas_101_Cerrado_AmAzonia_MAtlantica.xlsx"

@st.cache_data(show_spinner="Carregando dados MapBiomas…")
def load_data():
    cover = pd.read_excel(DATA_PATH, sheet_name="Cover")
    trans = pd.read_excel(DATA_PATH, sheet_name="Transition")
    cover["state"] = cover["state"].str.strip()
    trans["state"]  = trans["state"].str.strip()
    return cover, trans

cover_df, trans_df = load_data()

YEAR_COLS = [c for c in cover_df.columns if str(c).isdigit()]
YEARS     = [int(y) for y in YEAR_COLS]
BIOMES    = sorted(cover_df["biome"].unique())

# ── Helpers ──────────────────────────────────────────────────────────────────
def hex_to_rgba(hex_color: str, alpha: float = 0.45) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def get_color(label: str) -> str:
    if not isinstance(label, str):
        return "#aaaaaa"
    if label in COLORS:
        return COLORS[label]
    for key, color in COLORS.items():
        if key in label:
            return color
    return "#aaaaaa"

def fmt_ha(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.2f} Mha"
    elif abs(v) >= 1_000:
        return f"{v/1_000:.0f} mil ha"
    return f"{v:.0f} ha"

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 MapBiomas Observer")
    st.caption("Coleção 10 · Cerrado, Amazônia, Mata Atlântica")
    st.divider()

    sel_biomes = st.multiselect(
        "**Bioma**",
        options=BIOMES,
        default=BIOMES,
    )
    if not sel_biomes:
        sel_biomes = BIOMES

    states_available = sorted(
        cover_df[cover_df["biome"].isin(sel_biomes)]["state"].unique()
    )
    sel_states = st.multiselect(
        "**Estado**",
        options=states_available,
        default=states_available,
        help="Deixe vazio para incluir todos os estados do(s) bioma(s) selecionado(s).",
    )
    if not sel_states:
        sel_states = states_available

    st.divider()
    st.caption(
        "Dados: [MapBiomas](https://mapbiomas.org) | "
        "Área em hectares (ha) ou milhões de hectares (Mha)"
    )

# ── Header com métricas rápidas ───────────────────────────────────────────────
cover_sel = cover_df[
    cover_df["biome"].isin(sel_biomes) & cover_df["state"].isin(sel_states)
]
temp_sel = cover_sel[cover_sel["class_id"].isin(TEMP_CROP_IDS.keys())]

total_1985 = temp_sel[1985].sum() / 1e6
total_2024 = temp_sel[2024].sum() / 1e6
soy_2024   = cover_sel[cover_sel["class_id"] == 39][2024].sum() / 1e6
delta_pct  = (total_2024 - total_1985) / total_1985 * 100 if total_1985 > 0 else 0

st.markdown("### 🌾 Cultivos Temporários nos biomas selecionados")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Área total em 2024",     f"{total_2024:.2f} Mha")
c2.metric("Área total em 1985",     f"{total_1985:.2f} Mha")
c3.metric("Variação 1985→2024",     f"+{delta_pct:.1f}%", delta=f"{total_2024-total_1985:.2f} Mha")
c4.metric("Soja em 2024",           f"{soy_2024:.2f} Mha")
st.divider()

# ── Abas principais ───────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📈  Cobertura Temporal",
    "🔀  Transições — Sankey",
    "📋  Dados Brutos",
])


# ══════════════════════════════════════════════════════════════════════════════
# ABA 1 — COBERTURA TEMPORAL
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Controles ──────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns([3, 2, 1])

    with col_a:
        sel_classes = st.multiselect(
            "Classes de cultivo",
            options=list(TEMP_CROP_IDS.values()),
            default=list(TEMP_CROP_IDS.values()),
        )
    with col_b:
        group_by = st.radio(
            "Separar por",
            ["Classe", "Bioma", "Estado"],
            horizontal=True,
        )
    with col_c:
        unit = st.radio("Unidade", ["Mha", "mil ha"], horizontal=True)
        divisor = 1_000_000 if unit == "Mha" else 1_000

    sel_ids = [k for k, v in TEMP_CROP_IDS.items() if v in sel_classes]

    # ── Dados filtrados ─────────────────────────────────────────────────────
    filt = cover_sel[cover_sel["class_id"].isin(sel_ids)].copy()
    filt["class_label"] = filt["class_id"].map(TEMP_CROP_IDS)

    filt_long = filt.melt(
        id_vars=["biome", "state", "class_label"],
        value_vars=YEAR_COLS,
        var_name="year",
        value_name="area_ha",
    )
    filt_long["year"] = filt_long["year"].astype(int)

    # ── Gráfico 1: série temporal ─────────────────────────────────────────
    st.subheader("Evolução temporal (1985–2024)")

    if group_by == "Bioma":
        agg = (filt_long.groupby(["biome", "year"])["area_ha"]
               .sum().reset_index())
        agg["area"] = agg["area_ha"] / divisor
        fig = px.line(
            agg, x="year", y="area", color="biome",
            color_discrete_map=BIOME_COLORS,
            labels={"area": f"Área ({unit})", "year": "Ano", "biome": "Bioma"},
        )
    elif group_by == "Estado":
        agg = (filt_long.groupby(["state", "year"])["area_ha"]
               .sum().reset_index())
        agg["area"] = agg["area_ha"] / divisor
        fig = px.line(
            agg, x="year", y="area", color="state",
            labels={"area": f"Área ({unit})", "year": "Ano", "state": "Estado"},
        )
    else:  # Classe
        agg = (filt_long.groupby(["class_label", "year"])["area_ha"]
               .sum().reset_index())
        agg["area"] = agg["area_ha"] / divisor
        fig = px.line(
            agg, x="year", y="area", color="class_label",
            color_discrete_map=TEMP_CROP_COLORS,
            labels={"area": f"Área ({unit})", "year": "Ano", "class_label": "Classe"},
        )

    fig.update_traces(mode="lines+markers", marker=dict(size=4))
    fig.update_layout(
        height=400,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eeeeee"),
        xaxis=dict(gridcolor="#eeeeee"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Gráfico 2: área empilhada por classe ──────────────────────────────
    st.subheader("Composição das classes (área empilhada)")

    agg2 = (filt_long.groupby(["class_label", "year"])["area_ha"]
            .sum().reset_index())
    agg2["area"] = agg2["area_ha"] / divisor

    fig2 = px.area(
        agg2, x="year", y="area", color="class_label",
        color_discrete_map=TEMP_CROP_COLORS,
        labels={"area": f"Área ({unit})", "year": "Ano", "class_label": "Classe"},
    )
    fig2.update_layout(
        height=380,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eeeeee"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Gráfico 3: ranking de estados (ano selecionado) ────────────────────
    st.subheader("Ranking de estados por área")
    col_yr, col_cls = st.columns(2)
    sel_year_rank = col_yr.select_slider(
        "Ano", options=YEARS, value=2024
    )
    sel_class_rank = col_cls.selectbox(
        "Classe", options=list(TEMP_CROP_IDS.values()), index=0
    )

    rank_id = [k for k, v in TEMP_CROP_IDS.items() if v == sel_class_rank][0]
    rank_data = cover_sel[cover_sel["class_id"] == rank_id].copy()
    rank_agg = (rank_data.groupby(["state", "biome"])[sel_year_rank]
                .sum().reset_index()
                .rename(columns={sel_year_rank: "area_ha"})
                .sort_values("area_ha", ascending=True)
                .tail(20))
    rank_agg["area"] = rank_agg["area_ha"] / divisor

    fig3 = px.bar(
        rank_agg, x="area", y="state", color="biome",
        orientation="h",
        color_discrete_map=BIOME_COLORS,
        labels={"area": f"Área ({unit})", "state": "", "biome": "Bioma"},
        text=rank_agg["area"].apply(lambda v: f"{v:.2f}"),
    )
    fig3.update_traces(textposition="outside")
    fig3.update_layout(
        height=500,
        margin=dict(l=0, r=60, t=10, b=0),
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#eeeeee"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Tabela resumo ──────────────────────────────────────────────────────
    st.subheader("Variação por classe: 1985 → 2024")
    rows = []
    for cid, label in TEMP_CROP_IDS.items():
        sub = cover_sel[cover_sel["class_id"] == cid]
        a85 = sub[1985].sum()
        a24 = sub[2024].sum()
        pct = (a24 - a85) / a85 * 100 if a85 > 0 else 0
        rows.append({
            "Classe":         label,
            "1985 (Mha)":     round(a85 / 1e6, 3),
            "2024 (Mha)":     round(a24 / 1e6, 3),
            "Δ (Mha)":        round((a24 - a85) / 1e6, 3),
            "Δ (%)":          round(pct, 1),
        })
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Δ (%)":  st.column_config.NumberColumn(format="%.1f %%"),
            "Δ (Mha)": st.column_config.NumberColumn(format="%.3f"),
        },
    )


# ══════════════════════════════════════════════════════════════════════════════
# ABA 2 — SANKEY DE TRANSIÇÕES
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown(
        "**Como ler:** cada barra à esquerda é uma classe de origem; "
        "as faixas mostram para qual classe o território foi convertido no período selecionado. "
        "Largura = área em hectares."
    )

    # ── Controles ──────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        sel_period = st.selectbox(
            "Período de análise",
            options=list(PERIODS.keys()),
            index=5,  # 2010-2020 por padrão
        )
    with col2:
        sel_level_label = st.selectbox(
            "Nível de detalhe",
            options=list(LEVEL_OPTIONS.keys()),
            index=2,  # Nível 3 por padrão
        )
    with col3:
        min_flow = st.number_input(
            "Fluxo mínimo (ha)",
            min_value=0,
            value=50_000,
            step=10_000,
            help="Remove transições menores que este valor para melhorar a leitura.",
        )

    col4, col5 = st.columns(2)
    with col4:
        hide_not_obs = st.checkbox("Ocultar 'Not Observed'", value=True)
    with col5:
        focus_temp = st.checkbox(
            "Focar em cultivos temporários",
            value=False,
            help="Mostra apenas transições que envolvem cultivos temporários como origem ou destino.",
        )

    period_col    = PERIODS[sel_period]
    level_base    = LEVEL_OPTIONS[sel_level_label]
    col_from      = level_base + "_from"
    col_to        = level_base + "_to"

    # ── Filtragem ───────────────────────────────────────────────────────────
    t_filt = trans_df[
        trans_df["biome"].isin(sel_biomes) &
        trans_df["state"].isin(sel_states)
    ].copy()

    if hide_not_obs:
        t_filt = t_filt[
            ~t_filt[col_from].str.contains("Not Observed", na=False) &
            ~t_filt[col_to].str.contains("Not Observed", na=False)
        ]

    if focus_temp:
        temp_label = "Temporary Crop"
        t_filt = t_filt[
            t_filt[col_from].str.contains(temp_label, na=False) |
            t_filt[col_to].str.contains(temp_label, na=False)
        ]

    # ── Agregação ───────────────────────────────────────────────────────────
    sankey_agg = (
        t_filt.groupby([col_from, col_to])[period_col]
        .sum().reset_index()
        .rename(columns={col_from: "source", col_to: "target", period_col: "value"})
    )
    sankey_agg = sankey_agg[
        (sankey_agg["source"] != sankey_agg["target"]) &
        (sankey_agg["value"] >= min_flow)
    ].copy()

    if sankey_agg.empty:
        st.warning(
            "Nenhuma transição encontrada com os filtros atuais. "
            "Tente reduzir o fluxo mínimo ou ampliar a seleção de biomas/estados."
        )
    else:
        # ── Construção do Sankey ────────────────────────────────────────────
        all_nodes  = list(pd.unique(sankey_agg[["source", "target"]].values.ravel()))
        node_map   = {n: i for i, n in enumerate(all_nodes)}
        node_colors = [get_color(n) for n in all_nodes]
        link_colors = [hex_to_rgba(get_color(s), 0.45) for s in sankey_agg["source"]]

        fig_sk = go.Figure(go.Sankey(
            arrangement="snap",
            node=dict(
                pad=18,
                thickness=22,
                line=dict(color="white", width=0.5),
                label=all_nodes,
                color=node_colors,
                hovertemplate="<b>%{label}</b><br>Total: %{value:,.0f} ha<extra></extra>",
            ),
            link=dict(
                source=[node_map[s] for s in sankey_agg["source"]],
                target=[node_map[t] for t in sankey_agg["target"]],
                value=sankey_agg["value"].tolist(),
                color=link_colors,
                hovertemplate=(
                    "<b>%{source.label}</b> → <b>%{target.label}</b><br>"
                    "Área: %{value:,.0f} ha<extra></extra>"
                ),
            ),
        ))
        fig_sk.update_layout(
            height=620,
            margin=dict(l=10, r=10, t=30, b=10),
            font=dict(size=12, family="Arial"),
        )
        st.plotly_chart(fig_sk, use_container_width=True)

        # ── Tabela das principais transições ────────────────────────────────
        col_tk, col_tb = st.columns([1, 1])
        with col_tk:
            st.subheader(f"Top transições — {sel_period}")
            top = sankey_agg.nlargest(15, "value").copy()
            top["Área (Mha)"] = (top["value"] / 1e6).round(3)
            st.dataframe(
                top.rename(columns={"source": "Origem", "target": "Destino"})[
                    ["Origem", "Destino", "Área (Mha)"]
                ],
                use_container_width=True,
                hide_index=True,
            )
        with col_tb:
            st.subheader("Principais destinos dos cultivos")
            if "Temporary Crop" in sankey_agg["target"].str.cat():
                to_temp = sankey_agg[
                    sankey_agg["target"].str.contains("Temporary", na=False)
                ].copy()
            else:
                to_temp = sankey_agg[
                    sankey_agg["source"].str.contains("Temporary", na=False)
                ].copy()
            if not to_temp.empty:
                to_temp["Área (Mha)"] = (to_temp["value"] / 1e6).round(3)
                to_temp = to_temp.nlargest(15, "value")
                st.dataframe(
                    to_temp.rename(columns={"source": "Origem", "target": "Destino"})[
                        ["Origem", "Destino", "Área (Mha)"]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("Nenhuma transição para/de cultivos temporários nos filtros atuais.")

        # ── Totais por bioma ────────────────────────────────────────────────
        st.subheader(f"Volume total de transições por bioma — {sel_period}")
        bio_agg = (
            trans_df[trans_df["biome"].isin(sel_biomes) & trans_df["state"].isin(sel_states)]
            .copy()
        )
        bio_agg = bio_agg[bio_agg[col_from] != bio_agg[col_to]]
        if hide_not_obs:
            bio_agg = bio_agg[
                ~bio_agg[col_from].str.contains("Not Observed", na=False) &
                ~bio_agg[col_to].str.contains("Not Observed", na=False)
            ]
        bio_sum = (bio_agg.groupby("biome")[period_col]
                   .sum().reset_index()
                   .rename(columns={period_col: "area_ha"}))
        bio_sum["Área (Mha)"] = (bio_sum["area_ha"] / 1e6).round(2)
        bio_sum["Bioma"] = bio_sum["biome"]
        fig_bio = px.bar(
            bio_sum, x="Bioma", y="Área (Mha)",
            color="Bioma",
            color_discrete_map=BIOME_COLORS,
            text="Área (Mha)",
        )
        fig_bio.update_traces(textposition="outside")
        fig_bio.update_layout(
            height=350,
            showlegend=False,
            plot_bgcolor="white",
            yaxis=dict(gridcolor="#eeeeee"),
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_bio, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ABA 3 — DADOS BRUTOS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Consulta de dados brutos — Cobertura")

    col_lf, col_yr = st.columns(2)
    with col_lf:
        class_filter = st.selectbox(
            "Filtrar por classe",
            [
                "Cultivos temporários",
                "Agropecuária completa",
                "Floresta",
                "Vegetação não florestal",
                "Todas as classes",
            ],
        )
    with col_yr:
        year_range = st.select_slider(
            "Intervalo de anos",
            options=YEARS,
            value=(1985, 2024),
        )

    yr_cols = [y for y in YEAR_COLS if year_range[0] <= int(y) <= year_range[1]]

    raw = cover_sel.copy()
    if class_filter == "Cultivos temporários":
        raw = raw[raw["class_id"].isin(TEMP_CROP_IDS.keys())]
    elif class_filter == "Agropecuária completa":
        raw = raw[raw["class_level_1"] == "3. Farming"]
    elif class_filter == "Floresta":
        raw = raw[raw["class_level_1"] == "1. Forest"]
    elif class_filter == "Vegetação não florestal":
        raw = raw[raw["class_level_1"] == "2. Non Forest Natural Formation"]

    display_cols = (
        ["biome", "state", "municipality", "class_level_2", "class_level_3", "class_level_4"]
        + yr_cols
    )
    st.dataframe(
        raw[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=480,
        column_config={
            "biome":       st.column_config.TextColumn("Bioma"),
            "state":       st.column_config.TextColumn("Estado"),
            "municipality": st.column_config.TextColumn("Município"),
            "class_level_2": st.column_config.TextColumn("Classe N2"),
            "class_level_3": st.column_config.TextColumn("Classe N3"),
            "class_level_4": st.column_config.TextColumn("Classe N4"),
        },
    )

    csv = raw[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Exportar seleção como CSV",
        data=csv,
        file_name=f"mapbiomas_cobertura_filtrado.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("Consulta de dados brutos — Transições")

    col_tp, col_tl = st.columns(2)
    with col_tp:
        trans_period = st.selectbox(
            "Período",
            options=list(PERIODS.keys()),
            index=5,
            key="trans_raw_period",
        )
    with col_tl:
        trans_level = st.selectbox(
            "Nível de detalhe",
            options=list(LEVEL_OPTIONS.keys()),
            index=2,
            key="trans_raw_level",
        )

    tp_col  = PERIODS[trans_period]
    tl_base = LEVEL_OPTIONS[trans_level]

    t_raw = trans_df[
        trans_df["biome"].isin(sel_biomes) & trans_df["state"].isin(sel_states)
    ].copy()
    t_raw = t_raw[t_raw[tl_base + "_from"] != t_raw[tl_base + "_to"]]

    t_display_cols = [
        "biome", "state",
        tl_base + "_from", tl_base + "_to",
        tp_col,
    ]
    t_raw_sorted = t_raw[t_display_cols].sort_values(tp_col, ascending=False).reset_index(drop=True)
    t_raw_sorted[tp_col + "_Mha"] = (t_raw_sorted[tp_col] / 1e6).round(3)

    st.dataframe(
        t_raw_sorted[[
            "biome", "state",
            tl_base + "_from", tl_base + "_to",
            tp_col + "_Mha",
        ]].rename(columns={
            "biome": "Bioma",
            "state": "Estado",
            tl_base + "_from": "Classe origem",
            tl_base + "_to":   "Classe destino",
            tp_col + "_Mha":   "Área (Mha)",
        }),
        use_container_width=True,
        height=400,
        hide_index=True,
    )

    csv_t = t_raw_sorted.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Exportar transições como CSV",
        data=csv_t,
        file_name="mapbiomas_transicoes_filtrado.csv",
        mime="text/csv",
        key="dl_trans",
    )
