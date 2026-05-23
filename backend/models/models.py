from datetime import datetime
from extensions import db

# ──────────────────────────────────────────────────
# USERS
# ──────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id           = db.Column(db.Integer, primary_key=True)
    full_name    = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(100), unique=True, nullable=False)
    username     = db.Column(db.String(50), unique=True, nullable=False)
    password     = db.Column(db.String(255), nullable=False)
    role         = db.Column(db.Enum('admin','inspector','applicant'), default='applicant')
    phone_number = db.Column(db.String(15))
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    is_active    = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'id': self.id, 'full_name': self.full_name, 'email': self.email,
            'username': self.username, 'role': self.role,
            'phone_number': self.phone_number,
            'created_at': str(self.created_at), 'is_active': self.is_active
        }

# ──────────────────────────────────────────────────
# APPLICATIONS
# ──────────────────────────────────────────────────
class Application(db.Model):
    __tablename__ = 'applications'
    application_id   = db.Column(db.Integer, primary_key=True)
    applicant_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    building_name    = db.Column(db.String(150), nullable=False)
    building_type    = db.Column(db.String(100), nullable=False)
    address          = db.Column(db.Text, nullable=False)
    city             = db.Column(db.String(100), nullable=False)
    state            = db.Column(db.String(100), nullable=False)
    pincode          = db.Column(db.String(10), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    current_status   = db.Column(
        db.Enum('Pending','Under Inspection','Follow-up Required','Approved','Rejected'),
        default='Pending')
    priority_level   = db.Column(db.Enum('Low','Medium','High'), default='Medium')
    remarks          = db.Column(db.Text)

    applicant = db.relationship('User', foreign_keys=[applicant_id])

    def to_dict(self):
        return {
            'application_id': self.application_id,
            'applicant_id': self.applicant_id,
            'applicant_name': self.applicant.full_name if self.applicant else '',
            'building_name': self.building_name,
            'building_type': self.building_type,
            'address': self.address, 'city': self.city,
            'state': self.state, 'pincode': self.pincode,
            'application_date': str(self.application_date),
            'current_status': self.current_status,
            'priority_level': self.priority_level,
            'remarks': self.remarks
        }

# ──────────────────────────────────────────────────
# INSPECTIONS
# ──────────────────────────────────────────────────
class Inspection(db.Model):
    __tablename__ = 'inspections'
    inspection_id     = db.Column(db.Integer, primary_key=True)
    application_id    = db.Column(db.Integer, db.ForeignKey('applications.application_id'), nullable=False)
    inspector_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    inspection_date   = db.Column(db.DateTime)
    inspection_status = db.Column(
        db.Enum('Scheduled','In Progress','Completed','Failed'), default='Scheduled')
    findings          = db.Column(db.Text)
    remarks           = db.Column(db.Text)
    uploaded_images   = db.Column(db.String(255))
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    application = db.relationship('Application', foreign_keys=[application_id])
    inspector   = db.relationship('User', foreign_keys=[inspector_id])

    def to_dict(self):
        return {
            'inspection_id': self.inspection_id,
            'application_id': self.application_id,
            'building_name': self.application.building_name if self.application else '',
            'inspector_id': self.inspector_id,
            'inspector_name': self.inspector.full_name if self.inspector else '',
            'inspection_date': str(self.inspection_date),
            'inspection_status': self.inspection_status,
            'findings': self.findings, 'remarks': self.remarks,
            'uploaded_images': self.uploaded_images,
            'created_at': str(self.created_at)
        }

# ──────────────────────────────────────────────────
# FOLLOWUPS
# ──────────────────────────────────────────────────
class Followup(db.Model):
    __tablename__ = 'followups'
    followup_id      = db.Column(db.Integer, primary_key=True)
    inspection_id    = db.Column(db.Integer, db.ForeignKey('inspections.inspection_id'), nullable=False)
    followup_date    = db.Column(db.DateTime)
    followup_status  = db.Column(db.Enum('Pending','Completed','Skipped'), default='Pending')
    followup_remarks = db.Column(db.Text)

    inspection = db.relationship('Inspection', foreign_keys=[inspection_id])

    def to_dict(self):
        return {
            'followup_id': self.followup_id,
            'inspection_id': self.inspection_id,
            'followup_date': str(self.followup_date),
            'followup_status': self.followup_status,
            'followup_remarks': self.followup_remarks
        }

# ──────────────────────────────────────────────────
# NOC
# ──────────────────────────────────────────────────
class NOC(db.Model):
    __tablename__ = 'noc'
    noc_id               = db.Column(db.Integer, primary_key=True)
    application_id       = db.Column(db.Integer, db.ForeignKey('applications.application_id'), unique=True, nullable=False)
    approval_status      = db.Column(db.Enum('Pending','Approved','Rejected'), default='Pending')
    approved_by          = db.Column(db.Integer, db.ForeignKey('users.id'))
    issue_date           = db.Column(db.DateTime)
    expiry_date          = db.Column(db.DateTime)
    rejection_reason     = db.Column(db.Text)
    pdf_certificate_path = db.Column(db.String(255))

    application  = db.relationship('Application', foreign_keys=[application_id])
    approver     = db.relationship('User', foreign_keys=[approved_by])

    def to_dict(self):
        return {
            'noc_id': self.noc_id,
            'application_id': self.application_id,
            'building_name': self.application.building_name if self.application else '',
            'approval_status': self.approval_status,
            'approved_by': self.approved_by,
            'approver_name': self.approver.full_name if self.approver else '',
            'issue_date': str(self.issue_date) if self.issue_date else None,
            'expiry_date': str(self.expiry_date) if self.expiry_date else None,
            'rejection_reason': self.rejection_reason,
            'pdf_certificate_path': self.pdf_certificate_path
        }

# ──────────────────────────────────────────────────
# DOCUMENTS
# ──────────────────────────────────────────────────
class Document(db.Model):
    __tablename__ = 'documents'
    document_id    = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.application_id'), nullable=False)
    document_name  = db.Column(db.String(150), nullable=False)
    document_path  = db.Column(db.String(255), nullable=False)
    uploaded_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'document_id': self.document_id,
            'application_id': self.application_id,
            'document_name': self.document_name,
            'document_path': self.document_path,
            'uploaded_at': str(self.uploaded_at)
        }

# ──────────────────────────────────────────────────
# NOTIFICATIONS
# ──────────────────────────────────────────────────
class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title           = db.Column(db.String(150), nullable=False)
    message         = db.Column(db.Text, nullable=False)
    status          = db.Column(db.Enum('Unread','Read'), default='Unread')
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'title': self.title, 'message': self.message,
            'status': self.status, 'created_at': str(self.created_at)
        }

# ──────────────────────────────────────────────────
# ACTIVITY LOGS
# ──────────────────────────────────────────────────
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    log_id    = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action    = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'log_id': self.log_id, 'user_id': self.user_id,
            'action': self.action, 'timestamp': str(self.timestamp)
        }
