"""
__init__.py - INICIALIZADOR DE COMPONENTES
============================================
Importa y exporta todos los componentes de UI.

IMPORTA:
--------
    from app.components import (
        CardiacUI,
        NeurologyUI,
        MusculoskeletalUI,
        DigitalTwinsUI,
        AlertsUI,
        ReportGenerator,
        DataGenerator
    )
"""

from .cardiology_ui import CardiacUI
from .neurology_ui import NeurologyUI
from .musculoskeletal_ui import MusculoskeletalUI
from .digital_twins_ui import DigitalTwinsUI
from .alerts_and_reports_ui import AlertsUI, ReportGenerator
from .respiratory_ui import RespiratoryUI
from .metabolism_ui import MetabolismUI

__all__ = [
    'CardiacUI',
    'NeurologyUI',
    'MusculoskeletalUI',
    'DigitalTwinsUI',
    'AlertsUI',
    'ReportGenerator',
    'RespiratoryUI',
    'MetabolismUI'
]
