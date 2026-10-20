"""La "tira de monitor" de cada encabezado de módulo (2026-10-19).

Cada módulo abre con SU señal -- ECG, EEG, respiración, EMG, tacograma --
sobre la retícula milimétrica del papel de registro, como la tira que
imprime un monitor de cabecera. Es la identidad visual de la app: el
elemento memorable; todo lo demás se mantiene sobrio.

Escalas reales donde aplica (retícula: 1 mm = 6 px de viewBox):
    ECG  25 mm/s,  5 mm/mV (ganancia N/2, estándar para trazos altos)
    EEG  30 mm/s
    Resp  5 mm/s
Es un esquema ilustrativo, no un registro: el `<title>` del SVG lo dice.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict

import numpy as np

from visualization.art import tokens as T
from visualization.art import waves
from visualization.art.svg import join, map_signal, mm_grid, path_from_xy, svg_root, text, trace

W, H = 2400.0, 64.0   # alto = alto CSS de .bc-strip: nunca se recorta en vertical
MM = 6.0                 # px de viewBox por milímetro
PX_PER_S_ECG = 25 * MM   # 25 mm/s
PX_PER_S_EEG = 30 * MM   # 30 mm/s
PX_PER_S_RESP = 5 * MM   # 5 mm/s


def _draw(d: str, *, color: str = T.TRACE, width: float = 2.0, opacity: float = 1.0) -> str:
    # pathLength="1": la animación de "trazado" (CSS .bc-draw en
    # inject_global_theme) no necesita conocer la longitud real del trazo.
    return trace(d, color=color, width=width, opacity=opacity,
                 extra='pathLength="1" class="bc-draw"')


def _ecg_path(y_mid: float, mv_px: float, hr: float = 72.0, x0: float = 0.0) -> str:
    duration = W / PX_PER_S_ECG
    t = np.linspace(0, duration, 3200)
    v = waves.ecg(t, waves.regular_r_times(duration, hr, first_s=0.42))
    xs, ys = map_signal(t, v, x0=x0, width=W, y_mid=y_mid, px_per_unit=mv_px, t_start=0, t_end=duration)
    return path_from_xy(xs, ys)


def _strip_ecg() -> str:
    return _draw(_ecg_path(y_mid=44, mv_px=5 * MM))


def _strip_academia() -> str:
    # ECG con las ondas rotuladas en un latido: la lección empieza aquí.
    hr = 72.0
    mid, gain = 50.0, 4 * MM
    body = [_draw(_ecg_path(y_mid=mid, mv_px=gain, hr=hr))]
    r = 0.42 + 2 * 60.0 / hr
    wm = waves.wave_map()
    for name, wave in (("P", wm["P"]), ("R", wm["R"]), ("T", wm["T"])):
        x = (r + wave.center_s) * PX_PER_S_ECG
        y = mid - wave.amp_mv * gain - 7
        label = "QRS" if name == "R" else name
        body.append(text(x, max(y, 13), label, size=12, fill=T.INK, anchor="middle", weight=700))
    return join(body)


def _strip_calipers() -> str:
    # ECG con el compás midiendo QT en un latido y RR entre dos latidos.
    hr = 72.0
    rr = 60.0 / hr
    first = 0.42
    mid, gain = 40.0, 4 * MM
    body = [_draw(_ecg_path(y_mid=mid, mv_px=gain, hr=hr))]
    iv = waves.beat_intervals()
    r = first + 3 * rr
    q_on = (r + iv["qrs_on"]) * PX_PER_S_ECG
    t_off = (r + iv["t_off"]) * PX_PER_S_ECG
    r1, r2 = (first + 5 * rr) * PX_PER_S_ECG, (first + 6 * rr) * PX_PER_S_ECG
    ink = T.INK_2
    for x in (q_on, t_off):
        body.append(f'<path d="M{x:.1f} 12V52" stroke="{ink}" stroke-width="1.2" stroke-opacity="0.8"/>')
    body.append(f'<path d="M{q_on:.1f} 52H{t_off:.1f}" stroke="{ink}" stroke-width="1.4"/>')
    body.append(text((q_on + t_off) / 2, 62, "QT", size=11, fill=ink, anchor="middle", weight=700))
    for x in (r1, r2):
        body.append(f'<path d="M{x:.1f} 50V58" stroke="{ink}" stroke-width="1.2"/>')
    body.append(f'<path d="M{r1:.1f} 54H{r2:.1f}" stroke="{ink}" stroke-width="1.4"/>')
    body.append(text((r1 + r2) / 2, 62.5, "RR", size=11, fill=ink, anchor="middle", weight=700))
    return join(body)


def _strip_eeg() -> str:
    duration = W / PX_PER_S_EEG
    t = np.linspace(0, duration, 4800)
    v = waves.eeg_alpha(t)
    xs, ys = map_signal(t, v, x0=0, width=W, y_mid=32, px_per_unit=13, t_start=0, t_end=duration)
    return _draw(path_from_xy(xs, ys), width=1.5)


def _strip_resp() -> str:
    duration = W / PX_PER_S_RESP
    t = np.linspace(0, duration, 1400)
    v = waves.breathing(t, rate_rpm=15) - 0.5
    xs, ys = map_signal(t, v, x0=0, width=W, y_mid=32, px_per_unit=40, t_start=0, t_end=duration)
    return _draw(path_from_xy(xs, ys), width=2.2)


def _strip_emg() -> str:
    duration = W / PX_PER_S_ECG
    t = np.linspace(0, duration, 5200)
    v = waves.emg_bursts(t, burst_times=(1.4, 4.0, 6.6, 9.4, 12.2, 14.8))
    v = np.clip(v, -2.6, 2.6)
    xs, ys = map_signal(t, v, x0=0, width=W, y_mid=32, px_per_unit=10, t_start=0, t_end=duration)
    return _draw(path_from_xy(xs, ys), width=1.1)


def _strip_hrv() -> str:
    n = 96
    rr = waves.rr_series(n)
    xs = np.linspace(14, W - 14, n)
    lo, hi = rr.min(), rr.max()
    ys = 54 - (rr - lo) / (hi - lo) * 42
    body = [_draw(path_from_xy(xs, ys), width=1.6, opacity=0.85)]
    body.extend(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{T.TRACE}" stroke="{T.STRIP_BG}" stroke-width="2"/>'
        for x, y in zip(xs, ys)
    )
    return join(body)


def _strip_ppg() -> str:
    duration = W / PX_PER_S_ECG
    t = np.linspace(0, duration, 3200)
    v = waves.ppg(t, waves.regular_r_times(duration, 75, first_s=0.2))
    xs, ys = map_signal(t, v, x0=0, width=W, y_mid=54, px_per_unit=40, t_start=0, t_end=duration)
    return _draw(path_from_xy(xs, ys), width=2.0)


def _strip_multi() -> str:
    # Tres carriles como en un monitor de cabecera: ECG, pulso, respiración.
    duration = W / PX_PER_S_ECG
    t = np.linspace(0, duration, 3200)
    r_times = waves.regular_r_times(duration, 76, first_s=0.3)
    ecg_v = waves.ecg(t, r_times)
    ppg_v = waves.ppg(t, r_times)
    resp_v = waves.breathing(t, rate_rpm=16) - 0.5
    lanes = (
        (ecg_v, 19, 11, 1.0, 1.6),
        (ppg_v, 44, 16, 0.8, 1.6),
        (resp_v, 55, 12, 0.6, 1.6),
    )
    body = []
    for v, y_mid, scale, op, width in lanes:
        xs, ys = map_signal(t, v, x0=0, width=W, y_mid=y_mid, px_per_unit=scale, t_start=0, t_end=duration)
        body.append(_draw(path_from_xy(xs, ys), width=width, opacity=op))
    return join(body)


def _strip_twin() -> str:
    duration = W / PX_PER_S_ECG
    t = np.linspace(0, duration, 3200)
    ecg_v = waves.ecg(t, waves.regular_r_times(duration, 72, first_s=0.42))
    resp_v = waves.breathing(t, rate_rpm=15) - 0.5
    xs, ys = map_signal(t, ecg_v, x0=0, width=W, y_mid=34, px_per_unit=22, t_start=0, t_end=duration)
    xr, yr = map_signal(t, resp_v, x0=0, width=W, y_mid=54, px_per_unit=12, t_start=0, t_end=duration)
    return join([_draw(path_from_xy(xr, yr), width=1.6, opacity=0.55), _draw(path_from_xy(xs, ys))])


def _strip_pipeline() -> str:
    # Estados del paciente guardados en el tiempo: nodos sobre una tendencia.
    xs = np.arange(60.0, W, 120.0)
    k = np.arange(xs.size)
    ys = 32 - 11 * np.sin(k / 1.7) - 4 * np.cos(k / 0.9)
    t_dense = np.linspace(xs[0], xs[-1], 400)
    y_dense = np.interp(t_dense, xs, ys)
    body = [f'<path d="M0 56H{W:.0f}" stroke="{T.INK_3}" stroke-opacity="0.45" stroke-width="1"/>',
            _draw(path_from_xy(t_dense, y_dense), width=1.6, opacity=0.8)]
    for x, y in zip(xs, ys):
        body.append(f'<path d="M{x:.1f} {y + 6:.1f}V56" stroke="{T.INK_3}" stroke-opacity="0.5" stroke-width="1"/>')
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{T.STRIP_BG}" stroke="{T.TRACE}" stroke-width="2"/>')
    return join(body)


STRIP_KINDS: Dict[str, tuple] = {
    # kind: (función, descripción para lectores de pantalla)
    "ecg": (_strip_ecg, "tira de ECG, ritmo sinusal a 72 lpm"),
    "academia": (_strip_academia, "tira de ECG con las ondas P, QRS y T rotuladas"),
    "calculators": (_strip_calipers, "tira de ECG con el compás midiendo QT y RR"),
    "eeg": (_strip_eeg, "EEG con ritmo alfa dominante, como con los ojos cerrados"),
    "respiratory": (_strip_resp, "curva respiratoria, 15 respiraciones por minuto"),
    "emg": (_strip_emg, "EMG de superficie con tres contracciones"),
    "hrv": (_strip_hrv, "tacograma: un punto por cada intervalo RR"),
    "biomarkers": (_strip_ppg, "onda de pulso con muesca dicrótica"),
    "multisensor": (_strip_multi, "tres carriles de monitor: ECG, pulso y respiración"),
    "twin": (_strip_twin, "ECG y respiración del gemelo digital"),
    "pipeline": (_strip_pipeline, "línea de tiempo de estados guardados del paciente"),
}


@lru_cache(maxsize=None)
def signal_strip_svg(kind: str) -> str:
    """SVG de la tira de monitor para `kind` (ver `STRIP_KINDS`); "" si no existe.
    Determinista, así que se calcula una vez por proceso (`lru_cache`)."""
    entry = STRIP_KINDS.get(kind)
    if entry is None:
        return ""
    fn, desc = entry
    body = join([
        f'<rect width="{W:.0f}" height="{H:.0f}" fill="{T.STRIP_BG}"/>',
        mm_grid(0, 0, W, H, MM, key="strip"),
        fn(),
    ])
    return svg_root(
        W, H, body,
        label=f"Esquema ilustrativo: {desc}",
        desc="Dibujo generado por código para identificar el módulo; no es un registro del paciente.",
        preserve="xMinYMid slice",
    )
