from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import *
# from sqlalchemy import Column, Integer, ForeignKey, String, Numeric
from sqlalchemy.orm import relationship,aliased
from sqlalchemy import DateTime,func
from flask_login import *
# from main import add_sales 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sequence150@localhost:5432/myduka_rep'
db=SQLAlchemy(app)


class Products(db.Model):
    __tablename__='products'
    product_id = db.Column(db.Integer,primary_key= True)
    product_name = db.Column(db.String(255),nullable=False)
    buying_price = db.Column(db.Numeric(precision=15, scale=2),nullable=False)
    selling_price = db.Column(db.Numeric(precision=15, scale=2),nullable=False)
    stock_quantity = db.Column(db.Numeric(precision=15, scale=2),nullable=False)
    # relationship defination
    salesdetails = relationship('Salesdetails', back_populates='products')
    sales=relationship("Sales",back_populates="products")
                      
class Users(db.Model,UserMixin):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key= True)
    email=db.Column(db.String(255),nullable=False, unique=True)
    password=db.Column(db.String(255),nullable=False)
    username=db.Column(db.String(255),nullable=False)
    status=db.Column(db.String(255),nullable=False)
class Salesdetails(db.Model):
   __tablename__='salesdetails'
   salesdetails_id=db.Column(db.Integer,primary_key= True)
   sales_id=db.Column(db.Integer, db.ForeignKey('sales.sale_id'))
   product_id=db.Column(db.Integer, db.ForeignKey('products.product_id'))
   quantity=db.Column(db.Numeric(precision=15, scale=2),nullable=False)
   purchase_amount=db.Column(db.Numeric(precision=15, scale=2),nullable=False)
   # foreign key relationship defination
   sales=relationship("Sales",back_populates="salesdetails")
   products=relationship("Products",back_populates="salesdetails")
   


class Sales(db.Model):
   __tablename__='sales'
   sale_id=db.Column(db.Integer,primary_key= True)
   customer_id=db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
   product_id=db.Column(db.Integer, db.ForeignKey('products.product_id'))
   user_id=db.Column(db.Integer, db.ForeignKey('users.id'))
   total_amount=db.Column(db.Numeric(precision=15, scale=2),nullable=False)
   created_at=db.Column(DateTime,default=db.func.curent_timestamp())
   
   # foreign key relationship defination
   products=relationship("Products",back_populates="sales")
   customers=relationship("Customers",back_populates="sales")
   salesdetails = relationship('Salesdetails', back_populates='sales')
   payments = relationship('Payments', back_populates='sales')


class Customers(db.Model):
   __tablename__='customers'
   customer_id=db.Column(db.Integer,primary_key= True)
   full_name=db.Column(db.String(255),nullable=False)
   phone_number=db.Column(db.String(255),nullable=False)
   email=db.Column(db.String(255),nullable=False)
   # foreign key relationship defination
   sales=relationship("Sales",back_populates="customers")
   payments=relationship("Payments",back_populates="customers")

class Payments(db.Model):
   __tablename__='payments'
   payment_id=db.Column(db.Integer,primary_key= True)
   sales_id=db.Column(db.Integer, db.ForeignKey('sales.sale_id'))
   customer_id=db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
   payment_method=db.Column(db.String(255),nullable=False)
   amount=db.Column(db.Numeric(precision=15, scale=2),nullable=False)

   # foreign key relationship defination
   sales=relationship("Sales",back_populates="payments")
   customers=relationship("Customers",back_populates="payments")

class Employees(db.Model):
   __tablename__='employees'
   employee_id=db.Column(db.Integer,primary_key= True)
   employee_name=db.Column(db.String(255),nullable=False)
   employee_number=db.Column(db.String(255),nullable=False)
   employee_email=db.Column(db.String(255),nullable=False)
   employee_position=db.Column(db.String(255),nullable=False)

class SalesSummary(db.Model):
    __tablename__ = 'sales_summary'

    id = db.Column(db.Integer, primary_key=True)
    start_sale_id = db.Column(db.Integer)
    end_sale_id = db.Column(db.Integer)
    total_product_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    total_amount = db.Column(db.Numeric(precision=15, scale=2),nullable=False)
    start_created_at = db.Column(DateTime,default=db.func.curent_timestamp())
    end_created_at = db.Column(DateTime,default=db.func.curent_timestamp())

def update_status_to_online(user_id):
    user = Users.query.get(user_id)
    
    if user :
        user.status = "online"
        db.session.commit()
        return True
    else:
        return False
    

def update_status_to_offline(user_id):
    user = Users.query.get(user_id)
    
    if user :
        user.status = "offline"
        db.session.commit()
        return True
    else:
        return False
    

# def salesdetails1():
#     with app.app_context():
#         # Aliases for the two instances of the 'Sales' table
#         # sales_alias1 = aliased(Sales)
#         # sales_alias2 = aliased(Sales)

#         # Common Table Expression (CTE) to calculate the customer_group
#         ranked_sales_cte = (
#     db.session.query(
#         Sales.sale_id,
#         Sales.customer_id,
#         Sales.user_id,
#         Sales.total_amount,
#         Sales.created_at,
#         Sales.product_id,
#         func.row_number().over(order_by=Sales.created_at).label('row_number'),
#         func.row_number().over(partition_by=Sales.customer_id, order_by=Sales.created_at).label('customer_row_number')
#     )
#     .cte('ranked_sales')
# )

# # Main Query
#         result = (
#             db.session.query(
#                 func.min(ranked_sales_cte.c.sale_id).label('start_sale_id'),
#                 func.max(ranked_sales_cte.c.sale_id).label('end_sale_id'),
#                 func.count(ranked_sales_cte.c.product_id).label('total_product_id'),
#                 func.min(ranked_sales_cte.c.customer_id).label('customer_id'),
#                 func.min(ranked_sales_cte.c.user_id).label('user_id'),
#                 func.sum(ranked_sales_cte.c.total_amount).label('total_amount'),
#                 func.min(ranked_sales_cte.c.created_at).label('start_created_at'),
#                 func.max(ranked_sales_cte.c.created_at).label('end_created_at'),
#             )
#             .group_by(ranked_sales_cte.c.customer_id)
#             .order_by(func.min(ranked_sales_cte.c.created_at))
#             .all()
#         )
#         if result:
#     # Select the last tuple automatically
#             recent_sale = result[-1] 

#             # Extract values from the last tuple
#             start_sale_id = recent_sale.start_sale_id
#             end_sale_id = recent_sale.end_sale_id
#             total_product_id = recent_sale.total_product_id
#             customer_id = recent_sale.customer_id
#             user_id = recent_sale.user_id
#             total_amount = recent_sale.total_amount

#             # Create a new Salesdetails instance for the most recent sale
#             new_salesdetails = (start_sale_id,total_product_id,total_product_id,total_amount)
#             # Create a new Salesdetails instance for the most recent sale
#             # new_salesdetails =(start_sale_id,total_product_id,total_product_id,total_amount
            

#             # Add to the session and commit
#             # db.session.add(new_salesdetails)
#             # db.session.commit()
#         return new_salesdetails


# abc=salesdetails1()
# print(abc)
def generate_sales_summary():
    # Aliases for the two instances of the 'Sales' table
    # sales_alias1 = aliased(Sales)
    # sales_alias2 = aliased(Sales)

    with app.app_context():
    # Common Table Expression (CTE) to calculate the customer_group
        ranked_sales_cte = (
            db.session.query(
                Sales.sale_id,
                Sales.customer_id,
                Sales.user_id,
                Sales.total_amount,
                Sales.created_at,
                Sales.product_id,
                func.row_number().over(order_by=Sales.created_at).label('row_number'),
                func.row_number().over(partition_by=Sales.customer_id, order_by=Sales.created_at).label('customer_row_number'),
                (func.row_number().over(order_by=Sales.created_at) -
                    func.row_number().over(partition_by=Sales.customer_id, order_by=Sales.created_at)).label('customer_group')
            )
            .cte('ranked_sales')
        )

        # Main Query to select aggregated information based on customer_group
        result = (
            db.session.query(
                func.min(ranked_sales_cte.c.sale_id).label('start_sale_id'),
                func.max(ranked_sales_cte.c.sale_id).label('end_sale_id'),
                func.count(ranked_sales_cte.c.product_id).label('total_product_id'),
                func.min(ranked_sales_cte.c.customer_id).label('customer_id'),
                func.min(ranked_sales_cte.c.user_id).label('user_id'),
                func.sum(ranked_sales_cte.c.total_amount).label('total_amount'),
                func.min(ranked_sales_cte.c.created_at).label('start_created_at'),
                func.max(ranked_sales_cte.c.created_at).label('end_created_at'),
                func.min(ranked_sales_cte.c.customer_group).label('customer_group'),
            )
            .group_by(ranked_sales_cte.c.customer_group)
            .order_by(func.min(ranked_sales_cte.c.created_at))
            .all()
        )

        # Insert the result into the SalesSummary table
        for row in result:
            summary = SalesSummary(
                start_sale_id=row.start_sale_id,
                end_sale_id=row.end_sale_id,
                total_product_id=row.total_product_id,
                customer_id=row.customer_id,
                user_id=row.user_id,
                total_amount=row.total_amount,
                start_created_at=row.start_created_at,
                end_created_at=row.end_created_at
            )
            db.session.add(summary)

        # Commit the changes
        db.session.commit()

l=generate_sales_summary()
print(l)

