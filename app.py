import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from models import db, User, EncryptedFile, EncryptedNote
from crypto_utils import CryptoUtils
from datetime import datetime
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///graphical_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['USER_IMAGES_FOLDER'] = 'static/user_images'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
ALLOWED_FILE_TYPES = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar'}

db.init_app(app)

with app.app_context():
    db.create_all()


def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set


def calculate_distance(p1, p2):
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        if 'image' not in request.files:
            flash('No image uploaded!', 'danger')
            return redirect(url_for('register'))
        
        image = request.files['image']
        if image.filename == '':
            flash('No image selected!', 'danger')
            return redirect(url_for('register'))
        
        if image and allowed_file(image.filename, ALLOWED_EXTENSIONS):
            filename = secure_filename(f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}")
            full_path = os.path.join(app.config['USER_IMAGES_FOLDER'], filename)
            image.save(full_path)
            
            relative_path = f"user_images/{filename}"
            
            session['temp_user'] = {
                'username': username,
                'password': password,
                'image_path': relative_path
            }
            
            return redirect(url_for('select_points'))
        else:
            flash('Invalid image format! Use PNG, JPG, JPEG, GIF, or BMP.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/select_points')
def select_points():
    if 'temp_user' not in session:
        return redirect(url_for('register'))
    return render_template('select_points.html', image_path=session['temp_user']['image_path'])


@app.route('/save_points', methods=['POST'])
def save_points():
    if 'temp_user' not in session:
        return jsonify({'success': False, 'message': 'Session expired'}), 400
    
    data = request.get_json()
    points = data.get('points', [])
    
    if len(points) != 5:
        return jsonify({'success': False, 'message': 'Exactly 5 points required'}), 400
    
    temp_user = session['temp_user']
    
    encrypted_points, encryption_key = CryptoUtils.encrypt_click_points(points)
    
    new_user = User(
        username=temp_user['username'],
        image_path=temp_user['image_path'],
        encrypted_points=encrypted_points,
        encryption_key=encryption_key
    )
    new_user.set_password(temp_user['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    session.pop('temp_user', None)
    
    return jsonify({'success': True, 'message': 'Registration successful!'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash('Invalid username!', 'danger')
            return redirect(url_for('login'))
        
        if user.is_locked:
            flash('Account locked due to multiple failed attempts. Please contact support.', 'danger')
            return redirect(url_for('login'))
        
        if not user.check_password(password):
            flash('Invalid password!', 'danger')
            return redirect(url_for('login'))
        
        session['login_user_id'] = user.id
        session['login_attempts'] = 0
        
        return redirect(url_for('verify_points'))
    
    return render_template('login.html')


@app.route('/verify_points')
def verify_points():
    if 'login_user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['login_user_id'])
    if not user:
        return redirect(url_for('login'))
    
    attempts_left = 3 - session.get('login_attempts', 0)
    
    return render_template('verify_points.html', 
                         image_path=user.image_path,
                         attempts_left=attempts_left)


@app.route('/check_points', methods=['POST'])
def check_points():
    if 'login_user_id' not in session:
        return jsonify({'success': False, 'message': 'Session expired'}), 400
    
    user = User.query.get(session['login_user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 400
    
    data = request.get_json()
    clicked_points = data.get('points', [])
    
    if len(clicked_points) != 5:
        return jsonify({'success': False, 'message': 'Exactly 5 points required'}), 400
    
    try:
        original_points = CryptoUtils.decrypt_click_points(
            user.encrypted_points, 
            user.encryption_key
        )
    except Exception as e:
        return jsonify({'success': False, 'message': 'Decryption error'}), 500
    
    tolerance = 25
    all_matched = True
    
    for i in range(5):
        distance = calculate_distance(clicked_points[i], original_points[i])
        if distance > tolerance:
            all_matched = False
            break
    
    if all_matched:
        user.failed_attempts = 0
        db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        session.pop('login_user_id', None)
        session.pop('login_attempts', None)
        
        return jsonify({'success': True, 'message': 'Login successful!'})
    else:
        session['login_attempts'] = session.get('login_attempts', 0) + 1
        user.failed_attempts += 1
        
        if session['login_attempts'] >= 3:
            user.is_locked = True
            db.session.commit()
            session.pop('login_user_id', None)
            session.pop('login_attempts', None)
            return jsonify({'success': False, 'message': 'Account locked due to multiple failed attempts', 'locked': True}), 403
        
        db.session.commit()
        attempts_left = 3 - session['login_attempts']
        
        return jsonify({'success': False, 'message': f'Points do not match! {attempts_left} attempts left.'}), 401


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    files = EncryptedFile.query.filter_by(user_id=user.id).all()
    notes = EncryptedNote.query.filter_by(user_id=user.id).all()
    
    return render_template('dashboard.html', user=user, files=files, notes=notes)


@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash('No file uploaded!', 'danger')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    codeword = request.form.get('codeword')
    
    if not codeword:
        flash('Codeword is required!', 'danger')
        return redirect(url_for('dashboard'))
    
    if file.filename == '':
        flash('No file selected!', 'danger')
        return redirect(url_for('dashboard'))
    
    if file:
        file_data = file.read()
        
        encrypted_data, salt = CryptoUtils.encrypt_file_with_codeword(file_data, codeword)
        
        encrypted_filename = f"enc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(8)}.enc"
        encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename)
        
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        encrypted_file = EncryptedFile(
            user_id=session['user_id'],
            original_filename=secure_filename(file.filename),
            encrypted_filename=encrypted_filename,
            salt=salt,
            file_size=len(file_data)
        )
        
        db.session.add(encrypted_file)
        db.session.commit()
        
        flash('File encrypted and uploaded successfully!', 'success')
        return redirect(url_for('dashboard'))


@app.route('/decrypt_file/<int:file_id>', methods=['POST'])
def decrypt_file(file_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    encrypted_file = EncryptedFile.query.get(file_id)
    
    if not encrypted_file or encrypted_file.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'File not found'}), 404
    
    codeword = request.form.get('codeword')
    
    if not codeword:
        return jsonify({'success': False, 'message': 'Codeword required'}), 400
    
    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_file.encrypted_filename)
    
    try:
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = CryptoUtils.decrypt_file_with_codeword(
            encrypted_data, 
            codeword, 
            encrypted_file.salt
        )
        
        temp_filename = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{encrypted_file.original_filename}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        with open(temp_path, 'wb') as f:
            f.write(decrypted_data)
        
        return jsonify({
            'success': True, 
            'download_url': url_for('download_decrypted', filename=temp_filename)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Invalid codeword or decryption failed'}), 400


@app.route('/download_decrypted/<filename>')
def download_decrypted(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        flash('File not found!', 'danger')
        return redirect(url_for('dashboard'))
    
    original_name = filename.split('_', 2)[2] if '_' in filename else filename
    
    response = send_file(file_path, as_attachment=True, download_name=original_name)
    
    try:
        os.remove(file_path)
    except:
        pass
    
    return response


@app.route('/delete_file/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    encrypted_file = EncryptedFile.query.get(file_id)
    
    if not encrypted_file or encrypted_file.user_id != session['user_id']:
        flash('File not found!', 'danger')
        return redirect(url_for('dashboard'))
    
    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_file.encrypted_filename)
    
    try:
        if os.path.exists(encrypted_path):
            os.remove(encrypted_path)
    except:
        pass
    
    db.session.delete(encrypted_file)
    db.session.commit()
    
    flash('File deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/add_note', methods=['POST'])
def add_note():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not title or not content:
        flash('Title and content are required!', 'danger')
        return redirect(url_for('dashboard'))
    
    key = CryptoUtils.generate_key()
    encrypted_content = CryptoUtils.encrypt_data(content, key)
    
    note = EncryptedNote(
        user_id=session['user_id'],
        title=title,
        encrypted_content=encrypted_content.decode(),
        encryption_key=key.decode()
    )
    
    db.session.add(note)
    db.session.commit()
    
    flash('Note saved and encrypted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/view_note/<int:note_id>')
def view_note(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    note = EncryptedNote.query.get(note_id)
    
    if not note or note.user_id != session['user_id']:
        flash('Note not found!', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        decrypted_content = CryptoUtils.decrypt_data(
            note.encrypted_content, 
            note.encryption_key.encode()
        )
        return render_template('view_note.html', note=note, content=decrypted_content.decode())
    except Exception as e:
        flash('Error decrypting note!', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    note = EncryptedNote.query.get(note_id)
    
    if not note or note.user_id != session['user_id']:
        flash('Note not found!', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(note)
    db.session.commit()
    
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
