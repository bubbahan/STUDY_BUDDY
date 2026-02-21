"""
Live external API validator for StudyBuddy — tests OpenRouter AI endpoints.
Usage: python test_external_api.py
"""
import requests
import uuid
import time

BASE = 'http://127.0.0.1:5000'

# ----------------------------
# Step 1 — Authenticate
# ----------------------------
email = 'ext_test_' + str(uuid.uuid4())[:8] + '@sb.com'
r = requests.post(BASE + '/api/auth/register', json={
    'name': 'AI Tester', 'email': email,
    'password': 'pass1234', 'study_hours_per_day': 4,
    'preference': 'morning', 'exam_date': '2026-04-30'
})
print('Register:', r.status_code)

r = requests.post(BASE + '/api/auth/login', json={'email': email, 'password': 'pass1234'})
token = r.json().get('token', '')
H = {'Authorization': 'Bearer ' + token}
print('Login:', r.status_code, '| Got token:', bool(token))

if not token:
    print('ABORT: Could not get token.')
    raise SystemExit(1)

# Add a subject (needed for AI Tips to have context)
r = requests.post(BASE + '/api/subjects/', json={
    'name': 'Physics', 'difficulty': 'High', 'frequency': 2,
    'exam_date': '2026-04-30', 'study_goal': '2 hrs'
}, headers=H)
print('Add subject:', r.status_code)

# ----------------------------
# Step 2 — Test /api/ai/tips
# ----------------------------
print('\n--- Testing POST /api/ai/tips ---')
start = time.time()
r = requests.post(BASE + '/api/ai/tips', headers=H, timeout=60)
elapsed = round(time.time() - start, 1)
print('Status:', r.status_code, '| Time:', elapsed, 's')

if r.status_code == 200:
    result = r.json().get('result', '')
    print('Response length:', len(result), 'chars')
    print('First 300 chars:')
    print(result[:300])
    print('[PASS] /api/ai/tips')
else:
    try:
        err = r.json()
    except Exception:
        err = r.text
    print('[FAIL] /api/ai/tips ->', err)

# ----------------------------
# Step 3 — Test /api/ai/timetable
# ----------------------------
print('\n--- Testing POST /api/ai/timetable ---')
start = time.time()
r = requests.post(BASE + '/api/ai/timetable', headers=H, json={
    'subjects': [
        {'name': 'Physics', 'priority': 'High', 'notes': 'Weak in thermodynamics'},
        {'name': 'Mathematics', 'priority': 'Medium', 'notes': ''}
    ],
    'exam_date': '2026-04-30',
    'study_hours': 5,
    'preference': 'morning',
    'instructions': 'Include a short revision session on weekends'
}, timeout=60)
elapsed = round(time.time() - start, 1)
print('Status:', r.status_code, '| Time:', elapsed, 's')

if r.status_code == 200:
    result = r.json().get('result', '')
    print('Response length:', len(result), 'chars')
    print('First 500 chars:')
    print(result[:500])
    print('[PASS] /api/ai/timetable')
else:
    try:
        err = r.json()
    except Exception:
        err = r.text
    print('[FAIL] /api/ai/timetable ->', err)

# ----------------------------
# Step 4 — Direct OpenRouter ping
# ----------------------------
print('\n--- Direct OpenRouter API ping ---')
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from config import Config

start = time.time()
r2 = requests.post(
    Config.OPENROUTER_BASE_URL,
    headers={
        'Authorization': 'Bearer ' + Config.OPENROUTER_API_KEY,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:5000',
        'X-Title': 'StudyBuddy'
    },
    json={
        'model': Config.OPENROUTER_MODEL,
        'messages': [{'role': 'user', 'content': 'Reply with: pong'}],
        'max_tokens': 10
    },
    timeout=30
)
elapsed = round(time.time() - start, 1)
print('OpenRouter direct status:', r2.status_code, '| Time:', elapsed, 's')
if r2.status_code == 200:
    reply = r2.json()['choices'][0]['message']['content'].strip()
    print('Model reply:', reply)
    print('Model used:', r2.json().get('model', Config.OPENROUTER_MODEL))
    print('[PASS] OpenRouter API key and model are valid')
else:
    print('[FAIL] OpenRouter error:', r2.text[:300])
