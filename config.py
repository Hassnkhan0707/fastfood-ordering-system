import os

class Config:
    SECRET_KEY = 'your-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fastfood.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False