from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.models import Application, ActivityLog, Notification, User

app_bp = Blueprint('applications', __name__)

# ──────────────────────────────────────────────────
# CREATE APPLICATION
# ──────────────────────────────────────────────────
@app_bp.route('/applications', methods=['POST'])
@jwt_required()
def create_application():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') != 'applicant':
        return jsonify({'error': 'Only applicants can submit applications'}), 403
    data = request.get_json() or {}
    required = ['building_name','building_type','address','city','state','pincode']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    application = Application(
        applicant_id   = user_id,
        building_name  = data['building_name'],
        building_type  = data['building_type'],
        address        = data['address'],
        city           = data['city'],
        state          = data['state'],
        pincode        = data['pincode'],
        priority_level = data.get('priority_level', 'Medium'),
        remarks        = data.get('remarks', '')
    )
    db.session.add(application)
    db.session.commit()

    admins = User.query.filter_by(role='admin').all()
    for admin in admins:
        notif = Notification(user_id=admin.id,
                             title='New Application Submitted',
                             message=f'New application for {application.building_name} has been submitted.')
        db.session.add(notif)

    notif_app = Notification(user_id=user_id,
                              title='Application Submitted',
                              message=f'Your application for {application.building_name} is received and pending review.')
    db.session.add(notif_app)

    log = ActivityLog(user_id=user_id,
                      action=f'Submitted application for {application.building_name}')
    db.session.add(log)
    db.session.commit()

    return jsonify({'message': 'Application submitted', 'application': application.to_dict()}), 201

# ──────────────────────────────────────────────────
# GET ALL APPLICATIONS
# ──────────────────────────────────────────────────
@app_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')
    if role in ['admin', 'inspector']:
        apps = Application.query.order_by(Application.application_date.desc()).all()
    else:
        apps = Application.query.filter_by(applicant_id=user_id).order_by(Application.application_date.desc()).all()
    return jsonify([a.to_dict() for a in apps]), 200

# ──────────────────────────────────────────────────
# GET SINGLE APPLICATION
# ──────────────────────────────────────────────────
@app_bp.route('/applications/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')
    application = Application.query.get_or_404(app_id)
    if role == 'applicant' and application.applicant_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    return jsonify(application.to_dict()), 200

# ──────────────────────────────────────────────────
# UPDATE APPLICATION
# ──────────────────────────────────────────────────
@app_bp.route('/applications/<int:app_id>', methods=['PUT'])
@jwt_required()
def update_application(app_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')
    application = Application.query.get_or_404(app_id)

    if role == 'applicant' and application.applicant_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json() or {}
    application.building_name  = data.get('building_name', application.building_name)
    application.building_type  = data.get('building_type', application.building_type)
    application.address        = data.get('address', application.address)
    application.city           = data.get('city', application.city)
    application.state          = data.get('state', application.state)
    application.pincode        = data.get('pincode', application.pincode)
    application.priority_level = data.get('priority_level', application.priority_level)
    application.remarks        = data.get('remarks', application.remarks)

    if role in ['admin', 'inspector']:
        application.current_status = data.get('current_status', application.current_status)
        notif = Notification(user_id=application.applicant_id,
                             title='Application Status Updated',
                             message=f'Your application for {application.building_name} is now: {application.current_status}')
        db.session.add(notif)

    log = ActivityLog(user_id=user_id,
                      action=f'Updated application #{app_id}')
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Application updated', 'application': application.to_dict()}), 200

# ──────────────────────────────────────────────────
# DELETE APPLICATION
# ──────────────────────────────────────────────────
@app_bp.route('/applications/<int:app_id>', methods=['DELETE'])
@jwt_required()
def delete_application(app_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Only admins can delete applications'}), 403
    application = Application.query.get_or_404(app_id)
    db.session.delete(application)
    log = ActivityLog(user_id=int(get_jwt_identity()), action=f'Deleted application #{app_id}')
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Application deleted'}), 200
