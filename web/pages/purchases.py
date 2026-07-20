from nicegui import ui
from web.auth import WebAuth, get_db
from web.components.layout import page_container
from web.components.data_table import data_table
from inventory.services.purchase_service import PurchaseService
from inventory.services.supplier_service import SupplierService
from inventory.services.product_service import ProductService


def purchases_page():
    if not WebAuth.is_authenticated():
        ui.navigate.to('/login')
        return

    page_container()

    try:
        db = get_db()
        service = PurchaseService(db)
        rows = service.get_all()
    except Exception as e:
        ui.notify(f'Failed to load purchases: {e}', type='negative')
        rows = []

    columns = [
        {'name': 'purchase_id', 'label': 'ID', 'field': 'purchase_id', 'align': 'left'},
        {'name': 'purchase_date', 'label': 'Date', 'field': 'purchase_date', 'align': 'left'},
        {'name': 'supplier_name', 'label': 'Supplier', 'field': 'supplier_name', 'align': 'left'},
        {'name': 'total_amount', 'label': 'Total', 'field': 'total_amount', 'align': 'right'},
        {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'left'},
    ]

    with ui.column().classes('w-full p-6'):
        ui.label('Purchases').classes('text-2xl font-bold text-gray-800 mb-4')

        def show_purchase_dialog():
            user = WebAuth.current_user()
            try:
                db = get_db()
                supplier_service = SupplierService(db)
                product_service = ProductService(db)
                suppliers = supplier_service.get_all()
                products = product_service.get_all()
            except Exception as e:
                ui.notify(f'Failed to load data: {e}', type='negative')
                return

            items = []

            with ui.dialog() as dialog, ui.card().classes('w-[700px] max-w-full p-6'):
                ui.label('New Purchase').classes('text-lg font-semibold mb-4')

                supplier_opts = {str(s['supplier_id']): s['name'] for s in suppliers}
                supplier_select = ui.select(supplier_opts, label='Supplier').classes('w-full').props('outlined')

                with ui.row().classes('w-full gap-4'):
                    product_opts = {str(p['product_id']): f"{p['name']}" for p in products}
                    product_select = ui.select(product_opts, label='Product').classes('flex-1').props('outlined')
                    qty_input = ui.input('Qty', value='1').classes('w-20').props('outlined dense')
                    cost_input = ui.input('Cost', value='0').classes('w-24').props('outlined dense')

                    def add_item():
                        try:
                            items.append({
                                'product_id': int(product_select.value),
                                'name': next((p['name'] for p in products if str(p['product_id']) == product_select.value), ''),
                                'quantity': int(qty_input.value or 1),
                                'cost_price': float(cost_input.value or 0),
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
                                ui.label(f"${item['cost_price']:.2f}").classes('text-sm text-gray-600 w-24')
                                ui.label(f"${item['quantity'] * item['cost_price']:.2f}").classes('text-sm font-semibold w-24')
                                ui.button('x', on_click=lambda idx=i: (
                                    items.pop(idx),
                                    update_items_ui(),
                                )).props('dense flat color=red')
                    items_container.update()

                update_items_ui()

                def record_purchase():
                    try:
                        service.create(
                            supplier_id=int(supplier_select.value),
                            user_id=user.get('user_id'),
                            items=[{'product_id': i['product_id'], 'quantity': i['quantity'], 'cost_price': i['cost_price']} for i in items],
                        )
                        dialog.close()
                        ui.navigate.reload()
                    except Exception as e:
                        ui.notify(f'Purchase failed: {e}', type='negative')

                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('Cancel', on_click=dialog.close).props('flat')
                    ui.button('Record Purchase', color='#1A73E8', on_click=record_purchase)

                dialog.open()

        data_table(
            columns=columns,
            rows=rows,
            on_add=show_purchase_dialog,
            title='Purchase List',
        )
