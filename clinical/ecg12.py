"""Clinical ECG 12-lead helpers: plotting and lead derivation helpers.

This module exposes `plot_ecg_12_leads` which accepts a mapping of lead names
(`'I','II','III','aVR','aVL','aVF','V1'..'V6'`) to numpy arrays and plots a
12-lead layout using Plotly when available, falling back to Matplotlib.

It also provides `derive_12_leads_from_3` for educational demonstration of
how limb leads relate (I, II, III, aVR, aVL, aVF) from three electrodes.
"""
from __future__ import annotations
from typing import Dict, Tuple, Optional
import numpy as np


def derive_12_leads_from_3(lead_I: np.ndarray, lead_II: np.ndarray) -> Dict[str, np.ndarray]:
    """Derive limb leads III and augmented leads from I and II.

    Assumes leads are aligned and same sampling rate. Returns dict with keys
    'I','II','III','aVR','aVL','aVF'.
    """
    if lead_I.shape != lead_II.shape:
        raise ValueError('lead_I and lead_II must have same shape')
    lead_III = lead_II - lead_I
    aVR = -(lead_I + lead_II) / 2.0
    aVL = lead_I - lead_II / 2.0
    aVF = lead_II - lead_I / 2.0
    return {'I': lead_I, 'II': lead_II, 'III': lead_III, 'aVR': aVR, 'aVL': aVL, 'aVF': aVF}


def plot_ecg_12_leads(signals: Dict[str, np.ndarray], fs: int = 250, title: Optional[str] = 'ECG 12 leads') -> object:
    """Plot 12-lead ECG grid. Returns the plotting figure object used.

    If Plotly is available, returns a plotly Figure; otherwise draws with
    Matplotlib and returns the Figure object.
    """
    # Try plotly first
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        lead_order = ['I','II','III','aVR','aVL','aVF','V1','V2','V3','V4','V5','V6']
        n = len(next(iter(signals.values())))
        t = np.arange(n) / float(fs)
        fig = make_subplots(rows=12, cols=1, shared_xaxes=True, vertical_spacing=0.005)
        for i, lead in enumerate(lead_order, start=1):
            y = signals.get(lead, np.zeros(n))
            fig.add_trace(go.Scatter(x=t, y=y, name=lead, line={'width':1}), row=i, col=1)
            fig.update_yaxes(title_text=lead, row=i, col=1)
        fig.update_layout(height=2400, title=title, showlegend=False)
        return fig
    except Exception:
        import matplotlib.pyplot as plt
        lead_order = ['I','II','III','aVR','aVL','aVF','V1','V2','V3','V4','V5','V6']
        n = len(next(iter(signals.values())))
        t = np.arange(n) / float(fs)
        fig, axes = plt.subplots(12, 1, sharex=True, figsize=(12, 18))
        for i, lead in enumerate(lead_order):
            y = signals.get(lead, np.zeros(n))
            axes[i].plot(t, y, linewidth=0.8)
            axes[i].set_ylabel(lead)
            axes[i].set_yticks([])
        axes[-1].set_xlabel('Time (s)')
        fig.suptitle(title)
        fig.tight_layout(rect=[0, 0.03, 1, 0.97])
        return fig
