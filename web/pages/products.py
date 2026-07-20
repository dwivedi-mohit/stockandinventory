from nicegui import ui
from web.auth import WebAuth, get_db
from web.components.layout import page_container
from web.components.data_table import data_table
from inventory.services.product_service import ProductService


def products_page():
    if not WebAuth.is_authenticated():
        ui.navigate.to('/login')
        return

    page_container()

    try:
        db = get_db()
        service = ProductService(db)
        rows = service.get_all()
    except Exception as e:
        ui.notify(f'Failed to load products: {e}', type='negative')
        rows = []

    columns = [
        {'name': 'product_id', 'label': 'ID', 'field': 'product_id', 'align': 'left'},
        {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
        {'name': 'sku', 'label': 'SKU', 'field': 'sku', 'align': 'left'},
        {'name': 'selling_price', 'label': 'Sell Price', 'field': 'selling_price', 'align': 'right'},
        {'name': 'stock_quantity', 'label': 'Stock', 'field': 'stock_quantity', 'align': 'right'},
        {'name': 'min_stock_level', 'label': 'Min Stock', 'field': 'min_stock_level', 'align': 'right'},
    ]

    with ui.column().classes('w-full p-6'):
        ui.label('Products').classes('text-2xl font-bold text-gray-800 mb-4')

        def show_add_dialog():
            with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
                ui.label('Add Product').classes('text-lg font-semibold mb-4')
                name = ui.input('Name').props('outlined dense')
                sku = ui.input('SKU').props('outlined dense')
                cost_price = ui.input('Cost Price', value='0').props('outlined dense')
                selling_price = ui.input('Selling Price', value='0').props('outlined dense')
                stock = ui.input('Stock', value='0').props('outlined dense')
                min_stock = ui.input('Min Stock', value='0').props('outlined dense')

                def save():
                    try:
                        service.create(
                            name=name.value,
                            sku=sku.value,
                            selling_price=float(selling_price.value or 0),
                            cost_price=float(cost_price.value or 0),
                            stock_quantity=int(stock.value or 0),
                            min_stock_level=int(min_stock.value or 0),
                        )
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
            title='Product List',
        )
