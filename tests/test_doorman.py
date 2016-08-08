#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import pprint

import pytest
from flask import url_for

__author__ = "Israel Fruchter (ifruchte)"
__copyright__ = "Israel Fruchter (ifruchte)"
__license__ = "simple-bsd"

headers={"Content-Type": "application/json"}

def test_put_resource(client):
    assert client.put(url_for('lockedresource', id='box1'),
                      headers=headers, data=json.dumps(dict())
                      ).status_code == 200
    assert client.put(url_for('lockedresource', id='box2'),
                      headers=headers, data=json.dumps(dict(card_id=112233))
                      ).status_code == 200
    assert client.put(url_for('lockedresource', id='box3'),
                      headers=headers, data=json.dumps(dict(card_id=223344))
                      ).status_code == 200
    assert client.put(url_for('lockedresource', id='box4'),
                      headers=headers, data=json.dumps(dict(card_id=222222))
                      ).status_code == 200


def test_put_resource_duplicate(client):
    assert client.put(url_for('lockedresource', id='box1'), headers=headers, data=json.dumps(dict())).status_code == 405
    assert client.put(url_for('lockedresource', id='box1'), headers=headers, data=json.dumps(dict(card_id=112233))).status_code == 405


def test_patch_resource(client):
    assert client.patch(url_for('lockedresource', id='box2'), headers=headers, data=json.dumps(dict(card_id=111111, project="mighty"))).status_code == 200


def test_delete_resource(client):
    assert client.delete(url_for('lockedresource', id='box4')).status_code == 200


def test_get_resourcelist(client):
    res = client.get(url_for('lockedresourcelist'))
    assert res.status_code == 200
    data = json.loads(res.data.decode())
    assert len(data) == 3
    pprint.pprint(data)


def test_get_resourcelist_q(client):
    res = client.get(url_for('lockedresourcelist'), headers=headers,
                     data=json.dumps(dict(q="data.project != 'mighty'")))
    assert res.status_code == 200
    data = json.loads(res.data.decode())
    assert len(data) == 2
    pprint.pprint(data)


def test_lock(client):
    res = client.post(url_for('lock'), headers=headers,
                     data=json.dumps(dict(resource="box1", username="me")))
    assert res.status_code == 200

    res = client.post(url_for('lock'), headers=headers,
                     data=json.dumps(dict(resource="box1", username="me")))
    assert "locked by me" in str(res.data)
    assert res.status_code == 405

    res = client.delete(url_for('lock', id="box1"), headers=headers,
                     data=json.dumps(dict(username="me")))
    assert res.status_code == 200

def test_lock_duration(client):
    pass