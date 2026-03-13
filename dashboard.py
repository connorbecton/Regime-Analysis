"""
Regime Analysis Dashboard
Interactive visualization of the Enhanced Momentum Regime Model v2.0
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import signal_calculator as calc
import config

from dash import Dash, html, dcc, dash_table
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Load & calculate ─────────────────────────────────────────────────────────

def load_prices():
    csv_path = os.path.join(os.path.dirname(__file__), 'Prices.csv')
    df = pd.read_csv(csv_path)
    needed = ['XLU','XLP','XLV','XLF','XLY','XLI','XLB','XLK','XLC',
              'SPLV','SPHB','RPV','RPG','SPY','VYM','HYG','IEI']
    prices = df[['Date'] + needed].copy()
    prices = prices.apply(lambda col: pd.to_numeric(col, errors='coerce') if col.name != 'Date' else col)

    def parse_date(val):
        try:
            return pd.to_datetime(val)
        except Exception:
            return pd.Timestamp('1899-12-30') + pd.Timedelta(days=int(float(val)))

    prices['Date'] = prices['Date'].apply(parse_date)
    prices = prices.set_index('Date').dropna()
    prices = prices[prices.index <= pd.Timestamp.today()]
    return prices


prices = load_prices()
signals = calc.calculate_all_signals(prices)
signals['EWMA_Score'] = calc.calculate_ewma_score(signals['Composite'])
signals['Regime'] = signals['EWMA_Score'].apply(calc.classify_regime)

sweep_path = os.path.join(os.path.dirname(__file__), 'parameter_sweep_results.csv')
sweep = pd.read_csv(sweep_path)

# Current state
latest = signals.iloc[-1]
current_regime = latest['Regime']
current_ewma = latest['EWMA_Score']
current_composite = latest['Composite']

REGIME_COLORS = {'Defensive': '#e74c3c', 'Neutral': '#f39c12', 'Risk-On': '#27ae60'}
current_color = REGIME_COLORS[current_regime]

# ── Helper: regime background shapes ─────────────────────────────────────────

def regime_shapes(series):
    shapes = []
    colors = {'Defensive': 'rgba(231,76,60,0.12)', 'Risk-On': 'rgba(39,174,96,0.12)', 'Neutral': 'rgba(0,0,0,0)'}
    prev_regime = None
    start_date = None
    for date, regime in series.items():
        if regime != prev_regime:
            if prev_regime is not None and colors[prev_regime] != 'rgba(0,0,0,0)':
                shapes.append(dict(type='rect', xref='x', yref='paper',
                                   x0=start_date, x1=date, y0=0, y1=1,
                                   fillcolor=colors[prev_regime], line_width=0, layer='below'))
            start_date = date
            prev_regime = regime
    if prev_regime and colors[prev_regime] != 'rgba(0,0,0,0)':
        shapes.append(dict(type='rect', xref='x', yref='paper',
                           x0=start_date, x1=series.index[-1], y0=0, y1=1,
                           fillcolor=colors[prev_regime], line_width=0, layer='below'))
    return shapes


# ── Chart 1: EWMA Score history ───────────────────────────────────────────────

def ewma_chart():
    fig = go.Figure()
    fig.add_hrect(y0=config.THRESHOLD_DEFENSIVE, y1=signals['EWMA_Score'].max() + 2,
                  fillcolor='rgba(231,76,60,0.08)', line_width=0, annotation_text='Defensive zone',
                  annotation_position='top left')
    fig.add_hrect(y0=signals['EWMA_Score'].min() - 2, y1=config.THRESHOLD_RISKON,
                  fillcolor='rgba(39,174,96,0.08)', line_width=0, annotation_text='Risk-On zone',
                  annotation_position='bottom left')
    fig.add_hline(y=config.THRESHOLD_DEFENSIVE, line_dash='dash', line_color='#e74c3c', line_width=1)
    fig.add_hline(y=config.THRESHOLD_RISKON, line_dash='dash', line_color='#27ae60', line_width=1)
    fig.add_hline(y=0, line_color='grey', line_width=0.5)

    fig.add_trace(go.Scatter(x=signals.index, y=signals['EWMA_Score'],
                             mode='lines', name='EWMA Score',
                             line=dict(color='#2c3e50', width=2)))
    fig.add_trace(go.Scatter(x=[signals.index[-1]], y=[current_ewma],
                             mode='markers', name='Current',
                             marker=dict(color=current_color, size=10, symbol='circle')))

    fig.update_layout(title='EWMA Score Over Time', xaxis_title='', yaxis_title='Score',
                      height=320, margin=dict(l=50, r=20, t=40, b=20),
                      legend=dict(orientation='h', y=1.1), plot_bgcolor='white',
                      paper_bgcolor='white')
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
    return fig


# ── Chart 2: Signal Z-scores ──────────────────────────────────────────────────

def zscore_chart():
    signal_cols = {'Z_DefCyc': 'Def/Cyc', 'Z_ValGrw': 'Val/Grw',
                   'Z_HiDivMkt': 'HiDiv/Mkt', 'Z_CrdSprd': 'Credit Spread', 'Z_LoBHiB': 'Lo/Hi Beta'}
    colors_z = ['#3498db', '#9b59b6', '#e67e22', '#1abc9c', '#95a5a6']

    fig = go.Figure()
    fig.add_hline(y=1.5, line_dash='dot', line_color='#e74c3c', line_width=1)
    fig.add_hline(y=-1.5, line_dash='dot', line_color='#27ae60', line_width=1)
    fig.add_hline(y=0, line_color='grey', line_width=0.5)

    for (col, label), color in zip(signal_cols.items(), colors_z):
        fig.add_trace(go.Scatter(x=signals.index, y=signals[col],
                                 mode='lines', name=label,
                                 line=dict(color=color, width=1.5)))

    fig.update_layout(title='Signal Z-Scores', xaxis_title='', yaxis_title='Z-Score',
                      height=320, margin=dict(l=50, r=20, t=40, b=20),
                      legend=dict(orientation='h', y=1.15), plot_bgcolor='white',
                      paper_bgcolor='white')
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
    return fig


# ── Chart 3: Composite Score bar ─────────────────────────────────────────────

def composite_chart():
    tail = signals.tail(52)
    bar_colors = [REGIME_COLORS[r] for r in tail['Regime']]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=tail.index, y=tail['Composite'],
                         marker_color=bar_colors, name='Composite'))
    fig.add_hline(y=0, line_color='grey', line_width=0.5)
    fig.update_layout(title='Composite Score – Last 52 Weeks', xaxis_title='', yaxis_title='Score',
                      height=280, margin=dict(l=50, r=20, t=40, b=20),
                      plot_bgcolor='white', paper_bgcolor='white', showlegend=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
    return fig


# ── Chart 4: Regime history timeline ─────────────────────────────────────────

def regime_timeline():
    regime_map = {'Defensive': 1, 'Neutral': 0, 'Risk-On': -1}
    vals = signals['Regime'].map(regime_map)
    colors_r = [REGIME_COLORS[r] for r in signals['Regime']]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=signals.index, y=vals,
                         marker_color=colors_r, name='Regime'))
    fig.update_layout(title='Regime History', xaxis_title='', yaxis_title='',
                      height=200, margin=dict(l=50, r=20, t=40, b=20),
                      plot_bgcolor='white', paper_bgcolor='white', showlegend=False)
    fig.update_yaxes(tickvals=[-1, 0, 1], ticktext=['Risk-On', 'Neutral', 'Defensive'],
                     showgrid=False)
    fig.update_xaxes(showgrid=False)
    return fig


# ── Optimization table ────────────────────────────────────────────────────────

def sweep_table():
    display_cols = ['Threshold_Def', 'EWMA_Span', 'Hysteresis',
                    'Risk-On_n', 'Defensive_n',
                    'Risk-On_26wk_avg', 'Defensive_26wk_avg',
                    'Spread_26wk', 'Risk-On_26wk_wr', 'Defensive_26wk_wr']
    df = sweep[display_cols].copy().head(20)
    for col in ['Risk-On_26wk_avg', 'Defensive_26wk_avg', 'Spread_26wk',
                'Risk-On_26wk_wr', 'Defensive_26wk_wr']:
        df[col] = df[col].apply(lambda x: f'{x:.1%}' if pd.notna(x) else '')

    rename = {'Threshold_Def': 'Threshold', 'EWMA_Span': 'Span', 'Hysteresis': 'Hyst',
              'Risk-On_n': 'RO n', 'Defensive_n': 'Def n',
              'Risk-On_26wk_avg': 'RO 26wk', 'Defensive_26wk_avg': 'Def 26wk',
              'Spread_26wk': 'Spread', 'Risk-On_26wk_wr': 'RO WR', 'Defensive_26wk_wr': 'Def WR'}
    df = df.rename(columns=rename)

    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'name': c, 'id': c} for c in df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '6px', 'fontSize': '13px',
                    'fontFamily': 'Arial'},
        style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 0}, 'backgroundColor': '#eafaf1', 'fontWeight': 'bold'}
        ]
    )


# ── Layout ────────────────────────────────────────────────────────────────────

app = Dash(__name__)

# Recent signals table
recent = signals.tail(10)[['Z_DefCyc', 'Z_ValGrw', 'Z_HiDivMkt', 'Z_CrdSprd',
                            'Composite', 'EWMA_Score', 'Regime']].copy()
recent.index = recent.index.strftime('%Y-%m-%d')
recent = recent.reset_index().rename(columns={'Date': 'Date', 'Z_DefCyc': 'Def/Cyc Z',
                                               'Z_ValGrw': 'Val/Grw Z', 'Z_HiDivMkt': 'HiDiv Z',
                                               'Z_CrdSprd': 'CrdSprd Z'})
for col in ['Def/Cyc Z', 'Val/Grw Z', 'HiDiv Z', 'CrdSprd Z', 'EWMA_Score']:
    recent[col] = recent[col].round(3)
recent['Composite'] = recent['Composite'].round(1)

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f5f6fa',
                              'padding': '20px', 'maxWidth': '1400px', 'margin': '0 auto'}, children=[

    # Header
    html.Div(style={'marginBottom': '20px'}, children=[
        html.H1('Regime Analysis Dashboard', style={'margin': '0', 'color': '#2c3e50'}),
        html.P('Enhanced Momentum Regime Model v2.0', style={'color': '#7f8c8d', 'margin': '4px 0 0 0'})
    ]),

    # Current regime KPI cards
    html.Div(style={'display': 'flex', 'gap': '16px', 'marginBottom': '20px'}, children=[
        html.Div(style={'flex': 1, 'backgroundColor': current_color, 'color': 'white',
                        'borderRadius': '8px', 'padding': '20px', 'textAlign': 'center'}, children=[
            html.Div('CURRENT REGIME', style={'fontSize': '12px', 'opacity': '0.85', 'letterSpacing': '1px'}),
            html.Div(current_regime, style={'fontSize': '32px', 'fontWeight': 'bold', 'marginTop': '6px'})
        ]),
        html.Div(style={'flex': 1, 'backgroundColor': 'white', 'borderRadius': '8px',
                        'padding': '20px', 'textAlign': 'center', 'boxShadow': '0 1px 4px rgba(0,0,0,0.08)'}, children=[
            html.Div('EWMA SCORE', style={'fontSize': '12px', 'color': '#7f8c8d', 'letterSpacing': '1px'}),
            html.Div(f'{current_ewma:.2f}', style={'fontSize': '32px', 'fontWeight': 'bold',
                                                    'color': current_color, 'marginTop': '6px'}),
            html.Div(f'Threshold: ±{config.THRESHOLD_DEFENSIVE}',
                     style={'fontSize': '12px', 'color': '#95a5a6', 'marginTop': '4px'})
        ]),
        html.Div(style={'flex': 1, 'backgroundColor': 'white', 'borderRadius': '8px',
                        'padding': '20px', 'textAlign': 'center', 'boxShadow': '0 1px 4px rgba(0,0,0,0.08)'}, children=[
            html.Div('COMPOSITE SCORE', style={'fontSize': '12px', 'color': '#7f8c8d', 'letterSpacing': '1px'}),
            html.Div(f'{current_composite:.1f}', style={'fontSize': '32px', 'fontWeight': 'bold',
                                                         'color': '#2c3e50', 'marginTop': '6px'}),
            html.Div(f'Max possible: ±{config.MAX_COMPOSITE_SCORE:.0f}',
                     style={'fontSize': '12px', 'color': '#95a5a6', 'marginTop': '4px'})
        ]),
        html.Div(style={'flex': 1, 'backgroundColor': 'white', 'borderRadius': '8px',
                        'padding': '20px', 'textAlign': 'center', 'boxShadow': '0 1px 4px rgba(0,0,0,0.08)'}, children=[
            html.Div('AS OF', style={'fontSize': '12px', 'color': '#7f8c8d', 'letterSpacing': '1px'}),
            html.Div(signals.index[-1].strftime('%b %d, %Y'),
                     style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#2c3e50', 'marginTop': '6px'}),
            html.Div(f'{len(signals)} weeks of data',
                     style={'fontSize': '12px', 'color': '#95a5a6', 'marginTop': '4px'})
        ]),
    ]),

    # Charts row 1
    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '16px', 'marginBottom': '16px'}, children=[
        html.Div(style={'backgroundColor': 'white', 'borderRadius': '8px', 'padding': '16px',
                        'boxShadow': '0 1px 4px rgba(0,0,0,0.08)'}, children=[
            dcc.Graph(figure=ewma_chart(), config={'displayModeBar': False})
        ]),
        html.Div(style={'backgroundColor': 'white', 'borderRadius': '8px', 'padding': '16px',
                        'boxShadow': '0 1px 4px rgba(0,0,0,0.08)'}, children=[
            dcc.Graph(figure=zscore_chart(), config={'displayModeBar': False})
        ]),
    ]),

    # Charts row 2
    html.Div(style={'display': 'grid', 'gridTemplateColumns': '2fr 1fr', 'gap': '16px', 'marginBottom': '16px'}, children=[
        html.Div(style={'backgroundColor': 'white', 'borderRadius': '8px', 'padding': '16px',
                        'boxShadow': '0 1px 4px rgba(0,0,0,0.08)'}, children=[
            dcc.Graph(figure=composite_chart(), config={'displayModeBar': False})
        ]),
        html.Div(style={'backgroundColor': 'white', 'borderRadius': '8px', 'padding': '16px',
                        'boxShadow': '0 1px 4px rgba(0,0,0,0.08)'}, children=[
            dcc.Graph(figure=regime_timeline(), config={'displayModeBar': False})
        ]),
    ]),

    # Recent signals table
    html.Div(style={'backgroundColor': 'white', 'borderRadius': '8px', 'padding': '16px',
                    'boxShadow': '0 1px 4px rgba(0,0,0,0.08)', 'marginBottom': '16px'}, children=[
        html.H3('Recent Signals (Last 10 Weeks)', style={'margin': '0 0 12px 0', 'color': '#2c3e50'}),
        dash_table.DataTable(
            data=recent.to_dict('records'),
            columns=[{'name': c, 'id': c} for c in recent.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '6px', 'fontSize': '13px', 'fontFamily': 'Arial'},
            style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[
                {'if': {'filter_query': '{Regime} = "Defensive"'}, 'backgroundColor': 'rgba(231,76,60,0.1)'},
                {'if': {'filter_query': '{Regime} = "Risk-On"'}, 'backgroundColor': 'rgba(39,174,96,0.1)'},
                {'if': {'row_index': len(recent) - 1}, 'fontWeight': 'bold'},
            ]
        )
    ]),

    # Parameter sweep table
    html.Div(style={'backgroundColor': 'white', 'borderRadius': '8px', 'padding': '16px',
                    'boxShadow': '0 1px 4px rgba(0,0,0,0.08)'}, children=[
        html.H3('Top 20 Parameter Configurations', style={'margin': '0 0 4px 0', 'color': '#2c3e50'}),
        html.P('Sorted by 26-week spread (Risk-On avg return minus Defensive avg return). Top row highlighted.',
               style={'color': '#7f8c8d', 'fontSize': '13px', 'margin': '0 0 12px 0'}),
        sweep_table()
    ]),
])

if __name__ == '__main__':
    print("\nDashboard running at: http://localhost:8050\n")
    app.run(debug=False, host='0.0.0.0', port=8050)
