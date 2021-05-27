from flask import render_template, request, session, flash, redirect, url_for
from blog import app
from blog.models import Entry, db
from blog.forms import EntryForm, LoginForm


def create_or_edit_entry(*entry_id):
    errors = None
    if entry_id is int:
        entry = Entry.query.filter_by(id=entry_id).first_or_404()
        form = EntryForm(obj=entry)
    else:
        form = EntryForm()
        entry = Entry(
            title=form.title.data,
            body=form.body.data,
            is_published=form.is_published.data
        )
    if request.method == "POST":
        if form.validate_on_submit():
            if entry_id is int:
                form.populate_obj(entry)
            else:
                db.session.add(entry)
            db.session.commit()
        else:
            errors = form.errors
        return render_template("entry_form.html", form=form, errors=errors)


@app.route("/")
def index():
    all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())
    return render_template("homepage.html", all_posts=all_posts)


@app.route("/new-post/", methods=["GET", "POST"])
def create_entry():
    return create_or_edit_entry()


# def create_entry():
#     form = EntryForm()
#     errors = None
#     if request.method == "POST":
#         if form.validate_on_submit():
#             entry = Entry(
#                 title=form.title.data,
#                 body=form.body.data,
#                 is_published=form.is_published.data
#             )
#             db.session.add(entry)
#             db.session.commit()
#         else:
#             errors = form.errors
#         return render_template("entry_form.html", form=form, errors=errors)


@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    return create_or_edit_entry(entry_id)


# def edit_entry(entry_id):
#     entry = Entry.query.filter_by(id=entry_id).first_or_404()
#     form = EntryForm(obj=entry)
#     errors = None
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             form.populate_obj(entry)
#             db.session.commit()
#         else:
#             errors = form.errors
#     return render_template("entry_form.html", form=form, errors=errors)


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
