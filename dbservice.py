from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import *
# from sqlalchemy import Column, Integer, ForeignKey, String, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
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

