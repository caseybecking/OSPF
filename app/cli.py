# CSV
import csv
# APP
from app import db
from app.config import Config
# MODELS
from api.categories_type.models import CategoriesTypeModel as CategoriesType
from api.categories_group.models import CategoriesGroupModel as CategoriesGroup
from api.categories.models import CategoriesModel as Categories

def insert_categories():
    user_id = Config.DEFAULT_USER_ID
    categories_type = []
    categories_group = []
    with open("data/categories_data.csv", "r", encoding=str) as f_in:
        reader = csv.reader(f_in, quotechar="'")
        next(reader)  # skip header
        ## categories_type
        for row in reader:
            if row[2] not in categories_type:
                categories_type.append(row[2])
        ## categories_group
            if row[1] not in categories_group:
                categories_group.append(row[1])

    for category_type in categories_type:
        _categories_type = CategoriesType.query.filter_by(name=category_type, user_id=user_id).first()
        if _categories_type is None:
            cat = CategoriesType(name=category_type, user_id=user_id)
            db.session.add(cat)
            db.session.commit()
    for category_group in categories_group:
        _categories_group = CategoriesGroup.query.filter_by(name=category_group, user_id=user_id).first()
        if _categories_group is None:
            cat = CategoriesGroup(name=category_group, user_id=user_id)
            db.session.add(cat)
            db.session.commit()

    with open("data/categories_data.csv", "r", encoding=str) as f_in:
        reader = csv.reader(f_in, quotechar="'")
        next(reader)  # skip header
        ## categories_type
        for row in reader:
            category = row[0]
            category_group = row[1]
            category_type = row[2]
            _category_type_id = CategoriesType.query.filter_by(name=category_type, user_id=user_id).first().id
            _category_group_id = CategoriesGroup.query.filter_by(name=category_group, user_id=user_id).first().id
            _categories = Categories.query.filter_by(name=category, categories_group_id=_category_group_id, categories_type_id=_category_type_id, user_id=user_id).first()
            if _categories is None:
                cat = Categories(name=category, categories_group_id=_category_group_id, categories_type_id=_category_type_id, user_id=user_id)
                db.session.add(cat)
                db.session.commit()
