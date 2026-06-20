import numpy as np
import plotly.graph_objects as go


def _find_peak_markers(time: np.ndarray, signal: np.ndarray, window: int = 15):
    if len(signal) < window * 2:
        return np.array([], dtype=int)

    peaks = []
    for idx in range(window, len(signal) - window):
        segment = signal[idx - window:idx + window]
        if signal[idx] == np.max(segment) and signal[idx] > np.mean(segment) + 0.25 * np.std(segment):
            peaks.append(idx)
    return np.array(peaks, dtype=int)


def make_ecg_figure(
    time: np.ndarray,
    signal: np.ndarray,
    fs: int,
    window_start: float,
    window_width: float,
    amplitude_scale: float,
    title: str = 'ECG Real-Time Monitor',
    show_annotations: bool = True
):
    window_end = min(time[-1], window_start + window_width)
    mask = (time >= window_start) & (time <= window_end)
    display_time = time[mask]
    display_signal = signal[mask] * amplitude_scale

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=display_time,
        y=display_signal,
        mode='lines',
        line=dict(color='#0072B2', width=2),
        name='ECG'
    ))

    if show_annotations:
        peak_indices = _find_peak_markers(display_time, display_signal)
        fig.add_trace(go.Scatter(
            x=display_time[peak_indices],
            y=display_signal[peak_indices],
            mode='markers',
            marker=dict(color='#D62828', size=8),
            name='R Peaks'
        ))

    fig.update_layout(
        title=title,
        template='plotly_dark',
        paper_bgcolor='#111111',
        plot_bgcolor='#111111',
        margin=dict(l=16, r=16, t=48, b=24),
        xaxis=dict(
            title='Tiempo (s)',
            gridcolor='#2A2A2A',
            zerolinecolor='#4B4B4B',
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            title='mV',
            gridcolor='#2A2A2A',
            zerolinecolor='#4B4B4B'
        ),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    fig.update_xaxes(showspikes=True, spikemode='across', spikecolor='#FFD700', spikesnap='cursor')
    fig.update_yaxes(showspikes=True, spikemode='across', spikecolor='#FFD700', spikesnap='cursor')
    return fig
