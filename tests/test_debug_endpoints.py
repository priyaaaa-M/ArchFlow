import logging
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_root_debug_echo_and_log_error(caplog):
    # Verify root
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

    # Verify debug returns headers
    r = client.get("/debug")
    assert r.status_code == 200
    assert "headers" in r.json()

    # Verify echo returns body
    r = client.post("/echo", data="hello-test")
    assert r.status_code == 200
    assert r.json().get("received") == "hello-test"

    # Capture ERROR logs from /log-error
    caplog.set_level(logging.ERROR)
    with caplog:
        r = client.post("/log-error", json={"message": "test-error-message"})
        assert r.status_code == 200
        assert r.json().get("status") == "logged"
        # Ensure error-level message was emitted
        assert any("Forced error log: test-error-message" in rec.message for rec in caplog.records)
