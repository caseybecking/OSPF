from flask import Blueprint, render_template, url_for, session
from flask_login import login_required
import requests

categories_blueprint = Blueprint('categories', __name__)

@categories_blueprint.route('/categories')
@login_required
def categories():
    """
    Render the categories page.

    This view function fetches the categories from an external API and renders
    the categories/index.html template with the fetched categories and the user ID
    from the session.

    Returns:
        str: Rendered HTML template for the categories page.
    """
    api_url = url_for('categories', _external=True)
    _categories_group = requests.get(url_for('categories_group', _external=True),timeout=15).json().get('categories_group', [])
    _categories_type = requests.get(url_for('categories_type', _external=True), timeout=15).json().get('categories_type', [])
    response = requests.get(api_url, timeout=15)
    _categories = response.json().get('categories', [])
    user_id = session.get('_user_id')
    return render_template('categories/index.html', categories=_categories, user_id=user_id, categories_group=_categories_group, categories_type=_categories_type)

@categories_blueprint.route('/categories/group')
@login_required
def categories_group():
    """
    Fetch and return the categories group.

    This view function fetches the categories group from an external API and returns
    the categories group as a JSON response.

    Returns:
        list: List of categories group.
    """
    api_url = url_for('categories_group', _external=True)
    response = requests.get(api_url, timeout=15)
    _categories_group = response.json().get('categories_group', [])
    user_id = session.get('_user_id')
    return render_template('categories/group.html', categories_group=_categories_group, user_id=user_id)

@categories_blueprint.route('/categories/type')
@login_required
def categories_type():
    """
    Fetch and return the categories type.

    This view function fetches the categories type from an external API and returns
    the categories type as a JSON response.

    Returns:
        list: List of categories type.
    """
    api_url = url_for('categories_type', _external=True)
    response = requests.get(api_url, timeout=15)
    _categories_type = response.json().get('categories_type', [])
    user_id = session.get('_user_id')
    return render_template('categories/type.html', categories_type=_categories_type, user_id=user_id)
