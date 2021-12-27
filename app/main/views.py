from flask import render_template, Blueprint
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root

from app.auth.views import login_required

bp = Blueprint("main", __name__)

default_breadcrumb_root(bp, '.')

@bp.route("/")
@register_breadcrumb(bp, '.', 'Home')
@login_required
def index():
    return render_template("main/index.html")
