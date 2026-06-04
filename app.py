import os
import time
import string
import threading
import multiprocessing as mp
import fitz
import requests
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from ultracode import worker  # Importing the fast worker from original code

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------------------------------------
# TELEGRAM BOT CONFIGURATION
# ---------------------------------------------
TELEGRAM_BOT_TOKEN = "paste telegram bot token hear"
TELEGRAM_CHAT_ID = "paste telegram chat id hear"

# In-memory job storage (for local use)
jobs = {}

def bruteforce_job(job_id, pdf_path, start_year, end_year, first_letter, threads):
    manager = mp.Manager()
    found_event = manager.Event()
    queue = manager.Queue()
    
    if first_letter and first_letter in string.ascii_uppercase:
        letters_to_process = [first_letter]
    else:
        letters_to_process = list(string.ascii_uppercase)
        
    total_combs = len(letters_to_process) * (26**3) * (end_year - start_year + 1)
    
    if threads > len(letters_to_process):
        threads = len(letters_to_process)
        
    chunks = [[] for _ in range(threads)]
    for i, letter in enumerate(letters_to_process):
        chunks[i % threads].append(letter)
        
    jobs[job_id] = {
        'status': 'running',
        'progress': 0,
        'total': total_combs,
        'password': None,
        'unlocked_file': None,
        'speed': 0
    }
    
    processes = []
    for chunk in chunks:
        if chunk:
            p = mp.Process(target=worker, args=(pdf_path, chunk, start_year, end_year, found_event, queue))
            p.start()
            processes.append(p)
            
    tested_total = 0
    start_time = time.time()
    last_update_time = start_time
    last_tested = 0
    found_password = None
    
    while any(p.is_alive() for p in processes) or not queue.empty():
        if jobs[job_id].get('status') == 'cancelled':
            break
            
        try:
            msg = queue.get(timeout=0.2)
            if "found" in msg:
                found_password = msg["password"]
                found_event.set()
                break
            elif "tested" in msg:
                tested_total += msg["tested"]
                jobs[job_id]['progress'] = tested_total
                
                now = time.time()
                if now - last_update_time >= 0.5:
                    speed = (tested_total - last_tested) / (now - last_update_time)
                    jobs[job_id]['speed'] = int(speed)
                    last_update_time = now
                    last_tested = tested_total
        except:
            pass
            
    for p in processes:
        p.terminate()
        p.join()
        
    if found_password:
        jobs[job_id]['status'] = 'success'
        jobs[job_id]['password'] = found_password
        
        try:
            doc = fitz.open(pdf_path)
            doc.authenticate(found_password)
            unlocked_filename = "UNLOCKED_" + os.path.basename(pdf_path)
            unlocked_path = os.path.join(app.config['UPLOAD_FOLDER'], unlocked_filename)
            doc.save(unlocked_path)
            jobs[job_id]['unlocked_file'] = unlocked_filename
        except Exception as e:
            pass
    elif jobs[job_id].get('status') == 'cancelled':
        pass
    else:
        jobs[job_id]['status'] = 'failed'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/crack', methods=['POST'])
def start_crack():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    start_year = int(request.form.get('start_year', 1950))
    end_year = int(request.form.get('end_year', 2026))
    name_hint = request.form.get('name_hint', '').strip().upper()
    first_letter = name_hint[0] if name_hint else None
    threads = int(request.form.get('threads', max(1, mp.cpu_count())))
    
    filename = secure_filename(file.filename)
    job_id = str(int(time.time()))
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    file.save(pdf_path)
    
    t = threading.Thread(target=bruteforce_job, args=(job_id, pdf_path, start_year, end_year, first_letter, threads))
    t.start()
    
    return jsonify({'job_id': job_id})

@app.route('/api/status/<job_id>')
def job_status(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(jobs[job_id])

@app.route('/api/cancel/<job_id>', methods=['POST'])
def cancel_job(job_id):
    if job_id in jobs:
        jobs[job_id]['status'] = 'cancelled'
        return jsonify({'success': True})
    return jsonify({'error': 'Job not found'}), 404

@app.route('/api/download/<filename>')
def download(filename):
    from flask import send_from_directory
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return f"Error: File not found or expired. Please decrypt the file again. Details: {str(e)}", 404

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    import re
    import threading
    
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()
    
    if not name or not email or not message:
        return jsonify({"success": False, "error": "All fields are required"}), 400
        
    # 1. Strict Name Validation (Only letters and spaces, at least 3 characters)
    if not re.match(r'^[A-Za-z\s]{3,50}$', name):
        return jsonify({"success": False, "error": "Please enter a valid real name (letters only, min 3 chars)"}), 400
        
    # 2. Strict Email Validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
         return jsonify({"success": False, "error": "Please enter a genuine, valid email address"}), 400
         
    # Block short fake emails like "ok@gmail.com"
    local_part, domain = email.rsplit('@', 1)
    domain = domain.lower()
    
    if len(local_part) < 4:
         return jsonify({"success": False, "error": "Email prefix is too short. Please use a real email."}), 400
         
    fake_domains = ['test.com', 'example.com', 'mailinator.com', 'tempmail.com', '10minutemail.com', 'fake.com']
    if domain in fake_domains:
         return jsonify({"success": False, "error": "Disposable or fake email addresses are not allowed"}), 400
         
    if len(message) < 10:
         return jsonify({"success": False, "error": "Message is too short. Please explain your query."}), 400
    
    text = f"📩 *New Message from Aadhaar Tool*\n\n*Name:* {name}\n*Email:* {email}\n*Message:* {message}"
    
    # 3. Asynchronous Telegram Sending (Fast UI Response)
    def send_to_telegram(msg_text):
        if TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": msg_text,
                "parse_mode": "Markdown"
            }
            try:
                requests.post(url, json=payload, timeout=5)
            except Exception as e:
                pass

    t = threading.Thread(target=send_to_telegram, args=(text,))
    t.start()
            
    return jsonify({"success": True})

if __name__ == '__main__':
    print("🚀 Starting Ultracode Web GUI at http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
