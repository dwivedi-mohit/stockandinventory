from nicegui import ui
from web.auth import WebAuth, get_db
from web.components.layout import page_container
from web.components.data_table import data_table
from inventory.services.customer_service import CustomerService


def customers_page():
    if not WebAuth.is_authenticated():
        ui.navigate.to('/login')
        return

    page_container()

    try:
        db = get_db()
        service = CustomerService(db)
        rows = service.get_all()
    except Exception as e:
        ui.notify(f'Failed to load customers: {e}', type='negative')
        rows = []

    columns = [
        {'name': 'customer_id', 'label': 'ID', 'field': 'customer_id', 'align': 'left'},
        {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
        {'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left'},
        {'name': 'phone', 'label': 'Phone', 'field': 'phone', 'align': 'left'},
        {'name': 'loyalty_points', 'label': 'Loyalty Pts', 'field': 'loyalty_points', 'align': 'right'},
    ]

    with ui.column().classes('w-full p-6'):
        ui.label('Customers').classes('text-2xl font-bold text-gray-800 mb-4')

        def show_add_dialog():
            with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
                ui.label('Add Customer').classes('text-lg font-semibold mb-4')
                name = ui.input('Name').props('outlined dense')
                email = ui.input('Email').props('outlined dense')
                phone = ui.input('Phone').props('outlined dense')
                address = ui.textarea('Address').props('outlined dense')

                def save():
                    try:
                        service.create(name.value, email.value, phone.value, address.value)
                        dialog.close()
                        ui.navigate.reload()
                    except Exception as e:
                        ui.notify(f'Error: {e}', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('Cancel', on_click=dialog.close).props('flat')
                    ui.button('Save', color='#1A73E8', on_click=save)
                dialog.open()

        data_table(
            columns=columns,
            rows=rows,
            on_add=show_add_dialog,
            title='Customer List',
        )
