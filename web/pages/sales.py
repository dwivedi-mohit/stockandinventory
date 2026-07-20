from nicegui import ui
from web.auth import WebAuth, get_db
from web.components.layout import page_container
from web.components.data_table import data_table
from inventory.services.sale_service import SaleService
from inventory.services.customer_service import CustomerService
from inventory.services.product_service import ProductService


def sales_page():
    if not WebAuth.is_authenticated():
        ui.navigate.to('/login')
        return

    page_container()

    try:
        db = get_db()
        service = SaleService(db)
        rows = service.get_all()
    except Exception as e:
        ui.notify(f'Failed to load sales: {e}', type='negative')
        rows = []

    columns = [
        {'name': 'sale_id', 'label': 'Invoice #', 'field': 'sale_id', 'align': 'left'},
        {'name': 'sale_date', 'label': 'Date', 'field': 'sale_date', 'align': 'left'},
        {'name': 'customer_name', 'label': 'Customer', 'field': 'customer_name', 'align': 'left'},
        {'name': 'total_amount', 'label': 'Total', 'field': 'total_amount', 'align': 'right'},
        {'name': 'payment_method', 'label': 'Payment', 'field': 'payment_method', 'align': 'left'},
    ]

    with ui.column().classes('w-full p-6'):
        ui.label('Sales').classes('text-2xl font-bold text-gray-800 mb-4')

        def show_sale_dialog():
            user = WebAuth.current_user()
            try:
                db = get_db()
                customer_service = CustomerService(db)
                product_service = ProductService(db)
                customers = customer_service.get_all()
                products = product_service.get_all()
            except Exception as e:
                ui.notify(f'Failed to load data: {e}', type='negative')
                return

            items = []

            with ui.dialog() as dialog, ui.card().classes('w-[700px] max-w-full p-6'):
                ui.label('New Sale').classes('text-lg font-semibold mb-4')

                customer_opts = {str(c['customer_id']): c['name'] for c in customers}
                customer_select = ui.select(customer_opts, label='Customer').classes('w-full').props('outlined')

                with ui.row().classes('w-full gap-4'):
                    product_opts = {str(p['product_id']): f"{p['name']} (Stock: {p.get('stock_quantity', 0)})" for p in products}
                    product_select = ui.select(product_opts, label='Product').classes('flex-1').props('outlined')
                    qty_input = ui.input('Qty', value='1').classes('w-20').props('outlined dense')

                    def add_item():
                        try:
                            items.append({
                                'product_id': int(product_select.value),
                                'name': next((p['name'] for p in products if str(p['product_id']) == product_select.value), ''),
                                'quantity': int(qty_input.value or 1),
                                'price': next((p['selling_price'] for p in products if str(p['product_id']) == product_select.value), 0),
                            })
                            update_items_ui()
                        except Exception as e:
                            ui.notify(f'Error adding item: {e}', type='negative')

                    ui.button('Add Item', color='#1A73E8', on_click=add_item).props('dense')

                items_container = ui.column().classes('w-full mt-4')

                def update_items_ui():
                    items_container.clear()
                    with items_container:
                        if not items:
                            ui.label('No items added').classes('text-gray-400 text-sm')
                            return
                        for i, item in enumerate(items):
                            with ui.row().classes('w-full items-center gap-2 bg-gray-50 rounded p-2'):
                                ui.label(item['name']).classes('flex-1 text-sm')
                                ui.label(f"Qty: {item['quantity']}").classes('text-sm text-gray-600 w-16')
                                ui.label(f"${item['price']:.2f}").classes('text-sm text-gray-600 w-24')
                                ui.label(f"${item['quantity'] * item['price']:.2f}").classes('text-sm font-semibold w-24')
                                ui.button('x', on_click=lambda idx=i: (
                                    items.pop(idx),
                                    update_items_ui(),
                                )).props('dense flat color=red')
                    items_container.update()

                update_items_ui()

                def complete_sale():
                    try:
                        service.create(
                            user_id=user.get('user_id'),
                            items=[{'product_id': i['product_id'], 'quantity': i['quantity'], 'price': i['price']} for i in items],
                            customer_id=int(customer_select.value) if customer_select.value else None,
                        )
                        dialog.close()
                        ui.navigate.reload()
                    except Exception as e:
                        ui.notify(f'Sale failed: {e}', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('Cancel', on_click=dialog.close).props('flat')
                    ui.button('Complete Sale', color='#1A73E8', on_click=complete_sale)

                dialog.open()

        data_table(
            columns=columns,
            rows=rows,
            on_add=show_sale_dialog,
            title='Sales List',
        )
