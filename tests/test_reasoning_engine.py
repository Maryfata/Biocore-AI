"""
Tests unitarios para el Biomedical Reasoning Engine.

Cubre:
- Validación de métricas
- Detectores de patrones
- Generadores de hipótesis
- Estimadores de riesgo
- Clasificadores de estado autonómico
- Motor principal de razonamiento
"""

import unittest
from biomedical.reasoning_engine import (
    HRVMetrics,
    RiskLevel,
    AutonomicState,
    PhysiologicalFinding,
    ClinicalHypothesis,
    DifferentialDiagnosis,
    EducationalRecommendation,
    PhysiologicalPatternDetector,
    ClinicalHypothesisGenerator,
    DifferentialDiagnosisGenerator,
    RiskEstimator,
    EducationalRecommendationGenerator,
    AutonomicStateClassifier,
    BiomedicalReasoningEngine,
)


class TestHRVMetrics(unittest.TestCase):
    """Tests para validación de HRVMetrics."""

    def test_valid_metrics(self):
        """Test con métricas válidas."""
        metrics = HRVMetrics(
            bpm=70,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
            ai_score=0.3,
        )
        is_valid, msg = metrics.validate()
        self.assertTrue(is_valid)
        self.assertEqual(msg, "Válido")

    def test_invalid_bpm_high(self):
        """Test con BPM demasiado alto."""
        metrics = HRVMetrics(
            bpm=350,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
        )
        is_valid, msg = metrics.validate()
        self.assertFalse(is_valid)
        self.assertIn("BPM", msg)

    def test_invalid_bpm_low(self):
        """Test con BPM demasiado bajo."""
        metrics = HRVMetrics(
            bpm=-5,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
        )
        is_valid, msg = metrics.validate()
        self.assertFalse(is_valid)

    def test_invalid_sdnn(self):
        """Test con SDNN inválido."""
        metrics = HRVMetrics(
            bpm=70,
            sdnn=2.5,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
        )
        is_valid, msg = metrics.validate()
        self.assertFalse(is_valid)
        self.assertIn("SDNN", msg)

    def test_invalid_pnn50(self):
        """Test con pNN50 inválido."""
        metrics = HRVMetrics(
            bpm=70,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=150,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
        )
        is_valid, msg = metrics.validate()
        self.assertFalse(is_valid)
        self.assertIn("pNN50", msg)

    def test_invalid_entropy(self):
        """Test con entropía inválida."""
        metrics = HRVMetrics(
            bpm=70,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=15,
        )
        is_valid, msg = metrics.validate()
        self.assertFalse(is_valid)
        self.assertIn("Entropía", msg)

    def test_invalid_ai_score(self):
        """Test con AI score inválido."""
        metrics = HRVMetrics(
            bpm=70,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
            ai_score=1.5,
        )
        is_valid, msg = metrics.validate()
        self.assertFalse(is_valid)
        self.assertIn("AI Score", msg)

    def test_to_dict(self):
        """Test conversión a diccionario."""
        metrics = HRVMetrics(
            bpm=70,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
        )
        result = metrics.to_dict()
        self.assertEqual(result["bpm"], 70)
        self.assertEqual(result["sdnn"], 0.1)


class TestPatternDetector(unittest.TestCase):
    """Tests para detectores de patrones."""

    def setUp(self):
        """Configuración inicial."""
        self.detector = PhysiologicalPatternDetector()

    def test_detect_tachycardia_mild(self):
        """Test detección de taquicardia leve."""
        metrics = HRVMetrics(
            bpm=105,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
        )
        findings = self.detector.detect_all(metrics)
        tachycardia_found = any("Taquicardia" in f.name for f in findings)
        self.assertTrue(tachycardia_found)

    def test_detect_tachycardia_severe(self):
        """Test detección de taquicardia severa."""
        metrics = HRVMetrics(
            bpm=140,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
        )
        findings = self.detector.detect_all(metrics)
        tachycardia_found = any("severa" in f.name.lower() for f in findings)
        self.assertTrue(tachycardia_found)

    def test_detect_bradycardia(self):
        """Test detección de bradicardia."""
        metrics = HRVMetrics(
            bpm=45,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
        )
        findings = self.detector.detect_all(metrics)
        bradycardia_found = any("Bradicardia" in f.name for f in findings)
        self.assertTrue(bradycardia_found)

    def test_detect_high_variability(self):
        """Test detección de alta variabilidad."""
        metrics = HRVMetrics(
            bpm=70,
            sdnn=0.2,
            rmssd=0.08,
            pnn50=35,
            lf=1.0,
            hf=2.5,
            lf_hf=0.4,
            entropy=4.5,
        )
        findings = self.detector.detect_all(metrics)
        high_var_found = any("Alta" in f.name for f in findings)
        self.assertTrue(high_var_found)

    def test_detect_low_variability(self):
        """Test detección de baja variabilidad."""
        metrics = HRVMetrics(
            bpm=85,
            sdnn=0.03,
            rmssd=0.01,
            pnn50=5,
            lf=3.0,
            hf=1.0,
            lf_hf=3.0,
            entropy=1.5,
        )
        findings = self.detector.detect_all(metrics)
        low_var_found = any("Baja" in f.name for f in findings)
        self.assertTrue(low_var_found)

    def test_detect_sympathetic_dominance(self):
        """Test detección de dominancia simpática."""
        metrics = HRVMetrics(
            bpm=100,
            sdnn=0.08,
            rmssd=0.03,
            pnn50=10,
            lf=4.0,
            hf=1.0,
            lf_hf=4.0,
            entropy=2.5,
        )
        findings = self.detector.detect_all(metrics)
        symp_found = any("Simpática" in f.name for f in findings)
        self.assertTrue(symp_found)

    def test_detect_parasympathetic_dominance(self):
        """Test detección de dominancia parasimpática."""
        metrics = HRVMetrics(
            bpm=60,
            sdnn=0.15,
            rmssd=0.08,
            pnn50=30,
            lf=1.0,
            hf=3.0,
            lf_hf=0.33,
            entropy=4.0,
        )
        findings = self.detector.detect_all(metrics)
        parasym_found = any("Parasimpática" in f.name for f in findings)
        self.assertTrue(parasym_found)

    def test_detect_low_entropy(self):
        """Test detección de entropía baja."""
        metrics = HRVMetrics(
            bpm=75,
            sdnn=0.05,
            rmssd=0.02,
            pnn50=8,
            lf=2.0,
            hf=1.0,
            lf_hf=2.0,
            entropy=1.2,
        )
        findings = self.detector.detect_all(metrics)
        entropy_found = any("Entropía Baja" in f.name for f in findings)
        self.assertTrue(entropy_found)

    def test_detect_high_entropy(self):
        """Test detección de entropía alta."""
        metrics = HRVMetrics(
            bpm=75,
            sdnn=0.15,
            rmssd=0.06,
            pnn50=25,
            lf=1.5,
            hf=2.0,
            lf_hf=0.75,
            entropy=5.0,
        )
        findings = self.detector.detect_all(metrics)
        entropy_found = any("Entropía Alta" in f.name for f in findings)
        self.assertTrue(entropy_found)


class TestHypothesisGenerator(unittest.TestCase):
    """Tests para generador de hipótesis."""

    def test_acute_stress_hypothesis(self):
        """Test generación de hipótesis de estrés agudo."""
        findings = [
            PhysiologicalFinding(
                name="Taquicardia moderada",
                description="FC 115 bpm",
                confidence=0.9,
            ),
            PhysiologicalFinding(
                name="Variabilidad Cardíaca Baja (moderada)",
                description="SDNN bajo",
                confidence=0.85,
            ),
        ]
        metrics = HRVMetrics(
            bpm=115,
            sdnn=0.06,
            rmssd=0.02,
            pnn50=8,
            lf=3.0,
            hf=1.0,
            lf_hf=3.0,
            entropy=2.0,
        )
        hypotheses = ClinicalHypothesisGenerator.generate_hypotheses(findings, metrics)
        self.assertGreater(len(hypotheses), 0)
        stress_hyp = any("estrés" in h.hypothesis.lower() for h in hypotheses)
        self.assertTrue(stress_hyp)

    def test_good_health_hypothesis(self):
        """Test generación de hipótesis de buena salud."""
        findings = [
            PhysiologicalFinding(
                name="Variabilidad Cardíaca Alta",
                description="SDNN excelente",
                confidence=0.95,
            ),
            PhysiologicalFinding(
                name="Dominancia Parasimpática",
                description="LF/HF bajo",
                confidence=0.9,
            ),
        ]
        metrics = HRVMetrics(
            bpm=65,
            sdnn=0.18,
            rmssd=0.09,
            pnn50=35,
            lf=1.0,
            hf=3.0,
            lf_hf=0.33,
            entropy=4.2,
        )
        hypotheses = ClinicalHypothesisGenerator.generate_hypotheses(findings, metrics)
        self.assertGreater(len(hypotheses), 0)
        good_health = any("buena" in h.hypothesis.lower() for h in hypotheses)
        self.assertTrue(good_health)


class TestRiskEstimator(unittest.TestCase):
    """Tests para estimador de riesgo."""

    def test_low_risk(self):
        """Test estimación de riesgo bajo."""
        metrics = HRVMetrics(
            bpm=70,
            sdnn=0.15,
            rmssd=0.07,
            pnn50=25,
            lf=1.5,
            hf=2.5,
            lf_hf=0.6,
            entropy=4.0,
        )
        findings = []
        risk_level, risk_score = RiskEstimator.estimate_risk(metrics, findings)
        self.assertEqual(risk_level, RiskLevel.BAJO)
        self.assertLess(risk_score, 25)

    def test_moderate_risk(self):
        """Test estimación de riesgo moderado."""
        metrics = HRVMetrics(
            bpm=115,  # Aumentado de 110
            sdnn=0.08,
            rmssd=0.02,
            pnn50=6,  # Reducido de 10
            lf=3.5,  # Aumentado de 3.0
            hf=0.8,  # Reducido de 1.0
            lf_hf=4.375,  # Aumentado de 3.0
            entropy=2.0,  # Reducido de 2.5
        )
        findings = []
        risk_level, risk_score = RiskEstimator.estimate_risk(metrics, findings)
        self.assertIn(risk_level, [RiskLevel.MODERADO, RiskLevel.ALTO])
        self.assertGreaterEqual(risk_score, 25)

    def test_high_risk_low_variability(self):
        """Test estimación de riesgo alto por baja variabilidad."""
        metrics = HRVMetrics(
            bpm=95,
            sdnn=0.04,
            rmssd=0.01,
            pnn50=3,
            lf=2.5,
            hf=0.5,
            lf_hf=5.0,
            entropy=1.3,
        )
        findings = [
            PhysiologicalFinding(
                name="Variabilidad Cardíaca Baja (severa)",
                description="SDNN muy bajo",
                confidence=0.95,
            ),
        ]
        risk_level, risk_score = RiskEstimator.estimate_risk(metrics, findings)
        self.assertIn(risk_level, [RiskLevel.ALTO, RiskLevel.CRÍTICO])

    def test_critical_risk(self):
        """Test estimación de riesgo crítico."""
        metrics = HRVMetrics(
            bpm=155,
            sdnn=0.02,
            rmssd=0.005,
            pnn50=1,
            lf=5.0,
            hf=0.1,
            lf_hf=50.0,
            entropy=0.8,
        )
        findings = [
            PhysiologicalFinding(
                name="Variabilidad Cardíaca Baja (severa)",
                description="Crítico",
                confidence=0.95,
            ),
        ]
        risk_level, risk_score = RiskEstimator.estimate_risk(metrics, findings, ai_score=0.85)
        self.assertEqual(risk_level, RiskLevel.CRÍTICO)
        self.assertGreater(risk_score, 75)


class TestAutonomicStateClassifier(unittest.TestCase):
    """Tests para clasificador de estado autonómico."""

    def test_sympathetic_dominance(self):
        """Test clasificación de dominancia simpática."""
        metrics = HRVMetrics(
            bpm=110,
            sdnn=0.08,
            rmssd=0.02,
            pnn50=5,
            lf=4.0,
            hf=1.0,
            lf_hf=4.0,
            entropy=2.5,
        )
        state = AutonomicStateClassifier.classify(metrics)
        self.assertEqual(state, AutonomicState.SIMPÁTICO)

    def test_parasympathetic_dominance(self):
        """Test clasificación de dominancia parasimpática."""
        metrics = HRVMetrics(
            bpm=60,
            sdnn=0.16,
            rmssd=0.08,
            pnn50=30,
            lf=1.0,
            hf=3.5,
            lf_hf=0.28,
            entropy=4.0,
        )
        state = AutonomicStateClassifier.classify(metrics)
        self.assertEqual(state, AutonomicState.PARASIMPÁTICO)

    def test_balance(self):
        """Test clasificación de equilibrio."""
        metrics = HRVMetrics(
            bpm=72,
            sdnn=0.14,
            rmssd=0.055,  # Ajustado: < 0.06 para ser específico
            pnn50=25,
            lf=1.8,
            hf=2.0,
            lf_hf=0.9,  # Entre 0.7 y 2.5
            entropy=3.5,
        )
        state = AutonomicStateClassifier.classify(metrics)
        self.assertEqual(state, AutonomicState.EQUILIBRIO)

    def test_dysfunction(self):
        """Test clasificación de disfunción."""
        metrics = HRVMetrics(
            bpm=95,
            sdnn=0.03,
            rmssd=0.008,
            pnn50=2,
            lf=3.0,
            hf=0.8,
            lf_hf=3.75,
            entropy=1.0,
        )
        state = AutonomicStateClassifier.classify(metrics)
        self.assertEqual(state, AutonomicState.DISFUNCIÓN)


class TestBiomedicalReasoningEngine(unittest.TestCase):
    """Tests para motor principal de razonamiento."""

    def setUp(self):
        """Configuración inicial."""
        self.engine = BiomedicalReasoningEngine()

    def test_reason_normal_metrics(self):
        """Test razonamiento con métricas normales."""
        metrics = HRVMetrics(
            bpm=70,
            sdnn=0.15,
            rmssd=0.055,
            pnn50=26,
            lf=1.6,
            hf=2.0,
            lf_hf=0.8,
            entropy=4.0,
            ai_score=0.2,
        )
        output = self.engine.reason(metrics)
        
        self.assertIsNotNone(output)
        self.assertEqual(output.risk_level, RiskLevel.BAJO)
        self.assertGreater(len(output.findings), 0)
        self.assertGreater(len(output.recommendations), 0)
        self.assertEqual(output.autonomic_state, AutonomicState.EQUILIBRIO)

    def test_reason_stress_metrics(self):
        """Test razonamiento con métricas de estrés."""
        metrics = HRVMetrics(
            bpm=118,
            sdnn=0.07,
            rmssd=0.02,
            pnn50=7,
            lf=4.2,
            hf=0.8,
            lf_hf=5.25,
            entropy=2.1,
            ai_score=0.65,
        )
        output = self.engine.reason(metrics)
        
        self.assertIsNotNone(output)
        self.assertIn(output.risk_level, [RiskLevel.MODERADO, RiskLevel.ALTO])
        self.assertEqual(output.autonomic_state, AutonomicState.SIMPÁTICO)
        self.assertGreater(len(output.warnings), 0)

    def test_reason_invalid_metrics(self):
        """Test razonamiento con métricas inválidas."""
        metrics = HRVMetrics(
            bpm=400,
            sdnn=0.1,
            rmssd=0.05,
            pnn50=20,
            lf=2.0,
            hf=1.5,
            lf_hf=1.33,
            entropy=3.5,
        )
        output = self.engine.reason(metrics)
        
        self.assertEqual(len(output.warnings), 1)
        self.assertIn("Error de validación", output.warnings[0])

    def test_reason_output_serialization(self):
        """Test serialización de salida."""
        metrics = HRVMetrics(
            bpm=72,
            sdnn=0.14,
            rmssd=0.06,
            pnn50=22,
            lf=1.5,
            hf=2.3,
            lf_hf=0.65,
            entropy=3.8,
        )
        output = self.engine.reason(metrics)
        
        # Test to_dict
        output_dict = output.to_dict()
        self.assertIsInstance(output_dict, dict)
        self.assertIn("findings", output_dict)
        self.assertIn("risk_level", output_dict)
        self.assertEqual(output_dict["risk_level"], "bajo")
        
        # Test to_json
        output_json = output.to_json()
        self.assertIsInstance(output_json, str)
        self.assertIn("findings", output_json)

    def test_reason_extreme_metrics_critical(self):
        """Test razonamiento con métricas críticas."""
        metrics = HRVMetrics(
            bpm=160,
            sdnn=0.015,
            rmssd=0.003,
            pnn50=0.5,
            lf=6.0,
            hf=0.05,
            lf_hf=120.0,
            entropy=0.5,
            ai_score=0.92,
        )
        output = self.engine.reason(metrics)
        
        self.assertEqual(output.risk_level, RiskLevel.CRÍTICO)
        self.assertGreater(len(output.warnings), 0)
        self.assertIn("CRÍTICO", output.warnings[0])

    def test_reason_recovery_state(self):
        """Test razonamiento en estado de recuperación."""
        metrics = HRVMetrics(
            bpm=58,
            sdnn=0.18,
            rmssd=0.09,
            pnn50=38,
            lf=1.2,
            hf=3.8,
            lf_hf=0.32,
            entropy=4.3,
            ai_score=0.1,
        )
        output = self.engine.reason(metrics)
        
        self.assertEqual(output.risk_level, RiskLevel.BAJO)
        self.assertEqual(output.autonomic_state, AutonomicState.PARASIMPÁTICO)
        self.assertGreaterEqual(len(output.hypotheses), 1)

    def test_reason_complete_differential_diagnosis(self):
        """Test generación completa de diagnóstico diferencial."""
        metrics = HRVMetrics(
            bpm=125,
            sdnn=0.05,
            rmssd=0.015,
            pnn50=4,
            lf=5.0,
            hf=0.5,
            lf_hf=10.0,
            entropy=1.5,
            ai_score=0.75,
        )
        output = self.engine.reason(metrics)
        
        self.assertGreater(len(output.differential_diagnoses), 0)
        for dx in output.differential_diagnoses:
            self.assertGreater(dx.probability, 0)
            self.assertLess(dx.probability, 1)
            self.assertGreater(len(dx.cardinal_features), 0)

    def test_reason_education_recommendations(self):
        """Test generación de recomendaciones educativas."""
        metrics = HRVMetrics(
            bpm=95,
            sdnn=0.07,
            rmssd=0.025,
            pnn50=10,
            lf=3.5,
            hf=1.0,
            lf_hf=3.5,
            entropy=2.8,
        )
        output = self.engine.reason(metrics)
        
        self.assertGreater(len(output.recommendations), 0)
        for rec in output.recommendations:
            self.assertIn(rec.category, ["lifestyle", "monitoring", "investigation", "clinical_follow_up"])
            self.assertIn(rec.urgency, ["routine", "soon", "urgent"])
            self.assertIn(rec.evidence_level, ["A", "B", "C"])


if __name__ == "__main__":
    unittest.main()
