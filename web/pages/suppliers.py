from nicegui import ui
from web.auth import WebAuth, get_db
from web.components.layout import page_container
from web.components.data_table import data_table
from inventory.services.supplier_service import SupplierService


def suppliers_page():
    if not WebAuth.is_authenticated():
        ui.navigate.to('/login')
        return

    page_container()

    try:
        db = get_db()
        service = SupplierService(db)
        rows = service.get_all()
    except Exception as e:
        ui.notify(f'Failed to load suppliers: {e}', type='negative')
        rows = []

    columns = [
        {'name': 'supplier_id', 'label': 'ID', 'field': 'supplier_id', 'align': 'left'},
        {'name': 'name', 'label': 'Company', 'field': 'name', 'align': 'left'},
        {'name': 'contact_person', 'label': 'Contact', 'field': 'contact_person', 'align': 'left'},
        {'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left'},
        {'name': 'phone', 'label': 'Phone', 'field': 'phone', 'align': 'left'},
        {'name': 'city', 'label': 'City', 'field': 'city', 'align': 'left'},
    ]

    with ui.column().classes('w-full p-6'):
        ui.label('Suppliers').classes('text-2xl font-bold text-gray-800 mb-4')

        def show_add_dialog():
            with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
                ui.label('Add Supplier').classes('text-lg font-semibold mb-4')
                name = ui.input('Company Name').props('outlined dense')
                contact = ui.input('Contact Person').props('outlined dense')
                email = ui.input('Email').props('outlined dense')
                phone = ui.input('Phone').props('outlined dense')
                address = ui.textarea('Address').props('outlined dense')
                city = ui.input('City').props('outlined dense')

                def save():
                    try:
                        service.create(name.value, contact.value, email.value, phone.value, address.value, city.value)
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
            title='Supplier List',
        )
