from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from extensions import db
from models.models import Inspection, Followup, NOC, Document, Notification, ActivityLog, Application, User
from datetime import datetime, timedelta
import os

inspection_bp  = Blueprint('inspections', __name__)
followup_bp    = Blueprint('followups', __name__)
noc_bp         = Blueprint('noc', __name__)
document_bp    = Blueprint('documents', __name__)
notification_bp= Blueprint('notifications', __name__)
dashboard_bp   = Blueprint('dashboard', __name__)

ALLOWED_EXTENSIONS = {'pdf','png','jpg','jpeg','gif','doc','docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ══════════════════════════════════════════════════
# INSPECTIONS
# ══════════════════════════════════════════════════
@inspection_bp.route('/inspections', methods=['POST'])
@jwt_required()
def create_inspection():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') not in ['admin', 'inspector']:
        return jsonify({'error': 'Not authorized'}), 403
    data = request.get_json() or {}
    required = ['application_id','inspector_id','inspection_date']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    insp = Inspection(
        application_id    = data['application_id'],
        inspector_id      = data['inspector_id'],
        inspection_date   = datetime.strptime(data['inspection_date'], '%Y-%m-%d %H:%M:%S'),
        inspection_status = data.get('inspection_status', 'Scheduled'),
        findings          = data.get('findings', ''),
        remarks           = data.get('remarks', '')
    )
    db.session.add(insp)

    application = Application.query.get(data['application_id'])
    if application:
        application.current_status = 'Under Inspection'
        notif = Notification(user_id=application.applicant_id,
                             title='Inspection Scheduled',
                             message=f'Inspection for {application.building_name} scheduled on {data["inspection_date"]}')
        db.session.add(notif)

    log = ActivityLog(user_id=user_id, action=f'Inspection created for app #{data["application_id"]}')
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Inspection created', 'inspection': insp.to_dict()}), 201

@inspection_bp.route('/inspections', methods=['GET'])
@jwt_required()
def get_inspections():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') == 'inspector':
        insps = Inspection.query.filter_by(inspector_id=user_id).order_by(Inspection.created_at.desc()).all()
    else:
        insps = Inspection.query.order_by(Inspection.created_at.desc()).all()
    return jsonify([i.to_dict() for i in insps]), 200

@inspection_bp.route('/inspections/<int:insp_id>', methods=['PUT'])
@jwt_required()
def update_inspection(insp_id):
    claims = get_jwt()
    if claims.get('role') not in ['admin', 'inspector']:
        return jsonify({'error': 'Not authorized'}), 403
    insp = Inspection.query.get_or_404(insp_id)
    data = request.get_json() or {}
    insp.inspection_status = data.get('inspection_status', insp.inspection_status)
    insp.findings          = data.get('findings', insp.findings)
    insp.remarks           = data.get('remarks', insp.remarks)

    if insp.inspection_status == 'Failed':
        application = Application.query.get(insp.application_id)
        if application:
            application.current_status = 'Follow-up Required'
            notif = Notification(user_id=application.applicant_id,
                                 title='Follow-up Required',
                                 message=f'Inspection for {application.building_name} failed. Follow-up required.')
            db.session.add(notif)

    log = ActivityLog(user_id=int(get_jwt_identity()), action=f'Updated inspection #{insp_id}')
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Inspection updated', 'inspection': insp.to_dict()}), 200

@inspection_bp.route('/inspections/upload-image/<int:insp_id>', methods=['POST'])
@jwt_required()
def upload_inspection_image(insp_id):
    claims = get_jwt()
    if claims.get('role') not in ['admin', 'inspector']:
        return jsonify({'error': 'Not authorized'}), 403
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    filename = secure_filename(file.filename)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'inspections', filename)
    file.save(path)

    insp = Inspection.query.get_or_404(insp_id)
    insp.uploaded_images = filename
    db.session.commit()
    return jsonify({'message': 'Image uploaded', 'filename': filename}), 200

# ══════════════════════════════════════════════════
# FOLLOW-UPS
# ══════════════════════════════════════════════════
@followup_bp.route('/followups', methods=['POST'])
@jwt_required()
def create_followup():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') not in ['admin', 'inspector']:
        return jsonify({'error': 'Not authorized'}), 403
    data = request.get_json() or {}
    if not data.get('inspection_id'):
        return jsonify({'error': 'inspection_id required'}), 400

    fu = Followup(
        inspection_id    = data['inspection_id'],
        followup_date    = datetime.strptime(data['followup_date'], '%Y-%m-%d %H:%M:%S') if data.get('followup_date') else None,
        followup_status  = data.get('followup_status', 'Pending'),
        followup_remarks = data.get('followup_remarks', '')
    )
    db.session.add(fu)
    log = ActivityLog(user_id=user_id, action=f'Follow-up created for inspection #{data["inspection_id"]}')
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Follow-up created', 'followup': fu.to_dict()}), 201

@followup_bp.route('/followups', methods=['GET'])
@jwt_required()
def get_followups():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') == 'inspector':
        insps = [i.inspection_id for i in Inspection.query.filter_by(inspector_id=user_id).all()]
        fus = Followup.query.filter(Followup.inspection_id.in_(insps)).all()
    else:
        fus = Followup.query.all()
    return jsonify([f.to_dict() for f in fus]), 200

@followup_bp.route('/followups/<int:fu_id>', methods=['PUT'])
@jwt_required()
def update_followup(fu_id):
    claims = get_jwt()
    if claims.get('role') not in ['admin', 'inspector']:
        return jsonify({'error': 'Not authorized'}), 403
    fu = Followup.query.get_or_404(fu_id)
    data = request.get_json() or {}
    fu.followup_status  = data.get('followup_status', fu.followup_status)
    fu.followup_remarks = data.get('followup_remarks', fu.followup_remarks)
    db.session.commit()
    return jsonify({'message': 'Follow-up updated', 'followup': fu.to_dict()}), 200

# ══════════════════════════════════════════════════
# NOC
# ══════════════════════════════════════════════════
@noc_bp.route('/noc/approve', methods=['POST'])
@jwt_required()
def approve_noc():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Only admin can approve NOC'}), 403
    data = request.get_json() or {}
    if not data.get('application_id'):
        return jsonify({'error': 'application_id required'}), 400

    noc = NOC.query.filter_by(application_id=data['application_id']).first()
    if not noc:
        noc = NOC(application_id=data['application_id'])
        db.session.add(noc)

    noc.approval_status = 'Approved'
    noc.approved_by     = user_id
    noc.issue_date      = datetime.utcnow()
    noc.expiry_date     = datetime.utcnow() + timedelta(days=365)

    application = Application.query.get(data['application_id'])
    if application:
        application.current_status = 'Approved'
        notif = Notification(user_id=application.applicant_id,
                             title='NOC Approved!',
                             message=f'NOC for {application.building_name} has been APPROVED. Valid till {noc.expiry_date.strftime("%d-%m-%Y")}.')
        db.session.add(notif)

    log = ActivityLog(user_id=user_id, action=f'NOC Approved for application #{data["application_id"]}')
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'NOC Approved', 'noc': noc.to_dict()}), 200

@noc_bp.route('/noc/reject', methods=['POST'])
@jwt_required()
def reject_noc():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Only admin can reject NOC'}), 403
    data = request.get_json() or {}
    if not data.get('application_id'):
        return jsonify({'error': 'application_id required'}), 400

    noc = NOC.query.filter_by(application_id=data['application_id']).first()
    if not noc:
        noc = NOC(application_id=data['application_id'])
        db.session.add(noc)

    noc.approval_status  = 'Rejected'
    noc.approved_by      = user_id
    noc.rejection_reason = data.get('rejection_reason', 'Does not meet fire safety standards')

    application = Application.query.get(data['application_id'])
    if application:
        application.current_status = 'Rejected'
        notif = Notification(user_id=application.applicant_id,
                             title='NOC Rejected',
                             message=f'NOC for {application.building_name} has been REJECTED. Reason: {noc.rejection_reason}')
        db.session.add(notif)

    log = ActivityLog(user_id=user_id, action=f'NOC Rejected for application #{data["application_id"]}')
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'NOC Rejected', 'noc': noc.to_dict()}), 200

@noc_bp.route('/noc/<int:application_id>', methods=['GET'])
@jwt_required()
def get_noc(application_id):
    noc = NOC.query.filter_by(application_id=application_id).first()
    if not noc:
        return jsonify({'error': 'NOC not found'}), 404
    return jsonify(noc.to_dict()), 200

@noc_bp.route('/noc', methods=['GET'])
@jwt_required()
def get_all_noc():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') == 'applicant':
        app_ids = [a.application_id for a in Application.query.filter_by(applicant_id=user_id).all()]
        nocs = NOC.query.filter(NOC.application_id.in_(app_ids)).all()
    else:
        nocs = NOC.query.all()
    return jsonify([n.to_dict() for n in nocs]), 200

# ══════════════════════════════════════════════════
# DOCUMENTS
# ══════════════════════════════════════════════════
@document_bp.route('/upload-document', methods=['POST'])
@jwt_required()
def upload_document():
    user_id = int(get_jwt_identity())
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    application_id = request.form.get('application_id')
    if not application_id:
        return jsonify({'error': 'application_id required'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    filename = secure_filename(file.filename)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', filename)
    file.save(path)

    doc = Document(application_id=application_id, document_name=filename,
                   document_path=f'uploads/documents/{filename}')
    db.session.add(doc)
    log = ActivityLog(user_id=user_id, action=f'Document uploaded for app #{application_id}')
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Document uploaded', 'document': doc.to_dict()}), 201

@document_bp.route('/documents/<int:application_id>', methods=['GET'])
@jwt_required()
def get_documents(application_id):
    docs = Document.query.filter_by(application_id=application_id).all()
    return jsonify([d.to_dict() for d in docs]), 200

# ══════════════════════════════════════════════════
# NOTIFICATIONS
# ══════════════════════════════════════════════════
@notification_bp.route('/notifications/<int:user_id>', methods=['GET'])
@jwt_required()
def get_notifications(user_id):
    user_id_token = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') != 'admin' and user_id_token != user_id:
        return jsonify({'error': 'Access denied'}), 403
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notifs]), 200

@notification_bp.route('/notifications/mark-read/<int:notif_id>', methods=['PUT'])
@jwt_required()
def mark_notification_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    notif.status = 'Read'
    db.session.commit()
    return jsonify({'message': 'Marked as read'}), 200

# ══════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════
@dashboard_bp.route('/dashboard/admin', methods=['GET'])
@jwt_required()
def admin_dashboard():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    total_apps     = Application.query.count()
    pending        = Application.query.filter_by(current_status='Pending').count()
    under_insp     = Application.query.filter_by(current_status='Under Inspection').count()
    followup_req   = Application.query.filter_by(current_status='Follow-up Required').count()
    approved       = Application.query.filter_by(current_status='Approved').count()
    rejected       = Application.query.filter_by(current_status='Rejected').count()
    total_users    = User.query.count()
    total_insps    = Inspection.query.count()
    unread_notifs  = Notification.query.filter_by(status='Unread').count()

    recent_apps = Application.query.order_by(Application.application_date.desc()).limit(5).all()

    return jsonify({
        'total_applications': total_apps,
        'pending': pending,
        'under_inspection': under_insp,
        'followup_required': followup_req,
        'approved': approved,
        'rejected': rejected,
        'total_users': total_users,
        'total_inspections': total_insps,
        'unread_notifications': unread_notifs,
        'recent_applications': [a.to_dict() for a in recent_apps]
    }), 200

@dashboard_bp.route('/dashboard/inspector', methods=['GET'])
@jwt_required()
def inspector_dashboard():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') != 'inspector':
        return jsonify({'error': 'Inspector access required'}), 403

    my_insps   = Inspection.query.filter_by(inspector_id=user_id).count()
    scheduled  = Inspection.query.filter_by(inspector_id=user_id, inspection_status='Scheduled').count()
    completed  = Inspection.query.filter_by(inspector_id=user_id, inspection_status='Completed').count()
    failed     = Inspection.query.filter_by(inspector_id=user_id, inspection_status='Failed').count()

    insp_ids = [i.inspection_id for i in Inspection.query.filter_by(inspector_id=user_id).all()]
    pending_fu = Followup.query.filter(Followup.inspection_id.in_(insp_ids), Followup.followup_status=='Pending').count()

    recent_insps = Inspection.query.filter_by(inspector_id=user_id).order_by(Inspection.created_at.desc()).limit(5).all()

    return jsonify({
        'my_inspections': my_insps,
        'scheduled': scheduled,
        'completed': completed,
        'failed': failed,
        'pending_followups': pending_fu,
        'recent_inspections': [i.to_dict() for i in recent_insps]
    }), 200

@dashboard_bp.route('/dashboard/applicant', methods=['GET'])
@jwt_required()
def applicant_dashboard():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') != 'applicant':
        return jsonify({'error': 'Applicant access required'}), 403

    total   = Application.query.filter_by(applicant_id=user_id).count()
    pending = Application.query.filter_by(applicant_id=user_id, current_status='Pending').count()
    approved= Application.query.filter_by(applicant_id=user_id, current_status='Approved').count()
    rejected= Application.query.filter_by(applicant_id=user_id, current_status='Rejected').count()
    unread  = Notification.query.filter_by(user_id=user_id, status='Unread').count()

    recent_apps = Application.query.filter_by(applicant_id=user_id).order_by(Application.application_date.desc()).limit(5).all()

    return jsonify({
        'total_applications': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'unread_notifications': unread,
        'recent_applications': [a.to_dict() for a in recent_apps]
    }), 200
