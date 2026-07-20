from nicegui import ui
from web.auth import WebAuth

_dark_mode = False


def toggle_theme():
    global _dark_mode
    _dark_mode = not _dark_mode
    ui.dark_mode().set_value(_dark_mode)


NAV_ITEMS = [
    {'label': 'Dashboard', 'icon': 'dashboard', 'path': '/dashboard', 'role': None},
    {'label': 'Products', 'icon': 'inventory_2', 'path': '/products', 'role': None},
    {'label': 'Suppliers', 'icon': 'local_shipping', 'path': '/suppliers', 'role': None},
    {'label': 'Customers', 'icon': 'people', 'path': '/customers', 'role': None},
    {'label': 'Purchases', 'icon': 'shopping_cart', 'path': '/purchases', 'role': None},
    {'label': 'Sales', 'icon': 'point_of_sale', 'path': '/sales', 'role': None},
    {'label': 'Reports', 'icon': 'assessment', 'path': '/reports', 'role': 'manager'},
    {'label': 'Activity Log', 'icon': 'history', 'path': '/activity-log', 'role': 'admin'},
    {'label': 'Settings', 'icon': 'settings', 'path': '/settings', 'role': 'admin'},
]

_drawer = None


def toggle_drawer():
    if _drawer:
        _drawer.toggle()


def create_header():
    with ui.header(elevated=True).classes('bg-white border-b shadow-sm w-full'):
        with ui.row().classes('w-full items-center justify-between px-4 py-2'):
            with ui.row().classes('items-center gap-2'):
                ui.button(icon='menu', on_click=toggle_drawer).props('flat dense round')
                ui.label('Invictus').classes('text-xl font-bold text-[#1A73E8]')
            user = WebAuth.current_user()
            if user:
                with ui.row().classes('items-center gap-3'):
                    ui.button(icon='dark_mode', on_click=toggle_theme).props('flat dense round')
                    ui.label(f'{user.get("full_name", user.get("username", ""))}').classes('text-sm text-gray-600')
                    ui.label(f'({user.get("role", "")})').classes('text-xs text-gray-400')
                    ui.button('Sign Out', on_click=WebAuth.logout, color='grey').props('flat dense')


def create_sidebar():
    global _drawer
    with ui.left_drawer(value=True, top_corner=False, bottom_corner=False).classes('bg-white border-r') as drawer:
        _drawer = drawer
        with ui.column().classes('w-full p-4 gap-1'):
            for item in NAV_ITEMS:
                role_req = item.get('role')
                if role_req and not WebAuth.has_permission(role_req):
                    continue
                with ui.link(target=item['path']):
                    with ui.row().classes('w-full items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer'):
                        ui.icon(item['icon']).classes('text-gray-500')
                        ui.label(item['label']).classes('text-sm text-gray-700')
    return drawer


def page_container():
    create_header()
    create_sidebar()
