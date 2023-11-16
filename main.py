from flask import render_template, session, request, url_for, redirect, flash
from dbservice import *
from flask_login import LoginManager, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# with app.app_context():
#     db.create_all()

app.secret_key= "Ropi"
login_manager=LoginManager(app)


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.route("/")
def home():
    return render_template("landingpage.html")


@app.route("/register",methods=['POST','GET'])
def register():
    if request.method == "POST":
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password"]
        #hash the password
        hashed_password=generate_password_hash(password)
        #check if the email exist
        user=Users.query.filter_by(email=email).first()
        if user :
            flash("Email already exist")
        else:
            new_user=Users(password=hashed_password,
                           email=email,
                           username=username)
            db.session.add(new_user)
            db.session.commit()
            flash("You have succesfully registered")
            return redirect (url_for('login'))
        
    return render_template("register.html")
   
@app.route("/login" ,methods=['GET','POST'])
def login():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']

        user=Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password) :
            login_user(user)
            update_status_to_online(user.id)

            flash("Welcome")
            return redirect (url_for('dashboard'))
        else:
            flash("Invalid username or password")
            return redirect (url_for('login'))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    
    return render_template("dashboard.html")


@app.route("/products",methods=['POST','GET'])
def products():
    if request.method == "POST":
        product_name = request.form["product_name"]
        buying_price = request.form["buying_price"]
        selling_price = request.form["selling_price"]
        stock_quantity = request.form["stock_quantity"]
        
        new_product=Products(product_name = product_name,
                             buying_price = buying_price,
                             selling_price = selling_price,
                             stock_quantity = stock_quantity)
        
        db.session.add(new_product)
        db.session.commit()
        flash("Product added succesfully")
        return redirect(url_for("products"))
       
    records = Products.query.all()
    products = [prod for prod in records]
    return render_template("products.html", products = products)


@app.route("/add_sales" , methods=['POST'])
def add_sales():
    if request.method == "POST":
        product_id = request.form["product_id"]
        quantity = request.form["quantity"]
        user_id=Users.query.filter_by(status="online").first()
        created_at= datetime.now().replace(microsecond=0)
            
        new_product=Products(product_id = product_id,
                            quantity = quantity,
                            created_at = created_at,)
            
        db.session.add(new_product)
        db.session.commit()
        flash("Product added succesfully")
        
        return redirect("/sales")
@app.route("/sales",methods=['POST','GET'])
def sales():
    
       
    records1 = Products.query.all()
    products = [prod for prod in records1]
    
    records = Sales.query.all()
    sales = [sale for sale in records]
    return render_template("sales.html", sales=sales, products = products)
    

@app.route("/employees",methods=['POST','GET'])
def employees():
    if request.method == "POST":
        employee_name=request.form["name"]
        employee_number=request.form["phonenumber"]
        employee_email=request.form["email"]
        employee_position=request.form["position"]
        
         
        #check if the email exist
        user=Employees.query.filter_by(employee_email=employee_email).first()
        if user :
            flash("Email already exist")
        else:
            new_employee=Employees(employee_name=employee_name,
                           employee_number=employee_number,
                           employee_email=employee_email,
                           employee_position=employee_position)
            db.session.add(new_employee)
            db.session.commit()
            flash("You have succesfully registered")
            return redirect (url_for('employees'))
        
    records = Employees.query.all()
    employees = [emp for emp in records]
    return render_template("employees.html", employees = employees)    

@app.route("/customers",methods=['POST','GET'])
def customers():
    if request.method == "POST":
        full_name=request.form["name"]
        phone_number=request.form["phonenumber"]
        email=request.form["email"]
        
        
         
        #check if the email exist
        user=Customers.query.filter_by(email=email).first()
        if user :
            flash("Email already exist")
        else:
            new_customer=Customers(full_name=full_name,
                                    phone_number=phone_number,
                                    email=email)
            db.session.add(new_customer)
            db.session.commit()
            flash("You have succesfully registered")
            return redirect (url_for('customers'))
        
    records = Customers.query.all()
    customers = [cust for cust in records]
    return render_template("customers.html", customers = customers)   

@app.route("/users")
def users():
    records = Users.query.all()
    users = [use for use in records]
    return render_template("users.html", users = users)

@app.route("/logout")
def logout():
    logout_user()
    flash("Logged Out")
    return redirect(url_for("login"))

# def update_status(user_id):
#     user = Users.query.get(user_id)
    
#     if user in session:
#         user.status = "online"
#         db.session.commit()
#         return True
#     else:
#         return False 

if __name__ == "__main__":
    app.run(debug=True)

