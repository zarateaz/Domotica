import cv2, face_recognition, numpy as np, os, json, hashlib, random, smtplib, pandas as pd, threading
from flask import Flask, Response, render_template_string, jsonify, request
from cryptography.fernet import Fernet
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
BASE_DIR = "/home/zarate/Domotica"
LOGS_DIR = os.path.join(BASE_DIR, "logs")
FOLDER_ROSTROS = os.path.join(BASE_DIR, "rostros")
DB_JSON = os.path.join(BASE_DIR, "database.json")
KEY_FILE = os.path.join(BASE_DIR, "master.key")

if not os.path.exists(LOGS_DIR): os.makedirs(LOGS_DIR)

# Configuración Email Segura
CONFIG_EMAIL = {"usuario": "zaratepkm.6@gmail.com", "password": "sgxxufyttiggkxhl"}

scan_active, pending_user, current_otp = False, None, None
known_encodings, known_names = [], []

def get_cipher():
    if not os.path.exists(KEY_FILE): return None
    with open(KEY_FILE, "rb") as f: return Fernet(f.read())

def load_security():
    global known_encodings, known_names, pending_user
    cipher = get_cipher()
    if not cipher: return
    known_encodings, known_names, pending_user = [], [], None
    for f in os.listdir(FOLDER_ROSTROS):
        if f.endswith(".enc"):
            try:
                with open(os.path.join(FOLDER_ROSTROS, f), "rb") as enc_f:
                    data = cipher.decrypt(enc_f.read())
                    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                    enc = face_recognition.face_encodings(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    if enc:
                        known_encodings.append(enc[0])
                        known_names.append(os.path.splitext(f)[0].upper().strip())
            except: continue
    print(f"🚀 SENATI CORE: {len(known_names)} ESTUDIANTES LISTOS.")

load_security()

def marcar_asistencia(nombre, tipo="ALUMNO"):
    archivo = os.path.join(LOGS_DIR, f"asistencia_{tipo.lower()}s.xlsx")
    nuevo = {"NOMBRE/DNI": nombre, "FECHA": datetime.now().strftime("%d/%m/%Y"), "HORA": datetime.now().strftime("%H:%M:%S")}
    df = pd.read_excel(archivo) if os.path.exists(archivo) else pd.DataFrame()
    pd.concat([df, pd.DataFrame([nuevo])]).to_excel(archivo, index=False)

@app.route('/reload', methods=['POST'])
def reload(): load_security(); return jsonify({"status": "ok"})

@app.route('/request_otp', methods=['POST'])
def request_otp():
    global current_otp, pending_user
    if not pending_user: return jsonify({"success": False, "msg": "Identifícate primero"})
    
    try:
        with open(DB_JSON, "r") as f: db = json.load(f)
        user_data = db.get(pending_user)
        
        # Lógica de Desencriptación de Email
        cipher = get_cipher()
        email_enc = user_data.get("email") # Soporta campo antiguo o nuevo email_enc
        if not email_enc: return jsonify({"success": False, "msg": "Sin correo registrado"})
        
        try:
            # Intentar desencriptar (Si es nuevo formato cifrado)
            email_dest = cipher.decrypt(email_enc.encode()).decode()
        except:
            # Si falla, es porque es el formato antiguo (texto plano), lo usamos directo
            email_dest = email_enc

        current_otp = str(random.randint(100000, 999999))
        
        def send():
            try:
                msg = MIMEText(f"SISTEMA DE SEGURIDAD ZARATE OS\n\nTu código de acceso temporal para SENATI es: {current_otp}")
                msg['Subject'] = '🔑 RECUPERACIÓN DE ACCESO - DOMÓTICA'
                msg['From'], msg['To'] = CONFIG_EMAIL["usuario"], email_dest
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                    s.login(CONFIG_EMAIL["usuario"], CONFIG_EMAIL["password"])
                    s.sendmail(msg['From'], [msg['To']], msg.as_string())
            except Exception as e: print(f"Error SMTP: {e}")
            
        threading.Thread(target=send).start()
        return jsonify({"success": True, "msg": "Código de seguridad enviado!"})
    except Exception as e:
        return jsonify({"success": False, "msg": f"Error: {str(e)}"})

@app.route('/verify', methods=['POST'])
def verify():
    global pending_user, current_otp
    data = request.json
    code = data.get("code")
    if data.get("isGuest"):
        marcar_asistencia(code, "INVITADO")
        return jsonify({"success": True, "type": "guest"})
    
    with open(DB_JSON, "r") as f: db = json.load(f)
    valido = False
    if current_otp and code == current_otp: valido = True
    elif db.get(pending_user, {}).get("pin") == hashlib.sha256(code.encode()).hexdigest(): valido = True
    
    if valido:
        marcar_asistencia(pending_user, "ALUMNO")
        current_otp = None
        return jsonify({"success": True, "type": "student", "name": pending_user})
    return jsonify({"success": False})

@app.route('/get_status')
def get_status(): return jsonify({"active": scan_active, "user": pending_user})

@app.route('/toggle_scan', methods=['POST'])
def toggle():
    global scan_active, pending_user
    scan_active = not scan_active
    pending_user = None
    return jsonify({"status": scan_active})

def gen_frames():
    global scan_active, pending_user
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret: break
        if scan_active and not pending_user:
            rgb = cv2.cvtColor(cv2.resize(frame, (0,0), fx=0.25, fy=0.25), cv2.COLOR_BGR2RGB)
            locs = face_recognition.face_locations(rgb)
            if locs:
                encs = face_recognition.face_encodings(rgb, locs)
                for e in encs:
                    matches = face_recognition.compare_faces(known_encodings, e, 0.45)
                    if True in matches:
                        pending_user = known_names[matches.index(True)]
                        break
        _, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed(): return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html><html><head><title>ZARATE SENATI v13</title>
    <style>
        :root { --n: #00ffcc; --b: #000a12; --s: #004b8d; }
        body { background: var(--b); color: var(--n); font-family: 'Segoe UI', sans-serif; text-align: center; margin:0; overflow: hidden; }
        .cam-container { width: 400px; height: 400px; border-radius: 50%; border: 5px solid var(--s); margin: 30px auto; overflow: hidden; position: relative; box-shadow: 0 0 50px rgba(0,75,141,0.5); }
        #modal, #welcome { display: none; position: fixed; inset: 0; background: radial-gradient(circle, #001a2d 0%, #000a12 100%); z-index: 1000; }
        .keypad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; width: 300px; margin: 20px auto; }
        .key { border: 2px solid var(--n); padding: 20px; cursor: pointer; border-radius: 15px; font-size: 1.8em; color: var(--n); transition: 0.1s; background: rgba(0,255,204,0.05); }
        .key:active { background: var(--n); color: black; transform: scale(0.95); }
        #display { font-size: 3em; letter-spacing: 12px; height: 60px; color: white; margin-top: 20px; text-shadow: 0 0 10px var(--n); }
        .btn-main { padding: 15px 40px; border-radius: 30px; border: 1px solid var(--n); background: none; color: var(--n); cursor: pointer; font-weight: bold; font-size: 1.1em; }
        .logo-senati { width: 280px; filter: drop-shadow(0 0 15px var(--n)); margin-top: 50px; }
        .motivate { font-style: italic; color: #aaa; margin-top: 20px; font-size: 1.2em; }
    </style></head><body>
        <h1 style="margin-top:20px; letter-spacing: 5px;">[ SENATI BIOMETRIC CORE ]</h1>
        <div class="cam-container"><img src="/video_feed" style="width:100%"></div>
        <button onclick="fetch('/toggle_scan',{method:'POST'})" class="btn-main">ESCANEOR RADAR</button>
        <button onclick="openGuest()" class="btn-main" style="margin-left:15px; background: var(--s); border:none; color:white;">INVITADO</button>

        <div id="modal">
            <h2 id="m-title" style="margin-top:60px; font-size: 2em;"></h2>
            <div id="display"></div>
            <div class="keypad" id="keys"></div>
            <p onclick="otp()" style="color:#00ffcc; cursor:pointer; text-decoration:underline; opacity: 0.6;">¿OLVIDASTE TU PIN? RECUPERAR</p>
        </div>

        <div id="welcome">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Senati_Logo.png/800px-Senati_Logo.png" class="logo-senati">
            <h1 id="w-msg" style="font-size: 4.5em; color: white; margin: 20px 0;"></h1>
            <h2 style="color: var(--n); letter-spacing: 8px; font-size: 2.5em;">ACCESO AUTORIZADO</h2>
            <p class="motivate">"El futuro de la tecnología está en tus manos. ¡A estudiar!"</p>
        </div>

        <script>
            let code = ""; let isG = false; let open = false;
            function press(n) { if(code.length < (isG?8:6)) { code += n; upd(); } }
            function clr() { code = code.slice(0, -1); upd(); }
            function upd() { document.getElementById('display').innerText = isG ? code : "*".repeat(code.length); }
            function openGuest() { isG=true; open=true; document.getElementById('modal').style.display='block'; document.getElementById('m-title').innerText="INGRESE DNI INVITADO"; code=""; upd(); }
            function otp() { fetch('/request_otp', {method:'POST'}).then(r=>r.json()).then(d=>alert(d.msg)); }

            function send() {
                fetch('/verify', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({code:code, isGuest:isG})})
                .then(r=>r.json()).then(d => {
                    if(d.success) {
                        document.getElementById('modal').style.display='none';
                        document.getElementById('welcome').style.display='block';
                        document.getElementById('w-msg').innerText = d.type=="student" ? "HOLA " + d.name.split(' ')[0] : "INVITADO";
                        setTimeout(() => location.reload(), 5000);
                    } else { alert("ERROR DE ACCESO"); code=""; upd(); }
                });
            }

            setInterval(() => {
                if(!open) {
                    fetch('/get_status').then(r=>r.json()).then(d => {
                        if(d.user) { open=true; document.getElementById('modal').style.display='block'; document.getElementById('m-title').innerText="HOLA "+d.user; }
                    });
                }
            }, 1000);

            let k = ""; for(let i=1; i<=9; i++) k += `<div class="key" onclick="press(${i})">${i}</div>`;
            k += `<div class="key" style="color:#ff4444" onclick="clr()">X</div><div class="key" onclick="press(0)">0</div><div class="key" style="color:var(--n)" onclick="send()">OK</div>`;
            document.getElementById('keys').innerHTML = k;
        </script>
    </body></html>
    """)

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, threaded=True)
