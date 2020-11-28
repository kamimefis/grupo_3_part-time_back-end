from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()


class Persona(db.Model):
    id_persona = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=True, unique=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)
    codigo = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return "<User %r>" % self.correo
    def serialize(self):
        return {
            "id_persona":self.id_persona,
            "correo":self.correo,
            "username":self.username,
            "name":self.name,
            "last_name": self.last_name,
            "codigo": self.codigo,
            "telefono": self.telefono
        }