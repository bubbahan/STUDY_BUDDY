import requests
import json
import uuid
from collections import Counter

BASE = 'http://127.0.0.1:5000'
PASS = []
FAIL = []

# Unique email per run so tests don't collide
TEST_EMAIL = 'test_' + str(uuid.uuid4())[:8] + '@sb.com'
print('Test email: ' + TEST_EMAIL)


def check(label, r, expected_status=None, check_key=None):
    ok = True
    try:
        body = r.json()
    except Exception:
        body = {}
    if expected_status and r.status_code != expected_status:
        ok = False
    if check_key and check_key not in body:
        ok = False
    tag = 'PASS' if ok else 'FAIL'
    print(f'[{tag}] {label}: {r.status_code} -> {str(body)[:140]}')
    (PASS if ok else FAIL).append(label)
    return body

print('\n====== AUTH ======')
r = requests.post(f'{BASE}/api/auth/register', json={
    'name': 'API Tester', 'email': TEST_EMAIL, 'password': 'pass1234',
    'study_hours_per_day': 5, 'preference': 'morning'
})
check('Register', r, 201)

r = requests.post(f'{BASE}/api/auth/login', json={'email': TEST_EMAIL, 'password': 'pass1234'})
body = check('Login', r, 200, 'token')
token = body.get('token', '')
H = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

print('\n====== USER PROFILE ======')
r = requests.get(f'{BASE}/api/user/profile', headers=H)
body = check('GET /user/profile', r, 200, 'alarm_sound')
print('  alarm_sound=' + str(body.get('alarm_sound')) + '  profile_photo=' + str(body.get('profile_photo')))

r = requests.put(f'{BASE}/api/user/update', json={'alarm_sound': 'chime', 'name': 'API Tester'}, headers=H)
check('PUT /user/update (alarm_sound=chime)', r, 200)

r = requests.get(f'{BASE}/api/user/profile', headers=H)
body = check('GET profile - verify alarm_sound saved', r, 200)
saved = body.get('alarm_sound')
print('  alarm_sound after save: ' + str(saved) + '  -> ' + ('CORRECT' if saved == 'chime' else 'WRONG!'))

r = requests.put(f'{BASE}/api/user/update', json={'email': TEST_EMAIL}, headers=H)
check('PUT update same email (should 200)', r, 200)

print('\n====== SUBJECTS ======')
r = requests.post(f'{BASE}/api/subjects/', json={
    'name': 'Physics', 'difficulty': 'High', 'frequency': 2,
    'exam_date': '2026-04-10', 'study_goal': '2 hrs'
}, headers=H)
body = check('POST /subjects/ Physics freq=2', r, 201, 'id')
phys_id = body.get('id')

r = requests.post(f'{BASE}/api/subjects/', json={
    'name': 'Mathematics', 'difficulty': 'Medium', 'frequency': 1,
    'exam_date': '2026-05-01', 'study_goal': '1 hrs'
}, headers=H)
body = check('POST /subjects/ Mathematics freq=1', r, 201, 'id')
maths_id = body.get('id')

r = requests.post(f'{BASE}/api/subjects/', json={'name': 'Physics'}, headers=H)
check('POST duplicate subject (expect 400)', r, 400)

r = requests.get(f'{BASE}/api/subjects/', headers=H)
body = check('GET /subjects/', r, 200)
if isinstance(body, list):
    for s in body:
        print('  ' + s['name'] + ': diff=' + s['difficulty'] + ' freq=' + str(s['frequency']) + ' exam=' + str(s['exam_date']) + ' goal=' + str(s['study_goal']))

r = requests.get(f'{BASE}/api/subjects/' + str(phys_id), headers=H)
check('GET /subjects/<id>', r, 200, 'name')

r = requests.put(f'{BASE}/api/subjects/' + str(phys_id), json={'study_goal': '3 hrs', 'frequency': 3}, headers=H)
body = check('PUT /subjects/<id> update', r, 200)
print('  Updated study_goal=' + str(body.get('study_goal')) + ' freq=' + str(body.get('frequency')))

print('\n====== SYLLABUS ======')
r = requests.post(f'{BASE}/api/syllabus/' + str(phys_id), json={'topic_name': 'Kinematics'}, headers=H)
body = check('POST /syllabus/ add Kinematics', r, 201, 'id')
topic1_id = body.get('id')

r = requests.post(f'{BASE}/api/syllabus/' + str(phys_id), json={'topic_name': 'Thermodynamics'}, headers=H)
body = check('POST /syllabus/ add Thermodynamics', r, 201, 'id')
topic2_id = body.get('id')

r = requests.post(f'{BASE}/api/syllabus/' + str(phys_id), json={'topic_name': 'Optics'}, headers=H)
body = check('POST /syllabus/ add Optics', r, 201, 'id')

r = requests.get(f'{BASE}/api/syllabus/' + str(phys_id), headers=H)
body = check('GET /syllabus/<subject_id>', r, 200, 'topics')
print('  total=' + str(body.get('total')) + ' completed=' + str(body.get('completed')) + ' percent=' + str(body.get('percent')) + '%')

r = requests.put(f'{BASE}/api/syllabus/' + str(topic1_id) + '/toggle', headers=H)
body = check('PUT /syllabus/<id>/toggle (mark done)', r, 200)
print('  topic1 completed=' + str(body.get('completed')))

r = requests.get(f'{BASE}/api/syllabus/' + str(phys_id), headers=H)
body = check('GET syllabus after toggle', r, 200)
print('  Progress: ' + str(body.get('completed')) + '/' + str(body.get('total')) + ' = ' + str(body.get('percent')) + '%')

r = requests.delete(f'{BASE}/api/syllabus/' + str(topic2_id), headers=H)
check('DELETE /syllabus/<id>', r, 200)

r = requests.get(f'{BASE}/api/syllabus/' + str(phys_id), headers=H)
body = check('GET syllabus after delete (2 topics left)', r, 200)
print('  Remaining topics: ' + str(body.get('total')))

print('\n====== TIMETABLE ======')
r = requests.post(f'{BASE}/api/timetable/generate', headers=H)
body = check('POST /timetable/generate', r, 200, 'message')
print('  ' + str(body.get('message')))

r = requests.get(f'{BASE}/api/timetable', headers=H)
body = check('GET /timetable', r, 200)
if isinstance(body, dict) and body:
    # Flatten the grouped object for analysis
    all_entries = [entry for date_list in body.values() for entry in date_list]
    subj_count = Counter(e['subject'] for e in all_entries)
    print('  Total entries: ' + str(len(all_entries)))
    print('  Distribution: ' + str(dict(subj_count)))
    # Check ordering by hours
    hours = {k: sum(e['planned_hours'] for e in all_entries if e['subject'] == k) for k in subj_count}
    print('  Total planned hours: ' + str({k: round(v, 1) for k, v in hours.items()}))

print('\n====== CLEANUP ======')
r = requests.delete(f'{BASE}/api/subjects/' + str(maths_id), headers=H)
check('DELETE /subjects/ Maths', r, 200)
r = requests.get(f'{BASE}/api/subjects/', headers=H)
body = check('GET subjects after delete (1 left)', r, 200)
if isinstance(body, list):
    print('  Remaining: ' + str([s['name'] for s in body]))

print('\n============ RESULTS ============')
print('PASSED: ' + str(len(PASS)) + '/' + str(len(PASS) + len(FAIL)))
if FAIL:
    print('FAILED: ' + str(FAIL))
else:
    print('All endpoints valid!')
