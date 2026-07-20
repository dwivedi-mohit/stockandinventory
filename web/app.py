from nicegui import ui
from web.auth import WebAuth
from web.pages.login import create_login_page
from web.pages.dashboard import dashboard_page
from web.pages.products import products_page
from web.pages.suppliers import suppliers_page
from web.pages.customers import customers_page
from web.pages.sales import sales_page
from web.pages.purchases import purchases_page
from web.pages.reports import reports_page
from web.pages.activity_log import activity_log_page
from web.pages.settings import settings_page


@ui.page('/')
def index():
    if WebAuth.is_authenticated():
        ui.navigate.to('/dashboard')
    else:
        ui.navigate.to('/login')


@ui.page('/login')
def login():
    create_login_page()


@ui.page('/dashboard')
def dashboard():
    dashboard_page()


@ui.page('/products')
def products():
    products_page()


@ui.page('/suppliers')
def suppliers():
    suppliers_page()


@ui.page('/customers')
def customers():
    customers_page()


@ui.page('/sales')
def sales():
    sales_page()


@ui.page('/purchases')
def purchases():
    purchases_page()


@ui.page('/reports')
def reports():
    reports_page()


@ui.page('/activity-log')
def activity_log():
    activity_log_page()


@ui.page('/settings')
def settings_():
    settings_page()
