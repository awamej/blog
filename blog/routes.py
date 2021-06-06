from flask import render_template, request, session, flash, redirect, url_for
from sqlalchemy import or_

from blog import app
from blog.models import Entry, db
from blog.forms import EntryForm, LoginForm
import functools


def create_or_edit_entry(entry_id=None):
    errors = None
    if isinstance(entry_id, int):
        entry = Entry.query.filter_by(id=entry_id).first_or_404()
        form = EntryForm(obj=entry)
    else:
        form = EntryForm()
        entry = Entry(
            title=form.title.data,
            body=form.body.data,
            is_published=form.is_published.data,
            category=form.category.data
        )
    if request.method == "POST":
        if form.validate_on_submit():
            if isinstance(entry_id, int):
                form.populate_obj(entry)
                db.session.commit()
                flash('Post wyedytowany', 'success')
            else:
                db.session.add(entry)
                db.session.commit()
                flash('Post dodany', 'success')
            return redirect(url_for('index'))
        else:
            errors = form.errors
    return render_template("entry_form.html", form=form, errors=errors, entry_id=entry_id)


def login_required(view_func):
    @functools.wraps(view_func)
    def check_permissions(*args, **kwargs):
        if session.get('logged_in'):
            return view_func(*args, **kwargs)
        return redirect(url_for('login', next=request.path))

    return check_permissions


@app.route("/")
def index():
    search = request.args.get('search', default=None)
    category = request.args.get('category', default=None)
    entry_id = request.args.get('entry_id', default=None)
    query = Entry.query.filter_by(is_published=True)
    if search:
        query = query.filter(or_(Entry.title.contains(search), Entry.body.contains(search)))
    elif category:
        query = query.filter(Entry.category == category)
    elif entry_id:
        query = query.filter(Entry.id == entry_id)
    all_posts = query.order_by(Entry.pub_date.desc())
    return render_template("homepage.html", all_posts=all_posts)


@app.route("/new-post/", methods=["GET", "POST"])
@login_required
def create_entry():
    return create_or_edit_entry()


@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    return create_or_edit_entry(entry_id)


@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    errors = None
    next_url = request.args.get('next')
    if request.method == 'POST':
        if form.validate_on_submit():
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            errors = form.errors
    return render_template("login_form.html", form=form, errors=errors)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        flash('You are now logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/drafts/', methods=['GET'])
@login_required
def list_drafts():
    drafts = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
    return render_template("drafts.html", drafts=drafts)


@app.route('/delete-draft/<int:entry_id>', methods=['POST'])
@login_required
def delete_draft(entry_id):
    entry = Entry.query.filter_by(id=entry_id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash('Szkic usunięty.', 'success')
    return redirect(url_for('list_drafts'))


@app.route('/delete-entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = Entry.query.filter_by(id=entry_id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash('Wpis usunięty.', 'success')
    return redirect(url_for('index'))
