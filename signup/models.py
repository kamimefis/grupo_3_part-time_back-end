from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=True, unique=True)
    password = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    codigo = db.Column(db.Integer(), nullable=False)
    lists = db.relationship('Lista_de_espera', backref='poseedor', lazy=True) 
    def __repr__(self):
        return "<User %r>" % self.correo
    def serialize(self):
        return {
            "correo":self.correo,
            "username":self.username,
            "name":self.name,
            "id":self.id,
            "last_name": self.last_name,
            "codigo": self.last_name
        }

class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    persona_codigo = db.Column(db.Integer(), db.ForeignKey("persona.codigo"), nullable=False)
    rol = db.Column(db.String(25), nullable=False)
    def __repr__(self):
        return "<Roles %r>" % self.codigo_persona
    def serialize(self):
        return {
            "rol":self.rol,
            "codigo_persona":self.codigo_persona,
            "id":self.id
        }

class Lista_de_espera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer(), db.ForeignKey("persona.id"), nullable=False)
    restaurante_id = db.Column(db.Integer(), db.ForeignKey("restaurante.id"), unique=True ,nullable=False)
    numero_mesas = db.Column(db.Integer(), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def __repr__(self):
        return "<Lista_de_espera %r>" % self.id_persona
    def serialize(self):
        return {
            "id":self.id,
            "id_persona":self.id_persona,
            "id_restaurante":self.id_restaurante,
            "numero_mesas": self.numero_mesas,
            "fecha": self.fecha
        }

class Paginas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_pag = db.Column(db.String(50), nullable=False)
    URL = db.Column(db.String(50), nullable=False)
    def __repr__(self):
        return "<Paginas %r>" % self.nombre_pag
    def serialize(self):
        return {
            "id":self.id,
            "nombre_pag":self.nombre_pag,
            "URL": self.URL
        }

class Restaurante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    cantidad_maxima = db.Column(db.Integer(), nullable=False)
    lista = db.relationship('Lista_de_espera', backref='creador', uselist=False)
    def __repr__(self):
        return "<Restaurante %r>" % self.nombre
    def serialize(self):
        return {
            "id":self.id,
            "nombre":self.nombre,
            "cantidad_maxima": self.cantidad_maxima
        }

class Relacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rol_id = db.Column(db.Integer(), db.ForeignKey("rol.id"), nullable=False)
    paginas_id = db.Column(db.Integer(), db.ForeignKey("paginas.id"), nullable=False)


