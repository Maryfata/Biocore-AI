"""Audit logging for HIPAA compliance"""
from sqlalchemy.orm import Session
from db.models import AuditLog
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    @staticmethod
    async def log_access(
        db: Session,
        user_id: str,
        action: str,
        patient_id: str = None,
        resource: str = None,
        ip_address: str = None,
        status: str = "success"
    ):
        audit = AuditLog(
            user_id=user_id,
            action=action,
            patient_id=patient_id,
            resource=resource,
            ip_address=ip_address,
            status=status,
        )
        db.add(audit)
        db.commit()
        logger.info(
            f"AUDIT: {user_id} {action} {patient_id} {status}",
            extra={'ip': ip_address}
        )


audit_logger = AuditLogger()
