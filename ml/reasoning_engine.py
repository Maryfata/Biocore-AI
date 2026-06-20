"""Biomedical Reasoning Engine

Provides a rule- and score-based BiomedicalReasoningEngine that transforms
physiological HRV and spectral metrics into an explainable clinical-style
reasoning output.

This module is intentionally decoupled and does not modify existing code.
"""
from typing import Dict, Any, List, Optional
import math


class BiomedicalReasoningEngine:
    """Engine that converts physiological metrics into findings, hypotheses,
    differential diagnoses, risk estimate and an explanation.

    Expected inputs (keys, case-insensitive):
      BPM, SDNN, RMSSD, pNN50, LF, HF, LF/HF or LF_HF, Entropy
    """

    DEFAULT_THRESHOLDS = {
        "tachycardia_bpm": 100,
        "bradycardia_bpm": 50,
        "low_rmssd": 20,
        "low_sdnn": 30,
        "high_lf_hf": 2.5,
        "high_entropy": 1.5,
    }

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = dict(self.DEFAULT_THRESHOLDS)
        if thresholds:
            self.thresholds.update(thresholds)

    def _get(self, metrics: Dict[str, Any], keys: List[str], default=None):
        for k in keys:
            if k in metrics:
                return metrics[k]
            if k.lower() in metrics:
                return metrics[k.lower()]
            if k.upper() in metrics:
                return metrics[k.upper()]
        return default

    def analyze(self, metrics: Dict[str, float], ia_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform analysis and return structured reasoning output.

        Args:
            metrics: dictionary with physiological metrics.
            ia_result: optional dictionary with AI classifier outputs to incorporate.

        Returns:
            dict with keys: hallazgos, hipotesis, diagnosticos_diferenciales,
            riesgo, explicacion
        """
        m = {k: float(v) for k, v in metrics.items() if v is not None}

        bpm = self._get(m, ["BPM", "bpm"], default=None)
        sdnn = self._get(m, ["SDNN", "sdnn"], default=None)
        rmssd = self._get(m, ["RMSSD", "rmssd"], default=None)
        pnn50 = self._get(m, ["pNN50", "pnn50"], default=None)
        lf = self._get(m, ["LF", "lf"], default=None)
        hf = self._get(m, ["HF", "hf"], default=None)
        lf_hf = self._get(m, ["LF/HF", "LF_HF", "lf_hf", "lf/hf"], default=None)
        entropy = self._get(m, ["Entropy", "entropy"], default=None)

        findings = []
        hypotheses = []
        differentials = []

        # Basic BPM findings
        if bpm is not None:
            if bpm >= self.thresholds["tachycardia_bpm"]:
                findings.append(f"Taquicardia (BPM={bpm})")
            elif bpm <= self.thresholds["bradycardia_bpm"]:
                findings.append(f"Bradicardia (BPM={bpm})")
            else:
                findings.append(f"Frecuencia dentro de rango (BPM={bpm})")

        # HRV findings
        if rmssd is not None:
            if rmssd < self.thresholds["low_rmssd"]:
                findings.append(f"RMSSD reducido ({rmssd} ms) → pérdida de variabilidad vagal")
            else:
                findings.append(f"RMSSD en rango ({rmssd} ms)")

        if sdnn is not None:
            if sdnn < self.thresholds["low_sdnn"]:
                findings.append(f"SDNN reducido ({sdnn} ms) → baja variabilidad global")
            else:
                findings.append(f"SDNN en rango ({sdnn} ms)")

        # Spectral balance
        if lf_hf is not None:
            if lf_hf > self.thresholds["high_lf_hf"]:
                findings.append(f"Predominio simpático (LF/HF={lf_hf})")
            else:
                findings.append(f"Balance autonómico dentro de rango (LF/HF={lf_hf})")
        elif lf is not None and hf is not None and hf > 0:
            ratio = lf / hf
            if ratio > self.thresholds["high_lf_hf"]:
                findings.append(f"Predominio simpático (LF/HF≈{ratio:.2f})")

        if entropy is not None:
            if entropy > self.thresholds["high_entropy"]:
                findings.append(f"Alta entropía ({entropy}) → ritmo irregular o más caótico")
            else:
                findings.append(f"Entropía en rango ({entropy})")

        # Combine signals to form hypotheses
        score = 0.0
        # BPM contribution
        if bpm is not None and bpm >= self.thresholds["tachycardia_bpm"]:
            score += 1.0
        if rmssd is not None and rmssd < self.thresholds["low_rmssd"]:
            score += 1.0
        if sdnn is not None and sdnn < self.thresholds["low_sdnn"]:
            score += 0.8
        if lf_hf is not None and lf_hf > self.thresholds["high_lf_hf"]:
            score += 0.6
        if entropy is not None and entropy > self.thresholds["high_entropy"]:
            score += 1.2

        # Heuristic hypotheses
        if entropy is not None and entropy > self.thresholds["high_entropy"] and rmssd is not None and rmssd < self.thresholds["low_rmssd"]:
            hypotheses.append("Fibrilación auricular (FA) posible — ritmo irregular con baja variabilidad y alta entropía")
        if bpm is not None and bpm >= 140 and entropy is not None and entropy > self.thresholds["high_entropy"]:
            hypotheses.append("Taquiarritmia ventricular o taquicardia supraventricular — ritmo rápido y desorganizado")
        if rmssd is not None and rmssd < self.thresholds["low_rmssd"] and lf_hf is not None and lf_hf > 3.0:
            hypotheses.append("Actividad simpática elevada, posible respuesta a estrés agudo o arritmia ectópica")

        # AI classifier integration: reinforce or contradict
        if ia_result:
            label = ia_result.get("label") or ia_result.get("prediction")
            prob = ia_result.get("probability") or ia_result.get("score")
            if label:
                findings.append(f"Resultado IA: {label} (score={prob})")
                # If IA predicts AFib and entropy high, increase confidence
                if isinstance(label, str) and "af" in label.lower() and entropy is not None and entropy > self.thresholds["high_entropy"]:
                    hypotheses.append("IA apoya diagnóstico de Fibrilación Auricular")

        # Differential diagnoses (educational)
        if any("Fibrilación" in h or "FA" in h for h in hypotheses):
            differentials.extend(["Fibrilación auricular paroxística", "Taquicardia supraventricular", "Flutter auricular"]) 
        else:
            # generic differentials based on findings
            if rmssd is not None and rmssd < self.thresholds["low_rmssd"]:
                differentials.extend(["Episodios de estrés agudo", "Uso de estimulantes (cafeína, simpatomiméticos)", "Afección autonómica"]) 

        # Risk estimation (simple mapping)
        risk_score = score
        if bpm is not None and bpm >= 140:
            risk_score += 1.5
        if entropy is not None and entropy > self.thresholds["high_entropy"]:
            risk_score += 1.0

        if risk_score >= 3.0:
            risk = "alto"
        elif risk_score >= 1.5:
            risk = "moderado"
        else:
            risk = "bajo"

        # Build explanation
        explanation_lines = []
        explanation_lines.append(f"Puntuación heurística: {risk_score:.2f} (umbrales adaptativos)")
        explanation_lines.append("Se combinan signos vitales, HRV y espectro para generar hipótesis clínicas explicables.")
        if findings:
            explanation_lines.append("Hallazgos clave: " + "; ".join(findings[:4]))

        explanation = " ".join(explanation_lines)

        result = {
            "hallazgos": findings,
            "hipotesis": hypotheses,
            "diagnosticos_diferenciales": differentials,
            "riesgo": risk,
            "explicacion": explanation,
        }

        return result


if __name__ == "__main__":
    # Quick demo when run directly
    engine = BiomedicalReasoningEngine()
    demo = engine.analyze({"BPM": 112, "RMSSD": 18, "LF/HF": 3.5, "Entropy": 2.0}, ia_result={"label": "AFib", "probability": 0.82})
    import json
    print(json.dumps(demo, indent=2, ensure_ascii=False))
