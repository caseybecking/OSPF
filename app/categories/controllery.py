from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import logout_user, login_required
import requests

categories_blueprint = Blueprint('categories', __name__)

@categories_blueprint.route('categories')
@login_required
def 

