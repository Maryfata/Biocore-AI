"""Láminas educativas del Atlas visual de BIOCORE AI (2026-10-19).

Cada lámina = un dibujo SVG + una explicación en HTML + su fuente. El texto
largo vive en HTML (no dentro del SVG) para que se lea igual en un teléfono
que en un monitor: el SVG se escala, el HTML se reacomoda.

Honestidad (CLAUDE.md, reglas 3 y 4): las láminas son esquemas, no datos
del paciente, y lo dicen. Los valores que rotulan son o bien MEDIDOS sobre
el propio modelo dibujado (`waves.beat_intervals()`), o bien constantes del
código que la app ya usa para calcular (`BAND_LIMITS_HZ` del analizador EEG,
el generador del Respiratory Lab, las fórmulas de HRV de `render_hrv_page`),
o rangos de referencia con su cita. Nada se escribe "a ojo".

Algunas láminas aceptan un resaltado (`highlight=`, `active=`, `selected=`,
`dominant=`) para responder a lo que la persona elige en el laboratorio:
la onda P/QRS/T del ECG Lab, la estructura de conducción, los canales EEG
en uso, la banda dominante calculada, el patrón respiratorio elegido.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from visualization.art import tokens as T
from visualization.art import waves
from visualization.art.svg import (esc, fmt, join, map_signal, mm_grid, path_from_xy, smooth_path,
                                   svg_root, text, trace)

# ═══════════════════════════════════════════════════════════════════════
# Fuentes citadas por las láminas (las clínicas se importan de donde la app
# ya las usa para calcular -- una sola fuente por cita).
# ═══════════════════════════════════════════════════════════════════════

try:  # citas que ya viven en la capa clínica
    from clinical.calculators import ECG_PAPER_CITATION, QRS_AXIS_CITATION, QTC_THRESHOLDS_CITATION
except Exception:  # pragma: no cover - la app siempre tiene clinical/
    ECG_PAPER_CITATION = "Kligfield P, et al. Circulation 2007;115:1306–1324"
    QRS_AXIS_CITATION = "Surawicz B, Knilans TK. Chou's Electrocardiography in Clinical Practice, 6th ed. 2008"
    QTC_THRESHOLDS_CITATION = "Rautaharju PM, Surawicz B, Gettes LS. Circulation 2009;119:e241–e250"

CHOU_CITATION = (
    "Surawicz B, Knilans TK. Chou's Electrocardiography in Clinical Practice, 6th ed. "
    "Saunders Elsevier; 2008 (PR del adulto 0.12–0.20 s)"
)
QRS_WIDTH_CITATION = (
    "Surawicz B, Childers R, Deal BJ, Gettes LS. AHA/ACCF/HRS Recommendations for the "
    "Standardization and Interpretation of the Electrocardiogram, Part III. Circulation "
    "2009;119:e235–e240 (QRS ≥ 120 ms: bloqueo completo de rama en el adulto)"
)
GUYTON_CITATION = "Hall JE, Hall ME. Guyton y Hall. Tratado de fisiología médica, 14.ª ed. Elsevier; 2021"
JASPER_CITATION = (
    "Jasper HH. The ten-twenty electrode system of the International Federation. "
    "Electroencephalogr Clin Neurophysiol 1958;10:371–375"
)
ACNS_NOMENCLATURE_CITATION = (
    "Acharya JN, Hani A, Cheek J, Thirumala P, Tsuchida TN. American Clinical Neurophysiology "
    "Society Guideline 2: Guidelines for Standard Electrode Position Nomenclature. "
    "J Clin Neurophysiol 2016;33:308–311 (T7/T8/P7/P8 en lugar de T3/T4/T5/T6)"
)
KANE_GLOSSARY_CITATION = (
    "Kane N, Acharya J, Benickzy S, et al. A revised glossary of terms most commonly used by "
    "clinical electroencephalographers. Clin Neurophysiol Pract 2017;2:170–185"
)
AASM_CITATION = (
    "Berry RB, et al. The AASM Manual for the Scoring of Sleep and Associated Events. "
    "American Academy of Sleep Medicine (definiciones de apnea central, obstructiva y "
    "respiración de Cheyne-Stokes)"
)
TASK_FORCE_HRV_CITATION = (
    "Task Force of the European Society of Cardiology and the North American Society of Pacing "
    "and Electrophysiology. Heart rate variability: standards of measurement, physiological "
    "interpretation and clinical use. Circulation 1996;93:1043–1065"
)
DE_LUCA_CITATION = (
    "De Luca CJ. The use of surface electromyography in biomechanics. "
    "J Appl Biomech 1997;13:135–163"
)
HENNEMAN_CITATION = (
    "Henneman E. Relation between size of neurons and their susceptibility to discharge. "
    "Science 1957;126:1345–1347"
)


# ═══════════════════════════════════════════════════════════════════════
# Estructura común
# ═══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Plate:
    key: str
    title: str
    topic: str                      # agrupa el Atlas: Corazón, Cerebro, ...
    summary: str                    # una línea, para el índice del Atlas
    sources: Tuple[str, ...]
    build: Callable[..., Tuple[str, str]]  # (**kw) -> (svg, details_html)


def _ul(items: Iterable[str], cls: str = "") -> str:
    cls_attr = f' class="{cls}"' if cls else ""
    return f"<ul{cls_attr}>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def _ol(items: Iterable[str], highlight_index: Optional[int] = None) -> str:
    rows = []
    for i, item in enumerate(items):
        cls = ' class="bc-on"' if highlight_index == i else ""
        rows.append(f"<li{cls}>{item}</li>")
    return '<ol class="bc-steps">' + "".join(rows) + "</ol>"


def _ms(seconds: float) -> str:
    return f"{seconds * 1000:.0f} ms"


def _marker(x: float, y: float, n: int, *, on: bool = False, r: float = 13) -> str:
    """Círculo numerado (para láminas cuyos pasos SÍ son una secuencia)."""
    fill = T.TRACE if on else T.PANEL
    stroke = T.TRACE if on else T.INK_3
    ink = T.BACKGROUND if on else T.INK
    return (
        f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{r:g}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        + text(x, y + 5, n, size=14, fill=ink, anchor="middle", weight=700)
    )


# ═══════════════════════════════════════════════════════════════════════
# 1. Anatomía del complejo ECG
# ═══════════════════════════════════════════════════════════════════════

ECG_HIGHLIGHTS = ("P", "PR", "QRS", "ST", "T", "QT")


def _ecg_complex(highlight: Optional[str] = None) -> Tuple[str, str]:
    mm = 16.0                       # px de viewBox por mm de papel
    px_s = 25 * mm                  # 25 mm/s
    px_mv = 10 * mm                 # 10 mm/mV
    t0, t1 = -0.32, 0.68            # ventana de 1 s alrededor de un latido
    x0, top = 24.0, 46.0
    paper_w = (t1 - t0) * px_s      # 400
    paper_h = 18 * mm               # de -0.4 a +1.4 mV
    base = top + 14 * mm            # línea isoeléctrica (0 mV)
    W, H = x0 * 2 + paper_w, 452.0

    iv = waves.beat_intervals()
    wm = waves.wave_map()

    def X(t: float) -> float:
        return x0 + (t - t0) * px_s

    spans = {
        "P": (iv["p_on"], iv["p_off"], "Onda P"),
        "PR": (iv["p_on"], iv["qrs_on"], "Intervalo PR"),
        "QRS": (iv["qrs_on"], iv["qrs_off"], "Complejo QRS"),
        "ST": (iv["qrs_off"], iv["t_on"], "Segmento ST"),
        "T": (iv["t_on"], iv["t_off"], "Onda T"),
        "QT": (iv["qrs_on"], iv["t_off"], "Intervalo QT"),
    }
    body: List[str] = [
        f'<rect x="{fmt(x0)}" y="{fmt(top)}" width="{fmt(paper_w)}" height="{fmt(paper_h)}" '
        f'rx="6" fill="{T.STRIP_BG}"/>',
        mm_grid(x0, top, paper_w, paper_h, mm, key="ecg-complex"),
    ]
    if highlight in spans:
        a, b, _ = spans[highlight]
        body.append(
            f'<rect x="{fmt(X(a))}" y="{fmt(top)}" width="{fmt(X(b) - X(a))}" height="{fmt(paper_h)}" '
            f'fill="{T.TRACE_FILL}"/>'
        )
    t = np.linspace(t0, t1, 900)
    v = waves.beat(t)
    xs, ys = map_signal(t, v, x0=x0, width=paper_w, y_mid=base, px_per_unit=px_mv, t_start=t0, t_end=t1)
    body.append(trace(path_from_xy(xs, ys), width=3))

    # Rótulos de las ondas (letra sobre el pico o bajo el valle).
    for name in ("P", "Q", "R", "S", "T"):
        w = wm[name]
        peak_y = base - float(waves.beat(np.array([w.center_s]))[0]) * px_mv
        y = peak_y - 12 if w.amp_mv > 0 else peak_y + 26
        dx = {"Q": -10, "S": 10}.get(name, 0)
        body.append(text(X(w.center_s) + dx, y, name, size=19, fill=T.INK, anchor="middle", weight=700,
                         family=T.FONT_HEAD))

    # Corchetes de intervalos debajo del papel: dos filas que no se pisan.
    rows = ((("PR", 0), ("ST", 0)), (("QRS", 1),), (("QT", 2),))
    for row in rows:
        for key, level in row:
            a, b, _ = spans[key]
            y = top + paper_h + 22 + level * 30
            on = key == highlight
            color = T.TRACE if on else T.INK_2
            width = 2.4 if on else 1.4
            body.append(
                f'<path d="M{fmt(X(a))} {fmt(y - 6)}V{fmt(y)}H{fmt(X(b))}V{fmt(y - 6)}" fill="none" '
                f'stroke="{color}" stroke-width="{width:g}" stroke-linejoin="round"/>'
            )
            label = f"{key} {_ms(b - a)}"
            body.append(text((X(a) + X(b)) / 2, y + 17, label, size=14, fill=color if on else T.INK_2,
                             anchor="middle", weight=700 if on else 500))

    # Escala: un cuadro grande = 0.20 s × 0.5 mV.
    sx, sy = x0 + 6, top - 12
    body.append(
        f'<path d="M{fmt(sx)} {fmt(sy)}H{fmt(sx + 5 * mm)}" stroke="{T.INK_3}" stroke-width="1.6"/>'
    )
    body.append(text(sx + 5 * mm + 8, sy + 5, "0.20 s", size=13, fill=T.INK_3))
    body.append(text(x0 + paper_w - 4, sy + 5, "25 mm/s, 10 mm/mV", size=13, fill=T.INK_3, anchor="end"))

    label = "Esquema ilustrativo: un latido de ECG sobre papel milimétrico con sus ondas e intervalos"
    if highlight in spans:
        label += f"; resaltado: {spans[highlight][2]}"
    svg = svg_root(W, H, join(body), label=label,
                   desc="Latido modelo a 60 lpm. Los intervalos rotulados se midieron sobre el propio dibujo.")

    qt = iv["QT"]
    rows_html = [
        f"<strong>PR {_ms(iv['PR'])}</strong>: del inicio de P al inicio del QRS; normal 120–200 ms.",
        f"<strong>QRS {_ms(iv['QRS'])}</strong>: despolarización ventricular; ≥ 120 ms sugiere bloqueo de rama.",
        f"<strong>QT {_ms(qt)}</strong> (a 60 lpm QTc = QT): prolongado si QTc ≥ 450 ms en hombres o ≥ 460 ms en mujeres.",
        "<strong>Papel</strong>: un cuadro pequeño = 0.04 s y 0.1 mV; uno grande = 0.20 s y 0.5 mV.",
    ]
    details = (
        "<p>Latido modelo a 60 lpm. Los valores se <em>midieron</em> sobre este dibujo, "
        "no se escribieron aparte.</p>" + _ul(rows_html)
    )
    return svg, details


# ═══════════════════════════════════════════════════════════════════════
# 2. Sistema de conducción cardiaco
# ═══════════════════════════════════════════════════════════════════════

CONDUCTION_PARTS = ("SA Node", "Atria", "AV Node", "His Bundle", "Purkinje")
_CONDUCTION_TEXT = (
    "<strong>Nodo SA</strong>: marcapasos natural; inicia la despolarización auricular (onda P).",
    "<strong>Aurículas</strong>: el impulso recorre ambas aurículas y llega al nodo AV.",
    "<strong>Nodo AV</strong>: retraso fisiológico para el llenado ventricular (segmento PR).",
    "<strong>Haz de His y ramas</strong>: conducen el impulso por el tabique (inicio del QRS).",
    "<strong>Fibras de Purkinje</strong>: distribución rápida que sincroniza la contracción ventricular (QRS).",
)


def _conduction(highlight: Optional[str] = None) -> Tuple[str, str]:
    W, H = 560.0, 428.0
    on_i = CONDUCTION_PARTS.index(highlight) if highlight in CONDUCTION_PARTS else None

    def style(i: int, base_w: float = 3.0) -> Tuple[str, float, float]:
        if on_i is None:
            return T.TRACE, base_w, 0.95
        return (T.TRACE, base_w + 1.6, 1.0) if i == on_i else (T.INK_3, base_w, 0.5)

    # Contorno frontal (lado derecho del paciente a la izquierda): aurículas
    # arriba, ventrículos abajo, ápex hacia la izquierda del paciente.
    outline = smooth_path([
        (196, 112), (150, 130), (126, 178), (130, 236), (160, 292), (210, 346), (268, 390),
        (326, 414), (368, 404), (394, 370), (410, 310), (412, 246), (400, 182), (372, 134),
        (322, 112), (264, 110), (230, 106),
    ])
    body: List[str] = [
        # Grandes vasos: vena cava superior y cayado aórtico (contorno).
        f'<path d="M178 118V50M212 112V50M178 50H212" fill="none" stroke="{T.LINE}" stroke-width="2"/>',
        f'<path d="M262 110C258 68 280 40 312 40C346 40 364 64 364 100M290 110C288 84 298 68 314 68'
        f'C330 68 338 80 338 104" fill="none" stroke="{T.LINE}" stroke-width="2"/>',
        text(195, 40, "VCS", size=14, fill=T.INK_3, anchor="middle"),
        text(312, 30, "Aorta", size=14, fill=T.INK_3, anchor="middle"),
        f'<path d="{outline}" fill="{T.STRIP_BG}" stroke="{T.INK_3}" stroke-width="2.4"/>',
        # Plano auriculoventricular, tabique interauricular e interventricular.
        f'<path d="M130 214C200 234 330 236 410 206" fill="none" stroke="{T.LINE}" stroke-width="2"/>',
        f'<path d="M262 110C264 150 266 182 268 216" fill="none" stroke="{T.LINE}" stroke-width="2"/>',
        f'<path d="M268 222C276 286 296 352 326 412" fill="none" stroke="{T.LINE}" stroke-width="2.4"/>',
        text(172, 196, "AD", size=15, fill=T.INK_3, anchor="middle", weight=600),
        text(352, 190, "AI", size=15, fill=T.INK_3, anchor="middle", weight=600),
        text(206, 300, "VD", size=15, fill=T.INK_3, anchor="middle", weight=600),
        text(366, 266, "VI", size=15, fill=T.INK_3, anchor="middle", weight=600),
    ]
    # 2 Vías internodales + haz de Bachmann (antes que los nodos: quedan debajo).
    c, w, op = style(1, 2.2)
    for d in ("M202 132C216 160 240 196 262 216", "M192 134C190 178 232 208 260 222",
              "M208 126C238 132 258 164 266 212", "M206 120C252 110 310 116 356 142"):
        body.append(trace(d, color=c, width=w, opacity=op))
    # 4 Haz de His, rama derecha, rama izquierda y fascículo anterior.
    c, w, op = style(3, 3.2)
    for d in ("M268 228L274 258", "M272 258C262 296 252 330 246 362",
              "M276 258C290 298 306 346 318 396", "M280 270C318 284 360 294 392 298"):
        body.append(trace(d, color=c, width=w, opacity=op))
    # 5 Fibras de Purkinje: ramificación fina bajo el endocardio.
    c, w, op = style(4, 1.6)
    for d in ("M246 362C228 352 210 338 196 318", "M246 362C258 380 274 392 292 400",
              "M236 346C214 324 190 296 172 262", "M318 396C346 384 368 358 384 322",
              "M330 406C356 398 380 374 394 336", "M392 298C400 270 402 242 398 218",
              "M304 404C320 410 340 410 356 402"):
        body.append(trace(d, color=c, width=w, opacity=op))
    # 1 Nodo SA y 3 Nodo AV (encima de las vías).
    for i, (x, y, rx, ry) in ((0, (198, 124, 12, 8)), (2, (266, 222, 11, 7))):
        c, w, op = style(i)
        body.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}" fill-opacity="{op:g}" '
                    f'stroke="{T.STRIP_BG}" stroke-width="2"/>')
    for i, (x, y) in enumerate(((158, 106), (318, 136), (230, 236), (300, 262), (424, 352))):
        body.append(_marker(x, y, i + 1, on=(on_i == i)))

    label = "Esquema ilustrativo: sistema de conducción del corazón en cinco pasos"
    if on_i is not None:
        label += f"; resaltado: paso {on_i + 1}"
    svg = svg_root(W, H, join(body), label=label,
                   desc="Vista frontal: AD/AI aurículas, VD/VI ventrículos; los números siguen el orden de activación.")
    details = "<p>El impulso sigue siempre el mismo orden:</p>" + _ol(_CONDUCTION_TEXT, on_i)
    return svg, details


# ═══════════════════════════════════════════════════════════════════════
# 3. Derivaciones precordiales V1-V6
# ═══════════════════════════════════════════════════════════════════════

def _precordial() -> Tuple[str, str]:
    W, H = 600.0, 500.0
    cx = 300.0
    body: List[str] = []
    # Torso, cuello y clavículas.
    body.append(
        f'<path d="M262 30C262 64 252 82 226 94C166 110 116 128 92 168C78 192 76 232 80 300'
        f'C84 380 94 440 102 492M338 30C338 64 348 82 374 94C434 110 484 128 508 168C522 192 524 232 520 300'
        f'C516 380 506 440 498 492" fill="none" stroke="{T.INK_3}" stroke-width="2.4" stroke-linecap="round"/>'
    )
    body.append(
        f'<path d="M300 112C262 102 222 106 172 122M300 112C338 102 378 106 428 122" fill="none" '
        f'stroke="{T.LINE}" stroke-width="3" stroke-linecap="round"/>'
    )
    # Silueta del corazón detrás del esternón (lo que "miran" las derivaciones).
    body.append(
        f'<path d="M262 236C238 236 226 262 232 290C240 328 280 360 322 378C342 386 362 372 372 350'
        f'C386 320 390 290 380 264C370 240 344 228 320 236C304 240 284 236 262 236Z" '
        f'fill="{T.TRACE}" fill-opacity="0.07" stroke="{T.TRACE}" stroke-opacity="0.35" stroke-width="1.6"/>'
    )
    # Costillas: arcos desde el esternón hacia afuera (2.ª a 7.ª).
    rib_y = {2: 150, 3: 184, 4: 218, 5: 252, 6: 286, 7: 320}
    for n, y in rib_y.items():
        drop = 30 + n * 4
        for side in (-1, 1):
            x_in = cx + side * 20
            x_out = cx + side * (172 + n * 4)
            body.append(
                f'<path d="M{fmt(x_in)} {fmt(y)}C{fmt(cx + side * 90)} {fmt(y - 6)} '
                f'{fmt(cx + side * 150)} {fmt(y + drop * 0.35)} {fmt(x_out)} {fmt(y + drop)}" '
                f'fill="none" stroke="{T.LINE}" stroke-width="1.6" stroke-opacity="0.8"/>'
            )
    # Esternón.
    body.append(
        f'<path d="M284 116H316L320 170L314 318L300 336L286 318L280 170Z" fill="{T.PANEL}" '
        f'stroke="{T.INK_3}" stroke-width="2"/>'
    )

    # Espacios intercostales: punto medio entre dos costillas, junto al esternón.
    ics4 = (rib_y[4] + rib_y[5]) / 2 + 2
    ics5 = (rib_y[5] + rib_y[6]) / 2 + 10
    x_mcl, x_aal, x_mal = 412.0, 470.0, 512.0
    # Líneas de referencia verticales (lado izquierdo del paciente).
    for x, lab in ((x_mcl, "LMC"), (x_aal, "LAA"), (x_mal, "LAM")):
        body.append(
            f'<path d="M{fmt(x)} 152V440" stroke="{T.INK_3}" stroke-opacity="0.55" stroke-width="1.4" '
            f'stroke-dasharray="5 6"/>'
        )
        body.append(text(x, 146, lab, size=14, fill=T.INK_2, anchor="middle", weight=600, halo=T.PANEL))
    body.append(text(84, ics4 + 5, "4.º EIC", size=14, fill=T.INK_3))
    body.append(text(84, ics5 + 5, "5.º EIC", size=14, fill=T.INK_3))
    body.append(
        f'<path d="M150 {fmt(ics4)}H262M150 {fmt(ics5)}H262" stroke="{T.INK_3}" stroke-opacity="0.35" '
        f'stroke-width="1.2"/>'
    )

    v1 = (cx - 32, ics4)
    v2 = (cx + 32, ics4)
    v4 = (x_mcl, ics5 + 18)
    v3 = ((v2[0] + v4[0]) / 2, (v2[1] + v4[1]) / 2)
    v5 = (x_aal, v4[1])
    v6 = (x_mal, v4[1])
    for name, (x, y) in (("V1", v1), ("V2", v2), ("V3", v3), ("V4", v4), ("V5", v5), ("V6", v6)):
        body.append(
            f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="16" fill="{T.TRACE}" stroke="{T.STRIP_BG}" stroke-width="3"/>'
        )
        body.append(text(x, y + 5, name, size=14, fill=T.BACKGROUND, anchor="middle", weight=700))
    body.append(text(300, 482, "Vista frontal; el lado izquierdo del paciente queda a tu derecha",
                     size=13, fill=T.INK_3, anchor="middle"))
    svg = svg_root(W, H, join(body),
                   label="Esquema ilustrativo: colocación de los electrodos precordiales V1 a V6",
                   desc="Torso de frente con costillas, esternón y las líneas medioclavicular, axilar anterior y axilar media.")
    details = (
        "<p>Las seis precordiales miran el corazón en un plano horizontal, de derecha a izquierda:</p>"
        + _ul([
            "<strong>V1</strong>: 4.º espacio intercostal (EIC), borde esternal derecho.",
            "<strong>V2</strong>: 4.º EIC, borde esternal izquierdo.",
            "<strong>V3</strong>: a la mitad entre V2 y V4.",
            "<strong>V4</strong>: 5.º EIC, línea medioclavicular (LMC).",
            "<strong>V5</strong>: línea axilar anterior (LAA), a la altura de V4.",
            "<strong>V6</strong>: línea axilar media (LAM), a la altura de V4.",
        ])
        + "<p>Un electrodo un espacio más arriba o más abajo cambia la morfología del QRS: es el error más común.</p>"
    )
    return svg, details


# ═══════════════════════════════════════════════════════════════════════
# 4. Sistema hexaxial y eje eléctrico
# ═══════════════════════════════════════════════════════════════════════

HEXAXIAL_LEADS = (("I", 0), ("II", 60), ("III", 120), ("aVF", 90), ("aVL", -30), ("aVR", -150))


def _polar(cx: float, cy: float, r: float, deg: float) -> Tuple[float, float]:
    rad = np.deg2rad(deg)
    return cx + r * np.cos(rad), cy + r * np.sin(rad)


def _sector(cx: float, cy: float, r: float, a0: float, a1: float) -> str:
    x0, y0 = _polar(cx, cy, r, a0)
    x1, y1 = _polar(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{fmt(cx)} {fmt(cy)}L{fmt(x0)} {fmt(y0)}A{fmt(r)} {fmt(r)} 0 {large} 1 {fmt(x1)} {fmt(y1)}Z"


def _hexaxial(axis_deg: Optional[float] = None) -> Tuple[str, str]:
    W, H = 600.0, 510.0
    cx, cy, r = 336.0, 250.0, 176.0
    body: List[str] = [
        f'<path d="{_sector(cx, cy, r, -30, 90)}" fill="{T.TRACE}" fill-opacity="0.16"/>',
        f'<path d="{_sector(cx, cy, r, -90, -30)}" fill="{T.INK_3}" fill-opacity="0.08"/>',
        f'<path d="{_sector(cx, cy, r, 90, 180)}" fill="{T.INK_3}" fill-opacity="0.08"/>',
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="none" stroke="{T.INK_3}" stroke-width="1.6"/>',
    ]
    for name, deg in HEXAXIAL_LEADS:
        xa, ya = _polar(cx, cy, r, deg)
        xb, yb = _polar(cx, cy, r, deg + 180)
        body.append(f'<path d="M{fmt(xb)} {fmt(yb)}L{fmt(xa)} {fmt(ya)}" stroke="{T.INK_2}" stroke-width="1.6"/>')
        body.append(f'<circle cx="{fmt(xa)}" cy="{fmt(ya)}" r="4" fill="{T.INK}"/>')
        lx, ly = _polar(cx, cy, r + 32, deg)
        sign = "+" if deg > 0 else ("−" if deg < 0 else "")
        body.append(text(lx, ly - 2, name, size=17, fill=T.INK, anchor="middle", weight=700, family=T.FONT_HEAD))
        body.append(text(lx, ly + 15, f"{sign}{abs(deg)}°", size=13, fill=T.INK_3, anchor="middle"))
    halo = T.PANEL
    # El rótulo del sector normal se aparta del eje marcado (si lo hay) para
    # que la flecha no lo tape.
    label_deg = 40.0
    if axis_deg is not None and np.isfinite(axis_deg) and abs(float(axis_deg) - label_deg) < 32:
        label_deg = 76.0 if float(axis_deg) < label_deg else 4.0
    lx, ly = _polar(cx, cy, r * 0.6, label_deg)
    body.append(text(lx, ly, "Eje normal", size=16, fill=T.INK, anchor="middle", weight=700,
                     family=T.FONT_HEAD, halo=halo))
    body.append(text(lx, ly + 20, "−30° a +90°", size=14, fill=T.INK_2, anchor="middle", halo=halo))
    body.append(text(cx + 70, cy - 118, "Desviación izquierda", size=14, fill=T.INK_2, anchor="middle", halo=halo))
    body.append(text(cx - 100, cy + 112, "Desviación derecha", size=14, fill=T.INK_2, anchor="middle", halo=halo))
    if axis_deg is not None and np.isfinite(axis_deg):
        xa, ya = _polar(cx, cy, r - 14, float(axis_deg))
        body.append(
            f'<path d="M{fmt(cx)} {fmt(cy)}L{fmt(xa)} {fmt(ya)}" stroke="{T.TRACE}" stroke-width="5" '
            f'stroke-linecap="round"/>'
        )
        body.append(f'<circle cx="{fmt(xa)}" cy="{fmt(ya)}" r="7" fill="{T.TRACE}"/>')
    # Triángulo de Einthoven (recuadro, abajo a la izquierda): de dónde
    # salen I, II y III.
    ra, la, ll = (34.0, 376.0), (134.0, 376.0), (84.0, 462.0)
    body.append(
        f'<path d="M{fmt(ra[0])} {fmt(ra[1])}L{fmt(la[0])} {fmt(la[1])}L{fmt(ll[0])} {fmt(ll[1])}Z" '
        f'fill="none" stroke="{T.INK_3}" stroke-width="1.8"/>'
    )
    for lab, (x, y), dy in (("BD", ra, -11), ("BI", la, -11), ("PI", ll, 22)):
        body.append(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="5" fill="{T.TRACE}"/>')
        body.append(text(x, y + dy, lab, size=13, fill=T.INK_2, anchor="middle", weight=600))
    for lab, x, y in (("I", 84, 368), ("II", 48, 426), ("III", 122, 426)):
        body.append(text(x, y, lab, size=15, fill=T.INK, anchor="middle", weight=700, family=T.FONT_HEAD))
    body.append(text(84, 502, "Triángulo de Einthoven", size=13, fill=T.INK_3, anchor="middle"))

    label = "Esquema ilustrativo: sistema hexaxial de las derivaciones de miembros y eje eléctrico normal"
    if axis_deg is not None:
        label += f"; eje marcado en {axis_deg:.0f}°"
    svg = svg_root(W, H, join(body), label=label,
                   desc="0° apunta a la izquierda del paciente y +90° hacia los pies.")
    details = (
        "<p>Las seis derivaciones de miembros forman una rueda: 0° es la izquierda del paciente y +90°, "
        "los pies. BD, BI y PI son los electrodos del brazo derecho, brazo izquierdo y pierna izquierda.</p>"
        + _ul([
            "<strong>Eje normal</strong> del adulto: −30° a +90°.",
            "<strong>Desviación izquierda</strong>: más negativo que −30°.",
            "<strong>Desviación derecha</strong>: más allá de +90°.",
            "Atajo: si el QRS es positivo en I y en aVF, el eje cae entre 0° y +90°.",
        ])
    )
    return svg, details


# ═══════════════════════════════════════════════════════════════════════
# 5. Sistema 10-20 del EEG
# ═══════════════════════════════════════════════════════════════════════

def _ring(r: float, deg: float) -> Tuple[float, float]:
    rad = np.deg2rad(deg)
    return r * np.cos(rad), r * np.sin(rad)


# Coordenadas normalizadas (radio de la cabeza = 1; arriba = nariz).
EEG_1020_POSITIONS: Dict[str, Tuple[float, float]] = {
    "Fp1": _ring(0.8, -108), "Fp2": _ring(0.8, -72),
    "F7": _ring(0.8, -144), "F8": _ring(0.8, -36),
    "T7": _ring(0.8, 180), "T8": _ring(0.8, 0),
    "P7": _ring(0.8, 144), "P8": _ring(0.8, 36),
    "O1": _ring(0.8, 108), "O2": _ring(0.8, 72),
    "F3": (-0.33, -0.41), "F4": (0.33, -0.41),
    "C3": (-0.4, 0.0), "C4": (0.4, 0.0),
    "P3": (-0.33, 0.41), "P4": (0.33, 0.41),
    "Fz": (0.0, -0.4), "Cz": (0.0, 0.0), "Pz": (0.0, 0.4),
}
EEG_DEFAULT_ACTIVE = ("Fp1", "Fp2", "C3", "C4")   # los que dibuja EEG Neuro Lab


def _eeg_1020(active: Sequence[str] = EEG_DEFAULT_ACTIVE) -> Tuple[str, str]:
    W, H = 520.0, 540.0
    cx, cy, R = 260.0, 286.0, 214.0
    active = tuple(a for a in active if a in EEG_1020_POSITIONS)
    body: List[str] = [
        # Nariz y orejas, luego la cabeza encima.
        f'<path d="M236 {fmt(cy - R + 6)}L260 {fmt(cy - R - 30)}L284 {fmt(cy - R + 6)}" fill="{T.PANEL}" '
        f'stroke="{T.INK_3}" stroke-width="2.4" stroke-linejoin="round"/>',
        f'<path d="M{fmt(cx - R + 4)} {fmt(cy - 34)}C{fmt(cx - R - 26)} {fmt(cy - 30)} {fmt(cx - R - 26)} '
        f'{fmt(cy + 30)} {fmt(cx - R + 4)} {fmt(cy + 34)}" fill="{T.PANEL}" stroke="{T.INK_3}" stroke-width="2.4"/>',
        f'<path d="M{fmt(cx + R - 4)} {fmt(cy - 34)}C{fmt(cx + R + 26)} {fmt(cy - 30)} {fmt(cx + R + 26)} '
        f'{fmt(cy + 30)} {fmt(cx + R - 4)} {fmt(cy + 34)}" fill="{T.PANEL}" stroke="{T.INK_3}" stroke-width="2.4"/>',
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(R)}" fill="{T.PANEL}" stroke="{T.INK_3}" stroke-width="2.4"/>',
        # Líneas de referencia: nasion-inion, preauricular y el anillo del 10 %.
        f'<path d="M{fmt(cx)} {fmt(cy - R)}V{fmt(cy + R)}M{fmt(cx - R)} {fmt(cy)}H{fmt(cx + R)}" '
        f'stroke="{T.LINE}" stroke-width="1.2"/>',
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(0.8 * R)}" fill="none" stroke="{T.LINE}" stroke-width="1.2"/>',
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(0.4 * R)}" fill="none" stroke="{T.LINE}" '
        f'stroke-width="1" stroke-opacity="0.7"/>',
        text(cx, cy - R - 40, "Nasion", size=14, fill=T.INK_3, anchor="middle"),
        text(cx, cy + R + 26, "Inion", size=14, fill=T.INK_3, anchor="middle"),
        text(cx - R - 18, cy + 58, "A1", size=14, fill=T.INK_3, anchor="middle"),
        text(cx + R + 18, cy + 58, "A2", size=14, fill=T.INK_3, anchor="middle"),
    ]
    for name, (nx, ny) in EEG_1020_POSITIONS.items():
        x, y = cx + nx * R, cy + ny * R
        on = name in active
        fill = T.TRACE if on else T.STRIP_BG
        stroke = T.TRACE if on else T.INK_3
        ink = T.BACKGROUND if on else T.INK_2
        body.append(
            f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="21" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
        body.append(text(x, y + 5, name, size=14, fill=ink, anchor="middle", weight=700 if on else 600))
    listed = ", ".join(active) if active else "ninguno"
    svg = svg_root(
        W, H, join(body),
        label=f"Esquema ilustrativo: sistema internacional 10-20 visto desde arriba; resaltados {listed}",
        desc="Nariz arriba. Números impares a la izquierda, pares a la derecha, z en la línea media.",
    )
    details = (
        f"<p>Resaltados (cian): <strong>{esc(listed)}</strong>, los canales que dibuja este laboratorio.</p>"
        + _ul([
            "Letras: <strong>Fp</strong> frontopolar, <strong>F</strong> frontal, <strong>C</strong> central, "
            "<strong>T</strong> temporal, <strong>P</strong> parietal, <strong>O</strong> occipital.",
            "Números <strong>impares</strong> a la izquierda, <strong>pares</strong> a la derecha; "
            "<strong>z</strong> (cero) en la línea media.",
            "«10-20»: los electrodos se separan 10 % o 20 % de las distancias nasion–inion y entre los "
            "puntos preauriculares, así el mapa se adapta a cada cabeza.",
            "T7/T8/P7/P8 son los nombres actuales de T3/T4/T5/T6.",
        ])
    )
    return svg, details


# ═══════════════════════════════════════════════════════════════════════
# 6. Bandas del EEG
# ═══════════════════════════════════════════════════════════════════════

try:
    from src.signals.eeg.eeg_analyzer import BAND_CLASSIFICATION, BAND_LIMITS_HZ
except Exception:  # pragma: no cover
    BAND_LIMITS_HZ = {"delta": (0.5, 3.5), "theta": (4.0, 7.5), "alpha": (8.0, 12.0),
                      "beta": (13.0, 30.0), "gamma": (30.0, 45.0)}
    BAND_CLASSIFICATION = {}

_BAND_DRAW = (
    # banda, letra, nombre, frecuencia dibujada (Hz), amplitud relativa
    ("delta", "δ", "Delta", 2.0, 1.00),
    ("theta", "θ", "Theta", 6.0, 0.78),
    ("alpha", "α", "Alfa", 10.0, 0.62),
    ("beta", "β", "Beta", 20.0, 0.36),
    ("gamma", "γ", "Gamma", 38.0, 0.20),
)


def _eeg_bands(dominant: Optional[str] = None) -> Tuple[str, str]:
    row_h, top = 86.0, 18.0
    x_wave, w_wave = 150.0, 250.0
    W, H = 600.0, top + row_h * len(_BAND_DRAW) + 26
    body: List[str] = []
    t = np.linspace(0, 1.0, 700)
    for i, (band, letter, name, f_hz, amp) in enumerate(_BAND_DRAW):
        y0 = top + i * row_h
        mid = y0 + row_h / 2
        on = dominant == band
        dim = dominant is not None and not on
        if on:
            body.append(f'<rect x="4" y="{fmt(y0 + 4)}" width="{fmt(W - 8)}" height="{fmt(row_h - 8)}" rx="10" '
                        f'fill="{T.TRACE_FILL}"/>')
        body.append(text(28, mid + 12, letter, size=36, fill=T.TRACE if on else T.INK, anchor="middle",
                         weight=600, family=T.FONT_BODY))
        body.append(text(56, mid - 4, name, size=17, fill=T.INK, weight=700, family=T.FONT_HEAD))
        lo, hi = BAND_LIMITS_HZ.get(band, (0, 0))
        body.append(text(56, mid + 18, f"{lo:g}–{hi:g} Hz", size=14, fill=T.INK_2))
        v = waves.eeg_band(t, f_hz, amp, seed=17 + i)
        xs, ys = map_signal(t, v, x0=x_wave, width=w_wave, y_mid=mid, px_per_unit=30, t_start=0, t_end=1.0)
        body.append(trace(path_from_xy(xs, ys), width=2 if not dim else 1.6, opacity=0.45 if dim else 1.0))
        state = BAND_CLASSIFICATION.get(band, "")
        if state:
            short = state.split(" / ")[0]
            body.append(text(W - 14, mid + 5, short, size=13, fill=T.INK_2, anchor="end"))
        if i < len(_BAND_DRAW) - 1:
            body.append(f'<path d="M16 {fmt(y0 + row_h)}H{fmt(W - 16)}" stroke="{T.LINE}" stroke-opacity="0.5"/>')
    body.append(text(x_wave, H - 6, "1 segundo de cada ritmo", size=13, fill=T.INK_3))
    label = "Esquema ilustrativo: las cinco bandas del EEG, de la más lenta a la más rápida"
    if dominant:
        label += f"; banda dominante resaltada: {dominant}"
    svg = svg_root(W, H, join(body), label=label,
                   desc="A mayor frecuencia, menor amplitud. Rangos en hercios tal como los integra el analizador.")
    rows = []
    for band, letter, name, _, _ in _BAND_DRAW:
        lo, hi = BAND_LIMITS_HZ.get(band, (0, 0))
        state = BAND_CLASSIFICATION.get(band, "")
        mark = " — <strong>dominante en tu señal</strong>" if dominant == band else ""
        rows.append(f"<strong>{letter} {name}</strong> ({lo:g}–{hi:g} Hz): {esc(state)}{mark}")
    details = (
        "<p>Rangos <em>exactos</em> en los que EEG Neuro Lab integra la potencia (método de Welch). "
        "Muchos textos redondean a 0.5–4, 4–8, 8–13 y 13–30 Hz.</p>" + _ul(rows)
    )
    return svg, details


# ═══════════════════════════════════════════════════════════════════════
# 7. Patrones respiratorios (con el generador del Respiratory Lab)
# ═══════════════════════════════════════════════════════════════════════

RESPIRATORY_PATTERNS = (
    # pattern_type del generador, nombre, descripción
    ("normal", "Normal", "Ciclos regulares; en el adulto, 12–20 respiraciones por minuto."),
    ("tachypnea", "Taquipnea", "Más rápida (> 20/min) y más superficial."),
    ("bradypnea", "Bradipnea", "Más lenta (< 12/min) y más profunda."),
    ("apnea_central", "Apnea central", "Sin flujo y sin esfuerzo: el centro respiratorio no da la orden."),
    ("apnea_obstructive", "Apnea obstructiva", "Sin flujo pero con esfuerzo: la vía aérea está cerrada."),
    ("cheyne_stokes", "Cheyne-Stokes", "Crescendo-decrescendo periódico (insuficiencia cardiaca, lesión del SNC)."),
    ("ataxic", "Atáxica (Biot)", "Irregular en ritmo y profundidad (lesión del tronco encefálico)."),
)
_RESP_DURATION_S = 60.0
_RESP_CACHE: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]] = {}


def respiratory_traces(pattern_type: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(t, flujo, esfuerzo torácico) de 60 s, del MISMO `RespiratorySignalGenerator`
    del Respiratory Lab. El generador usa el RNG global de NumPy; aquí se
    siembra y se RESTAURA el estado, para que el dibujo sea siempre el mismo
    sin alterar la aleatoriedad del resto de la app."""
    if pattern_type in _RESP_CACHE:
        return _RESP_CACHE[pattern_type]
    from src.signals.respiration import RespiratoryPattern, RespiratorySignalGenerator

    state = np.random.get_state()
    try:
        np.random.seed(20261019)
        sig = RespiratorySignalGenerator(sampling_rate=12).generate_respiration(
            duration=_RESP_DURATION_S, params=RespiratoryPattern(pattern_type=pattern_type),
        )
    finally:
        np.random.set_state(state)
    out = (np.asarray(sig["time"]), np.asarray(sig["airflow"]), np.asarray(sig["chest_wall"]))
    _RESP_CACHE[pattern_type] = out
    return out


def _resp_tile_svg(pattern_type: str, name: str, scales: Tuple[float, float]) -> str:
    W, H = 300.0, 112.0
    t, flow, chest = respiratory_traces(pattern_type)
    flow_px, chest_px = scales
    body = [
        f'<rect width="{W:.0f}" height="{H:.0f}" rx="8" fill="{T.STRIP_BG}"/>',
        mm_grid(0, 0, W, H, 6, key="resp-tile"),
        f'<path d="M0 40H{W:.0f}M0 86H{W:.0f}" stroke="{T.INK_3}" stroke-opacity="0.25"/>',
    ]
    xs, ys = map_signal(t, flow, x0=6, width=W - 12, y_mid=40, px_per_unit=flow_px)
    body.append(trace(path_from_xy(xs, ys), color=T.SERIES[0], width=1.8))
    xs, ys = map_signal(t, chest, x0=6, width=W - 12, y_mid=86, px_per_unit=chest_px)
    body.append(trace(path_from_xy(xs, ys), color=T.SERIES[1], width=1.8))
    return svg_root(W, H, join(body), label=f"Esquema ilustrativo: patrón {name}, flujo y esfuerzo en 60 s")


def respiratory_gallery_html(selected: Optional[str] = None) -> str:
    """Galería de los 7 patrones (HTML con un SVG por patrón; se acomoda en
    columnas según el ancho). `selected` = `pattern_type` resaltado."""
    traces_all = [respiratory_traces(p) for p, _, _ in RESPIRATORY_PATTERNS]
    flow_max = max(float(np.max(np.abs(f))) for _, f, _ in traces_all) or 1.0
    chest_max = max(float(np.max(np.abs(c))) for _, _, c in traces_all) or 1.0
    scales = (34.0 / flow_max, 22.0 / chest_max)
    tiles = []
    for pattern_type, name, desc in RESPIRATORY_PATTERNS:
        on = pattern_type == selected
        badge = '<span class="bc-chip">Elegido en el laboratorio</span>' if on else ""
        tiles.append(
            f'<div class="bc-tile{" bc-on" if on else ""}">'
            f'<div class="bc-tile-head"><strong>{esc(name)}</strong>{badge}</div>'
            f'{_resp_tile_svg(pattern_type, name, scales)}'
            f'<p>{esc(desc)}</p></div>'
        )
    legend = (
        '<div class="bc-legend">'
        f'<span><i style="background:{T.SERIES[0]}"></i>Flujo aéreo</span>'
        f'<span><i style="background:{T.SERIES[1]}"></i>Esfuerzo torácico</span>'
        '<span>60 s por patrón, misma escala en todos</span></div>'
    )
    return legend + '<div class="bc-tiles">' + "".join(tiles) + "</div>"


def _respiratory(selected: Optional[str] = None) -> Tuple[str, str]:
    details = (
        "<p>La clave de las apneas está en el segundo trazo: en la <strong>obstructiva</strong> el tórax "
        "sigue intentando respirar; en la <strong>central</strong> también se detiene. Una apnea dura "
        "10 s o más.</p>"
    )
    return respiratory_gallery_html(selected), details


# ═══════════════════════════════════════════════════════════════════════
# 8. Del ECG al tacograma (HRV)
# ═══════════════════════════════════════════════════════════════════════

TACHOGRAM_EXAMPLE_RR_MS = (820.0, 872.0, 905.0, 866.0, 828.0, 858.0)


def hrv_example_metrics(rr_ms: Sequence[float] = TACHOGRAM_EXAMPLE_RR_MS) -> Dict[str, float]:
    """SDNN y RMSSD del ejemplo, con las MISMAS fórmulas de `render_hrv_page()`."""
    rr = np.asarray(rr_ms, dtype=float)
    diffs = np.diff(rr)
    return {
        "sdnn": float(np.std(rr, ddof=1)),
        "rmssd": float(np.sqrt(np.mean(diffs ** 2))),
        "mean": float(np.mean(rr)),
    }


def _tachogram() -> Tuple[str, str]:
    W, H = 640.0, 420.0
    rr = np.asarray(TACHOGRAM_EXAMPLE_RR_MS) / 1000.0
    r_times = np.concatenate([[0.30], 0.30 + np.cumsum(rr)])
    t_end = r_times[-1] + 0.36
    x0, w = 30.0, W - 60
    px_s = w / t_end
    ecg_mid, ecg_top, ecg_h = 140.0, 40.0, 150.0
    body: List[str] = [
        f'<rect x="{fmt(x0)}" y="{fmt(ecg_top)}" width="{fmt(w)}" height="{fmt(ecg_h)}" rx="6" fill="{T.STRIP_BG}"/>',
        mm_grid(x0, ecg_top, w, ecg_h, px_s * 0.04, key="tacho"),
    ]
    t = np.linspace(0, t_end, 1500)
    v = waves.ecg(t, r_times)
    xs, ys = map_signal(t, v, x0=x0, width=w, y_mid=ecg_mid, px_per_unit=70, t_start=0, t_end=t_end)
    body.append(trace(path_from_xy(xs, ys), width=2.2))
    r_x = x0 + r_times * px_s
    r_y = ecg_mid - float(waves.beat(np.array([0.0]))[0]) * 70
    for x in r_x:
        body.append(f'<circle cx="{fmt(x)}" cy="{fmt(r_y)}" r="5" fill="{T.INK}" stroke="{T.STRIP_BG}" stroke-width="2"/>')
    for i, ms in enumerate(TACHOGRAM_EXAMPLE_RR_MS):
        a, b = r_x[i], r_x[i + 1]
        yb = ecg_top + 14
        body.append(f'<path d="M{fmt(a)} {fmt(yb + 6)}V{fmt(yb)}H{fmt(b)}V{fmt(yb + 6)}" fill="none" '
                    f'stroke="{T.INK_2}" stroke-width="1.4"/>')
        body.append(text((a + b) / 2, yb - 4, f"{ms:.0f}", size=13, fill=T.INK_2, anchor="middle", weight=600))
    body.append(text(x0, 28, "ECG: cada punto blanco es una onda R; entre dos R, el intervalo RR en ms",
                     size=13, fill=T.INK_3))

    # Tacograma: un punto por intervalo, alineado bajo su corchete.
    g_top, g_h = 250.0, 130.0
    lo, hi = 780.0, 940.0
    body.append(f'<path d="M{fmt(x0)} {fmt(g_top + g_h)}H{fmt(x0 + w)}" stroke="{T.INK_3}" stroke-width="1.2"/>')
    for val in (800, 850, 900):
        yv = g_top + g_h - (val - lo) / (hi - lo) * g_h
        body.append(f'<path d="M{fmt(x0)} {fmt(yv)}H{fmt(x0 + w)}" stroke="{T.LINE}" stroke-opacity="0.45"/>')
        body.append(text(x0 + w + 4, yv + 4, f"{val}", size=12, fill=T.INK_3))
    pts = []
    for i, ms in enumerate(TACHOGRAM_EXAMPLE_RR_MS):
        xm = (r_x[i] + r_x[i + 1]) / 2
        ym = g_top + g_h - (ms - lo) / (hi - lo) * g_h
        pts.append((xm, ym))
        body.append(f'<path d="M{fmt(xm)} {fmt(ecg_top + ecg_h + 4)}V{fmt(ym - 9)}" stroke="{T.INK_3}" '
                    f'stroke-opacity="0.35" stroke-dasharray="3 5"/>')
    body.append(trace(path_from_xy([p[0] for p in pts], [p[1] for p in pts]), width=2))
    for xm, ym in pts:
        body.append(f'<circle cx="{fmt(xm)}" cy="{fmt(ym)}" r="6" fill="{T.TRACE}" stroke="{T.PANEL}" stroke-width="2"/>')
    body.append(text(x0, g_top - 10, "Tacograma: RR (ms) latido a latido", size=13, fill=T.INK_3))
    svg = svg_root(W, H, join(body),
                   label="Esquema ilustrativo: cómo los intervalos RR del ECG forman el tacograma de HRV",
                   desc="Seis intervalos RR de ejemplo, con la arritmia sinusal respiratoria típica.")
    m = hrv_example_metrics()
    details = (
        "<p>La HRV no mide la frecuencia cardiaca: mide <em>cuánto cambia</em> el intervalo entre latidos. "
        "En este ejemplo de seis intervalos:</p>"
        + _ul([
            f"<strong>SDNN {m['sdnn']:.0f} ms</strong>: desviación estándar de todos los RR (variabilidad global).",
            f"<strong>RMSSD {m['rmssd']:.0f} ms</strong>: raíz cuadrática media de las diferencias sucesivas "
            "(tono vagal, corto plazo).",
            "Calculados con las mismas fórmulas que HRV Analysis aplica a tu serie.",
        ])
    )
    return svg, details


# ═══════════════════════════════════════════════════════════════════════
# 9. Unidad motora y EMG de superficie
# ═══════════════════════════════════════════════════════════════════════

def _motor_unit() -> Tuple[str, str]:
    W, H = 640.0, 430.0
    body: List[str] = []
    # Médula espinal en corte transversal (sustancia gris en mariposa).
    body.append(f'<circle cx="96" cy="112" r="62" fill="{T.PANEL}" stroke="{T.INK_3}" stroke-width="2.2"/>')
    # Sustancia gris en mariposa: astas posteriores (arriba, finas) y
    # anteriores (abajo, anchas), donde viven las motoneuronas.
    gray = smooth_path([
        (96, 98), (84, 82), (74, 84), (80, 100), (72, 112), (66, 128), (74, 142), (88, 140),
        (96, 128), (104, 140), (118, 142), (126, 128), (120, 112), (112, 100), (118, 84),
        (108, 82),
    ])
    body.append(f'<path d="{gray}" fill="{T.LINE}" fill-opacity="0.35" stroke="{T.INK_3}" stroke-width="1.4"/>')
    body.append(text(96, 194, "Médula espinal", size=14, fill=T.INK_3, anchor="middle"))
    # Motoneurona alfa en el asta anterior + axón por la raíz ventral.
    body.append(f'<circle cx="114" cy="132" r="8" fill="{T.TRACE}" stroke="{T.PANEL}" stroke-width="2"/>')
    axon = "M120 138C176 172 214 214 246 252C258 266 270 274 290 276"
    body.append(trace(axon, width=3))
    body.append(text(170, 150, "Motoneurona α", size=14, fill=T.INK, weight=600, halo=T.PANEL))
    body.append(text(196, 256, "Axón", size=14, fill=T.INK_2, halo=T.PANEL))

    # Piel y electrodos de superficie.
    body.append(f'<path d="M260 196H620" stroke="{T.INK_3}" stroke-width="2"/>')
    body.append(text(624, 190, "Piel", size=13, fill=T.INK_3, anchor="end"))
    for x in (380.0, 470.0):
        body.append(f'<rect x="{fmt(x - 18)}" y="184" width="36" height="12" rx="3" fill="{T.INK_2}"/>')
        body.append(f'<path d="M{fmt(x)} 184V120" stroke="{T.INK_3}" stroke-width="1.6"/>')
    body.append(text(425, 214, "Electrodos de superficie", size=13, fill=T.INK_2, anchor="middle"))

    # Fibras musculares: las de la unidad motora en cian, el resto tenues.
    unit_rows = {1, 3, 5, 6}
    branch_x = 290.0
    for i in range(8):
        y = 238 + i * 20
        on = i in unit_rows
        color = T.TRACE if on else T.LINE
        body.append(
            f'<path d="M300 {fmt(y)}H600" stroke="{color}" stroke-width="{9 if on else 8}" '
            f'stroke-linecap="round" stroke-opacity="{0.9 if on else 0.55}"/>'
        )
        if on:
            jx = 340 + (i % 3) * 60
            body.append(trace(f"M{fmt(branch_x)} 276C{fmt(branch_x + 20)} 276 {fmt(jx - 20)} {fmt(y)} {fmt(jx)} {fmt(y)}",
                              width=2))
            body.append(f'<circle cx="{fmt(jx)}" cy="{fmt(y)}" r="5" fill="{T.INK}" stroke="{T.PANEL}" stroke-width="2"/>')
    body.append(text(450, 414, "Fibras de una misma unidad motora (cian) entre otras fibras", size=13,
                     fill=T.INK_2, anchor="middle"))

    # Señal registrada: poca fuerza (pocas unidades) -> más fuerza (interferencia).
    box_x, box_y, box_w, box_h = 300.0, 30.0, 320.0, 86.0
    body.append(f'<rect x="{fmt(box_x)}" y="{fmt(box_y)}" width="{fmt(box_w)}" height="{fmt(box_h)}" rx="8" '
                f'fill="{T.STRIP_BG}"/>')
    rng = np.random.default_rng(42)
    t = np.linspace(0, 1, 900)
    env = 0.08 + 0.92 * np.clip((t - 0.15) / 0.7, 0, 1) ** 1.4
    emg = env * rng.standard_normal(t.size)
    xs, ys = map_signal(t, np.clip(emg, -2.4, 2.4), x0=box_x + 8, width=box_w - 16, y_mid=box_y + box_h / 2,
                        px_per_unit=15, t_start=0, t_end=1)
    body.append(trace(path_from_xy(xs, ys), width=1.1))
    body.append(text(box_x + 10, box_y - 6, "poca fuerza", size=13, fill=T.INK_3))
    body.append(text(box_x + box_w - 10, box_y - 6, "más fuerza", size=13, fill=T.INK_3, anchor="end"))
    body.append(f'<path d="M380 120V114M470 120V114" stroke="{T.INK_3}" stroke-width="1.6"/>')
    svg = svg_root(W, H, join(body),
                   label="Esquema ilustrativo: una unidad motora y cómo la registra la EMG de superficie",
                   desc="Motoneurona alfa de la médula, su axón y las fibras que inerva; arriba, la EMG al aumentar la fuerza.")
    details = (
        "<p>Una <strong>unidad motora</strong> es una motoneurona α y todas las fibras musculares que inerva. "
        "Para hacer más fuerza el sistema nervioso:</p>"
        + _ol([
            "<strong>Recluta más unidades</strong>, de las pequeñas a las grandes (principio del tamaño).",
            "<strong>Acelera la descarga</strong> de las que ya están activas.",
        ])
        + "<p>La EMG de superficie suma todos esos potenciales: por eso su amplitud RMS crece con la fuerza "
          "y, con la fatiga, el espectro se desplaza a frecuencias más bajas.</p>"
    )
    return svg, details


# ═══════════════════════════════════════════════════════════════════════
# Registro de láminas y Atlas
# ═══════════════════════════════════════════════════════════════════════

PLATES: Dict[str, Plate] = {
    p.key: p for p in (
        Plate("ecg_complex", "Anatomía del complejo ECG", "Corazón",
              "Ondas P, QRS y T; intervalos PR, QRS y QT sobre papel milimétrico.",
              (ECG_PAPER_CITATION, CHOU_CITATION, QRS_WIDTH_CITATION, QTC_THRESHOLDS_CITATION), _ecg_complex),
        Plate("conduction", "Sistema de conducción cardiaco", "Corazón",
              "Del nodo SA a las fibras de Purkinje, en orden de activación.",
              (GUYTON_CITATION,), _conduction),
        Plate("precordial", "Derivaciones precordiales V1–V6", "Corazón",
              "Dónde va cada electrodo del tórax y por qué importa.",
              (ECG_PAPER_CITATION,), _precordial),
        Plate("hexaxial", "Sistema hexaxial y eje eléctrico", "Corazón",
              "Las seis derivaciones de miembros y el eje normal −30° a +90°.",
              (QRS_AXIS_CITATION,), _hexaxial),
        Plate("tachogram", "Del ECG al tacograma", "Corazón",
              "Cómo los intervalos RR se convierten en variabilidad (HRV).",
              (TASK_FORCE_HRV_CITATION,), _tachogram),
        Plate("eeg_1020", "Sistema internacional 10-20", "Cerebro",
              "Mapa de electrodos del EEG visto desde arriba.",
              (JASPER_CITATION, ACNS_NOMENCLATURE_CITATION), _eeg_1020),
        Plate("eeg_bands", "Bandas del EEG", "Cerebro",
              "Delta, theta, alfa, beta y gamma: frecuencia, amplitud y estado.",
              ("Rangos: BAND_LIMITS_HZ de src/signals/eeg/eeg_analyzer.py (lo que mide EEG Neuro Lab)",
               KANE_GLOSSARY_CITATION), _eeg_bands),
        Plate("respiratory_patterns", "Patrones respiratorios", "Respiración",
              "Siete patrones con flujo y esfuerzo: normal, apneas, Cheyne-Stokes…",
              (AASM_CITATION, "Trazos: RespiratorySignalGenerator del Respiratory Lab (simulación)"),
              _respiratory),
        Plate("motor_unit", "Unidad motora y EMG de superficie", "Músculo",
              "De la motoneurona a la señal: reclutamiento y frecuencia de descarga.",
              (DE_LUCA_CITATION, HENNEMAN_CITATION), _motor_unit),
    )
}

ATLAS_TOPICS = ("Corazón", "Cerebro", "Respiración", "Músculo")
ATLAS: Tuple[str, ...] = tuple(PLATES.keys())


def get_plate(key: str) -> Plate:
    return PLATES[key]


def plate_figure_html(key: str, **kwargs) -> str:
    """<figure> completo de una lámina: etiqueta, dibujo, explicación y fuente.

    Pensado para `st.markdown(..., unsafe_allow_html=True)`: una sola línea
    lógica de HTML, sin líneas en blanco (ver la nota de `svg.py`). Las
    láminas son deterministas: se memorizan por (lámina, resaltado).
    """
    frozen = tuple(sorted((k, tuple(v) if isinstance(v, list) else v) for k, v in kwargs.items()))
    return _plate_figure_html_cached(key, frozen)


@lru_cache(maxsize=256)
def _plate_figure_html_cached(key: str, frozen_kwargs: tuple) -> str:
    plate = PLATES[key]
    art, details = plate.build(**dict(frozen_kwargs))
    sources = "".join(f"<li>{esc(s)}</li>" for s in plate.sources)
    return (
        f'<figure class="bc-plate" id="lamina-{plate.key}">'
        f'<div class="bc-plate-top"><span class="bc-chip">Esquema ilustrativo</span>'
        f'<span class="bc-plate-topic">{esc(plate.topic)}</span></div>'
        f'<div class="bc-plate-art">{art}</div>'
        f'<figcaption><strong class="bc-plate-title">{esc(plate.title)}</strong>{details}'
        f'<details class="bc-src"><summary>Fuentes</summary><ul>{sources}</ul></details></figcaption>'
        f"</figure>"
    )
