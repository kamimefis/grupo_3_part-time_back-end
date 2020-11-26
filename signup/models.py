from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

inscripcion = db.Table('inscripcion',
    db.Column('id_persona',db.Integer, db.ForeignKey('persona.id_persona')),
    db.Column('id_lista', db.Integer, db.ForeignKey('lista_de_espera.id_lista'))
)

class Persona(db.Model):
    id_persona = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=True, unique=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)
    codigo = db.Column(db.Integer, nullable=False)
    roles_id = db.Column(db.Integer, db.ForeignKey('roles.id_roles'), nullable=False)
    rol = db.relationship('roles', backref=db.backref('rol', lazy=True))

    inscripciones = db.relationship('Lista_de_espera', secondary=inscripcion, backref=db.backref('integrantes'), lazy=True) 
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
        }
class Lista_de_espera(db.Model):
    id_lista = db.Column(db.Integer, primary_key=True) 
    restaurante_id = db.Column(db.Integer, db.ForeignKey("restaurante.id_restaurante"), unique=True, nullable=False)
    numero_mesas = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def __repr__(self):
        return "<Lista_de_espera %r>" % self.id
    def serialize(self):
        return {
            "id_lista":self.id_lista,
            "id_persona":self.id_persona,
            "restaurante_id":self.restaurante_id,
            "numero_mesas": self.numero_mesas,
            "fecha": self.fecha
        }
class Restaurante(db.Model):
    id_restaurante = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    cantidad_maxima = db.Column(db.Integer, nullable=False)
    lista = db.relationship('Lista_de_espera', backref='creador', uselist=False)
    def __repr__(self):
        return "<Restaurante %r>" % self.nombre
    def serialize(self):
        return {
            "id_restaurante":self.id_restaurante,
            "nombre":self.nombre,
            "cantidad_maxima": self.cantidad_maxima
        }
class Roles(db.Model):
    id_roles = db.Column(db.Integer, primary_key=True)
    rol = db.Column(db.String(25), nullable=False)
    relaciones = db.relationship('Relacion', backref='rol', lazy=True)

    def __repr__(self):
        return "<Roles %r>" % self.rol
    def serialize(self):
        return {
            "id_roles":self.id_roles,
            "rol":self.rol
        }
class Relacion(db.Model):
    id_relacion = db.Column(db.Integer, primary_key=True) 
    id_paginas = db.Column(db.Integer, db.ForeignKey('paginas.id_paginas'), nullable=False)  
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id_roles'), nullable=False)
    def __repr__(self):
        return "<Relacion %r>" % self.id
    def serialize(self):
        return {
            "id_relacion":self.id_relacion,
            "id_rol":self.rol_id,
            "id_paginas": self.id_paginas
        }
class Paginas(db.Model):
    id_paginas = db.Column(db.Integer, primary_key=True)
    nombre_pagina = db.Column(db.String(50), nullable=False)
    ruta_pagina = db.Column(db.String(50), nullable=False)
    relaciones = db.relationship('Relacion', backref='pag', lazy=True)
    def __repr__(self):
        return "<Paginas %r>" % self.nombre_pagina
    def serialize(self):
        return {
            "id_paginas":self.id_paginas,
            "nombre_pagina":self.nombre_pagina,
            "ruta_pagina": self.ruta_pagina
        }

