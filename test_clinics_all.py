import asyncio
import json
import urllib.request
import urllib.error

async def run_test():
    login_data = urllib.parse.urlencode({'username': 'admin@saludbolivia.com', 'password': 'Password123!'}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login', data=login_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        r = urllib.request.urlopen(req)
        response_data = json.loads(r.read().decode('utf-8'))
        token = response_data['access_token']
    except urllib.error.HTTPError as e:
        print(f"Login failed: {e.code} {e.read().decode()}")
        return

    # Get Medical Centers
    print("\n--- Retrieving All Medical Centers ---")
    req = urllib.request.Request(f'http://127.0.0.1:8000/api/v1/clinics/', headers={
        'Authorization': f'Bearer {token}'
    })
    
    try:
        r = urllib.request.urlopen(req)
        get_clinic = json.loads(r.read().decode('utf-8'))
        print(json.dumps(get_clinic, indent=2))
    except urllib.error.HTTPError as e:
        print(f"Get clinic failed: {e.code} {e.read().decode()}")
        return

if __name__ == "__main__":
    asyncio.run(run_test())
