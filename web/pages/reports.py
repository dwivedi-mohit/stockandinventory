from nicegui import ui
from web.auth import WebAuth, get_db
from web.components.layout import page_container
from inventory.services.report_service import ReportService


def reports_page():
    if not WebAuth.is_authenticated() or not WebAuth.has_permission('manager'):
        ui.navigate.to('/dashboard')
        return

    page_container()

    try:
        db = get_db()
        service = ReportService(db)
    except Exception as e:
        ui.notify(f'Failed to connect: {e}', type='negative')
        return

    report_types = [
        'Inventory Valuation',
        'Sales Report',
        'Profit & Loss',
        'Low Stock',
        'Best Selling Products',
        'Supplier Performance',
        'Category Summary',
    ]

    with ui.column().classes('w-full p-6'):
        ui.label('Reports').classes('text-2xl font-bold text-gray-800 mb-4')

        with ui.row().classes('w-full gap-4 items-end'):
            report_type = ui.select(report_types, label='Report Type').classes('w-64').props('outlined')
            start_date = ui.input('Start Date', placeholder='YYYY-MM-DD').props('outlined dense')
            end_date = ui.input('End Date', placeholder='YYYY-MM-DD').props('outlined dense')
            generate_btn = ui.button('Generate', color='#1A73E8')

        result_container = ui.column().classes('w-full mt-6')

        def generate_report():
            result_container.clear()
            rtype = report_type.value
            if not rtype:
                return

            with result_container:
                with ui.card().classes('w-full p-4'):
                    try:
                        if rtype == 'Inventory Valuation':
                            data = service.inventory_valuation()
                            ui.label('Inventory Valuation').classes('text-lg font-semibold mb-4')
                            for d in data:
                                ui.label(f"{d.get('name', '')}: Cost ${d.get('cost_price', 0):.2f} / Sale ${d.get('selling_price', 0):.2f} / Value ${d.get('total_value', 0):.2f}")

                        elif rtype == 'Low Stock':
                            data = service.low_stock()
                            ui.label('Low Stock Products').classes('text-lg font-semibold mb-4')
                            for d in data:
                                ui.label(f"{d.get('name', '')} — Stock: {d.get('stock_quantity', 0)} / Min: {d.get('min_stock_level', 0)}")

                        elif rtype == 'Category Summary':
                            data = service.category_summary()
                            ui.label('Category Summary').classes('text-lg font-semibold mb-4')
                            for d in data:
                                ui.label(f"{d.get('category_name', '')}: {d.get('product_count', 0)} products, {d.get('total_stock', 0)} units")

                        elif rtype == 'Best Selling Products':
                            data = service.best_selling_products(start_date.value or None, end_date.value or None)
                            ui.label('Best Selling Products').classes('text-lg font-semibold mb-4')
                            for d in data:
                                ui.label(f"{d.get('product_name', '')} — {d.get('total_quantity', 0)} units sold")

                        elif rtype == 'Sales Report':
                            data = service.sales_report(start_date.value or None, end_date.value or None)
                            ui.label('Sales Report').classes('text-lg font-semibold mb-4')
                            for d in data:
                                ui.label(f"{d.get('period', '')}: {d.get('total_sales', 0)} sales, ${d.get('total_revenue', 0):.2f}")

                        elif rtype == 'Profit & Loss':
                            data = service.profit_loss_summary(start_date.value or None, end_date.value or None)
                            ui.label('Profit & Loss Summary').classes('text-lg font-semibold mb-4')
                            if data:
                                ui.label(f"Revenue: ${data[0].get('total_revenue', 0):.2f}")
                                ui.label(f"COGS: ${data[0].get('total_cogs', 0):.2f}")
                                ui.label(f"Gross Profit: ${data[0].get('gross_profit', 0):.2f}")

                        elif rtype == 'Supplier Performance':
                            data = service.supplier_performance(start_date.value or None, end_date.value or None)
                            ui.label('Supplier Performance').classes('text-lg font-semibold mb-4')
                            for d in data:
                                ui.label(f"{d.get('supplier_name', '')}: {d.get('total_purchases', 0)} purchases, ${d.get('total_amount', 0):.2f}")
                    except Exception as e:
                        ui.notify(f'Report error: {e}', type='negative')

        generate_btn.on_click(generate_report)
