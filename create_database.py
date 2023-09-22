


from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Create User class for the 'user' table
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email_address = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(10))
    street_address = db.Column(db.String(255))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.Integer)

# Create Pet class for the 'pet' table
class Pet(db.Model):
    pet_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    owner = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    breed = db.Column(db.String(50))
    weight = db.Column(db.Integer)
    owner_user = db.relationship('User', backref='pets')

# Create Device class for the 'device' table
class Device(db.Model):
    device_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    owner = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    device_type = db.Column(db.String(50))
    owner_user = db.relationship('User', backref='devices')

# Function to create the tables in the database
def create_tables():
    # Create all tables defined in the models
    db.create_all()

# Function to create the root user
def create_root_user():
    # Replace 'mysql://username:password@localhost/lt_data' with your MySQL connection details and the database name 'lt_data'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb://username:password@localhost/lt_data'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the app with the database
    db.init_app(app)

    # Create the tables
    create_tables()

    # Create the root user
    root_user = User(
        username='root',
        password='changepassword',
        email_address='root@example.com',
        first_name='Root',
        last_name='User',
        phone_number='1234567890',
        street_address='123 Main St',
        city='Cityville',
        state='ST',
        zip_code=12345
    )
    db.session.add(root_user)
    db.session.commit()

def create_custom_user():
    # Replace 'mysql://username:password@localhost/lt_data' with your MySQL connection details and the database name 'lt_data'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb://username:password@localhost/lt_data'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the app with the database
    db.init_app(app)

    # Create the tables
    create_tables()

    # Create the root user
    root_user = User(
        username='thebreckoning',
        password='changepassword',
        email_address='root@example.com',
        first_name='Root',
        last_name='User',
        phone_number='1234567890',
        street_address='123 Main St',
        city='Cityville',
        state='ST',
        zip_code=12345
    )
    db.session.add(root_user)
    db.session.commit()

if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)

    # Call the function to create the root user
    create_root_user()
