from nicegui import ui
from web.auth import WebAuth, get_db
from web.components.layout import page_container
from inventory.services.user_service import UserService
from inventory.services.settings_service import SettingsService


def settings_page():
    if not WebAuth.is_authenticated() or not WebAuth.has_permission('admin'):
        ui.navigate.to('/dashboard')
        return

    page_container()

    try:
        db = get_db()
        user_service = UserService(db)
        settings_service = SettingsService(db)
    except Exception as e:
        ui.notify(f'Failed to connect: {e}', type='negative')
        return

    with ui.column().classes('w-full p-6'):
        ui.label('Settings').classes('text-2xl font-bold text-gray-800 mb-4')

        with ui.tabs().classes('w-full') as tabs:
            users_tab = ui.tab('Users')
            company_tab = ui.tab('Company')
            profile_tab = ui.tab('Profile')

        with ui.tab_panels(tabs, value=users_tab).classes('w-full'):
            with ui.tab_panel(users_tab):
                ui.label('User Management').classes('text-lg font-semibold mb-4')

                try:
                    rows = user_service.get_all()
                    columns = [
                        {'name': 'user_id', 'label': 'ID', 'field': 'user_id'},
                        {'name': 'username', 'label': 'Username', 'field': 'username'},
                        {'name': 'email', 'label': 'Email', 'field': 'email'},
                        {'name': 'role', 'label': 'Role', 'field': 'role'},
                        {'name': 'is_active', 'label': 'Active', 'field': 'is_active'},
                        {'name': 'last_login', 'label': 'Last Login', 'field': 'last_login'},
                    ]
                    ui.table(columns=columns, rows=rows, pagination={'rowsPerPage': 10}).classes('w-full')
                except Exception as e:
                    ui.notify(f'Failed to load users: {e}', type='negative')

            with ui.tab_panel(company_tab):
                ui.label('Company Settings').classes('text-lg font-semibold mb-4')
                try:
                    company = settings_service.get_company_settings()

                    with ui.column().classes('w-full max-w-lg gap-4'):
                        name = ui.input('Company Name', value=company.get('company_name', '')).props('outlined')
                        address = ui.textarea('Address', value=company.get('address', '')).props('outlined')
                        phone = ui.input('Phone', value=company.get('phone', '')).props('outlined')
                        email = ui.input('Email', value=company.get('email', '')).props('outlined')
                        tax_id = ui.input('Tax ID', value=company.get('tax_id', '')).props('outlined')
                        currency = ui.input('Currency', value=company.get('currency', 'USD')).props('outlined')
                        tax_rate = ui.input('Tax Rate (%)', value=str(company.get('tax_rate', 0))).props('outlined')

                        def save_settings():
                            try:
                                settings_service.update_company_settings(
                                    company_name=name.value,
                                    address=address.value,
                                    phone=phone.value,
                                    email=email.value,
                                    tax_id=tax_id.value,
                                    currency_symbol=currency.value,
                                    tax_rate=float(tax_rate.value or 0),
                                )
                                ui.notify('Settings saved!', type='positive')
                            except Exception as e:
                                ui.notify(f'Failed to save: {e}', type='negative')

                        ui.button('Save Settings', color='#1A73E8', on_click=save_settings)
                except Exception as e:
                    ui.notify(f'Failed to load settings: {e}', type='negative')

            with ui.tab_panel(profile_tab):
                ui.label('My Profile').classes('text-lg font-semibold mb-4')
                user = WebAuth.current_user()
                if user:
                    ui.label(f"Username: {user.get('username', '')}").classes('text-sm')
                    ui.label(f"Email: {user.get('email', '')}").classes('text-sm')
                    ui.label(f"Name: {user.get('full_name', '')}").classes('text-sm')
                    ui.label(f"Role: {user.get('role', '')}").classes('text-sm')
