# Graphical Password Authentication System

A comprehensive Flask web application implementing secure graphical password authentication using the **Pass Point Scheme** combined with **AES encryption** for file storage.

## Features

### 1. Pass Point Authentication
- **Dual-Factor Authentication**: Traditional password + graphical Pass Point selection
- **5 Secret Points**: Users select 5 click points on their personal image
- **Tolerance Verification**: ±25 pixel tolerance for easier point matching
- **Smart Image Scaling**: Images automatically scaled to optimal size (800x600 max) for better accuracy
- **Account Lockout**: Automatic lockout after 3 failed login attempts

### 2. File Encryption System
- **User-Specified Codeword**: Custom encryption key for each file
- **PBKDF2 Key Derivation**: 100,000 iterations with SHA-256
- **AES/Fernet Encryption**: Industry-standard encryption
- **No Codeword Storage**: Codewords are never stored, only salt is kept
- **Secure Decryption**: Re-enter codeword to decrypt files

### 3. Encrypted Notepad
- **Automatic Encryption**: Notes encrypted with AES/Fernet
- **Unique Keys**: Each note has its own encryption key
- **Secure Storage**: Notes stored encrypted in database
- **On-Demand Decryption**: View notes securely

### 4. Security Features
- **Password Hashing**: Werkzeug with salt
- **Click Point Encryption**: Coordinates encrypted with AES/Fernet
- **Session Management**: Secure Flask sessions
- **Failed Attempt Tracking**: Monitor and lock suspicious accounts
- **Multi-Layer Security**: Password + Graphical + File encryption

## How to Use

### Registration Process

1. **Navigate to Register Page**
   - Click "Register" in the navigation bar
   - Or visit `/register`

2. **Create Account**
   - Enter your desired username
   - Create a strong password
   - Upload a personal image (PNG, JPG, JPEG, GIF, BMP)
   - Click "Continue to Point Selection"

3. **Select Pass Points**
   - Your uploaded image will appear with a grid overlay
   - Click exactly **5 secret points** on the image in sequence
   - **Remember the location and order** - you'll need these to login!
   - Click "Complete Registration"

### Login Process

1. **Navigate to Login Page**
   - Click "Login" in the navigation bar
   - Or visit `/login`

2. **Enter Credentials**
   - Enter your username and password
   - Click "Continue"

3. **Verify Pass Points**
   - Your image will appear (automatically scaled for optimal viewing)
   - Click the **same 5 points** in the **same sequence**
   - Points must be within ±25 pixels of original locations (generous tolerance)
   - You have **3 attempts** before account lockout
   - Click "Verify & Login"

### Dashboard Features

#### Upload & Encrypt File

1. Click "Choose File" and select a file
2. Enter a custom **codeword** (remember this!)
3. Click "Encrypt & Upload"
4. File is encrypted with AES and stored securely

**Important**: The codeword is NOT stored anywhere. You must remember it to decrypt the file later!

#### Decrypt & Download File

1. Find your file in "My Encrypted Files"
2. Click "Decrypt" button
3. Enter the **same codeword** you used during upload
4. Click "Decrypt & Download"
5. File downloads in its original format

If you forget the codeword, the file **cannot be recovered**!

#### Add Encrypted Note

1. Enter a title for your note
2. Write your secret content
3. Click "Save Encrypted Note"
4. Note is automatically encrypted and stored

#### View Note

1. Find your note in "My Encrypted Notes"
2. Click "View"
3. Note is decrypted and displayed
4. Click "Back to Dashboard" or "Delete Note"

#### Delete Files/Notes

- Click "Delete" button next to any file or note
- Confirm the deletion
- Data is permanently removed

### Logout

- Click "Logout" in the navigation bar
- Session is cleared and you're redirected to home page

## Security Best Practices

### For Users

1. **Choose a Complex Password**: Use a mix of uppercase, lowercase, numbers, and symbols
2. **Select Unique Pass Points**: Don't choose obvious points (corners, center)
3. **Remember Point Order**: The sequence matters as much as the locations
4. **Use Strong Codewords**: Make file codewords long and complex
5. **Keep Codewords Safe**: Store them in a password manager
6. **Don't Share Credentials**: Never share your password, points, or codewords

### For Developers

1. **Password Security**: Werkzeug password hashing with salt
2. **Click Point Encryption**: AES/Fernet encryption of coordinates
3. **PBKDF2 Key Derivation**: 100,000 iterations prevents brute force
4. **No Codeword Storage**: Only salt stored, key re-derived on decrypt
5. **Session Security**: Flask sessions with secure secret key
6. **Account Lockout**: Prevents brute force Pass Point attacks

## Technical Stack

- **Backend**: Flask 3.1.2
- **Database**: SQLite with SQLAlchemy ORM
- **Encryption**: cryptography (Fernet/AES, PBKDF2)
- **Password Security**: Werkzeug
- **Image Processing**: Pillow
- **Frontend**: Bootstrap 5.3.0, Font Awesome 6.4.0
- **JavaScript**: Vanilla JS with HTML5 Canvas

## File Structure

```
├── app.py                    # Main Flask application
├── models.py                 # Database models (User, EncryptedFile, EncryptedNote)
├── crypto_utils.py           # Encryption utilities
├── templates/                # HTML templates
│   ├── base.html            # Base template with navbar
│   ├── index.html           # Landing page
│   ├── register.html        # Registration form
│   ├── select_points.html   # Pass Point selection
│   ├── login.html           # Login form
│   ├── verify_points.html   # Pass Point verification
│   ├── dashboard.html       # User dashboard
│   └── view_note.html       # Note viewer
├── static/
│   ├── css/
│   │   └── style.css        # Custom styles
│   ├── js/
│   │   ├── select_points.js # Point selection logic
│   │   ├── verify_points.js # Point verification logic
│   │   └── dashboard.js     # Dashboard interactions
│   ├── uploads/             # Encrypted files storage
│   └── user_images/         # User authentication images
└── graphical_auth.db        # SQLite database

```

## Database Schema

### User Table
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Hashed password (Werkzeug)
- `image_path`: Path to user's image
- `encrypted_points`: AES-encrypted click coordinates
- `encryption_key`: Key for decrypting click points
- `failed_attempts`: Counter for failed login attempts
- `is_locked`: Boolean for account lockout status
- `created_at`: Registration timestamp

### EncryptedFile Table
- `id`: Primary key
- `user_id`: Foreign key to User
- `original_filename`: Original file name
- `encrypted_filename`: Encrypted file name on disk
- `salt`: Base64-encoded salt for PBKDF2
- `file_size`: Original file size
- `uploaded_at`: Upload timestamp

### EncryptedNote Table
- `id`: Primary key
- `user_id`: Foreign key to User
- `title`: Note title
- `encrypted_content`: AES-encrypted note content
- `encryption_key`: Unique Fernet key for this note
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Environment Variables

- `SESSION_SECRET`: Flask session secret key (auto-generated if not set)

## Running the Application

```bash
python app.py
```

The application will run on `http://0.0.0.0:5000`

## Security Warnings

⚠️ **This is a development server. DO NOT use in production without:**
- Using a production WSGI server (Gunicorn, uWSGI)
- Setting up HTTPS/TLS encryption
- Implementing rate limiting
- Adding CSRF protection
- Setting secure session cookies
- Regular security audits

## Troubleshooting

### Can't Login - Points Not Matching
- Make sure you're clicking the exact same points in the same order
- Remember there's a ±10 pixel tolerance
- After 3 failed attempts, account is locked

### Forgot Codeword
- Unfortunately, if you forget the codeword, the file cannot be decrypted
- This is by design for maximum security
- Always keep codewords in a safe place

### Image Not Loading
- Check that image is in a supported format (PNG, JPG, JPEG, GIF, BMP)
- Try uploading a different image
- Clear browser cache

### Account Locked
- Contact system administrator to unlock
- (In development, delete user from database and re-register)

## License

This project is for educational and demonstration purposes.

## Credits

Developed as a comprehensive cybersecurity demonstration of:
- Graphical password authentication (Pass Point Scheme)
- AES encryption with PBKDF2 key derivation
- Multi-factor authentication
- Secure session management
