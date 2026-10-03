def test_health(client):
    r=client.get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_home_requires_login(client):
    assert client.post('/api/generate-home',json={"budget":50000,"room_type":"Living Room"}).status_code==401

def test_home_plan(auth_client):
    r=auth_client.post('/api/generate-home',json={"budget":50000,"room_type":"Living Room","style":"modern","lights":2,"fans":1,"tables":1,"notes":""})
    assert r.status_code==200
    data=r.json(); assert data['estimated_total']<=data['budget']; assert data['items']; assert data['source']=='fallback'

def test_party_plan(auth_client):
    r=auth_client.post('/api/generate-party',json={"budget":30000,"guests":30,"event_type":"Birthday","venue_type":"Indoor","city":"Chennai","notes":""})
    assert r.status_code==200; assert r.json()['estimated_total']<=30000

def test_jewelry_plan(auth_client):
    r=auth_client.post('/api/generate-jewelry',data={"budget":"10000","occasion":"Wedding","style":"Traditional","outfit_color":"red","notes":""})
    assert r.status_code==200; assert r.json()['items']

def test_history_page(auth_client):
    r=auth_client.get('/history'); assert r.status_code==200; assert 'Your saved plans' in r.text
