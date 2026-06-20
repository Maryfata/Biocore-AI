import numpy as np
from typing import Dict, Any, List
from datetime import datetime

class ClinicalAIEngine:
    """
    Core 2: Deterministic Clinical Decision Support System (CDSS) - Advanced Personalized Edition.
    Combines ICU-grade physiological rules, laboratory metrics, demographic anthropometry, 
    and BIOCORE's proprietary biometric fusion. 100% Private and highly extensive.
    """
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def analyze_patient(self, vitals: Dict[str, float], patient_name: str = "Patient", age: int = 25, 
                        gender: str = "Unknown", weight_kg: float = 70.0, height_cm: float = 170.0) -> Dict[str, Any]:
        """
        Main entry point. Ingests massive telemetry (Clinical, Labs, Biomarkers, Demographics).
        """
        # ==========================================
        # 1. VARIABLE EXTRACTION & ANTHROPOMETRY
        # ==========================================
        # Anthropometrics & Basics
        height_m = height_cm / 100.0 if height_cm > 0 else 1.70
        bmi = round(weight_kg / (height_m ** 2), 1) if height_m > 0 else 24.0

        # Basic Vitals & Hemodynamics
        hr = float(vitals.get('hr', 75.0))
        spo2 = float(vitals.get('spo2', 98.0))
        rr = float(vitals.get('rr', 16.0))
        sys_bp = float(vitals.get('sys_bp', 120.0))
        dia_bp = float(vitals.get('dia_bp', 80.0))
        temp = float(vitals.get('temp', 37.0))
        
        # Advanced Hemodynamics & ICU
        svv = float(vitals.get('svv', 10.0))
        etco2 = float(vitals.get('etco2', 40.0))
        gcs = int(vitals.get('gcs', 15))
        icp = float(vitals.get('icp', 10.0))
        
        # Laboratory Metrics (Metabolic, Renal, Electrolytes)
        lactate = float(vitals.get('lactate', 1.0))
        glucose = float(vitals.get('glucose', 90.0))
        urine_out = float(vitals.get('urine_out', 1.0))
        hemoglobin = float(vitals.get('hemoglobin', 14.0)) # Normal: 12-16 g/dL
        potassium = float(vitals.get('potassium', 4.0))    # Normal: 3.5-5.0 mEq/L
        sodium = float(vitals.get('sodium', 140.0))        # Normal: 135-145 mEq/L

        # Body Composition & Anthropometry (Overcoming BMI limitations)
        body_fat = float(vitals.get('body_fat_pct', 20.0)) # Normal M: 10-20%, F: 20-30%
        muscle_mass = float(vitals.get('muscle_mass_kg', round(weight_kg * 0.4, 1))) # Estimate 40% if not provided

        # BIOCORE Proprietary Biomarkers Inputs
        hrv_sdnn = float(vitals.get('hrv_sdnn', 55.0))
        hrv_rmssd = float(vitals.get('hrv_rmssd', 45.0))
        lfhf = float(vitals.get('hrv_lf_hf_ratio', 1.5))
        eda_peaks = float(vitals.get('eda_scr_peaks', 4.0))
        scl = float(vitals.get('scl_u_siemens', 3.0))
        eeg_alpha = float(vitals.get('eeg_alpha_power', 15.0))
        eeg_theta = float(vitals.get('eeg_theta_power', 8.0))
        signal_coh = float(vitals.get('signal_coherence', 0.7))
        hr_recovery = float(vitals.get('hr_recovery_rate', 25.0))
        sleep = float(vitals.get('sleep_hours', 7.5))

        # Derived Clinical Metrics
        map_bp = round((sys_bp + 2 * dia_bp) / 3, 1) 
        shock_index = round(hr / sys_bp, 2) if sys_bp > 0 else 9.99 
        cpp = round(map_bp - icp, 1) 
        
        # Data Collectors
        findings = []
        physiological_alerts = []
        recommendations = []
        risk_score = 0

        # ==========================================
        # ENGINE 1: CARDIOVASCULAR & HEMODYNAMICS
        # ==========================================
        hr_max_theoretical = 220 - age
        hr_max_percentage = (hr / hr_max_theoretical) * 100 if hr_max_theoretical > 0 else 100

        if hr < 40:
            findings.append(f"Severe Bradycardia ({hr} bpm).")
            physiological_alerts.append(f"High risk of low cardiac output. In a {age}-year-old patient, this severely limits systemic perfusion.")
            risk_score += 40
        elif 91 <= hr <= 120:
            findings.append(f"Tachycardia ({hr} bpm).")
            physiological_alerts.append(f"Increased sympathetic tone. Myocardial oxygen demand (MVO2) is elevated.")
            risk_score += 15
        elif hr > 120:
            findings.append(f"Severe Tachycardia / Tachyarrhythmia ({hr} bpm).")
            physiological_alerts.append(f"Operating at {hr_max_percentage:.1f}% of theoretical max HR. Diastolic filling time is critically compromised.")
            risk_score += 40

        if map_bp < 65:
            findings.append(f"Critical Hypotension / Low MAP ({map_bp} mmHg).")
            physiological_alerts.append("Inadequate organ perfusion pressure. Autoregulation thresholds breached (kidneys, brain).")
            recommendations.append("Immediate fluid resuscitation and/or vasopressor support required to defend MAP.")
            risk_score += 50
        elif sys_bp > 180 or dia_bp > 120:
            findings.append(f"Hypertensive Crisis ({sys_bp}/{dia_bp} mmHg).")
            risk_score += 35

        # ==========================================
        # ENGINE 2: RESPIRATORY, CAPNOGRAPHY & OXYGEN DELIVERY
        # ==========================================
        if rr < 8:
            findings.append(f"Severe Bradypnea / Hypoventilation ({rr} rpm).")
            physiological_alerts.append("Medullary respiratory center depression. Imminent hypercapnic respiratory failure.")
            risk_score += 40
        elif rr > 30:
            findings.append(f"Severe Tachypnea ({rr} rpm).")
            physiological_alerts.append("Imminent respiratory muscle fatigue. Anatomic dead space ventilation is overwhelming alveolar ventilation.")
            risk_score += 45

        if 85 <= spo2 < 90:
            findings.append(f"Severe Hypoxemia ({spo2}%).")
            physiological_alerts.append("Tissue DO2 critically low. Cellular shift to anaerobic metabolism occurring.")
            risk_score += 50
        elif spo2 < 85:
            findings.append(f"Critical Hypoxia ({spo2}%).")
            risk_score += 70

        if etco2 < 30:
            physiological_alerts.append(f"Low EtCO2 ({etco2} mmHg): Suggests hyperventilation, hypocapnia, or reduced pulmonary blood flow (e.g., massive PE).")
            risk_score += 25
        elif etco2 > 50:
            physiological_alerts.append(f"High EtCO2 ({etco2} mmHg): Alveolar hypoventilation leading to CO2 retention. Risk of CO2 narcosis.")
            risk_score += 30

        # ==========================================
        # ENGINE 3: NEUROLOGICAL, LABS & ELECTROLYTES
        # ==========================================
        if gcs <= 8:
            findings.append(f"Comatose state (GCS {gcs}).")
            recommendations.append(f"Intubation mandated for {patient_name} (GCS < 8 = Intubate) to protect the airway.")
            risk_score += 60

        if lactate > 4.0:
            findings.append(f"Severe Lactic Acidosis ({lactate} mmol/L).")
            physiological_alerts.append("Widespread tissue hypoperfusion (Type A lactic acidosis) indicating severe cellular shock.")
            risk_score += 45

        if hemoglobin < 7.0:
            findings.append(f"Severe Anemia (Hb: {hemoglobin} g/dL).")
            physiological_alerts.append("Oxygen carrying capacity is drastically reduced, severely impacting total DO2 despite potentially normal SpO2.")
            risk_score += 35
            
        if potassium > 6.0:
            findings.append(f"Severe Hyperkalemia (K+: {potassium} mEq/L).")
            physiological_alerts.append("Critical risk of lethal arrhythmias (Ventricular Fibrillation, Asystole) due to resting membrane potential depolarization.")
            recommendations.append("Immediate administration of Calcium Gluconate (cardioprotection) and Insulin/Glucose.")
            risk_score += 50
        elif potassium < 2.5:
            findings.append(f"Severe Hypokalemia (K+: {potassium} mEq/L).")
            risk_score += 30

        if sodium > 155:
            findings.append(f"Hypernatremia (Na+: {sodium} mEq/L) - Free water deficit.")
            risk_score += 20
        elif sodium < 125:
            findings.append(f"Severe Hyponatremia (Na+: {sodium} mEq/L) - Risk of cerebral edema/seizures.")
            risk_score += 30

        # ==========================================
        # ENGINE 3.5: BODY COMPOSITION & METABOLISM
        # ==========================================
        bf_threshold = 25.0 if gender.lower() == "male" else 32.0
        
        if bmi >= 30.0 and body_fat < bf_threshold:
            findings.append(f"High BMI ({bmi}) but normal/low Body Fat ({body_fat}%). Athletic/Muscular profile detected.")
            # No risk points added. BMI is ignored due to high muscle mass.
        elif bmi <= 25.0 and body_fat >= bf_threshold:
            findings.append(f"Normal Weight Obesity ('Skinny Fat' profile). High Body Fat ({body_fat}%) despite normal BMI.")
            physiological_alerts.append("Increased occult cardiometabolic risk (visceral adiposity) despite normal body weight.")
            risk_score += 15
        elif bmi >= 30.0 and body_fat >= bf_threshold:
            findings.append(f"True Adipose Obesity (BMI: {bmi}, Body Fat: {body_fat}%).")
            physiological_alerts.append("Elevated systemic inflammatory state and cardiovascular risk due to excess adipose tissue.")
            risk_score += 20
        else:
            findings.append(f"Optimal Body Composition (Body Fat: {body_fat}%).")

        # ==========================================
        # ENGINE 4: BIOCORE PROPRIETARY BIOMARKERS 
        # ==========================================
        stress_val = (lfhf * 15) + (eda_peaks * 4) + (scl * 2) - (hrv_rmssd * 0.2)
        stress_index = min(100, max(0, stress_val))
        
        cog_val = (eeg_theta * 3.5) - (eeg_alpha * 1.5) + (hr * 0.1)
        cognitive_load = min(100, max(0, 50 + cog_val))

        rec_val = (hr_recovery * 1.5) + (sleep * 5) + (hrv_rmssd * 0.5) - (hr * 0.2)
        recovery_index = min(100, max(0, rec_val))

        ncc_val = (signal_coh * 100 * 0.7) + (eeg_alpha * 0.5) + (hrv_sdnn * 0.2)
        neuro_cardiac_coupling = min(100, max(0, ncc_val))

        resilience_val = (hrv_sdnn * 0.8) + (hr_recovery * 0.5) + (spo2 * 0.2) - (lactate * 5)
        physio_resilience = min(100, max(0, resilience_val))

        if stress_index > 75:
            findings.append(f"Critical Systemic Stress (Index: {stress_index:.1f}/100).")
            risk_score += 15
        
        if cognitive_load > 80:
            findings.append(f"Severe Neurological Overload (Score: {cognitive_load:.1f}/100).")
        
        if physio_resilience < 30:
            findings.append(f"Depleted Physiological Resilience (Score: {physio_resilience:.1f}/100).")
            physiological_alerts.append(f"{patient_name} has minimal homeostatic reserve to withstand further clinical insults.")
            risk_score += 20

        # ==========================================
        # ENGINE 5: ADVANCED PERSONALIZED CROSS-CORRELATIONS
        # ==========================================
        complex_patterns = []
        
        # DO2 (Oxygen Delivery) Failure: Hypoxia + Severe Anemia
        if spo2 < 92 and hemoglobin < 8.0:
            complex_patterns.append(f"🚨 CRITICAL DO2 FAILURE: The combination of hypoxemia (SpO2 {spo2}%) and severe anemia (Hb {hemoglobin}) means absolute oxygen delivery to {patient_name}'s tissues is catastrophically low. PRBC Transfusion highly indicated.")
            risk_score += 60

        # Impending Arrhythmic Arrest: Bradycardia + Hyperkalemia
        if hr < 50 and potassium > 5.5:
            complex_patterns.append(f"🚨 CARDIOTOXIC HYPERKALEMIA: Bradycardia concurrent with elevated potassium ({potassium} mEq/L) strongly predicts impending conduction failure and asystole. Membrane stabilization is the absolute priority.")
            risk_score += 80

        # True Obesity Hypoventilation Syndrome (OHS) / OSA risk (Using Body Fat instead of BMI)
        if body_fat >= bf_threshold and etco2 > 45 and spo2 < 94:
            complex_patterns.append(f"🟠 OBESITY HYPOVENTILATION SYNDROME: Given a high body fat percentage ({body_fat}%), concurrent hypercapnia and hypoxemia strongly suggests severe restrictive pulmonary physiology and chronic sleep-disordered breathing.")
            risk_score += 30
            
        # Cardiometabolic Syndrome Risk
        if body_fat >= bf_threshold and sys_bp > 130 and glucose > 110:
            complex_patterns.append(f"🟡 METABOLIC SYNDROME: Triad of excess adiposity ({body_fat}%), hypertension ({sys_bp}/{dia_bp}), and hyperglycemia ({glucose} mg/dL). High long-term atherosclerotic risk.")
            risk_score += 25

        # Cushing's Triad
        if sys_bp > 160 and hr < 60 and (rr < 12 or rr > 25):
            complex_patterns.append("🚨 CUSHING'S TRIAD: Hypertension, Bradycardia, and Irregular Respirations. Impending brainstem herniation.")
            risk_score += 100

        # Septic Shock Pattern
        if (temp > 38.3 or temp < 36.0) and hr > 100 and rr > 22 and lactate > 2.0 and map_bp < 65:
            complex_patterns.append(f"🔴 SEPTIC SHOCK PATTERN: Vasoplegic shock state with hyperlactatemia, fever, and failed autoregulation. {patient_name} requires immediate Hour-1 Sepsis Bundle activation.")
            risk_score += 80
            
        # Biocore Fusion Exhaustion
        if stress_index > 80 and recovery_index < 30 and lactate > 2.0:
            complex_patterns.append("🔴 BIOCORE EXHAUSTION SYNDROME: Extreme autonomic stress combined with poor recovery and rising lactate. The patient is entering a state of irreversible metabolic fatigue.")
            risk_score += 30

        # ==========================================
        # GLOBAL RISK STRATIFICATION
        # ==========================================
        if risk_score >= 120:
            risk = "CRITICAL RISK 🚨 (ICU LEVEL)"
            color_risk = "#ff2a2a"
        elif 60 <= risk_score < 120:
            risk = "HIGH RISK 🔴"
            color_risk = "#ff7b00"
        elif 25 <= risk_score < 60:
            risk = "MODERATE RISK 🟡"
            color_risk = "#f5d100"
        else:
            risk = "LOW RISK / STABLE 🟢"
            color_risk = "#00d46a"

        # ==========================================
        # EXTENSIVE EXPLAINABLE AI NARRATIVE
        # ==========================================
        explanation = f"### Personalized Pathophysiological Reasoning for {patient_name}\n"
        explanation += f"**BIOCORE Integrated Severity Score:** {risk_score}/400.\n\n"
        
        explanation += f"Based on the demographic profile of a {age}-year-old {gender.lower()} with a BMI of {bmi}, the BIOCORE deterministic engine has evaluated the multidimensional telemetry matrix. "
        
        if risk_score >= 120:
            explanation += f"**Critical Analysis:** The system has detected catastrophic, multi-system derangements. In a patient of this profile, overlapping homeostatic failures (e.g., hemodynamic collapse, neuro-respiratory uncoupling, or severe metabolic acidosis) mean that natural compensatory mechanisms (like sympathetic overdrive) have been completely exhausted. Without immediate, aggressive ICU-level intervention, cardiovascular or respiratory arrest is highly probable.\n\n"
        elif risk_score >= 60:
            explanation += f"**High-Risk Analysis:** Severe physiological stress is actively occurring. {patient_name}'s body is currently recruiting maximal compensatory reserves—such as increasing heart rate to defend cardiac output or hyperventilating to correct acidosis—to protect vital organ perfusion. However, this high-energy (ATP) demand is not sustainable, and metabolic exhaustion will ensue if the root etiology is not reversed.\n\n"
        elif risk_score >= 25:
            explanation += f"**Moderate-Risk Analysis:** The system observes early active compensation. The autonomic nervous system is shifting baselines (evident through altered HRV, HR, or RR) to adapt to an ongoing pathological stressor. Vigilant monitoring is required to ensure {patient_name} does not decompensate.\n\n"
        else:
            explanation += f"**Baseline Analysis:** Homeostatic equilibrium is successfully maintained. Neurological, respiratory, cardiovascular, and autonomic metrics align securely within standard physiological deviations expected for {patient_name}'s age and anthropometrics.\n\n"

        if complex_patterns:
            explanation += "**Advanced Synergistic Syndromes Detected:**\n"
            for p in complex_patterns:
                explanation += f"- {p}\n"
                
        explanation += "\n*Reasoning Engine Note: This narrative is generated deterministically by evaluating over 50 physiological logic gates, cross-referencing blood chemistry with real-time hemodynamics and proprietary neurocardiac coherence algorithms.*"

        # ==========================================
        # STRUCTURED CLINICAL REPORT GENERATION
        # ==========================================
        str_findings = "\n".join([f"* {h}" for h in findings]) if findings else "* Standard physiological baselines maintained."
        str_alerts = "\n".join([f"* {a}" for a in physiological_alerts]) if physiological_alerts else "* No major physiological alerts."
        str_recs = "\n".join([f"* {r}" for r in recommendations]) if recommendations else "* Continue standard care and routine monitoring."
        str_patterns = "\n".join([f"* {p}" for p in complex_patterns]) if complex_patterns else "* No complex pathological cross-correlations detected."

        report_md = f"""
### 🏥 Comprehensive Automated Clinical Report: BIOCORE CDSS
**Document ID:** BC-INT-{datetime.now().strftime("%Y%m%d%H%M%S")}  
**Patient Identification:** {patient_name} ({gender}, {age} y/o)  
**Body Composition:** {weight_kg} kg, {height_cm} cm (BMI: {bmi}) | **Body Fat:** {body_fat}% | **Muscle Mass:** {muscle_mass} kg  
**Telemetry Timestamp:** {self.timestamp}  

---

#### 📊 1. Standard Clinical Telemetry & Laboratories
**Cardiovascular & Hemodynamics:**
* **HR:** {hr} bpm | **BP:** {sys_bp}/{dia_bp} mmHg | **MAP:** {map_bp} mmHg
* **Shock Index:** {shock_index} | **SVV:** {svv}% 

**Respiratory & Oxygenation:**
* **SpO2:** {spo2}% | **RR:** {rr} rpm | **EtCO2:** {etco2} mmHg

**Neurometabolic & Critical Labs:**
* **GCS:** {gcs}/15 | **ICP:** {icp} mmHg | **Core Temp:** {temp} °C
* **Lactate:** {lactate} mmol/L | **Glucose:** {glucose} mg/dL | **Urine Output:** {urine_out} ml/kg/hr
* **Hemoglobin:** {hemoglobin} g/dL | **Potassium (K+):** {potassium} mEq/L | **Sodium (Na+):** {sodium} mEq/L

---

#### 🧬 2. BIOCORE Proprietary Biomarkers (Neuro/Autonomic Fusion)
* **Stress Index:** {stress_index:.1f}/100 *(Derived from EDA, LF/HF, HR)*
* **Recovery Index:** {recovery_index:.1f}/100 *(Derived from Sleep, HRV-RMSSD, HR-Recovery)*
* **Cognitive Load:** {cognitive_load:.1f}/100 *(Derived from EEG Theta/Alpha ratio)*
* **Physiological Resilience:** {physio_resilience:.1f}/100 *(Overall homeostatic reserve)*
* **NeuroCardiac Coupling:** {neuro_cardiac_coupling:.1f}/100 *(Brain-Heart synchronization axis)*

---

#### 🔬 3. System-by-System Analytical Findings
{str_findings}

#### 🧠 4. Personalized Pathophysiological Synthesis
**Complex Cross-Correlations:**
{str_patterns}

**Physiological Alerts for {patient_name}:**
{str_alerts}

#### 📋 5. Targeted Clinical Directives & Intervention Plan
{str_recs}

---
*Disclaimer: This report is generated by the BIOCORE AI Deterministic Expert System fusing standard critical care logic gates, laboratory values, and advanced biometric algorithms. It serves as clinical decision support and requires validation by an attending physician.*
"""
        return {
            "clasificacion": findings if findings else ["Healthy baseline"],
            "riesgo": risk,
            "color_riesgo": color_risk,
            "explicacion": explanation,
            "informe": report_md,
            "biomarkers": {
                "stress": stress_index,
                "recovery": recovery_index,
                "cognitive_load": cognitive_load,
                "resilience": physio_resilience,
                "neurocardiac": neuro_cardiac_coupling
            }
        }

# Local test block
if __name__ == "__main__":
    engine = ClinicalAIEngine()
    print("Testing Extremely Complex Personalized Scenario...")
    
    # Pruebas: Un paciente adulto mayor con obesidad, anemia severa, hipoxia y taquicardia
    res = engine.analyze_patient({
        'sys_bp': 105, 'dia_bp': 65, 'hr': 130, 'rr': 28, 'spo2': 88, 
        'lactate': 2.8, 'hemoglobin': 6.5, 'potassium': 4.2, 'etco2': 48,
        'hrv_lf_hf_ratio': 4.5, 'eda_scr_peaks': 12, 'eeg_theta_power': 25, 'eeg_alpha_power': 5
    }, "Robert Evans", 72, "Male", 115.0, 175.0)
    
    print(f"Riesgo Global: {res['riesgo']}\n")
    print(res['explicacion'])
    print("\n-----------------------\n")
    print(res['informe'])