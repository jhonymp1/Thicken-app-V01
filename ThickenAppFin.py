
# Thicken-app — Pearson-only correlations, bilingual ES/EN UI
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import re
import io
import base64
from pathlib import Path

# === Utilidad simple para mostrar ES/EN ===
def t(es: str, en: str) -> str:
    return f"{es} / {en}"

# ===============================
# Apariencia: imágenes, CSS y estilo de gráficos
# ===============================
ASSETS_DIR = Path(__file__).parent / "assets"
IMG_HERO = ASSETS_DIR / "espesador_hero.jpg"      # espesador rojo (vista general)
IMG_SIDE = ASSETS_DIR / "espesador_puente.jpg"    # puente y pozo de alimentación
IMG_THICKENER = ASSETS_DIR / "thickener.png"                    # sección final (próximamente)
IMG_FEEDWELL = ASSETS_DIR / "feedwell aceleration2.png"         # sección final (próximamente)

PALETTE = {
    "bg": "#0d1822",        # fondo principal (azul petróleo casi negro)
    "panel": "#142433",     # tarjetas / expanders
    "line": "#24394c",      # bordes
    "text": "#e4ebf1",      # texto principal
    "muted": "#9fb1c1",     # texto secundario
    "ink": "#0f2233",       # azul petróleo (texto dentro de figuras claras)
    "steel": "#3b7ca3",     # azul acero (más claro para contrastar en oscuro)
    "accent": "#d6283f",    # rojo del espesador
    "sand": "#e9e4d8",      # crema de las franjas
}
BASE_FONT_PX = 18  # tamaño base de fuente de toda la app (Streamlit usa 16 px por defecto)

@st.cache_data(show_spinner=False)
def _img_b64(path: str) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    return base64.b64encode(p.read_bytes()).decode()

def inject_css():
    P = PALETTE
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');
    html {{ font-size: {BASE_FONT_PX}px !important; }}
    html, body, [class*="css"], .stMarkdown, .stText, label, button, input, textarea {{
        font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
    }}
    .stApp {{ background: radial-gradient(1200px 600px at 85% -10%, #17324a 0%, {P['bg']} 55%) fixed; color: {P['text']}; }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{ padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1500px; }}
    .stMarkdown p, .stMarkdown li, label, [data-testid="stWidgetLabel"] p {{ font-size: 1rem !important; }}
    [data-testid="stCaptionContainer"], .stCaption {{ color: {P['muted']} !important; font-size: .9rem !important; }}

    /* Encabezados de sección con barra roja lateral */
    h2, h3 {{
        color: {P['text']} !important;
        border-left: 5px solid {P['accent']};
        padding: .15rem 0 .15rem .7rem !important;
        margin-top: 2.2rem !important;
        font-weight: 600 !important;
        letter-spacing: -.01em;
    }}
    h3 {{ font-size: 1.55rem !important; }}

    /* Sidebar */
    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg, #08121b 0%, {P['panel']} 100%);
        border-right: 1px solid {P['line']};
    }}
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
        margin-top: 1rem !important; font-size: 1.15rem !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
        background: rgba(255,255,255,.04); border: 1px dashed {P['line']};
    }}
    section[data-testid="stSidebar"] hr {{ border-color: {P['line']}; }}
    .side-photo {{ border-radius: 10px; overflow: hidden; margin: -.5rem 0 1rem 0;
                   box-shadow: 0 6px 18px rgba(0,0,0,.45); border: 1px solid {P['line']}; }}
    .side-photo img {{ width: 100%; height: 160px; object-fit: cover; display: block; }}
    .side-photo span {{ display:block; font-size:.78rem; color:{P['muted']}; padding:.35rem .6rem;
                        background: #08121b; letter-spacing:.08em; }}

    /* Hero */
    .hero {{ position: relative; border-radius: 14px; overflow: hidden; height: 290px; margin-bottom: 1.2rem;
             box-shadow: 0 14px 40px rgba(0,0,0,.45); border: 1px solid {P['line']}; }}
    .hero img {{ width: 100%; height: 100%; object-fit: cover; object-position: center 62%; display: block; }}
    .hero .veil {{ position: absolute; inset: 0;
                   background: linear-gradient(90deg, rgba(13,24,34,.95) 0%, rgba(13,24,34,.7) 45%, rgba(13,24,34,.05) 100%); }}
    .hero .txt {{ position: absolute; left: 2.2rem; top: 50%; transform: translateY(-50%); max-width: 680px; color: #fff; }}
    .hero .kicker {{ font-family: 'IBM Plex Mono', monospace; font-size: .8rem; letter-spacing: .18em;
                     text-transform: uppercase; color: {P['sand']}; opacity: .9; }}
    .hero h1 {{ color: #fff !important; font-size: 3.2rem !important; font-weight: 700 !important; margin: .2rem 0 .5rem 0 !important;
                padding: 0 !important; border: none !important; letter-spacing: -.02em; }}
    .hero h1 .bar {{ display:inline-block; width: 46px; height: 6px; background: {P['accent']};
                     vertical-align: middle; margin-left: .6rem; border-radius: 3px; }}
    .hero p {{ font-size: 1.02rem; line-height: 1.5; opacity: .92; margin: 0; }}

    /* Banda fotográfica de sección */
    .band {{ position: relative; border-radius: 12px; overflow: hidden; height: 130px; margin: 2.4rem 0 .4rem 0;
             border: 1px solid {P['line']}; }}
    .band img {{ width: 100%; height: 100%; object-fit: cover; object-position: center 40%; display:block; }}
    .band .veil {{ position:absolute; inset:0; background: linear-gradient(90deg, rgba(13,24,34,.9), rgba(13,24,34,.2)); }}

    /* Sección final: próximamente */
    .soon-img {{ text-align: center; margin: 1.2rem 0; }}
    .soon-img img {{ max-width: 100%; border-radius: 12px; border: 1px solid {P['line']};
                     box-shadow: 0 10px 30px rgba(0,0,0,.4); }}
    .soon-msg {{ text-align: center; margin: 1.4rem 0; }}
    .soon-msg span {{ display: inline-block; font-family: 'IBM Plex Mono', monospace; font-size: 1.6rem;
                      letter-spacing: .25em; text-transform: uppercase; color: {P['sand']};
                      border: 1px solid {P['accent']}; border-radius: 10px; padding: .6rem 1.8rem;
                      background: rgba(214,40,63,.12); }}

    /* Expanders, tablas y botones */
    div[data-testid="stExpander"] {{ border: 1px solid {P['line']}; border-radius: 10px; background: {P['panel']}; }}
    div[data-testid="stExpander"] summary {{ font-weight: 500; }}
    div[data-testid="stExpander"] summary p {{ font-size: 1rem !important; }}
    div[data-testid="stDataFrame"] {{ border-radius: 8px; overflow: hidden; border: 1px solid {P['line']}; }}
    .stDownloadButton button, .stButton button {{ border-radius: 8px; font-weight: 500; }}
    .stDownloadButton button {{ border: 1px solid {P['steel']}; color: #cfe3f1; background: transparent; }}
    .stDownloadButton button:hover {{ background: {P['steel']}; color: #fff; border-color: {P['steel']}; }}
    div[data-testid="stPlotlyChart"] {{ background: {P['panel']}; border-radius: 10px; border: 1px solid {P['line']}; padding: .4rem; }}
    /* Figuras de matplotlib: tarjetas claras (también se descargan así, listas para informes) */
    div[data-testid="stImage"] img, .stPyplot img {{ border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

def render_hero(title: str, subtitle: str):
    b64 = _img_b64(str(IMG_HERO))
    if b64 is None:  # sin imagen: encabezado simple
        st.title(title); st.caption(subtitle); return
    st.markdown(f"""
    <div class="hero">
      <img src="data:image/jpeg;base64,{b64}" alt="Espesador">
      <div class="veil"></div>
      <div class="txt">
        <div class="kicker">{t("Analítica de espesadores", "Thickener analytics")}</div>
        <h1>{title}<span class="bar"></span></h1>
        <p>{subtitle}</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_band(path: Path):
    b64 = _img_b64(str(path))
    if b64 is None:
        return
    st.markdown(f'<div class="band"><img src="data:image/jpeg;base64,{b64}" alt=""><div class="veil"></div></div>',
                unsafe_allow_html=True)

def render_centered_image(path: Path, alt: str = ""):
    """Muestra una imagen PNG centrada; si no existe, avisa sin romper la app."""
    b64 = _img_b64(str(path))
    if b64 is None:
        st.caption(f"⚠️ Imagen no encontrada / Image not found: {path.name}")
        return
    st.markdown(f'<div class="soon-img"><img src="data:image/png;base64,{b64}" alt="{alt}"></div>',
                unsafe_allow_html=True)

def apply_plot_style():
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.edgecolor": "#c9d2da", "axes.labelcolor": PALETTE["ink"],
        "axes.titlecolor": PALETTE["ink"], "axes.titleweight": "semibold",
        "xtick.color": "#4a5b6a", "ytick.color": "#4a5b6a",
        "grid.color": "#e6ebf0", "axes.spines.top": False, "axes.spines.right": False,
        "axes.prop_cycle": plt.cycler(color=["#1f4e6b", PALETTE["accent"], "#e0a526", "#3a8f6b", "#7a5aa6", "#5f7f95"]),
        "font.family": "sans-serif",
        "font.size": 13, "axes.titlesize": 16, "axes.labelsize": 14,
        "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 12,
    })
    px.defaults.template = "plotly_dark"
    px.defaults.color_discrete_sequence = ["#5aa9d6", PALETTE["accent"], "#f0b43c", "#4fbf8f", "#a98be0", "#9fb1c1"]

def style_plotly(fig):
    """Fondo transparente y fuente más grande para que el gráfico se integre al tema oscuro."""
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="IBM Plex Sans, sans-serif", size=15, color=PALETTE["text"]),
                      title_font=dict(size=19), legend=dict(font=dict(size=14)))
    fig.update_xaxes(gridcolor=PALETTE["line"]); fig.update_yaxes(gridcolor=PALETTE["line"])
    return fig

# ===============================
# Config de la app
# ===============================
st.set_page_config(page_title="Thicken-app", page_icon="🛢️", layout="wide")
inject_css()
apply_plot_style()
render_hero("Thicken-app", t(
    "Trabaja con los nombres originales del Excel; solo cambian si los renombras en la UI. Remuestreo toma el primer valor del intervalo.",
    "Works with original Excel column names; they only change if you rename them in the UI. Resampling takes the first value of each interval."
))

# ===============================
# Sidebar: Parámetros
# ===============================
with st.sidebar:
    _side_b64 = _img_b64(str(IMG_SIDE))
    if _side_b64:
        st.markdown(f'<div class="side-photo"><img src="data:image/jpeg;base64,{_side_b64}" alt="Puente del espesador">'
                    f'<span>Thicken-app</span></div>', unsafe_allow_html=True)
    st.header(t("⚙️ Parámetros", "⚙️ Settings"))
    freq_input = st.text_input(
        t("Frecuencia de remuestreo (p.ej., 10min, 5min, 30min, 1h)", "Resampling frequency (e.g., 10min, 5min, 30min, 1h)"),
        value="10min"
    )
    use_resampled_for_corr = st.checkbox(t("Usar datos remuestreados para correlación", "Use resampled data for correlation"), value=True)
    min_frac = st.slider(t("Mínimo de datos válidos por columna (fracción)", "Minimum valid data per column (fraction)"), 0.05, 0.8, 0.20, 0.05)
    show_diagnostics = st.checkbox(t("Mostrar diagnósticos", "Show diagnostics"), value=False)

    st.markdown("---")
    uploaded = st.file_uploader("📤 " + t("Cargar Excel", "Upload Excel"), type=["xlsx", "xls"])
    apply_cleaning = st.checkbox(
        t("🧹 Limpiar tabla (quitar columnas sin nombre, columnas vacías y filas vacías)",
          "🧹 Clean table (drop unnamed columns, empty columns and empty rows)"),
        value=True,
        help=t("Revisa el detalle de lo eliminado en la sección 'Limpieza de datos'.",
               "See what was removed in the 'Data cleaning' section.")
    )

# ===============================
# Utilidades
# ===============================

def is_unnamed(col) -> bool:
    c = str(col).strip().lower()
    return (c == "") or c.startswith("unnamed") or (c in {"nan", "none"})

def normalize_freq(f: str) -> str:
    """Convierte alias antiguos de pandas (T, H, S, L) a los nuevos (min, h, s, ms)."""
    f = str(f).strip()
    m = re.fullmatch(r"(\d*)\s*([A-Za-z]+)", f)
    if not m:
        return f
    num, unit = m.groups()
    unit = {"T": "min", "H": "h", "S": "s", "L": "ms"}.get(unit, unit)
    return f"{num}{unit}"

freq = normalize_freq(freq_input)

def normalize_column_names(cols) -> pd.Index:
    """Limpia nombres de columna; vacíos/NaN -> '' (luego se descartan con is_unnamed)."""
    out = []
    for c in cols:
        try:
            if pd.isna(c):
                out.append("")
                continue
        except (TypeError, ValueError):
            pass
        out.append(re.sub(r"\s+", " ", str(c)).strip())
    return pd.Index(out)

def excel_col_letter(i: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA ..."""
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s

def _is_blank(v) -> bool:
    try:
        if pd.isna(v):
            return True
    except (TypeError, ValueError):
        pass
    return str(v).strip() == ""

def load_table_from_a1(uploaded, apply_cleaning: bool):
    """
    Lee la tabla que empieza en A1 (fila 1 = encabezados).
    Devuelve (df, reporte). El reporte detalla todo lo eliminado o renombrado.
    """
    raw = pd.read_excel(uploaded, header=None)
    report = {"cols_sin_nombre": [], "cols_vacias": [], "filas_vacias": [],
              "renombradas": [], "filas_total": 0, "cols_total": 0}
    if raw.empty:
        return pd.DataFrame(), report

    headers = list(normalize_column_names(raw.iloc[0].tolist()))
    data = raw.iloc[1:].copy()
    data.columns = range(data.shape[1])
    data.index = range(2, 2 + len(data))  # índice = número de fila en Excel
    letters = [excel_col_letter(i) for i in range(len(headers))]
    report["filas_total"], report["cols_total"] = len(data), len(headers)

    blank_mask = data.apply(lambda col: col.map(_is_blank))
    keep_cols = list(range(len(headers)))

    if apply_cleaning:
        # Columnas sin nombre (se reporta cuántos datos tenían)
        for i, h in enumerate(headers):
            if is_unnamed(h):
                n_vals = int((~blank_mask[i]).sum())
                report["cols_sin_nombre"].append({"Columna Excel": letters[i], "Valores con datos": n_vals})
        keep_cols = [i for i in keep_cols if not is_unnamed(headers[i])]
        # Columnas con nombre pero sin ningún dato
        for i in keep_cols:
            if blank_mask[i].all():
                report["cols_vacias"].append({"Columna Excel": letters[i], "Nombre": headers[i]})
        keep_cols = [i for i in keep_cols if not blank_mask[i].all()]
        # Filas totalmente vacías (considerando solo las columnas conservadas)
        empty_rows = blank_mask[keep_cols].all(axis=1)
        report["filas_vacias"] = [int(r) for r in empty_rows[empty_rows].index]
        data = data.loc[~empty_rows, keep_cols]
    else:
        data = data[keep_cols]

    # Nombres válidos y únicos (obligatorio: la app no funciona con nombres vacíos o repetidos)
    names = []
    for i in keep_cols:
        names.append(headers[i] if not is_unnamed(headers[i]) else f"Col_{letters[i]}")
    unique = _make_unique(names)
    for i, old, new in zip(keep_cols, names, unique):
        if is_unnamed(headers[i]) or old != new:
            report["renombradas"].append({"Columna Excel": letters[i],
                                          "Nombre original": headers[i] or "(vacío)",
                                          "Nombre asignado": new})
    data.columns = unique
    data = data.infer_objects().reset_index(drop=True)
    return data, report

def show_cleaning_report(report: dict, apply_cleaning: bool):
    n_cs, n_cv = len(report["cols_sin_nombre"]), len(report["cols_vacias"])
    n_fv, n_rn = len(report["filas_vacias"]), len(report["renombradas"])
    estado = t("activada", "on") if apply_cleaning else t("desactivada", "off")
    resumen = t(
        f"Limpieza {estado}: {n_cs} columnas sin nombre, {n_cv} columnas vacías y {n_fv} filas vacías eliminadas; {n_rn} columnas renombradas.",
        f"Cleaning {estado}: {n_cs} unnamed columns, {n_cv} empty columns and {n_fv} empty rows removed; {n_rn} columns renamed."
    )
    with st.expander("🧹 " + t("Limpieza de datos", "Data cleaning") + f" — {resumen}", expanded=False):
        st.caption(t(f"Tabla original: {report['filas_total']} filas de datos × {report['cols_total']} columnas.",
                     f"Original table: {report['filas_total']} data rows × {report['cols_total']} columns."))
        if n_cs:
            st.markdown("**" + t("Columnas sin nombre eliminadas", "Unnamed columns removed") + "**")
            df_cs = pd.DataFrame(report["cols_sin_nombre"])
            st.dataframe(df_cs, use_container_width=True, hide_index=True)
            if (df_cs["Valores con datos"] > 0).any():
                st.warning(t("⚠️ Algunas columnas sin nombre tenían datos. Si los necesitas, ponles un encabezado en el Excel o desactiva la limpieza.",
                             "⚠️ Some unnamed columns contained data. If you need them, add a header in Excel or turn cleaning off."))
        if n_cv:
            st.markdown("**" + t("Columnas vacías eliminadas", "Empty columns removed") + "**")
            st.dataframe(pd.DataFrame(report["cols_vacias"]), use_container_width=True, hide_index=True)
        if n_fv:
            st.markdown("**" + t("Filas vacías eliminadas (número de fila en Excel)", "Empty rows removed (Excel row number)") + "**")
            filas = report["filas_vacias"]
            st.write(", ".join(map(str, filas[:200])) + (" …" if len(filas) > 200 else ""))
        if n_rn:
            st.markdown("**" + t("Columnas renombradas (siempre se aplica: la app necesita nombres únicos y no vacíos)",
                                 "Renamed columns (always applied: the app needs unique, non-empty names)") + "**")
            st.dataframe(pd.DataFrame(report["renombradas"]), use_container_width=True, hide_index=True)
        if not (n_cs or n_cv or n_fv or n_rn):
            st.success(t("No se eliminó ni renombró nada.", "Nothing was removed or renamed."))

def drop_ghost_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    first_data_row = df.iloc[0]
    first_row_empty_mask = first_data_row.replace(r"^\s*$", np.nan, regex=True).isna()
    tmp_all = df.replace(r"^\s*$", np.nan, regex=True)
    all_empty_mask = tmp_all.isna().all(axis=0)
    drop_mask = first_row_empty_mask & all_empty_mask
    return df.loc[:, ~drop_mask]

def to_numeric_locale_aware(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_numeric_dtype(out[col]) or pd.api.types.is_datetime64_any_dtype(out[col]):
            continue
        ser = out[col].astype(str)
        ser = ser.str.replace("\u00A0", "", regex=False)
        ser = ser.str.replace("%", "", regex=False).str.strip()
        sample = ser.dropna().head(200)
        cnt_comma = sample.str.contains(",", regex=False).sum()
        cnt_dot = sample.str.contains(r"\.", regex=True).sum()
        cnt_both = sample.str.contains(r".*[,].*[.].*|.*[.].*[,].*", regex=True).sum()
        if cnt_both > 0 or (cnt_comma > cnt_dot and cnt_comma > 0):
            ser = ser.str.replace(r"\.", "", regex=True)
            ser = ser.str.replace(",", ".", regex=False)
        else:
            ser = ser.str.replace(r"(?<=\d)[\s']", "", regex=True)
            ser = ser.str.replace(r"[^0-9\.\-+eE]", "", regex=True)
        out[col] = pd.to_numeric(ser, errors="coerce")
    return out

def diagnose_numeric(df: pd.DataFrame, label: str):
    num = df.select_dtypes(include=[np.number])
    if num.empty:
        st.warning(t("[DIAG] No hay columnas numéricas.", "[DIAG] No numeric columns."))
        return num
    stats = pd.DataFrame({
        "non_null": num.notna().sum(),
        "nulls": num.isna().sum(),
        "std": num.std(ddof=0),
        "min": num.min(),
        "max": num.max(),
    }).sort_values("non_null", ascending=False)
    with st.expander(t("🔍 Diagnóstico numérico", "🔍 Numeric diagnostics") + f": {label}", expanded=False):
        st.write(t(f"Columnas numéricas: {num.shape[1]}", f"Numeric columns: {num.shape[1]}"))
        st.dataframe(stats)
    return num

# === Pearson solamente ===

def compute_correlations(num_df: pd.DataFrame, min_frac: float = 0.2):
    if num_df.empty:
        return None
    min_valid = max(3, int(min_frac * len(num_df)))
    valid_cols = []
    for c in num_df.columns:
        ser = num_df[c].dropna()
        if ser.size >= min_valid and ser.std(ddof=0) > 1e-12:
            valid_cols.append(c)
    num_df = num_df[valid_cols]
    if len(valid_cols) < 2:
        return None
    pear = num_df.corr(method="pearson", min_periods=min_valid)
    if pear is not None:
        pear.index.name = None
        pear.columns.name = None
    return pear

# ==== utilidades para descarga de figuras ====

def _sanitize_filename(text: str) -> str:
    import re as _re
    ttxt = _re.sub(r"[^A-Za-z0-9_\-]+", "_", str(text or "fig"))
    return ttxt[:120]

def fig_to_png_bytes(fig) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=200, bbox_inches='tight')
    buf.seek(0)
    return buf

# Heatmap único (Pearson)

def plot_one_heatmap(mat: pd.DataFrame, title_suffix=""):
    fig, ax = plt.subplots(figsize=(12, 9))
    if mat is None or mat.isna().all().all():
        ax.set_title(t("Pearson: sin datos suficientes", "Pearson: not enough data"), fontsize=14)
        ax.axis("off")
        st.pyplot(fig)
        return fig
    mask = np.triu(np.ones_like(mat, dtype=bool))
    with sns.axes_style("white"):
        sns.heatmap(
            mat, mask=mask, annot=True, fmt=".2f",
            cmap="magma", linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax, annot_kws={"size": 11, "color": "black"}
        )
    ax.set_title(t("Pearson", "Pearson") + f" {title_suffix}", fontsize=16, pad=10)
    plt.tight_layout()
    st.pyplot(fig)
    return fig


def top_abs_corr_dataframe(mat: pd.DataFrame, k: int = 20) -> pd.DataFrame:
    if mat is None or getattr(mat, "empty", True):
        return pd.DataFrame(columns=["Var 1", "Var 2", "corr"])
    m = mat.copy().astype(float)
    mask = np.triu(np.ones(m.shape, dtype=bool), k=1)
    m = m.abs().where(mask)
    s = m.stack().dropna()
    s.index = s.index.set_names(["Var 1", "Var 2"])
    s.name = "corr"
    df_top = (
        s.reset_index()
        .sort_values("corr", ascending=False)
        .head(k)
        .reset_index(drop=True)
    )
    return df_top


def _make_unique(names: list[str]) -> list[str]:
    seen = {}
    out = []
    for n in names:
        base = (n or "").strip()
        if base == "":
            base = "col"
        if base not in seen:
            seen[base] = 1
            out.append(base)
        else:
            seen[base] += 1
            out.append(f"{base}_{seen[base]}")
    return out


def find_time_column(df: pd.DataFrame) -> str | None:
    candidates = [
        "Date","date","Fecha","fecha","Date Time","date time",
        "Timestamp","timestamp","Time","time","Datetime","datetime"
    ]
    for c in df.columns:
        if str(c) in candidates:
            ts = pd.to_datetime(df[c], errors="coerce")
            if ts.notna().sum() >= 3:
                return c
    for c in df.columns:
        ts = pd.to_datetime(df[c], errors="coerce")
        if ts.notna().sum() >= max(3, int(0.2*len(df))):
            return c
    return None

# ===============================
# Lógica principal
# ===============================
if uploaded is None:
    st.info(t("Carga un archivo Excel para comenzar.", "Upload an Excel file to start."))
    st.stop()

# 1) Leer Excel: la tabla siempre empieza en A1 (fila 1 = encabezados, fila 2 en adelante = datos)
try:
    df, clean_report = load_table_from_a1(uploaded, apply_cleaning)
except Exception as e:
    st.error(t(f"No se pudo leer el Excel: {e}", f"Could not read Excel: {e}"))
    st.stop()

# 2) Reporte de limpieza (qué se eliminó / renombró)
show_cleaning_report(clean_report, apply_cleaning)

if df.empty:
    st.error(t("El Excel no tiene datos debajo de la fila 1.", "The Excel file has no data below row 1."))
    st.stop()

# Estado de sesión
original_cols_clean = list(df.columns)
signature = tuple(original_cols_clean)
if ("df_signature" not in st.session_state) or (st.session_state.df_signature != signature):
    st.session_state.df_signature = signature
    st.session_state.col_names_current = original_cols_clean.copy()
    st.session_state.time_col = None
    st.session_state.vars_plot = []
    st.session_state.var_sec = "(ninguna)"

df = df.set_axis(st.session_state.col_names_current, axis=1)

# 5) Detectar columna de tiempo
if st.session_state.time_col is None or st.session_state.time_col not in df.columns:
    time_col = find_time_column(df)
    if time_col is None:
        st.error(t("No se encontró una columna de tiempo reconocible (p. ej., 'Date', 'Date Time', 'Fecha').",
                   "No recognizable time column found (e.g., 'Date', 'Date Time', 'Fecha')."))
        st.stop()
    st.session_state.time_col = time_col

time_col = st.session_state.time_col

# Convertir a datetime y ordenar
df = df.copy()
df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
df = df.dropna(subset=[time_col]).sort_values(time_col)

# ===============================
# Sidebar: Renombrar columnas
# ===============================
with st.sidebar:
    st.subheader(t("✏️ Renombrar columnas", "✏️ Rename columns"))
    st.caption(t("Los nombres visibles son los **originales/actuales**. Solo cambian al pulsar **Aplicar**.",
                 "Visible names are the **original/current** ones. They only change when you press **Apply**."))

    allow_rename_time = st.checkbox(
        t(f"Permitir renombrar la columna de tiempo ('{time_col}')", f"Allow renaming the time column ('{time_col}')"), value=False,
        help=t("No recomendado; podría afectar el remuestreo y los gráficos.", "Not recommended; it may affect resampling and charts.")
    )

    current_cols_now = list(df.columns)
    col1, col2 = st.columns(2)
    with col1:
        reset_names = st.button("↩️ " + t("Reset", "Reset"), use_container_width=True)
    with col2:
        apply_renames = st.button("✅ " + t("Aplicar", "Apply"), type="primary", use_container_width=True)

    default_names = st.session_state.col_names_current.copy()
    if reset_names:
        default_names = original_cols_clean.copy()

    if not allow_rename_time:
        idx_time = current_cols_now.index(time_col)
        default_names[idx_time] = st.session_state.col_names_current[idx_time]

    typed_names = default_names.copy()
    for i, col in enumerate(current_cols_now):
        if (not allow_rename_time) and (col == time_col):
            st.text_input(f"{col} " + t("(bloqueada)", "(locked)"), value=default_names[i], disabled=True, key=f"rename_{i}")
            typed_names[i] = default_names[i]
            continue
        typed_names[i] = st.text_input(f"{col}", value=default_names[i], key=f"rename_{i}")

if apply_renames:
    new_names = _make_unique([x.strip() for x in typed_names])
    if not allow_rename_time:
        idx_time = list(df.columns).index(time_col)
        new_names[idx_time] = df.columns[idx_time]
    mapping = {old: new for old, new in zip(df.columns, new_names) if old != new}
    if mapping:
        df = df.set_axis(new_names, axis=1)
        st.session_state.col_names_current = new_names
        if allow_rename_time and time_col in mapping:
            st.session_state.time_col = mapping[time_col]
        time_col = st.session_state.time_col
        st.success(t(f"Columnas renombradas: {mapping}", f"Renamed columns: {mapping}"))
    else:
        st.info(t("No hubo cambios en los nombres de columnas.", "No column name changes."))

# 6) Conversión numérica
df_num_crudo = to_numeric_locale_aware(df)

# 7) Remuestreo (primer valor del intervalo)
df_resampled = (
    df_num_crudo
    .set_index(time_col)
    .resample(freq)
    .first()
    .reset_index()
)

# ===============================
# Serie de tiempo
# ===============================
st.subheader(t("📊 Serie de tiempo", "📊 Time series"))
plot_df = df_resampled if time_col in df_resampled.columns else df_num_crudo
num_cols_plot = [c for c in plot_df.columns if c != time_col and pd.api.types.is_numeric_dtype(plot_df[c])]

options_key = ("plot_options_key", tuple(num_cols_plot), time_col)
if "plot_options_key" not in st.session_state or st.session_state.plot_options_key != options_key:
    st.session_state.plot_options_key = options_key
    prev_vars = st.session_state.get("vars_plot", [])
    st.session_state.vars_plot = [c for c in prev_vars if c in num_cols_plot] or (num_cols_plot[:2] if len(num_cols_plot) >= 2 else num_cols_plot[:1])
    prev_sec = st.session_state.get("var_sec", "(ninguna)")
    st.session_state.var_sec = prev_sec if prev_sec in num_cols_plot else "(ninguna)"

vars_plot = st.multiselect(
    t("Variables a graficar (eje primario)", "Variables to plot (primary axis)"),
    options=num_cols_plot,
    default=st.session_state.vars_plot,
    key="vars_plot"
)

var_sec = st.selectbox(
    t("Variable en eje secundario (opcional)", "Secondary-axis variable (optional)"),
    options=["(ninguna)"] + num_cols_plot,
    index=(["(ninguna)"] + num_cols_plot).index(st.session_state.var_sec) if st.session_state.var_sec in (["(ninguna)"] + num_cols_plot) else 0,
    key="var_sec"
)

if vars_plot or (var_sec != "(ninguna)"):
    y_cols = vars_plot.copy()
    if var_sec != "(ninguna)" and var_sec not in y_cols:
        y_cols.append(var_sec)
    if y_cols:
        fig_ts = px.line(
            plot_df, x=time_col, y=y_cols,
            title=t("Serie de tiempo (remuestreado)", "Time series (resampled)") if plot_df is df_resampled else t("Serie de tiempo (crudo)", "Time series (raw)")
        )
        if var_sec != "(ninguna)":
            fig_ts.update_traces(yaxis="y2", selector=dict(name=var_sec))
            fig_ts.update_layout(
                yaxis=dict(title=t("Eje primario", "Primary axis")),
                yaxis2=dict(title=var_sec, overlaying="y", side="right")
            )
        st.plotly_chart(style_plotly(fig_ts), use_container_width=True)
else:
    st.info(t("Selecciona al menos una variable para graficar.", "Select at least one variable to plot."))

# ===============================
# Histogramas
# ===============================
st.subheader(t("Histogramas (exploración de distribución)", "Histograms (distribution exploration)"))
st.caption(t(
    "Selecciona columnas numéricas. El origen crudo/remuestreado sigue el switch de la barra lateral (\"Usar datos remuestreados para correlación\").",
    "Select numeric columns. Source (raw/resampled) follows the sidebar switch (\"Use resampled data for correlation\")."
))

try:
    _df_num = df_num_crudo.copy()
except NameError:
    _df_num = df.copy()
try:
    _df_res = df_resampled.copy()
except NameError:
    _df_res = None

try:
    use_resampled_hist = bool(use_resampled_for_corr)
except NameError:
    use_resampled_hist = True

if use_resampled_hist and _df_res is not None and st.session_state.get('time_col', None) in _df_res.columns:
    df_base_hist = _df_res
    st.caption(t("Base usada: remuestreado", "Base used: resampled"))
else:
    df_base_hist = _df_num
    st.caption(t("Base usada: crudo", "Base used: raw"))

num_candidates = [c for c in df_base_hist.columns if c != st.session_state.get('time_col', None) and pd.api.types.is_numeric_dtype(df_base_hist[c])]

with st.expander(t("Configuración de gráfico", "Chart settings"), expanded=False):
    cols_sel = st.multiselect(t("Columnas numéricas", "Numeric columns"), options=num_candidates, default=num_candidates[:1])
    bins_method = st.selectbox(t("Método de bins", "Bin method"), options=["auto","fd","sturges","scott","sqrt","rice"], index=0)
    show_kde = st.checkbox(t("Mostrar KDE (curva de densidad)", "Show KDE (density curve)"), value=True)
    show_vlines = st.checkbox(t("Mostrar media / mediana / moda", "Show mean / median / mode"), value=True)
    use_log = st.checkbox(t("Escala logarítmica (x)", "Log scale (x)"), value=False)

from numpy import histogram_bin_edges as _bin_edges

def _hist_series(series, title=None, idx: int = 0):
    s = pd.to_numeric(series, errors='coerce').dropna()
    if s.empty:
        st.info(t(f"Sin datos válidos para {getattr(series, 'name', 'serie')}", f"No valid data for {getattr(series, 'name', 'series')}")); return
    try:
        edges = _bin_edges(s.values, bins=bins_method)
    except Exception:
        edges = _bin_edges(s.values, bins='auto')

    fig, ax = plt.subplots(figsize=(13, 6))
    sns.histplot(s, bins=edges, kde=show_kde, ax=ax)

    if show_vlines:
        mu=s.mean(); med=s.median()
        try:
            mode_val=s.mode().iloc[0]
        except Exception:
            mode_val=None
        ax.axvline(mu, ls='--', c='k', label=t("media=","mean=")+f"{mu:.4g}")
        ax.axvline(med, ls='--', c='b', label=t("mediana=","median=")+f"{med:.4g}")
        if mode_val is not None:
            ax.axvline(mode_val, ls='--', c='g', label=t("moda=","mode=")+f"{mode_val:.4g}")

    if use_log:
        try: ax.set_xscale('log')
        except Exception: pass

    ax.set_title(title or f"Distribución / Distribution – {getattr(series, 'name', '')}"); ax.grid(True, linestyle=':', alpha=0.5)
    if show_vlines: ax.legend()
    st.pyplot(fig)

    fname = f"hist_{_sanitize_filename(getattr(series, 'name', 'serie'))}.png"
    buf = fig_to_png_bytes(fig)
    st.download_button(t("⬇️ Descargar histograma (PNG)", "⬇️ Download histogram (PNG)"), data=buf, file_name=fname, mime="image/png", key=f"dl_hist_{idx}")

    q = s.quantile([0.05,0.25,0.5,0.75,0.95])
    stats_df = pd.DataFrame({'métrica':['count','missing','mean','std','min','p5','p25','median','p75','p95','max','skew','kurtosis'],
                             'valor':[int(s.count()), int(series.size - s.count()), s.mean(), s.std(ddof=0), s.min(), q.get(0.05), q.get(0.25), q.get(0.5), q.get(0.75), q.get(0.95), s.max(), s.skew(), s.kurt()]})
    st.dataframe(stats_df, use_container_width=True)

if cols_sel:
    containers = st.columns(2) if len(cols_sel) > 1 else [st.container()]
    for i,c in enumerate(cols_sel):
        holder = containers[i % len(containers)]
        with holder:
            _hist_series(df_base_hist[c], title=f"{c}", idx=i)
else:
    st.info(t("Selecciona al menos una columna numérica en las opciones de histograma.", "Select at least one numeric column in histogram options."))

# ===============================
# 📦 Diagramas de caja (outliers)
# ===============================
st.subheader(t("📦 Diagramas de caja (identificación de outliers)", "📦 Box plots (outlier identification)"))
st.caption(t(
    "Regla IQR: es outlier todo valor menor que Q1 − k·IQR o mayor que Q3 + k·IQR (k = 1.5 estándar; k = 3 solo extremos). "
    "Usa la misma base (cruda/remuestreada) que los histogramas.",
    "IQR rule: a value is an outlier if below Q1 − k·IQR or above Q3 + k·IQR (k = 1.5 standard; k = 3 extremes only). "
    "Uses the same base (raw/resampled) as the histograms."
))

with st.expander(t("Configuración de gráfico", "Chart settings"), expanded=False):
    box_cols = st.multiselect(t("Columnas numéricas", "Numeric columns"), options=num_candidates,
                              default=num_candidates[:1], key="box_cols")
    box_k = st.number_input(t("Factor k del IQR", "IQR factor k"), min_value=0.5, max_value=5.0, value=1.5, step=0.5, key="box_k")
    box_show_points = st.checkbox(t("Mostrar todos los puntos (dispersión)", "Show all points (strip)"), value=False, key="box_points")
    box_show_mean = st.checkbox(t("Mostrar media (▲)", "Show mean (▲)"), value=True, key="box_mean")
    box_horizontal = st.checkbox(t("Orientación horizontal", "Horizontal orientation"), value=False, key="box_horiz")

_time_col_box = st.session_state.get('time_col', None)

def _iqr_limits(s: pd.Series, k: float):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return q1, q3, iqr, q1 - k * iqr, q3 + k * iqr

def _boxplot_series(series: pd.Series, k: float, idx: int = 0):
    name = getattr(series, 'name', 'serie')
    s = pd.to_numeric(series, errors='coerce').dropna()
    if s.empty:
        st.info(t(f"Sin datos válidos para {name}", f"No valid data for {name}")); return None
    q1, q3, iqr, lo, hi = _iqr_limits(s, k)
    mask_out = (s < lo) | (s > hi)

    fig, ax = plt.subplots(figsize=(9, 6) if not box_horizontal else (12, 4))
    ax.boxplot(s.values, vert=not box_horizontal, whis=k, widths=0.5, showmeans=box_show_mean,
               patch_artist=True, boxprops=dict(facecolor="#9ecae1", alpha=0.8),
               medianprops=dict(color="#08306b", lw=2),
               meanprops=dict(marker="^", markerfacecolor="white", markeredgecolor="k"),
               flierprops=dict(marker="o", markerfacecolor="#d62728", markeredgecolor="none", alpha=0.6, markersize=4))
    if box_show_points:
        rng = np.random.default_rng(0)
        pts = s.values if len(s) <= 5000 else rng.choice(s.values, 5000, replace=False)
        jit = 1 + rng.uniform(-0.15, 0.15, size=len(pts))
        if box_horizontal:
            ax.scatter(pts, jit, s=4, alpha=0.25, color="k")
        else:
            ax.scatter(jit, pts, s=4, alpha=0.25, color="k")
    for lim, lbl in [(lo, t("lím. inf.", "lower lim.")), (hi, t("lím. sup.", "upper lim."))]:
        (ax.axvline if box_horizontal else ax.axhline)(lim, ls=':', c='gray', lw=1)
    ax.set_xticks([]) if not box_horizontal else ax.set_yticks([])
    (ax.set_ylabel if not box_horizontal else ax.set_xlabel)(name)
    ax.set_title(f"{name}\n{int(mask_out.sum())} outliers ({100*mask_out.mean():.1f} %) · k={k}", fontsize=11)
    ax.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    st.pyplot(fig)
    st.download_button(t("⬇️ Descargar diagrama de caja (PNG)", "⬇️ Download box plot (PNG)"),
                       data=fig_to_png_bytes(fig), file_name=f"boxplot_{_sanitize_filename(name)}.png",
                       mime="image/png", key=f"dl_box_{idx}")

    return {
        t("Variable", "Variable"): name, "n": int(s.count()),
        "Q1": q1, t("Mediana", "Median"): s.median(), "Q3": q3, "IQR": iqr,
        t("Lím. inferior", "Lower limit"): lo, t("Lím. superior", "Upper limit"): hi,
        t("Outliers bajos", "Low outliers"): int((s < lo).sum()),
        t("Outliers altos", "High outliers"): int((s > hi).sum()),
        t("% outliers", "% outliers"): round(100 * mask_out.mean(), 2),
    }

if box_cols:
    resumen_box = []
    containers = st.columns(2) if len(box_cols) > 1 else [st.container()]
    for i, c in enumerate(box_cols):
        with containers[i % len(containers)]:
            r = _boxplot_series(df_base_hist[c], box_k, idx=i)
            if r: resumen_box.append(r)

    if resumen_box:
        st.markdown("**" + t("Resumen de outliers por variable", "Outlier summary by variable") + "**")
        st.dataframe(pd.DataFrame(resumen_box).round(4), use_container_width=True, hide_index=True)

        # Tabla de registros outlier (con su fecha/hora) y descarga CSV
        with st.expander(t("Ver registros outlier (con fecha/hora)", "View outlier records (with timestamp)"), expanded=False):
            filas = []
            for c in box_cols:
                s = pd.to_numeric(df_base_hist[c], errors='coerce')
                sv = s.dropna()
                if sv.empty:
                    continue
                _, _, _, lo, hi = _iqr_limits(sv, box_k)
                m = (s < lo) | (s > hi)
                if m.any():
                    sub = pd.DataFrame({
                        t("Variable", "Variable"): c,
                        t("Valor", "Value"): s[m],
                        t("Tipo", "Type"): np.where(s[m] < lo, t("bajo", "low"), t("alto", "high")),
                    })
                    if _time_col_box in df_base_hist.columns:
                        sub.insert(0, _time_col_box, df_base_hist.loc[m, _time_col_box])
                    filas.append(sub)
            if filas:
                out_df = pd.concat(filas, ignore_index=True)
                st.dataframe(out_df, use_container_width=True, hide_index=True)
                st.download_button(t("⬇️ Descargar outliers (CSV)", "⬇️ Download outliers (CSV)"),
                                   data=out_df.to_csv(index=False).encode("utf-8-sig"),
                                   file_name="outliers.csv", mime="text/csv", key="dl_outliers_csv")
            else:
                st.success(t("No se encontraron outliers con el criterio actual.", "No outliers found with the current criterion."))
else:
    st.info(t("Selecciona al menos una columna numérica en las opciones del diagrama de caja.",
              "Select at least one numeric column in the box plot options."))

# ===============================
# 🔥 Mapa de calor de correlaciones (Pearson)
# ===============================
st.subheader(t("🔥 Mapa de calor de correlaciones (Pearson)", "🔥 Correlation heatmap (Pearson)"))
base_for_corr = df_resampled if use_resampled_for_corr else df_num_crudo
label = t("remuestreado", "resampled") if use_resampled_for_corr else t("crudo", "raw")

if show_diagnostics:
    _ = diagnose_numeric(base_for_corr, label)

num_df = base_for_corr.select_dtypes(include=[np.number])
pear = compute_correlations(num_df, min_frac=min_frac)

if pear is None:
    st.warning(t("No hay suficientes columnas numéricas con datos válidos para calcular correlaciones.",
                 "Not enough numeric columns with valid data to compute correlations."))
else:
    fig_heat = plot_one_heatmap(pear, title_suffix=f"({label})")
    fname_hm = f"heatmap_pearson_{_sanitize_filename(label)}.png"
    st.download_button(t("⬇️ Descargar mapa de calor (PNG)", "⬇️ Download heatmap (PNG)"), data=fig_to_png_bytes(fig_heat), file_name=fname_hm, mime="image/png", key="dl_heatmap")

    st.markdown("**" + t("Top correlaciones – Pearson", "Top correlations – Pearson") + "**")
    st.dataframe(top_abs_corr_dataframe(pear), use_container_width=True)

# ===============================
# Notas
# ===============================
with st.expander(t("ℹ️ Notas", "ℹ️ Notes")):
    st.markdown(
        f"""
- {t('Los nombres originales del Excel se preservan y **solo cambian** si pulsas **Aplicar** en *Renombrar columnas*.',
       'Original Excel column names are preserved and **only change** after you press **Apply** in *Rename columns*.')}
- {t(f'El nombre vigente de tiempo es: **`{time_col}`** (puedes habilitar su renombre si lo necesitas).',
       f'Current time column is: **`{time_col}`** (you can enable renaming if needed).')}
- {t('El remuestreo toma el **primer valor** del intervalo (`.first()`).', 'Resampling takes the **first value** of the interval (`.first()`).')}
- {t('Las selecciones del gráfico permanecen aunque renombres (se guardan en sesión).', 'Chart selections persist across renames (stored in session).')}
- {t('Encontrarás botones para **descargar** los histogramas, el **mapa de calor (Pearson)** y la **gráfica de valores medidos vs. predichos** en PNG.',
       'You will find buttons to **download** histograms, the **heatmap (Pearson)**, and the **measured vs. predicted** chart as PNG.')}
        """
    )

# ===============================
# Modelado y exploración (dinámico)
# ===============================
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

render_band(IMG_SIDE)
st.subheader(t("Modelado y exploración (dinámico)", "Modeling & exploration (dynamic)"))
st.caption(t("Elige objetivo y predictores desde el Excel; prueba modelo lineal, Random Forest o polinómico.",
            "Pick target and predictors from Excel; try linear, Random Forest, or polynomial models."))

try:
    df_base_model = base_for_corr.copy()
except NameError:
    df_base_model = df_num_crudo.copy() if 'df_num_crudo' in globals() else df.copy()

_suggestions = ['Torque','Bed Mass','Rake Lift','Flocculant','UF Flow','Tonnage','UF Density','Torque (%)','Masa de cama','Densidad UF','Caudal UF','Tonelaje','Rake Lift (%)']
cols_all = list(df_base_model.columns)
num_cols = [c for c in cols_all if pd.api.types.is_numeric_dtype(df_base_model[c])]

def _default_target():
    patt = re.compile(r"uf\s*dens|densidad\s*uf|solid\s*in\s*discharge|solidos.*descarga", re.I)
    for c in cols_all:
        if patt.search(str(c)):
            return c
    return num_cols[0] if num_cols else (cols_all[0] if cols_all else None)

if 'ml_target' not in st.session_state:
    st.session_state.ml_target = _default_target()
if 'ml_features' not in st.session_state:
    defaults = [c for c in cols_all if c != st.session_state.ml_target]
    order = sorted(defaults, key=lambda c: (0 if any(s.lower() in str(c).lower() for s in _suggestions) else 1, c))
    st.session_state.ml_features = order[:5]

left, right = st.columns(2)
with left:
    target_col = st.selectbox(t("Variable objetivo (y)", "Target variable (y)"), options=cols_all,
                              index=(cols_all.index(st.session_state.ml_target) if st.session_state.ml_target in cols_all else 0), key='ml_target')
with right:
    feature_cols = st.multiselect(t("Variables explicativas (X)", "Predictor variables (X)"), options=[c for c in cols_all if c != target_col],
                                  default=[c for c in st.session_state.ml_features if c in cols_all and c != target_col], key='ml_features')

with st.expander(t("Opciones de preprocesamiento", "Preprocessing options")):
    drop_na = st.checkbox(t("Eliminar filas con NA en columnas seleccionadas", "Drop rows with NA in selected columns"), value=True)
    standardize = st.checkbox(t("Estandarizar X (media 0, var 1) — solo OLS/polinómico", "Standardize X (mean 0, var 1) — OLS/polynomial only"), value=False)

with st.expander(t("Modelo", "Model")):
    model_name = st.selectbox(t("Tipo de modelo", "Model type"), options=["Lineal (OLS)", "Random Forest", "Polinómico (grado k)"], index=1)
    if model_name == "Random Forest":
        n_estimators = st.slider("n_estimators", 50, 600, 200, 25)
        max_depth = st.slider(t("max_depth (None = sin límite)", "max_depth (None = unlimited)"), 0, 40, 0, 1)
        max_depth = None if max_depth == 0 else max_depth
        rf_bootstrap = st.checkbox("bootstrap", True)
        rf_random_state = st.number_input("random_state", min_value=0, value=42, step=1)
    elif model_name == "Polinómico (grado k)":
        poly_degree = st.slider(t("Grado del polinomio", "Polynomial degree"), 2, 5, 2)
        include_bias = st.checkbox(t("Incluir bias en PolynomialFeatures", "Include bias in PolynomialFeatures"), False)

if target_col is None or not feature_cols:
    st.info(t("Selecciona una variable objetivo y al menos una variable explicativa.", "Select a target and at least one predictor."))
else:
    work = df_base_model[[target_col] + feature_cols].copy()

    if drop_na:
        work = work.dropna(subset=[target_col] + feature_cols)

    for c in [target_col] + feature_cols:
        if not pd.api.types.is_numeric_dtype(work[c]):
            work[c] = pd.to_numeric(work[c], errors='coerce')
    work = work.dropna(subset=[target_col] + feature_cols)

    if len(work) < 10:
        st.warning(t("No hay suficientes filas válidas después del preprocesamiento (se requieren ≥ 10).",
                     "Not enough valid rows after preprocessing (need ≥ 10)."))
    else:
        X = work[feature_cols]
        y = work[target_col]

        if standardize and model_name in {"Lineal (OLS)", "Polinómico (grado k)"}:
            mu = X.mean(axis=0); sigma = X.std(axis=0).replace(0, 1); Xs = (X - mu) / sigma
        else:
            Xs = X

        if model_name == "Lineal (OLS)":
            reg = LinearRegression(); reg.fit(Xs, y); pred_fn = (lambda Z: reg.predict((Z - mu) / sigma) if standardize else reg.predict(Z))
        elif model_name == "Random Forest":
            reg = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, bootstrap=rf_bootstrap, random_state=rf_random_state, n_jobs=-1)
            reg.fit(X, y); pred_fn = reg.predict
        else:
            poly = PolynomialFeatures(degree=poly_degree, include_bias=include_bias)
            from sklearn.pipeline import Pipeline
            if standardize:
                reg = Pipeline([("poly", poly), ("lin", LinearRegression())]); reg.fit(Xs, y); pred_fn = (lambda Z: reg.predict(((Z - mu) / sigma)))
            else:
                reg = Pipeline([("poly", poly), ("lin", LinearRegression())]); reg.fit(X, y); pred_fn = reg.predict

        train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=42)
        if model_name == "Lineal (OLS)" and standardize:
            mu_tr = train_X.mean(axis=0); sigma_tr = train_X.std(axis=0).replace(0, 1)
            reg_e = LinearRegression().fit((train_X - mu_tr) / sigma_tr, train_y)
            preds = reg_e.predict((test_X - mu_tr) / sigma_tr)
        elif model_name == "Polinómico (grado k)":
            from sklearn.pipeline import Pipeline
            if standardize:
                mu_tr = train_X.mean(axis=0); sigma_tr = train_X.std(axis=0).replace(0, 1)
                pipe_e = Pipeline([("poly", PolynomialFeatures(degree=poly_degree, include_bias=include_bias)), ("lin", LinearRegression())]).fit((train_X - mu_tr) / sigma_tr, train_y)
                preds = pipe_e.predict((test_X - mu_tr) / sigma_tr)
            else:
                pipe_e = Pipeline([("poly", PolynomialFeatures(degree=poly_degree, include_bias=include_bias)), ("lin", LinearRegression())]).fit(train_X, train_y)
                preds = pipe_e.predict(test_X)
        else:
            preds = reg.predict(test_X)

        mse = mean_squared_error(test_y, preds); rmse = float(np.sqrt(mse)); r2 = r2_score(test_y, preds)
        st.markdown("**" + t("Resumen del modelo (hold-out 80/20):", "Model summary (hold-out 80/20):") + "**")
        st.write({t("Observaciones", "Observations"): len(X), t("Features", "Features"): len(feature_cols), t("Modelo", "Model"): model_name, "MSE": round(mse,3), "RMSE": round(rmse,3), "R2": round(r2,3)})

        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.scatter(test_y, preds, alpha=0.7)
        min_v = min(test_y.min(), preds.min()); max_v = max(test_y.max(), preds.max())
        ax1.plot([min_v, max_v], [min_v, max_v], 'r--')
        ax1.set_xlabel(t(f"Valor real de {target_col}", f"Actual value of {target_col}")); ax1.set_ylabel(t(f"Valor predicho de {target_col}", f"Predicted value of {target_col}")); ax1.set_title(t("Comparación entre valores reales y predichos", "Actual vs predicted")); ax1.grid(True)
        st.pyplot(fig1)

        fname_sc = f"medidos_vs_predichos_{_sanitize_filename(target_col)}.png"
        st.download_button(t("⬇️ Descargar imagen (PNG)", "⬇️ Download image (PNG)"), data=fig_to_png_bytes(fig1), file_name=fname_sc, mime="image/png", key="dl_scatter")

        with st.expander(t("Predicción manual", "Manual prediction")):
            st.caption(t("Ingresa valores para las variables X. Los no especificados usarán la mediana del dataset.", "Enter values for X; unspecified use dataset median."))
            med = X.median(); p5 = X.quantile(0.05); p95 = X.quantile(0.95)
            user_vals = {}; cols_ui = st.columns(2) if len(feature_cols)>1 else [st.container()]
            for i, feat in enumerate(feature_cols):
                col = cols_ui[i % len(cols_ui)]
                with col:
                    vmin=float(p5.get(feat, X[feat].min())); vmax=float(p95.get(feat, X[feat].max())); vdef=float(med.get(feat, X[feat].median()))
                    step=(vmax-vmin)/100 if vmax>vmin else 0.01
                    user_vals[feat]=st.number_input(f"{feat}", value=round(vdef,4), min_value=float(min(vmin,vdef,vmax)), max_value=float(max(vmin,vdef,vmax)), step=step)
                    st.caption(t(f"Límites del campo (P5–P95): {vmin:.4g} – {vmax:.4g}",
                                 f"Input limits (P5–P95): {vmin:.4g} – {vmax:.4g}"))
            if st.button(t("Calcular predicción", "Compute prediction"), type="primary"):
                row = pd.DataFrame([user_vals]); yhat = float(np.asarray(pred_fn(row)).ravel()[0])
                st.success(t(f"Predicción estimada para {target_col}: {yhat:.4f}", f"Estimated prediction for {target_col}: {yhat:.4f}"))

# ===============================
# Próximamente / Coming soon
# ===============================
st.markdown("---")
render_centered_image(IMG_THICKENER, "Thickener")
st.markdown('<div class="soon-msg"><span>Coming soon</span></div>', unsafe_allow_html=True)
render_centered_image(IMG_FEEDWELL, "Feedwell acceleration")
