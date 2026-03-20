def test_create_app(client):
    response = client.get('/')
    assert response.status_code in (200, 302, 404)
