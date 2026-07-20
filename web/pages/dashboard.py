from nicegui import ui
from web.auth import WebAuth
from web.components.layout import page_container
from inventory.services.product_service import ProductService
from inventory.services.sale_service import SaleService
from web.auth import get_db


def dashboard_page():
    if not WebAuth.is_authenticated():
        ui.navigate.to('/login')
        return

    page_container()

    with ui.column().classes('w-full p-6'):
        ui.label('Dashboard').classes('text-2xl font-bold text-gray-800 mb-6')

        stats = {}
        sale_stats = {}
        error_msg = None

        try:
            db = get_db()
            product_service = ProductService(db)
            sale_service = SaleService(db)
            stats = product_service.get_dashboard_stats()
            sale_stats = sale_service.get_dashboard_stats()
        except Exception as e:
            error_msg = str(e)

        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('flex-1 p-6 shadow-sm rounded-xl'):
                ui.label('Total Products').classes('text-sm text-gray-500')
                ui.label(str(stats.get('total_products', 0))).classes('text-3xl font-bold text-gray-800 mt-2')

            with ui.card().classes('flex-1 p-6 shadow-sm rounded-xl'):
                ui.label('Total Stock').classes('text-sm text-gray-500')
                ui.label(str(stats.get('total_stock', 0))).classes('text-3xl font-bold text-gray-800 mt-2')

            with ui.card().classes('flex-1 p-6 shadow-sm rounded-xl'):
                ui.label('Inventory Value').classes('text-sm text-gray-500')
                total_value = stats.get('total_value', 0)
                ui.label(f'${total_value:,.2f}').classes('text-3xl font-bold text-gray-800 mt-2')

            with ui.card().classes('flex-1 p-6 shadow-sm rounded-xl'):
                ui.label('Low Stock Alerts').classes('text-sm text-gray-500')
                ui.label(str(stats.get('low_stock_count', 0))).classes('text-3xl font-bold text-red-500 mt-2')

        with ui.row().classes('w-full gap-4 mt-6'):
            with ui.card().classes('flex-1 p-6 shadow-sm rounded-xl'):
                ui.label('Total Sales').classes('text-sm text-gray-500')
                ui.label(str(sale_stats.get('count', 0))).classes('text-3xl font-bold text-gray-800 mt-2')

            with ui.card().classes('flex-1 p-6 shadow-sm rounded-xl'):
                ui.label('Total Revenue').classes('text-sm text-gray-500')
                total_revenue = sale_stats.get('total', 0)
                ui.label(f'${total_revenue:,.2f}').classes('text-3xl font-bold text-gray-800 mt-2')

        if error_msg:
            ui.notify(f'Database error: {error_msg}', type='negative', position='bottom-right')
