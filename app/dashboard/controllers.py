from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

dashboards = Blueprint('dashboards', __name__)

@dashboards.route('/')
@login_required
def index():
    return render_template('dashboards/index.html')