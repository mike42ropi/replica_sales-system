def get_consecutive_sales(customer_id):
     with app.app_context():
        sales = Sales.query.filter_by(customer_id=customer_id).order_by(Sales.sale_id).all()

        
        sales = Sales.query.order_by(Sales.customer_id).all()

        for i in range(1, len(sales)):
            if sales[i].customer_id == sales[i].customer_id + 1:
                return False

        return True

# Example usage:
consecutive_sales_lists = get_consecutive_sales(Sales.customer_id)
print(consecutive_sales_lists)







