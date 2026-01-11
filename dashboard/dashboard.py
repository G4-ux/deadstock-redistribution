"""
Inventory Optimization & Redistribution Dashboard - Dark Theme Edition

Single-file Streamlit app for inventory management with stunning visuals
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from logic.preprocessing import load_inventory
from logic.scoring import compute_deadstock_score
from logic.ranking import get_redistribution_recommendations

# ---- Page config ----
st.set_page_config(
    page_title="Inventory Optimization Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Dark Theme CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --primary: #8B5CF6;
    --secondary: #3B82F6;
    --accent: #06B6D4;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
}

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
    background-attachment: fixed;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: radial-gradient(circle at 20% 50%, rgba(139,92,246,0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(59,130,246,0.1) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

.main .block-container {
    backdrop-filter: blur(10px);
    background: rgba(15,23,42,0.3);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.stButton>button {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 12px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(139,92,246,0.4);
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(139,92,246,0.6);
}

[data-testid="stMetricValue"] {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

[data-testid="stMetricLabel"] {
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 600;
}

div[data-testid="stMetric"] {
    background: rgba(30,41,59,0.7);
    backdrop-filter: blur(10px);
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid rgba(139,92,246,0.2);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: all 0.3s;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    border-color: var(--primary);
    box-shadow: 0 8px 30px rgba(139,92,246,0.4);
}

div[data-testid="stExpander"] {
    background: rgba(30,41,59,0.7);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    border: 1px solid rgba(139,92,246,0.2);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,23,42,0.95), rgba(30,41,59,0.95));
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(139,92,246,0.3);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: rgba(30,41,59,0.7);
    backdrop-filter: blur(10px);
    padding: 0.8rem;
    border-radius: 16px;
    border: 1px solid rgba(139,92,246,0.2);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 0.6rem 1.8rem;
    font-weight: 600;
    color: #94A3B8;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(139,92,246,0.4);
}

.stDownloadButton>button {
    background: linear-gradient(135deg, var(--success), var(--accent));
    border: none;
    border-radius: 12px;
    padding: 0.6rem 2rem;
    font-weight: 600;
}

h1, h2, h3 { color: #F1F5F9; font-weight: 800; }
h1 { font-size: 3rem; }

hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
}

::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-track { background: #0F172A; }
::-webkit-scrollbar-thumb { 
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---- Helper Functions ----





def get_plotly_theme():
    """Dark theme for Plotly charts"""
    return {
        'plot_bgcolor': 'rgba(15,23,42,0.5)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': '#F1F5F9', 'family': 'Inter'},
        'title': {'font': {'size': 18, 'color': '#F1F5F9'}},
        'xaxis': {'gridcolor': 'rgba(139,92,246,0.1)', 'linecolor': 'rgba(139,92,246,0.3)'},
        'yaxis': {'gridcolor': 'rgba(139,92,246,0.1)', 'linecolor': 'rgba(139,92,246,0.3)'}
    }

# ---- Sidebar ----
with st.sidebar:
    st.markdown("### 📤 Upload Data")
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xls", "xlsx"])
    st.caption("**Required columns:** SKU, Store, Stock, Sales, Sell_Through")
    
    if uploaded_file:
        df = load_data(uploaded_file)
        if df is not None:
            st.success(f"✅ Loaded {len(df):,} rows")
        else:
            df = generate_placeholder_data()
            st.warning("⚠️ Using sample data")
    else:
        df = generate_placeholder_data()
        st.info("ℹ️ Using sample data")
    
    st.markdown("---")
    st.caption("💡 Upload your file for real insights")

# ---- Header ----
st.markdown("""
<h1 style='text-align: center; margin-bottom: 0.5rem;'>
    📦 Inventory Optimization Dashboard
</h1>
<p style='text-align: center; color: #94A3B8; font-size: 1.1rem; margin-bottom: 2rem;'>
    Real-time insights • Smart redistribution • Data-driven decisions
</p>
""", unsafe_allow_html=True)
st.markdown("---")

df_raw = load_inventory("data/raw/synthetic_retail_sales_inventory.csv")
df_scored = compute_deadstock_score(df_raw)
recs = get_redistribution_recommendations(df_scored)


# ---- Metrics ----
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total SKUs", f"{df['SKU'].nunique():,}")
with col2:
    slow_skus = sku_summary["Slow_Moving"].sum() if not sku_summary.empty else 0
    st.metric("Slow-moving SKUs", slow_skus, delta=f"-{slow_skus}" if slow_skus > 0 else None, delta_color="inverse")
with col3:
    over_skus = sku_summary["Overstocked"].sum() if not sku_summary.empty else 0
    st.metric("Overstocked SKUs", over_skus, delta=f"-{over_skus}" if over_skus > 0 else None, delta_color="inverse")
with col4:
    st.metric("Avg Sell-through", f"{df['Sell_Through'].mean():.2%}")

st.markdown("<br>", unsafe_allow_html=True)

# ---- Tabs ----
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🎯 Recommendations", "🔍 SKU Explorer", "📁 Raw Data"])

with tab1:
    st.markdown("### 🔎 Detection & Analysis")
    
    # Summary expander
    with st.expander("📋 SKU-Level Summary", expanded=False):
        if not sku_summary.empty:
            st.dataframe(sku_summary.style.format({"Avg_Sell_Through": "{:.2%}"}), use_container_width=True, height=350)
        else:
            st.info("No data available")
    
    # Flagged items
    st.markdown("#### 🎯 Flagged Items")
    display_df = df.copy().sort_values(["SKU", "Store"]).reset_index(drop=True)
    display_df["Slow_Moving"] = display_df["Slow_Moving"].map({True: "⚠️ Yes", False: ""})
    display_df["Overstocked"] = display_df["Overstocked"].map({True: "📦 Yes", False: ""})
    
    def highlight_row(val):
        if val in ["⚠️ Yes", "📦 Yes"]:
            return 'background-color: rgba(239,68,68,0.2); color: #FCA5A5; font-weight: 600'
        return ''
    
    styled = display_df.style.map(highlight_row, subset=["Slow_Moving", "Overstocked"]).format({"Sell_Through": "{:.2%}"})
    st.dataframe(styled, use_container_width=True, height=400)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    st.markdown("### 📊 Inventory Distribution")
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        fig = px.histogram(df, x="Stock", nbins=30, title="Stock Distribution", color_discrete_sequence=["#8B5CF6"])
        fig.update_layout(**get_plotly_theme(), height=400, margin=dict(l=20,r=20,t=60,b=40))
        fig.update_traces(marker_line_color='rgba(139,92,246,0.5)', marker_line_width=1.5)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("📈 Median Stock", f"{int(df['Stock'].median()):,}")
        st.metric("📊 Total Stock", f"{int(df['Stock'].sum()):,}")
        st.metric("🏪 Stores", f"{df['Store'].nunique()}")
        st.metric("📦 Records", f"{len(df):,}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🏆 Store Performance Ranking")
    
    store_rank = df.groupby("Store")["Sell_Through"].mean().reset_index().sort_values("Sell_Through", ascending=False)
    fig2 = px.bar(store_rank, x="Store", y="Sell_Through", title="Average Sell-Through by Store",
                  color="Sell_Through", color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"])
    fig2.update_layout(**get_plotly_theme(), height=450, margin=dict(l=20,r=20,t=60,b=40))
    fig2.update_traces(marker_line_color='rgba(139,92,246,0.3)', marker_line_width=2)
    fig2.update_yaxes(tickformat='.0%')
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("### 🎯 Smart Redistribution Recommendations")
    st.markdown("**Strategy:** Transfer from *low-demand* to *high-demand* stores")
    
    if not recs.empty:
        recs_display = recs.copy()
        recs_display["Action"] = recs_display.apply(lambda r:
            "🔄 Transfer low→high" if (r["High_Count"]>0 and r["Low_Count"]>0) else
            "💰 Promotions needed" if r["Low_Count"]>0 else
            "📈 Replenish stock" if r["High_Count"]>0 else "✅ No action", axis=1)
        
        st.dataframe(recs_display.sort_values(["High_Count", "Low_Count"], ascending=False), 
                     use_container_width=True, height=450)
        
        st.markdown("### 📍 Transfer Opportunity Matrix")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            opp_df = recs_display[recs_display["High_Count"] > 0]
            if not opp_df.empty:
                fig3 = px.scatter(opp_df, x="Low_Count", y="High_Count", size="High_Count", color="High_Count",
                                  hover_name="SKU", title="SKU Transfer Priorities",
                                  color_continuous_scale=["#8B5CF6", "#3B82F6", "#06B6D4"])
                fig3.update_layout(**get_plotly_theme(), height=450, margin=dict(l=20,r=20,t=60,b=40))
                st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.metric("🎯 Priority", len(recs_display[(recs_display["High_Count"]>0) & (recs_display["Low_Count"]>0)]))
            st.metric("💰 Clearance", len(recs_display[(recs_display["High_Count"]==0) & (recs_display["Low_Count"]>0)]))
            st.metric("📈 Restock", len(recs_display[(recs_display["High_Count"]>0) & (recs_display["Low_Count"]==0)]))
    else:
        st.info("No recommendations")
    
    with st.expander("💡 Implementation Guide"):
        st.markdown("""
        1. **🎯 Prioritize** - Focus on high/low demand SKUs
        2. **📊 Validate** - Check actual stock levels
        3. **🚚 Calculate** - Determine transfer quantities
        4. **💰 Analyze** - Factor in shipping costs
        5. **📅 Schedule** - Plan delivery routes
        6. **📈 Monitor** - Track improvements
        """)

with tab3:
    st.markdown("### 🔍 SKU Deep Dive")
    
    if df['SKU'].nunique() > 0:
        selected_sku = st.selectbox("Select SKU", sorted(df['SKU'].unique()))
        
        if selected_sku:
            sku_df = df[df['SKU'] == selected_sku].sort_values('Sell_Through', ascending=False)
            st.markdown(f"<h2 style='text-align: center;'>📦 {selected_sku}</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([2.5, 1])
            
            with col1:
                st.markdown("#### 🏪 Store Performance")
                sku_display = sku_df[['Store','Stock','Sales','Sell_Through','Slow_Moving','Overstocked']].copy()
                sku_display['Slow_Moving'] = sku_display['Slow_Moving'].map({True: "⚠️", False: ""})
                sku_display['Overstocked'] = sku_display['Overstocked'].map({True: "📦", False: ""})
                st.dataframe(sku_display.style.format({"Sell_Through": "{:.2%}"}), 
                             use_container_width=True, height=320)
            
            with col2:
                st.metric("💼 Total Stock", f"{int(sku_df['Stock'].sum()):,}")
                st.metric("💰 Total Sales", f"{int(sku_df['Sales'].sum()):,}")
                st.metric("📈 Avg Sell-Through", f"{sku_df['Sell_Through'].mean():.2%}")
                st.metric("🏪 Stores", len(sku_df))
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                fig4 = px.bar(sku_df, x='Store', y='Sell_Through', color='Sell_Through',
                              title=f"{selected_sku} - Sell-Through", color_continuous_scale=["#EF4444","#F59E0B","#10B981"])
                fig4.update_layout(**get_plotly_theme(), height=400, margin=dict(l=20,r=20,t=60,b=40))
                fig4.update_yaxes(tickformat='.0%')
                st.plotly_chart(fig4, use_container_width=True)
            
            with col2:
                fig5 = px.scatter(sku_df, x='Stock', y='Sales', size='Stock', color='Sell_Through',
                                  hover_name='Store', title='Stock vs Sales', color_continuous_scale="Viridis")
                fig5.update_layout(**get_plotly_theme(), height=400, margin=dict(l=20,r=20,t=60,b=40))
                st.plotly_chart(fig5, use_container_width=True)
            
            # Insights
            st.markdown("#### 💡 Insights")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                best_store = sku_df.loc[sku_df['Sell_Through'].idxmax(), 'Store']
                best_rate = sku_df['Sell_Through'].max()
                st.markdown(f"""
                <div style='padding:1rem; background:rgba(16,185,129,0.1); border-radius:12px; border-left:4px solid #10B981'>
                    <h4 style='color:#10B981; margin:0'>🏆 Top Performer</h4>
                    <p style='color:#CBD5E1; margin:0.5rem 0 0'><strong>{best_store}</strong><br>{best_rate:.2%}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with c2:
                worst_store = sku_df.loc[sku_df['Sell_Through'].idxmin(), 'Store']
                worst_rate = sku_df['Sell_Through'].min()
                st.markdown(f"""
                <div style='padding:1rem; background:rgba(239,68,68,0.1); border-radius:12px; border-left:4px solid #EF4444'>
                    <h4 style='color:#EF4444; margin:0'>⚠️ Needs Attention</h4>
                    <p style='color:#CBD5E1; margin:0.5rem 0 0'><strong>{worst_store}</strong><br>{worst_rate:.2%}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with c3:
                balance = "Balanced" if sku_df['Stock'].std() < sku_df['Stock'].mean() else "Unbalanced"
                st.markdown(f"""
                <div style='padding:1rem; background:rgba(59,130,246,0.1); border-radius:12px; border-left:4px solid #3B82F6'>
                    <h4 style='color:#3B82F6; margin:0'>📊 Stock Balance</h4>
                    <p style='color:#CBD5E1; margin:0.5rem 0 0'>Std: {sku_df['Stock'].std():.1f}<br>{balance}</p>
                </div>
                """, unsafe_allow_html=True)

with tab4:
    st.markdown("### 📁 Raw Data & Export")
    
    col1, col2 = st.columns(2)
    with col1:
        show_slow = st.checkbox("Show only slow-moving")
    with col2:
        show_over = st.checkbox("Show only overstocked")
    
    filtered_df = df.copy()
    if show_slow:
        filtered_df = filtered_df[filtered_df['Slow_Moving'] == True]
    if show_over:
        filtered_df = filtered_df[filtered_df['Overstocked'] == True]
    
    st.dataframe(filtered_df.style.format({"Sell_Through": "{:.2%}"}), use_container_width=True, height=500)
    
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Filtered CSV", csv, f"filtered_{datetime.now():%Y%m%d_%H%M%S}.csv", "text/csv")
    with col2:
        full_csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Full CSV", full_csv, f"full_{datetime.now():%Y%m%d_%H%M%S}.csv", "text/csv")
    with col3:
        st.caption(f"📊 Showing {len(filtered_df):,} of {len(df):,} records")

# ---- Footer ----
st.markdown("---")
st.markdown("""
<div style='padding:2rem; background:linear-gradient(135deg,rgba(139,92,246,0.1),rgba(59,130,246,0.1)); 
     border-radius:16px; border:1px solid rgba(139,92,246,0.3); margin:2rem 0'>
    <h2 style='text-align:center; margin-top:0'>✨ Key Takeaways</h2>
    <p style='font-size:1.1rem; line-height:1.8; color:#CBD5E1'>
        This dashboard identifies <strong style='color:#8B5CF6'>slow-moving SKUs</strong> (&lt;20% sell-through) and 
        <strong style='color:#3B82F6'>overstocked items</strong> (stock &gt; 3× sales). 
        Use recommendations to optimize inventory distribution and improve sell-through rates.
    </p>
    <p style='color:#94A3B8; margin-bottom:0'>
        <strong>Next Steps:</strong> Configure transfer rules • Validate with operations • 
        Integrate with order management • Set up alerts • Monitor KPIs
    </p>
</div>
<p style='text-align:center; color:#64748B; margin-top:2rem'>
    🚀 Built with Streamlit • Powered by AI • Production-ready
</p>
""", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Deadstock Redistribution — Demo", layout="wide")
st.title("Deadstock Redistribution — Demo")

data_path = Path("data/raw/synthetic_retail_sales_inventory.csv")

if data_path.exists():
	df = pd.read_csv(data_path)
	st.markdown(f"**Loaded dataset:** {data_path} — {df.shape[0]} rows, {df.shape[1]} columns")
	st.dataframe(df.head(100))
	with st.expander("Columns"):
		st.write(list(df.columns))
else:
	st.warning(f"Sample dataset not found at {data_path}.")
	st.info("Place your CSV at data/raw/synthetic_retail_sales_inventory.csv to view it here.")

