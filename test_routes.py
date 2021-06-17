import pytest
import os
import tempfile

from flask import Flask, render_template, session, redirect, request, url_for
from unittest.mock import Mock

from blog import routes
from blog.routes import index, login_required, list_drafts
from blog.models import Entry
import config


@pytest.fixture
def client(monkeypatch):
    db_fd, db_uri = tempfile.mkstemp()
    monkeypatch.setenv('DATABASE_URL', db_uri)
    import blog

    blog.app.config['TESTING'] = True

    with blog.app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_uri)


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_login_required_redirects_and_pass_next(client):
    client.get('/drafts/', follow_redirects=True)
    assert request.path == '/login/'
    assert request.args.get('next') == '/drafts/'


def test_if_drafts_require_login(client):
    client.get('/drafts/', follow_redirects=True)
    assert request.path == '/login/'


# def test_if_new_post_requires_login(client):
#     client.get('/new_post/', follow_redirects=True)
#     assert request.path == '/login/'


# czy jakoś inaczej powinnam przekazać 3?
def test_if_edit_post_requires_login(client):
    client.get('/edit-post/3', follow_redirects=True)
    assert request.path == '/login/'


# czy jakoś automatycznie można podstawić id spoza zakresu czy trzeba konkretne ręcznie?
# def test_if_404_if_wrong_entry_id(client):
#     response = client.get('/edit-post/20', follow_redirects=True)
#     assert response.status_code == 404

