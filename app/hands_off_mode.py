"""BIOCORE HANDS-OFF MODE - Voice & Gesture Control

Universal hands-free control system combining:
- Voice commands (speech-to-text)
- Gesture recognition (MediaPipe)
- Eye gaze (optional)
- Keyboard shortcuts
"""

import streamlit as st
from enum import Enum
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    from gesture_controller import GestureController
except Exception:
    GestureController = None


# ============================================================================
# DATA MODELS
# ============================================================================

class ControlMode(str, Enum):
    """Hands-off control modes"""
    VOICE = "voice"
    GESTURE = "gesture"
    HYBRID = "hybrid"          # Voice + Gesture
    KEYBOARD = "keyboard"
    DISABLED = "disabled"


class VoiceCommand(str, Enum):
    """Available voice commands"""
    NEXT_TAB = "next tab"
    PREVIOUS_TAB = "previous tab"
    GENERATE_REPORT = "generate report"
    ANALYZE = "analyze"
    CLEAR = "clear"
    HELP = "help"
    PAUSE = "pause"
    RESUME = "resume"
    ZOOM_IN = "zoom in"
    ZOOM_OUT = "zoom out"
    SAVE = "save"
    EXPORT = "export"
    EXPLAIN = "explain"
    JARVIS = "jarvis"


class GestureCommand(str, Enum):
    """Available gesture commands"""
    OPEN_PALM = "open_palm"        # Pause/Resume
    POINTING = "pointing"          # Next
    THUMBS_UP = "thumbs_up"        # Confirm
    THUMBS_DOWN = "thumbs_down"    # Cancel
    PINCH = "pinch"                # Zoom
    FIST = "fist"                  # Menu
    PEACE = "peace"                # Previous
    OK_SIGN = "ok_sign"            # Report


@dataclass
class HandsOffEvent:
    """Event from hands-off control"""
    control_mode: ControlMode
    command: str
    confidence: float
    timestamp: str


# ============================================================================
# VOICE CONTROL
# ============================================================================

class VoiceController:
    """Voice command recognition and processing"""
    
    def __init__(self):
        """Initialize voice controller"""
        self.recognizer = sr.Recognizer() if sr else None
        self.available = sr is not None
        self.last_command: Optional[str] = None
        self.confidence_threshold = 0.7
        
        if not self.available:
            print("WARNING: Speech recognition not available. Install: pip install SpeechRecognition")
    
    def listen(self, duration: int = 3) -> Optional[str]:
        """Listen for voice command
        
        Parameters:
        -----------
        duration : int
            Seconds to listen
            
        Returns:
        --------
        str or None
            Recognized command or None if not recognized
        """
        if not self.available:
            return None
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=duration)
            
            # Try Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            self.last_command = text.lower()
            return text.lower()
        
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None
    
    def parse_command(self, text: str) -> Optional[VoiceCommand]:
        """Parse voice text into command
        
        Parameters:
        -----------
        text : str
            Raw voice input
            
        Returns:
        --------
        VoiceCommand or None
            Recognized command or None
        """
        text = text.lower().strip()
        
        # Direct matches
        for cmd in VoiceCommand:
            if cmd.value in text:
                return cmd
        
        # Fuzzy matching
        if any(word in text for word in ['next', 'forward', 'right']):
            return VoiceCommand.NEXT_TAB
        if any(word in text for word in ['previous', 'back', 'left']):
            return VoiceCommand.PREVIOUS_TAB
        if any(word in text for word in ['report', 'generate', 'create']):
            return VoiceCommand.GENERATE_REPORT
        if any(word in text for word in ['analyze', 'analysis', 'scan']):
            return VoiceCommand.ANALYZE
        if any(word in text for word in ['jarvis', 'copilot', 'assistant']):
            return VoiceCommand.JARVIS
        
        return None


# ============================================================================
# GESTURE CONTROL
# ============================================================================

class EnhancedGestureController:
    """Enhanced gesture recognition with better feedback"""
    
    def __init__(self):
        """Initialize gesture controller"""
        self.controller = None
        self.available = False
        self.last_gesture: Optional[str] = None
        self.gesture_callbacks: Dict[str, Callable] = {}

        if not GestureController:
            print("GestureController module unavailable. Gesture recognition disabled.")
            return

        try:
            self.controller = GestureController()
            self.available = self.controller.available
        except Exception as e:
            print(f"Gesture controller initialization failed: {e}")
            self.controller = None
            self.available = False
    
    def detect_gesture(self, image_data: np.ndarray) -> Optional[GestureCommand]:
        """Detect gesture from image
        
        Parameters:
        -----------
        image_data : np.ndarray
            Image from webcam
            
        Returns:
        --------
        GestureCommand or None
            Detected gesture command or None
        """
        if not self.available or not self.controller:
            return None
        
        try:
            gesture = self.controller.detect_gesture(image_data)
            if gesture:
                self.last_gesture = gesture
                return self._map_gesture_to_command(gesture)
            return None
        except Exception as e:
            print(f"Gesture detection error: {e}")
            return None
    
    def _map_gesture_to_command(self, gesture: str) -> Optional[GestureCommand]:
        """Map gesture string to command"""
        mapping = {
            'open_palm': GestureCommand.OPEN_PALM,
            'index': GestureCommand.POINTING,
            'thumbs_up': GestureCommand.THUMBS_UP,
            'thumbs_down': GestureCommand.THUMBS_DOWN,
            'pinch': GestureCommand.PINCH,
            'fist': GestureCommand.FIST,
            'peace': GestureCommand.PEACE,
            'ok_sign': GestureCommand.OK_SIGN,
        }
        return mapping.get(gesture.lower())


# ============================================================================
# HANDS-OFF CONTROLLER (MAIN)
# ============================================================================

class HandsOffController:
    """Master hands-off control system"""
    
    def __init__(self, mode: ControlMode = ControlMode.HYBRID):
        """Initialize hands-off controller
        
        Parameters:
        -----------
        mode : ControlMode
            Control mode (voice, gesture, hybrid, keyboard)
        """
        self.mode = mode
        self.voice_controller = VoiceController() if mode in [ControlMode.VOICE, ControlMode.HYBRID] else None
        self.gesture_controller = EnhancedGestureController() if mode in [ControlMode.GESTURE, ControlMode.HYBRID] else None
        self.events: List[HandsOffEvent] = []
        self.command_callbacks: Dict[str, Callable] = {}
        self.default_handlers_registered = False
    
    def set_mode(self, mode: ControlMode):
        """Switch controller mode and initialize required inputs."""
        self.mode = mode
        if mode in [ControlMode.VOICE, ControlMode.HYBRID] and not self.voice_controller:
            self.voice_controller = VoiceController()
        if mode in [ControlMode.GESTURE, ControlMode.HYBRID] and not self.gesture_controller:
            self.gesture_controller = EnhancedGestureController()

    def _update_status(self, message: str):
        """Update shared status feedback."""
        st.session_state.hands_off_feedback = message

    def _navigate_tab(self, offset: int = 1):
        tabs = st.session_state.get('page_tabs', [])
        current = st.session_state.get('selected_page')
        if not tabs or current not in tabs:
            self._update_status('No hay páginas activas para navegar.')
            return
        index = tabs.index(current)
        st.session_state.selected_page = tabs[(index + offset) % len(tabs)]
        self._update_status(f'Vista cambiada a: {st.session_state.selected_page}')

    def _toggle_pause_resume(self):
        active = st.session_state.get('hands_off_enabled', True)
        st.session_state.hands_off_enabled = not active
        self._update_status('Manos libres ' + ('activado' if not active else 'pausado'))

    def _generate_report(self):
        st.session_state.report_requested = True
        self._update_status('Solicitud de reporte enviada.')

    def _ask_jarvis(self):
        st.session_state.jarvis_query = 'Analiza el estado actual del paciente.'
        self._update_status('Jarvis activado: solicitando análisis.')

    def _analyze(self):
        st.session_state.analysis_requested = True
        self._update_status('Solicitud de análisis generada.')

    def _explain(self):
        st.session_state.explain_requested = True
        self._update_status('Solicitud de explicación enviada.')

    def _zoom_in(self):
        st.session_state.zoom_action = 'in'
        self._update_status('Zoom in activado.')

    def _zoom_out(self):
        st.session_state.zoom_action = 'out'
        self._update_status('Zoom out activado.')

    def _save(self):
        st.session_state.save_requested = True
        self._update_status('Guardado solicitado.')

    def _export(self):
        st.session_state.export_requested = True
        self._update_status('Exportación solicitada.')

    def _show_help(self):
        self._update_status('Comandos: next tab, previous tab, generate report, analyze, explain, jarvis, save, export, zoom in, zoom out.')

    def _register_default_handlers(self):
        if self.default_handlers_registered:
            return
        self.register_command_handler('next_tab', lambda: self._navigate_tab(1))
        self.register_command_handler('previous_tab', lambda: self._navigate_tab(-1))
        self.register_command_handler('generate_report', self._generate_report)
        self.register_command_handler('analyze', self._analyze)
        self.register_command_handler('explain', self._explain)
        self.register_command_handler('jarvis', self._ask_jarvis)
        self.register_command_handler('pause', self._toggle_pause_resume)
        self.register_command_handler('resume', self._toggle_pause_resume)
        self.register_command_handler('zoom_in', self._zoom_in)
        self.register_command_handler('zoom_out', self._zoom_out)
        self.register_command_handler('save', self._save)
        self.register_command_handler('export', self._export)
        self.register_command_handler('help', self._show_help)
        self.default_handlers_registered = True

    def register_command_handler(self, command: str, callback: Callable):
        """Register handler for command
        
        Parameters:
        -----------
        command : str
            Command name
        callback : Callable
            Function to call when command received
        """
        self.command_callbacks[command] = callback
    
    def process_voice_input(self, voice_text: str):
        """Process voice input and execute command
        
        Parameters:
        -----------
        voice_text : str
            Raw voice input
        """
        if not self.voice_controller:
            return
        
        command = self.voice_controller.parse_command(voice_text)
        if command:
            self._execute_command(command.value, "voice")
    
    def process_gesture_input(self, gesture: str):
        """Process gesture input and execute command
        
        Parameters:
        -----------
        gesture : str
            Detected gesture
        """
        if not self.gesture_controller:
            return
        
        gesture_cmd = self.gesture_controller._map_gesture_to_command(gesture)
        if gesture_cmd:
            self._execute_command(gesture_cmd.value, "gesture")
    
    def _execute_command(self, command: str, source: str):
        """Execute command
        
        Parameters:
        -----------
        command : str
            Command to execute
        source : str
            Source (voice, gesture, keyboard)
        """
        if command in self.command_callbacks:
            self.command_callbacks[command]()
        
        # Log event
        event = HandsOffEvent(
            control_mode=ControlMode(source) if source != "keyboard" else ControlMode.KEYBOARD,
            command=command,
            confidence=0.9,
            timestamp=st.session_state.get("current_time", "unknown")
        )
        self.events.append(event)


# ============================================================================
# STREAMLIT INTEGRATION
# ============================================================================

def initialize_hands_off():
    """Initialize hands-off mode in session"""
    if 'hands_off_controller' not in st.session_state:
        st.session_state.hands_off_controller = HandsOffController()
        st.session_state.hands_off_enabled = True
    return st.session_state.hands_off_controller


def render_hands_off_panel():
    """Render hands-off control panel"""
    
    st.markdown("""
    <div class='biocore-panel' style='background: linear-gradient(135deg, #2a1a2e 0%, #3a1a4e 100%);
        border: 2px solid #a020f0; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
        <div style='display: flex; align-items: center; gap: 15px;'>
            <div style='font-size: 2.5rem;'>🤲</div>
            <div>
                <div style='font-size: 1.3rem; font-weight: bold; color: #d946ef;'>HANDS-OFF UNIVERSAL CONTROL</div>
                <div style='font-size: 0.9rem; color: #ec4899;'>Voice • Gesture • Keyboard • AI Copilot</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    controller = initialize_hands_off()
    controller._register_default_handlers()
    
    if 'hands_off_feedback' not in st.session_state:
        st.session_state.hands_off_feedback = 'Esperando comando manos libres...'
    if 'page_tabs' not in st.session_state:
        st.session_state.page_tabs = []
    if 'jarvis_query' not in st.session_state:
        st.session_state.jarvis_query = ''
    if 'analysis_requested' not in st.session_state:
        st.session_state.analysis_requested = False
    if 'explain_requested' not in st.session_state:
        st.session_state.explain_requested = False
    if 'zoom_action' not in st.session_state:
        st.session_state.zoom_action = None
    if 'save_requested' not in st.session_state:
        st.session_state.save_requested = False
    if 'export_requested' not in st.session_state:
        st.session_state.export_requested = False

    # Mode selector
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎤 Voice Mode", use_container_width=True):
            controller.set_mode(ControlMode.VOICE)
            st.success("Voice mode activated")
    
    with col2:
        if st.button("🖐️ Gesture Mode", use_container_width=True):
            controller.set_mode(ControlMode.GESTURE)
            st.success("Gesture mode activated")
    
    with col3:
        if st.button("🔄 Hybrid Mode", use_container_width=True):
            controller.set_mode(ControlMode.HYBRID)
            st.success("Hybrid mode activated")
    
    with col4:
        if st.button("⌨️ Keyboard", use_container_width=True):
            controller.set_mode(ControlMode.KEYBOARD)
            st.success("Keyboard shortcuts enabled")
    
    # Current mode display
    st.markdown(f"**Current Mode:** `{controller.mode.value.upper()}`")

    # Voice Control
    if controller.mode in [ControlMode.VOICE, ControlMode.HYBRID]:
        st.markdown("### 🎤 Voice Commands")
        
        if controller.voice_controller and controller.voice_controller.available:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info("📢 Say or type: 'next tab', 'generate report', 'jarvis', 'explain', 'zoom in'.")
                st.text_input('Simulate voice command', key='hands_off_voice_input')
                voice_input = st.session_state.get('hands_off_voice_input', '').strip()
                if st.button('▶️ Ejecutar comando de voz', use_container_width=True):
                    if voice_input:
                        controller.process_voice_input(voice_input)
                        st.success(f"✓ Ejecutado: '{voice_input}'")
                    else:
                        st.warning('Ingresa un comando de voz válido.')

            with col2:
                if st.button("🔴 Start Listening (3s)", use_container_width=True):
                    with st.spinner("Listening..."):
                        voice_input = controller.voice_controller.listen(duration=3)
                        if voice_input:
                            st.success(f"✓ Heard: '{voice_input}'")
                            controller.process_voice_input(voice_input)
                        else:
                            st.warning("No se pudo reconocer el habla")
            
            # Available commands
            st.markdown("**Available Commands:**")
            commands_grid = """
            | Command | Action |
            |---------|--------|
            | 🎬 next tab | Go to next section |
            | ⬅️ previous tab | Go to previous |
            | 📋 generate report | Create report |
            | 🔍 analyze | Ask for analysis |
            | 🧠 explain | Explain current state |
            | 🤖 jarvis | Talk to JARVIS |
            | ⏸️ pause | Pause control |
            | ▶️ resume | Resume control |
            | 🔍 zoom in | Magnify chart |
            | 🔍 zoom out | Reduce chart |
            | 💾 save | Save current data |
            | 📤 export | Export results |
            | ❓ help | Show available commands |
            """
            st.markdown(commands_grid)
        else:
            st.warning("⚠️ Speech recognition not available. Install: `pip install SpeechRecognition`")
    
    # Gesture Control
    if controller.mode in [ControlMode.GESTURE, ControlMode.HYBRID]:
        st.markdown("### 🖐️ Gesture Recognition")
        
        if controller.gesture_controller and controller.gesture_controller.available:
            st.info("📷 Webcam gesture control enabled")
            image = st.camera_input('Capture hand gesture', key='hands_off_camera')
            if image is not None:
                try:
                    gesture_label = controller.gesture_controller.detect_gesture(image.read())
                    if gesture_label:
                        controller.process_gesture_input(gesture_label)
                        st.success(f'Gesto detectado: {gesture_label}')
                    else:
                        st.warning('Gesto no reconocido. Intenta con más claridad.')
                except Exception as e:
                    st.warning(f'Error en detección de gesto: {e}')
        else:
            st.warning("⚠️ Gesture recognition not available. Install: `pip install mediapipe opencv-python`")
            st.markdown('**Emulated gestures:**')
            c1, c2, c3, c4, c5 = st.columns(5)
            if c1.button('🖐️ Palma'):
                controller.process_gesture_input('open_palm')
            if c2.button('☝️ Índice'):
                controller.process_gesture_input('index')
            if c3.button('✌️ Dos'):
                controller.process_gesture_input('two_fingers')
            if c4.button('👌 OK'):
                controller.process_gesture_input('ok_sign')
            if c5.button('🤏 Pinch'):
                controller.process_gesture_input('pinch')
    
    # Keyboard Shortcuts
    if controller.mode in [ControlMode.KEYBOARD, ControlMode.HYBRID]:
        st.markdown("### ⌨️ Keyboard Shortcuts")
        
        shortcuts_grid = """
        | Key | Action |
        |-----|--------|
        | →/N | Next tab |
        | ←/P | Previous tab |
        | R | Generate report |
        | A | Analyze |
        | E | Explain |
        | J | Open JARVIS |
        | Space | Pause/Resume |
        | +/= | Zoom in |
        | -/_ | Zoom out |
        | S | Save |
        | X | Export |
        | ? | Help |
        """
        st.markdown(shortcuts_grid)
        st.text_input('Keyboard shortcut emulator', key='hands_off_keyboard_input')
        key_input = st.session_state.get('hands_off_keyboard_input', '').strip().lower()
        if st.button('Ejecutar atajo', use_container_width=True):
            shortcut_map = {
                'n': 'next_tab',
                'p': 'previous_tab',
                'r': 'generate_report',
                'a': 'analyze',
                'e': 'explain',
                'j': 'jarvis',
                ' ': 'pause',
                '+': 'zoom_in',
                '-': 'zoom_out',
                's': 'save',
                'x': 'export',
                '?': 'help',
            }
            command = shortcut_map.get(key_input)
            if command:
                controller._execute_command(command, 'keyboard')
                st.success(f'Atajo ejecutado: {command}')
            else:
                st.warning('Atajo desconocido. Usa n,p,r,a,e,j,+,-,s,x,?.')
    
    # Status indicator
    st.markdown('---')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = '🟢 Active' if st.session_state.get('hands_off_enabled', True) else '🔴 Inactive'
        st.metric('Status', status)
    
    with col2:
        events_count = len(controller.events)
        st.metric('Commands', events_count)
    
    with col3:
        if st.button('🗑️ Clear', use_container_width=True):
            controller.events = []
            st.session_state.hands_off_feedback = 'Esperando comando manos libres...'
            st.rerun()

    st.markdown('### 📌 Feedback')
    st.write(st.session_state.get('hands_off_feedback', ''))
    if st.session_state.jarvis_query:
        st.info(f'Jarvis trigger: {st.session_state.jarvis_query}')
    if st.session_state.analysis_requested:
        st.info('Analysis requested from hands-off control.')
    if st.session_state.explain_requested:
        st.info('Explain request queued.')
    if st.session_state.zoom_action:
        st.info(f'Zoom action: {st.session_state.zoom_action}')
    if st.session_state.save_requested:
        st.info('Save requested by hands-off control.')
    if st.session_state.export_requested:
        st.info('Export requested by hands-off control.')


def render_hands_off_footer():
    """Render hands-off status footer"""
    st.markdown("""
    <div style='position: fixed; bottom: 0; left: 0; right: 0; 
                background: rgba(26, 26, 46, 0.95); padding: 10px; text-align: center;
                border-top: 2px solid #a020f0;'>
        <small style='color: #ec4899;'>
            🤲 <b>HANDS-OFF MODE ACTIVE</b> - Use voice, gestures, or keyboard to control BIOCORE
        </small>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def apply_hands_off_shortcuts(key: str):
    """Apply keyboard shortcut
    
    Parameters:
    -----------
    key : str
        Key pressed
    """
    shortcuts = {
        'n': 'next_tab',
        'p': 'previous_tab',
        'r': 'generate_report',
        'a': 'analyze',
        'j': 'jarvis',
        ' ': 'pause_resume',
        '+': 'zoom_in',
        '-': 'zoom_out',
        's': 'save',
        'e': 'export',
    }
    
    if key.lower() in shortcuts:
        return shortcuts[key.lower()]
    return None


if __name__ == "__main__":
    # Test
    controller = HandsOffController(ControlMode.HYBRID)
    print("Hands-off controller initialized")
    print(f"Voice available: {controller.voice_controller.available if controller.voice_controller else False}")
    print(f"Gesture available: {controller.gesture_controller.available if controller.gesture_controller else False}")
