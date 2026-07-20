from nicegui import ui
from web.auth import WebAuth
from inventory.exceptions import AuthenticationError


def create_login_page():
    if WebAuth.is_authenticated():
        ui.navigate.to('/dashboard')
        return

    ui.dark_mode().set_value(False)

    with ui.column().classes('absolute-center items-center w-full max-w-md'):
        with ui.card().classes('w-full p-8 shadow-xl rounded-2xl'):
            ui.label('Invictus').classes('text-3xl font-bold text-[#1A73E8] text-center w-full mb-1')
            ui.label('Inventory Management System').classes('text-sm text-gray-400 text-center w-full mb-8')

            username = ui.input('Username or Email').classes('w-full').props('outlined dense autofocus')
            password = ui.input('Password', password=True, password_toggle_button=True).classes('w-full').props('outlined dense')

            error_label = ui.label().classes('text-red-500 text-sm w-full text-center')
            error_label.set_visibility(False)

            def handle_login():
                error_label.set_visibility(False)
                try:
                    WebAuth.login(username.value, password.value)
                    ui.navigate.to('/dashboard')
                except AuthenticationError as e:
                    error_label.set_text(str(e))
                    error_label.set_visibility(True)

            ui.button('Sign In', on_click=handle_login, color='#1A73E8').classes('w-full mt-4')
