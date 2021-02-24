from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, SearchStation, FollowForm
from app.models import User, Metar, Taf, Pirep, Follow, Airsigmet
from datetime import datetime
from sqlalchemy import desc
import os


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = SearchStation()
    followed = Metar.query.from_statement(db.text(f"SELECT DISTINCT ON (station_id) station_id, * FROM (metar JOIN follow ON (((metar.station_id = follow.code))) AND user_id = {current_user.id}) ORDER BY station_id, observation_time DESC;")).all()
    if form.validate_on_submit():
        station_id = form.station_id.data.upper()
        return redirect(url_for('station', station_id=station_id))
    return render_template('index.html', title='Home', form=form, followed=followed)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.lower(), email=form.email.data, phone=form.phone.data, first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    return render_template('user.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.phone = form.phone.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/station/<station_id>', methods=['GET', 'POST'])
@login_required
def station(station_id):
    station_metar = Metar.query.filter_by(station_id=station_id).order_by(Metar.id.desc()).limit(1).first()
    taf_time = Taf.query.filter_by(station_id=station_id).order_by(Taf.id.desc()).first()
    print(taf_time)
    if taf_time is not None:
        station_taf = Taf.query.filter_by(station_id=station_id, issue_time=taf_time.issue_time).all()
    else:
        station_taf = None
    pirep = Pirep.query.from_statement(db.text(f"select * from pirep where  earth_distance(ll_to_earth(pirep.latitude, pirep.longitude), ll_to_earth({station_metar.latitude}, {station_metar.longitude})) < 160934.0 AND pirep.observation_time >= (NOW() - INTERVAL '12 hours' ) ORDER BY observation_time DESC;")).all()
    return render_template('station.html', title=f"{station_id} Weather", metar=station_metar, tafs=station_taf, station=station_id, taf_time=taf_time, pireps=pirep)

@app.route('/follow', methods=['GET', 'POST'])
@login_required
def follow():
    form = FollowForm()
    if form.validate_on_submit():
        to_follow = Follow(code=form.station_id.data.upper(), text_alert=form.text_alert.data, email_alert=form.email_alert.data, user_id=current_user.id)
        db.session.add(to_follow)
        db.session.commit()
        flash(f'Congratulations, you are now following {form.station_id.data}!')
        return redirect(url_for('index'))
    return render_template('follow.html', title='Follow', form=form)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')


@app.route('/map', methods=['GET', 'POST'])
@login_required
def map():
    latlong = Metar.query.from_statement(db.text(f"SELECT DISTINCT ON (station_id) station_id, * FROM metar;")).all()
    MTN_OBSCN = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'MTN OBSCN';"))
    IFR = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'IFR';"))
    TURB = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'TURB';"))
    ICE = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'ICE';"))
    pireps = Pirep.query.from_statement(db.text("SELECT * FROM pirep WHERE observation_time >= NOW() - INTERVAL '1 HOUR';")).all()
    CONVECTIVE = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'CONVECTIVE';"))
    ASH = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'ASH';"))
    return render_template('map.html', title='Follow', latlong=latlong, MTN_OBSCN=MTN_OBSCN, pireps=pireps, IFR=IFR, TURB=TURB, ICE=ICE, CONVECTIVE=CONVECTIVE, ASH=ASH)