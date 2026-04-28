import os
import time
import threading
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

app = Flask(__name__)

def run_bot(cookie_string, thread_id, msg_list, delay, prefix):
    options = Options()
    # options.add_argument("--headless") # Render par headless zaroori hai
    driver = webdriver.Firefox(options=options)

    try:
        driver.get("https://www.facebook.com")
        
        # Cookie Parser: String se Dictionary banana
        for cookie in cookie_string.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})

        driver.refresh()
        time.sleep(5)

        # E2EE Chat URL
        driver.get(f"https://www.facebook.com/messages/t/{thread_id}")
        time.sleep(10)

        while True:
            for raw_msg in msg_list:
                full_message = f"{prefix} {raw_msg}".strip()
                
                # JAVASCRIPT INJECTION (Typing indicator bypass karne ke liye)
                script = """
                var msg = arguments[0];
                var textBox = document.querySelector('div[role="textbox"]');
                if(textBox) {
                    textBox.focus();
                    document.execCommand('insertText', false, msg);
                    return true;
                }
                return false;
                """
                
                success = driver.execute_script(script, full_message)
                
                if success:
                    # Send button par click
                    send_btn = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Press Enter to send"]')
                    send_btn.click()
                    print(f"Sent: {full_message}")
                
                time.sleep(int(delay))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cookies = request.form.get('cookies')
        thread_id = request.form.get('thread_id')
        prefix = request.form.get('prefix')
        delay = request.form.get('delay')
        
        # File handle karna
        msg_file = request.files['msg_file']
        messages = msg_file.read().decode('utf-8').splitlines()

        # Bot ko separate thread mein chalana taaki web page freeze na ho
        threading.Thread(target=run_bot, args=(cookies, thread_id, messages, delay, prefix)).start()
        return "Bot started successfully! Check your console."

    return '''
    <!DOCTYPE html>
    <html>
    <head><title>E2EE Messenger Bot</title></head>
    <body>
        <h2>Messenger E2EE Bot Dashboard</h2>
        <form method="POST" enctype="multipart/form-data">
            <textarea name="cookies" placeholder="Paste Cookies String here..." rows="5" style="width:100%"></textarea><br><br>
            <input type="text" name="thread_id" placeholder="E2EE Thread ID" style="width:100%"><br><br>
            <input type="text" name="prefix" placeholder="Message Prefix (Optional)" style="width:100%"><br><br>
            <input type="number" name="delay" placeholder="Delay in Seconds" style="width:100%"><br><br>
            <label>Upload Message File (.txt):</label><br>
            <input type="file" name="msg_file"><br><br>
            <button type="submit" style="padding:10px 20px; background:green; color:white;">Start Bot</button>
        </form>
    </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
