from flask import Flask, current_app, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, UserNeed, Identity, AnonymousIdentity, identity_changed
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
principals = Principal(app)

# Define roles
admin_permission = Permission(RoleNeed('admin'))
operator_permission = Permission(RoleNeed('operator'))

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __init__(self, email, password, role):
        self.email = email
        self.password = generate_password_hash(password)
        self.role = role

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(email='admin@example.com', password='adminpass', role='admin')
        operator = User(email='operator@example.com', password='operatorpass', role='operator')
        db.session.add(admin)
        db.session.add(operator)
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# Identity loaded listener
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    print('Identity loaded')
    identity.user = current_user
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
        if current_user.role == 'admin':
            print('Admin role added')
            identity.provides.add(RoleNeed('admin'))
        if current_user.role == 'operator':
            print('Operator role added')
            identity.provides.add(RoleNeed('operator'))

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            if user.role == 'operator':
                return redirect(url_for('operator_dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/admin_dashboard')
@login_required
@admin_permission.require(http_exception=403)
def admin_dashboard():
    return "Admin Dashboard"

@app.route('/operator_dashboard')
@login_required
@operator_permission.require(http_exception=403)
def operator_dashboard():
    return "Operator Dashboard"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
