from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from extensions import db, bcrypt
from models.models import User, ActivityLog, Notification

auth_bp = Blueprint('auth', __name__)

# ──────────────────────────────────────────────────
# REGISTER
# ──────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    required = ['full_name','email','username','password','role']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 409

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        full_name    = data['full_name'],
        email        = data['email'],
        username     = data['username'],
        password     = hashed_pw,
        role         = data.get('role', 'applicant'),
        phone_number = data.get('phone_number', '')
    )
    db.session.add(user)
    db.session.commit()

    notif = Notification(user_id=user.id, title='Welcome to Fire NOC System',
                         message=f'Hello {user.full_name}, your account has been created successfully.')
    db.session.add(notif)
    db.session.commit()

    log = ActivityLog(user_id=user.id, action=f'New user registered: {user.username}')
    db.session.add(log)
    db.session.commit()

    return jsonify({'message': 'User registered successfully', 'user': user.to_dict()}), 201

# ──────────────────────────────────────────────────
# LOGIN
# ──────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )

    log = ActivityLog(user_id=user.id, action=f'{user.role} logged in: {user.username}')
    db.session.add(log)
    db.session.commit()

    return jsonify({'token': token, 'user': user.to_dict()}), 200

# ──────────────────────────────────────────────────
# PROFILE (GET / UPDATE)
# ──────────────────────────────────────────────────
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    identity = int(get_jwt_identity())
    user = User.query.get(identity)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    identity = int(get_jwt_identity())
    user = User.query.get(identity)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json() or {}
    user.full_name    = data.get('full_name', user.full_name)
    user.phone_number = data.get('phone_number', user.phone_number)
    if data.get('password'):
        user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200

# ──────────────────────────────────────────────────
# USERS LIST (admin only)
# ──────────────────────────────────────────────────
@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200
