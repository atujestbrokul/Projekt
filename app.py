from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, LoginManager, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_reviews.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Modele bazy danych
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    reviews = db.relationship('Review', backref='author', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    reviews = db.relationship('Review', backref='book', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(1000), nullable=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Ładowanie użytkownika
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Strona główna
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

# Strona rejestracji
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Rejestracja udana, możesz się zalogować!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Strona logowania
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        flash('Błędne dane logowania', 'danger')
    return render_template('login.html')

# Strona wylogowania
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Strona książki
@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        text = request.form.get('text')
        review = Review(rating=rating, text=text, book_id=book.id, user_id=current_user.id)
        db.session.add(review)
        db.session.commit()
        flash('Opinia została dodana!', 'success')
    reviews = Review.query.filter_by(book_id=book_id).all()
    return render_template('book_details.html', book=book, reviews=reviews)

# Uruchomienie aplikacji
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
