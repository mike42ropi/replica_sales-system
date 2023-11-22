from flask import render_template, session, request, url_for, redirect, flash
from dbservice import *
from flask_login import LoginManager, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

with app.app_context():
    db.create_all()

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
            generate_sales_summary()
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


@app.route("/add-sales" , methods=['GET','POST'])
def add_sales():
    if request.method == "POST":
        # product_id=request.form["product_id"]
        user_id1=db.session.query(Users.id).filter(Users.status == 'online').all()
        user_id=int(list(user_tuple[0] for user_tuple in user_id1)[0])
        if 'total_amount' in request.form:
            total_amount = request.form['total_amount']
            # Process the total_amount
            # ...
        
            total_amount = request.form["total_amount"]
            product_id = request.form["product_id"]
            customer_id = request.form["customer_id"]
            created_at= datetime.now().replace(microsecond=0)

        # total_amount=stotal_amount1))

        new_product=Sales(customer_id = customer_id,
                          product_id=product_id,
                             user_id=user_id,
                            total_amount=total_amount,                           
                            created_at = created_at)
            
        db.session.add(new_product)
        db.session.commit()
        generate_sales_summary()
        flash("Sale made")
        
        
            
        return redirect("/sales")
@app.route("/sales",methods=['POST','GET'])
def sales():
   
    
    records1 = Products.query.all()
    products = [prod for prod in records1]

    records2 = Customers.query.all()
    customers = [cust for cust in records2]
    
    records = Sales.query.all()
    sales = [sal for sal in records]
    return render_template("sales.html", sales = sales, products = products, customers = customers)
    
@app.route("/sale-s", methods=['POST', 'GET'])
def salessummary():
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
                func.row_number().over(partition_by=Sales.customer_id, order_by=Sales.created_at).label('customer_row_number')
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
                end_created_at=row.end_created_at,
                customer_group=row.customer_group
            )
            db.session.add(summary)

        # Commit the changes
        db.session.commit()

    # Attach the event listener to the 'after_insert' event of the Sales table
        event.listen(Sales, 'after_insert', generate_sales_summary)

    # Call the function to generate and insert the initial sales summary
        generate_sales_summary(db, None, None)

        return render_template("salesdetails.html", salesdetails=salesdetails)
@app.route("/salesdetails", methods=['POST', 'GET'])
def salesdetails():
        with app.app_context():
        # Aliases for the two instances of the 'Sales' table
        # sales_alias1 = aliased(Sales)
        # sales_alias2 = aliased(Sales)

        # Common Table Expression (CTE) to calculate the customer_group
            ranked_sales_cte = (
                db.session.query(
                    Sales.sale_id,
                    Sales.customer_id,
                    Sales.user_id,
                    Sales.total_amount,
                    Sales.created_at,
                    Sales.product_id,
                    )
                .cte('ranked_sales')
            )

            # Main Query to select aggregated information based on customer_group
            result = (db.session.query(
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
                .group_by(ranked_sales_cte.c.customer_id) 
                .order_by(func.min(ranked_sales_cte.c.created_at))
                .all()
            )

            # Check if there are results
            if result:
                # Select the last tuple automatically
                recent_sale = result[-1]

                # Extract values from the last tuple
                start_sale_id = recent_sale.start_sale_id
                end_sale_id = recent_sale.end_sale_id
                total_product_id = recent_sale.total_product_id
                customer_id = recent_sale.customer_id
                user_id = recent_sale.user_id
                total_amount = recent_sale.total_amount

                # Create a new Salesdetails instance for the most recent sale
                new_salesdetails = Salesdetails(
                    sales_id=start_sale_id,
                    product_id=total_product_id,
                    quantity=total_product_id,
                    purchase_amount=total_amount,
                )

                # Add to the session and commit
                db.session.add(new_salesdetails)
                db.session.commit()
        records = Salesdetails.query.all()
        salesdetails = [sd for sd in records] 
        return render_template("salesdetails.html", salesdetails=salesdetails)

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
    user=Users.query.filter_by(status="online").first()
    if 'user_id' not in session:
        update_status_to_offline(user.id)
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

