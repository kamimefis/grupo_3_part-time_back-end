from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import inspect
from flask_login import LoginManager,UserMixin



db = SQLAlchemy()

inscripcion = db.Table('inscripcion',
    db.Column('id_persona',db.Integer, db.ForeignKey('personas.id_persona')),
    db.Column('id_lista', db.Integer, db.ForeignKey('listas_de_espera.id_lista'))
)

class Personas(db.Model, UserMixin):
    
    id_persona = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(50), nullable=False, unique=True)
    usuario = db.Column(db.String(50), nullable=True, unique=True)
    contraseña = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(25), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)
    codigo = db.Column(db.Integer, nullable=False)
    roles_id = db.Column(db.Integer, db.ForeignKey('roles.id_roles'), nullable=False)
    

    inscripciones = db.relationship('Listas_de_espera', secondary=inscripcion, backref=db.backref('integrantes'), lazy=True) 

    def is_active(self):
        # """True, as all users are active."""
        return True

    def get_id(self):
        # """Return the email address to satisfy Flask-Login's requirements."""
        return self.id_persona

    def is_authenticated(self):
        # """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        # """False, as anonymous users aren't supported."""
        return False
    def toDict(self): return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }
    # def __repr__(self):
    #     return "<Personas %r>" % self.correo
    def serialize(self):
        return {
            "id_persona":self.id_persona,
            "correo":self.correo,
            "roles_id":self.roles_id,
            "usuario":self.usuario,
            "nombre":self.nombre,
            "apellido": self.apellido,
            "codigo": self.codigo,
            "telefono": self.telefono
        }
class Listas_de_espera(db.Model):
    id_lista = db.Column(db.Integer, primary_key=True) 
    restaurante_id = db.Column(db.Integer, db.ForeignKey("restaurantes.id_restaurante"), unique=True, nullable=False)
    numero_mesas = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def __repr__(self):
        return "<Listas_de_espera %r>" % self.id
    def serialize(self):
        return {
            "id_lista":self.id_lista,
            "id_persona":self.id_persona,
            "restaurante_id":self.restaurante_id,
            "numero_mesas": self.numero_mesas,
            "fecha": self.fecha
        }
class Restaurantes(db.Model):
    id_restaurante = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    direccion= db.Column(db.String(50), nullable=False)
    telefono= db.Column(db.Integer, nullable=False)
    cantidad_maxima = db.Column(db.Integer, nullable=False)
    capacidad_lista_espera= db.Column(db.Integer, nullable=False)
    lista = db.relationship('Listas_de_espera', backref='creador', uselist=False)
    def __repr__(self):
        return "<Restaurantes %r>" % self.nombre
    def serialize(self):
        return {
            "id_restaurante":self.id_restaurante,
            "nombre":self.nombre,
            "cantidad_maxima": self.cantidad_maxima,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "capacidad_lista_espera": self.capacidad_lista_espera
        }
class Roles(db.Model):
    id_roles = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(25), nullable=False)
    personas = db.relationship('Personas', backref='rol', lazy=True)
    relaciones = db.relationship('Relaciones', backref='rol', lazy=True)

    def __repr__(self):
        return "<Roles %r>" % self.nombre_rol
    def serialize(self):
        return {
            "id_roles":self.id_roles,
            "rol":self.nombre_rol
        }
class Relaciones(db.Model):
    id_relacion = db.Column(db.Integer, primary_key=True) 
    id_paginas = db.Column(db.Integer, db.ForeignKey('paginas.id_paginas'), nullable=False)  
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id_roles'), nullable=False)
    def __repr__(self):
        return "<Relaciones %r>" % self.id
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
    relaciones = db.relationship('Relaciones', backref='pag', lazy=True)
    def __repr__(self):
        return "<Paginas %r>" % self.nombre_pagina
    def serialize(self):
        return {
            "id_paginas":self.id_paginas,
            "nombre_pagina":self.nombre_pagina,
            "ruta_pagina": self.ruta_pagina
        }