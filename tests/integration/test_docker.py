import wait
import requests


def test_integration(docker_compose):
    wait.tcp.open(5000, host='localhost')

    requests.delete("http://localhost:5000/resource/1")

    res = requests.put("http://localhost:5000/resource/1", json=dict(name="moshe", card_id="1234"))
    assert res.status_code == 200

    res = requests.get("http://localhost:5000/resources")
    assert res.status_code == 200
