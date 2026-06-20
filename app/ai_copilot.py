"""BIOCORE AI COPILOT - JARVIS-Style Biomédical Assistant

Advanced AI copilot for real-time biomedical analysis, explanation, and guidance.
Integrates with all signal analysis modules.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import anthropic  # type: ignore[import]
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_AVAILABLE = False

import streamlit as st

# ============================================================================
# DATA MODELS
# ============================================================================

class CopilotMode(str, Enum):
    """Copilot operation modes"""
    ANALYSIS = "analysis"           # Explain current analysis
    GUIDANCE = "guidance"           # Educational guidance
    CLINICAL = "clinical"           # Clinical decision support
    RESEARCH = "research"           # Research insights
    EMERGENCY = "emergency"         # Alert/emergency mode


@dataclass
class BiometricsContext:
    """Current biomedical state for copilot context"""
    ecg_hr: Optional[float] = None
    ecg_arrhythmia: Optional[str] = None
    hrv_sdnn: Optional[float] = None
    hrv_lf_hf: Optional[float] = None
    eeg_bands: Optional[Dict[str, float]] = None
    emg_activation: Optional[float] = None
    spo2: Optional[float] = None
    respiratory_rate: Optional[float] = None
    timestamp: Optional[str] = None
    alerts: Optional[List[str]] = None


@dataclass
class CopilotResponse:
    """Structured copilot response"""
    mode: CopilotMode
    text: str                          # Main response
    summary: str                       # Short summary
    recommendations: List[str]         # Action items
    warnings: List[str]                # Clinical warnings
    references: List[str]              # Literature references
    confidence: float                  # 0-1 confidence score
    follow_up_questions: List[str]     # Suggested follow-ups


# ============================================================================
# BIOCORE AI COPILOT
# ============================================================================

class BioCoreCopilot:
    """Advanced AI assistant for BIOCORE biomédical platform"""
    
    def __init__(self):
        """Initialize JARVIS copilot"""
        if not ANTHROPIC_AVAILABLE:
            print("⚠️ Anthropic not available")
            self.client = None
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("anthropic_api_key", None)
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
            else:
                self.client = None
        
        self.model = "claude-3-5-sonnet-20241022"
        self.conversation_history: List[Dict] = []
        self.context: Optional[BiometricsContext] = None
        self.mode = CopilotMode.ANALYSIS
        
        # System prompt for medical expertise
        self.system_prompt = """You are JARVIS, an advanced AI copilot for BIOCORE - a professional biomedical signal analysis platform.

You are an expert in:
- ECG analysis and arrhythmia detection
- HRV analysis and autonomic nervous system
- EEG analysis and neurological patterns
- EMG analysis and neuromuscular physiology
- PPG, SpO2, respiratory, temperature, blood pressure
- Clinical decision support
- Medical education and explanation
- Research methodology

Your role:
1. EXPLAIN: Make complex biomedical findings understandable
2. GUIDE: Educate users about physiological concepts
3. SUPPORT: Provide clinical decision support (always recommend consulting professionals)
4. INTERPRET: Translate data into clinical insights
5. ALERT: Identify potentially dangerous patterns

Communication style:
- Clear, professional, but accessible
- Always cite confidence levels
- Recommend clinical validation for any findings
- Include relevant references when appropriate
- Adapt to user expertise level (student, clinician, researcher)

CRITICAL: You are a SUPPORTING tool only. Always recommend proper clinical validation and professional oversight."""
    
    def set_context(self, context: BiometricsContext):
        """Set current biomedical context for analysis"""
        self.context = context
    
    def set_mode(self, mode: CopilotMode):
        """Set copilot operational mode"""
        self.mode = mode
    
    def _build_context_prompt(self) -> str:
        """Build context prompt from current biometrics"""
        if not self.context:
            return "No current biometric data available."
        
        context_parts = []
        
        if self.context.ecg_hr is not None:
            context_parts.append(f"Heart Rate: {self.context.ecg_hr:.1f} bpm")
        
        if self.context.ecg_arrhythmia:
            context_parts.append(f"Arrhythmia Detected: {self.context.ecg_arrhythmia}")
        
        if self.context.hrv_sdnn is not None:
            context_parts.append(f"HRV SDNN: {self.context.hrv_sdnn:.1f} ms")
        
        if self.context.hrv_lf_hf is not None:
            context_parts.append(f"HRV LF/HF Ratio: {self.context.hrv_lf_hf:.2f}")
        
        if self.context.eeg_bands:
            eeg_str = ", ".join([f"{k}: {v:.1f}" for k, v in self.context.eeg_bands.items()])
            context_parts.append(f"EEG Bands: {eeg_str}")
        
        if self.context.emg_activation is not None:
            context_parts.append(f"EMG Activation: {self.context.emg_activation:.1f}%")
        
        if self.context.spo2 is not None:
            context_parts.append(f"SpO2: {self.context.spo2:.1f}%")
        
        if self.context.respiratory_rate is not None:
            context_parts.append(f"Respiratory Rate: {self.context.respiratory_rate:.1f} breaths/min")
        
        if self.context.alerts:
            context_parts.append(f"Active Alerts: {', '.join(self.context.alerts)}")
        
        return "Current Biometric State:\n" + "\n".join(context_parts)
    
    def analyze(self, user_query: str, use_context: bool = True) -> CopilotResponse:
        """Analyze user query and provide response
        
        Parameters:
        -----------
        user_query : str
            User's question or request
        use_context : bool
            Include current biometric context in analysis
            
        Returns:
        --------
        CopilotResponse
            Structured response from copilot
        """
        
        if not ANTHROPIC_AVAILABLE or not self.client:
            return CopilotResponse(
                mode=self.mode,
                text="❌ JARVIS is not available. Install: pip install anthropic",
                summary="Anthropic API required",
                recommendations=["Install anthropic: pip install anthropic"],
                warnings=["JARVIS unavailable"],
                references=[],
                confidence=0,
                follow_up_questions=[]
            )
        
        # Build full prompt with context
        if use_context:
            context_prompt = self._build_context_prompt()
            full_query = f"{context_prompt}\n\nUser Query: {user_query}"
        else:
            full_query = user_query
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": full_query
        })
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt,
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Parse response into structured format
            copilot_response = self._parse_response(assistant_message)
            
            return copilot_response
        except Exception as e:
            return CopilotResponse(
                mode=self.mode,
                text=f"❌ Error: {str(e)}",
                summary="Error processing query",
                recommendations=["Check API key", "Check internet connection"],
                warnings=[f"Error: {str(e)}"],
                references=[],
                confidence=0,
                follow_up_questions=[]
            )
    
    def _parse_response(self, response_text: str) -> CopilotResponse:
        """Parse Claude response into structured CopilotResponse"""
        
        # Extract sections from response
        lines = response_text.split('\n')
        summary = lines[0] if lines else response_text[:100]
        
        recommendations = []
        warnings = []
        references = []
        
        for line in lines:
            if line.startswith('- '):
                recommendations.append(line[2:])
            elif '⚠️' in line or 'WARNING' in line.upper():
                warnings.append(line)
            elif '📚' in line or 'REFERENCE' in line.upper():
                references.append(line)
        
        # Determine confidence (placeholder logic)
        confidence = 0.85
        
        follow_up_questions = [
            "Would you like more details about this finding?",
            "Should I analyze a specific time period?",
            "Do you need historical comparison?"
        ]
        
        return CopilotResponse(
            mode=self.mode,
            text=response_text,
            summary=summary,
            recommendations=recommendations or ["Review findings with clinical team"],
            warnings=warnings or [],
            references=references or [],
            confidence=confidence,
            follow_up_questions=follow_up_questions
        )
    
    def explain_metric(self, metric_name: str, value: float) -> str:
        """Explain a specific biomedical metric"""
        query = f"Explain the clinical significance of {metric_name} = {value}. What does this value indicate about patient state?"
        response = self.analyze(query, use_context=True)
        return response.text
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_summary(self) -> Dict:
        """Get copilot session summary"""
        return {
            "mode": self.mode.value,
            "messages": len(self.conversation_history),
            "context_available": self.context is not None,
            "conversation_items": len(self.conversation_history) // 2
        }


# ============================================================================
# STREAMLIT INTEGRATION
# ============================================================================

def initialize_copilot():
    """Initialize copilot in Streamlit session"""
    if 'biocore_copilot' not in st.session_state:
        st.session_state.biocore_copilot = BioCoreCopilot()
    return st.session_state.biocore_copilot


def render_copilot_panel():
    """Render copilot UI panel"""
    st.markdown("""
    <div class='biocore-panel' style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #0f3460; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
        <div style='display: flex; align-items: center; gap: 15px;'>
            <div style='font-size: 2.5rem;'>🤖</div>
            <div>
                <div style='font-size: 1.3rem; font-weight: bold; color: #00d4ff;'>JARVIS AI COPILOT</div>
                <div style='font-size: 0.9rem; color: #7bc8ff;'>Advanced Biomedical Intelligence Assistant</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    copilot = initialize_copilot()
    
    # Mode selector
    col1, col2 = st.columns([1, 2])
    with col1:
        mode = st.radio("Mode", [mode.value for mode in CopilotMode], 
                       label_visibility="collapsed")
        copilot.set_mode(CopilotMode(mode))
    
    with col2:
        mode_descriptions = {
            "analysis": "Explain current signals",
            "guidance": "Learn about physiology",
            "clinical": "Clinical decision support",
            "research": "Research insights",
            "emergency": "Alert interpretation"
        }
        st.info(f"📌 {mode_descriptions.get(mode, '')}")
    
    # Chat interface
    st.markdown("### 💬 Chat with JARVIS")
    
    # Display conversation history
    if st.session_state.biocore_copilot.conversation_history:
        st.markdown("**Conversation History:**")
        for i, msg in enumerate(st.session_state.biocore_copilot.conversation_history):
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content'][:200]}...")
            else:
                st.markdown(f"**JARVIS:** {msg['content'][:200]}...")
    
    # Input section
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask JARVIS anything about your biomedical signals...",
            placeholder="e.g., 'Why is my heart rate elevated?'",
            key="jarvis_input"
        )
    
    with col2:
        if st.button("📤 Send", use_container_width=True):
            if user_input:
                with st.spinner("🤖 JARVIS thinking..."):
                    response = copilot.analyze(user_input)
                    
                    # Display response
                    st.markdown("### JARVIS Response")
                    st.markdown(response.text)
                    
                    # Display metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confidence", f"{response.confidence:.0%}")
                    with col2:
                        st.metric("Recommendations", len(response.recommendations))
                    with col3:
                        st.metric("Warnings", len(response.warnings))
                    
                    # Show recommendations
                    if response.recommendations:
                        st.markdown("**Recommendations:**")
                        for rec in response.recommendations:
                            st.write(f"• {rec}")
                    
                    # Show warnings
                    if response.warnings:
                        st.warning("**⚠️ Clinical Warnings:**\n" + "\n".join(response.warnings))
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Summarize Findings"):
            response = copilot.analyze("Summarize the current findings in one paragraph")
            st.info(response.summary)
    
    with col2:
        if st.button("🎓 Educational Explanation"):
            copilot.set_mode(CopilotMode.GUIDANCE)
            response = copilot.analyze("Explain what this data means in simple terms")
            st.info(response.text)
    
    with col3:
        if st.button("🔍 Deeper Analysis"):
            response = copilot.analyze("What are the underlying physiological mechanisms?")
            st.info(response.text)
    
    with col4:
        if st.button("🗑️ Clear History"):
            copilot.clear_history()
            st.success("Conversation cleared")
            st.rerun()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_copilot_summary() -> Dict:
    """Get copilot session summary"""
    if 'biocore_copilot' in st.session_state:
        return st.session_state.biocore_copilot.get_summary()
    return {"status": "not_initialized"}


if __name__ == "__main__":
    # Quick test
    copilot = BioCoreCopilot()
    context = BiometricsContext(
        ecg_hr=95.0,
        ecg_arrhythmia="None",
        hrv_sdnn=45.0,
        hrv_lf_hf=2.5
    )
    copilot.set_context(context)
    response = copilot.analyze("Is my heart rate normal?")
    print(response.text)
