from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, FoodItem, Order, OrderItem
from config import Config
import random
import string

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables and seed initial data
with app.app_context():
    db.create_all()
    
    # Seed food items if database is empty
    if FoodItem.query.count() == 0:
        initial_foods = [
            FoodItem(name="Classic Beef Burger", category="Burger", price=550, image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop"),
            FoodItem(name="Crispy Chicken Burger", category="Burger", price=490, image_url="https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=400&h=300&fit=crop"),
            FoodItem(name="Double Cheese Melt", category="Burger", price=680, image_url="https://images.unsplash.com/photo-1550547660-d9450f859349?w=400&h=300&fit=crop"),
            FoodItem(name="Grilled Chicken Sandwich", category="Sandwich", price=520, image_url="https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&h=300&fit=crop"),
            FoodItem(name="Club Sandwich", category="Sandwich", price=450, image_url="https://images.unsplash.com/photo-1578674914187-d3306b1b8d93?w=400&h=300&fit=crop"),
            FoodItem(name="Spicy Paneer Wrap", category="Sandwich", price=470, image_url="https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400&h=300&fit=crop"),
            FoodItem(name="Hot & Crispy Fried Chicken", category="Chicken", price=620, image_url="https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=400&h=300&fit=crop"),
            FoodItem(name="Chicken Popcorn Box", category="Chicken", price=380, image_url="https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=400&h=300&fit=crop"),
            FoodItem(name="Buffalo Wings (6pcs)", category="Chicken", price=590, image_url="https://images.unsplash.com/photo-1562967916-eb82221dfb92?w=400&h=300&fit=crop"),
            FoodItem(name="Zinger Stacker", category="Burger", price=720, image_url="https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400&h=300&fit=crop"),
            FoodItem(name="Philly Cheesesteak", category="Sandwich", price=790, image_url="https://images.unsplash.com/photo-1553909489-cd47e0907980?w=400&h=300&fit=crop"),
            FoodItem(name="BBQ Chicken Wrap", category="Chicken", price=540, image_url="https://images.unsplash.com/photo-1626074353765-517a681e40be?w=400&h=300&fit=crop"),
            FoodItem(name="French Fries Large", category="Sides", price=250, image_url="https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&h=300&fit=crop"),
            FoodItem(name="Onion Rings", category="Sides", price=280, image_url="https://images.unsplash.com/photo-1639024471283-035188835b0b?w=400&h=300&fit=crop"),
            FoodItem(name="Soft Drink (500ml)", category="Beverages", price=120, image_url="https://images.unsplash.com/photo-1622484214939-6a2b3c1c1b8d?w=400&h=300&fit=crop"),
        ]
        db.session.add_all(initial_foods)
        db.session.commit()
        
        # Create a demo user (username: customer, password: 1234)
        # In production, hash this password!
        demo_user = User.query.filter_by(username='customer').first()
        if not demo_user:
            demo_user = User(username='customer', password='1234', full_name='Demo Customer')
            db.session.add(demo_user)
            db.session.commit()

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # Simple password check (in production, use hashed passwords!)
        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('menu'))
        else:
            flash('Invalid username or password. Use customer/1234 for demo.', 'danger')
    
    return render_template('login.html')

@app.route('/menu')
@login_required
def menu():
    # Get all available food items
    food_items = FoodItem.query.filter_by(is_available=True).all()
    
    # Group by category for display
    categories = {}
    for item in food_items:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item)
    
    return render_template('menu.html', user=current_user, categories=categories)

@app.route('/order/<int:food_id>', methods=['GET', 'POST'])
@login_required
def order_food(food_id):
    food_item = FoodItem.query.get_or_404(food_id)
    
    if request.method == 'POST':
        quantity = int(request.form.get('quantity', 1))
        total_amount = food_item.price * quantity
        
        # Create new order
        new_order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status='pending',
            payment_method='easypaisa'
        )
        db.session.add(new_order)
        db.session.flush()  # Get order ID
        
        # Add order item
        order_item = OrderItem(
            order_id=new_order.id,
            food_item_id=food_item.id,
            quantity=quantity,
            price_at_time=food_item.price
        )
        db.session.add(order_item)
        db.session.commit()
        
        # Redirect to payment page
        return redirect(url_for('payment', order_id=new_order.id))
    
    return render_template('payment.html', food_item=food_item, order=None)

@app.route('/payment/<int:order_id>')
@login_required
def payment(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    order_item = order.items[0] if order.items else None
    food_item = order_item.food_item if order_item else None
    
    return render_template('payment.html', order=order, food_item=food_item)

@app.route('/process_payment/<int:order_id>', methods=['POST'])
@login_required
def process_payment(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    # Generate mock transaction ID
    transaction_id = 'EP' + ''.join(random.choices(string.digits, k=10))
    
    # Update order status
    order.status = 'paid'
    order.transaction_id = transaction_id
    
    db.session.commit()
    
    flash(f'Payment successful! Transaction ID: {transaction_id}', 'success')
    return redirect(url_for('order_confirmation', order_id=order.id))

@app.route('/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('order_confirmation.html', order=order)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)