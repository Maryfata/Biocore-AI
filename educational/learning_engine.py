"""Learning engine: orchestrates lessons, quizzes and scoring for students."""
from __future__ import annotations
from typing import List, Dict, Any
from dataclasses import dataclass, field
from typing import Optional

try:
    from educational import rural_mode
except Exception:
    # local import path fallback
    from . import rural_mode


@dataclass
class QuizQuestion:
    prompt: str
    choices: List[str]
    answer: int


@dataclass
class LearningEngine:
    student_id: str
    progress: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0

    def register_lesson(self, lesson_id: str) -> None:
        self.progress.setdefault(lesson_id, {'completed': False, 'score': 0.0})

    def save_progress_local(self) -> None:
        """Persist progress to local storage (Modo Rural)."""
        try:
            rural_mode.save_progress(self.student_id, self.progress)
        except Exception:
            pass

    def load_progress_local(self) -> Optional[Dict[str, Any]]:
        """Load persisted progress if available and merge into current state."""
        try:
            data = rural_mode.load_progress(self.student_id)
            if data:
                self.progress.update(data)
                return data
        except Exception:
            return None
        return None

    def grade_quiz(self, questions: Dict[int, QuizQuestion], responses: Dict[int, int]) -> float:
        """Grade a quiz given questions and a mapping of responses.

        Returns percentage score (0-100).
        """
        correct = 0
        for qid, q in questions.items():
            if responses.get(qid) == q.answer:
                correct += 1
        score = float(correct) / max(1, len(questions)) * 100.0
        return score

    def submit_quiz(self, lesson_id: str, questions: Dict[int, QuizQuestion], responses: Dict[int, int]) -> float:
        """Record the quiz result and update progress state."""
        score = self.grade_quiz(questions, responses)
        self.progress.setdefault(lesson_id, {})
        self.progress[lesson_id]['completed'] = True
        self.progress[lesson_id]['score'] = score
        self.score = (self.score + score) / 2.0 if self.score else score
        return score

    def get_progress(self) -> Dict[str, Any]:
        return self.progress


def generate_quiz(topic: str = 'ecg_basics', level: str = 'basic') -> Dict[int, QuizQuestion]:
    """Return a small bank of quiz questions for a given topic and difficulty level.

    The number of questions scales with difficulty to address the earlier complaint
    about too few intermediate questions.
    """
    # Simple hardcoded question examples for scaffolding. Can be replaced by DB.
    pool: Dict[str, List[QuizQuestion]] = {
        'ecg_basics': [
            QuizQuestion('¿Cuál es la frecuencia cardíaca normal adulta (aprox.)?', ['30-50', '60-100', '110-150', '150-200'], 1),
            QuizQuestion('¿Qué representa el complejo QRS?', ['Despolarización ventricular', 'Repolarización ventricular', 'Despolarización auricular', 'Actividad muscular'], 0),
            QuizQuestion('¿Qué derivada es útil para ver la pared lateral?', ['V1', 'V2', 'V5', 'aVR'], 2),
            QuizQuestion('¿Qué indica una elevación ST persistente?', ['Isquemia crónica', 'Infarto agudo (STEMI)', 'Hipertensión', 'Arritmia'], 1),
            QuizQuestion('¿Qué mide el intervalo PR?', ['Tiempo entre P y inicio QRS', 'Duración QRS', 'Frecuencia cardíaca', 'QTc'], 0),
            QuizQuestion('¿Qué es una PVC?', ['Extrasístole ventricular', 'Taquicardia supraventricular', 'Bloqueo AV', 'Fibrilación auricular'], 0),
            QuizQuestion('¿Cómo se calcula la FC desde RR?', ['60/mean(RR)', 'mean(RR)/60', 'sum(RR)/n', '60*mean(RR)'], 0),
            QuizQuestion('¿Cuál banda EEG sugiere relajación con ojos cerrados?', ['Delta', 'Theta', 'Alpha', 'Beta'], 2),
            QuizQuestion('¿Cuál derivada muestra mejor el IEC anterior (V1-V4)?', ['V1-V4', 'V5-V6', 'I, aVL', 'aVF'], 0),
            QuizQuestion('¿Qué signo sugiere HVI en el ECG?', ['Voltajes precordiales bajos', 'Elevación ST difusa', 'R grandes en V5-V6', 'Ondas U prominentes'], 2),
            QuizQuestion('¿Cuál es una causa frecuente de bradicardia?', ['Hipertiroidismo', 'Bloqueo AV', 'Fiebre', 'Deshidratación'], 1),
            QuizQuestion('¿Qué significa un eje eléctrico izquierdo (valor negativo en II)?', ['Posible HVI', 'Infarto lateral', 'Hiperkalemia', 'Taquicardia'], 0),
            QuizQuestion('¿Qué patrón sugiere bloqueo de rama derecha?', ['R predominant in V1', 'Deep S in V1', 'Large R in V5', 'ST depression in II'], 0),
            QuizQuestion('¿Cuál es la intervención inicial para STEMI sospechado?', ['Administrar analgesia y observar', 'Activar reperfusión (PCI/Trombolisis)', 'Enviar a fisioterapia', 'Iniciar antibióticos'], 1),
        ],
    }

    questions = pool.get(topic, pool['ecg_basics'])
    if level == 'basic':
        count = min(5, len(questions))
    elif level == 'intermediate':
        count = min(8, len(questions))
    else:
        count = min(12, len(questions))

    # Select first `count` questions (deterministic for now). Could randomize later.
    selected = {i: questions[i] for i in range(count)}
    return selected


@dataclass
class PersistenceMixin:
    """Mixin providing save/load helpers for LearningEngine using rural_mode."""

    def save_progress_local(self, student_id: str) -> None:
        try:
            rural_mode.save_progress(student_id, self.progress)
        except Exception:
            pass

    def load_progress_local(self, student_id: str) -> Optional[Dict[str, Any]]:
        try:
            data = rural_mode.load_progress(student_id)
            if data:
                self.progress.update(data)
                return data
        except Exception:
            return None
        return None
