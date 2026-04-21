import asyncio
import json
import urllib.request
import urllib.error

async def run_test():
    # Login as admin to get token
    login_data = urllib.parse.urlencode({'username': 'admin@saludbolivia.com', 'password': 'Password123!'}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login', data=login_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    try:
        r = urllib.request.urlopen(req)
        response_data = json.loads(r.read().decode('utf-8'))
        token = response_data['access_token']
        print(f"Logged in, token: {token[:10]}...")
    except urllib.error.HTTPError as e:
        print(f"Login failed: {e.code} {e.read().decode()}")
        return

    # Create Medical Center
    print("\n--- Creating Medical Center ---")
    clinic_data = {
        "name": "Centro Médico de Prueba",
        "address": "Calle Prueba #123",
        "location_wkt": "POINT(-68.1193 -16.4897)",
        "phone": "2223334"
    }
    
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/clinics/', data=json.dumps(clinic_data).encode('utf-8'), headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    })
    
    try:
        r = urllib.request.urlopen(req)
        created_clinic = json.loads(r.read().decode('utf-8'))
        print(f"Created clinic response: {json.dumps(created_clinic, indent=2)}")
        clinic_id = created_clinic.get('id')
    except urllib.error.HTTPError as e:
        print(f"Create clinic failed: {e.code} {e.read().decode()}")
        return

    # Get Medical Center
    print("\n--- Retrieving Medical Center ---")
    req = urllib.request.Request(f'http://127.0.0.1:8000/api/v1/clinics/{clinic_id}', headers={
        'Authorization': f'Bearer {token}'
    })
    
    try:
        r = urllib.request.urlopen(req)
        get_clinic = json.loads(r.read().decode('utf-8'))
        print(f"Retrieved clinic response: {json.dumps(get_clinic, indent=2)}")
    except urllib.error.HTTPError as e:
        print(f"Get clinic failed: {e.code} {e.read().decode()}")
        return

if __name__ == "__main__":
    asyncio.run(run_test())
