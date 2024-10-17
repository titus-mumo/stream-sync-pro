from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship

db = SQLAlchemy()  # Create an instance of SQLAlchemy

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    def get_id(self):
        return int(self.user_id)

class Following(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to the user who is following (follower)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    
    # Foreign key to the user being followed
    followed_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    
    # Relationships to access the user models easily
    follower = relationship('User', foreign_keys=[follower_id], backref='following')
    followed = relationship('User', foreign_keys=[followed_id], backref='followers')
    
    def __repr__(self):
        return f"Following(follower={self.follower_id}, followed={self.followed_id})"