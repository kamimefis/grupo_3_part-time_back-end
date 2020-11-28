import os
import re
from flask_mysqldb import MySQL
# import pymysql
# pymysql.install_as_MySQLdb()
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS 
from flask_bcrypt import Bcrypt 
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import Persona, db, Restaurante#, Roles, Lista_de_espera, Paginas, Relacion, db

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://uugolckfi3r7ndi8:uFPEk5YYKRbyuhfRaKYr@bt0g90jhwshtofahhgs4-mysql.services.clever-cloud.com:3306/bt0g90jhwshtofahhgs4'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
app.config["ENV"] = "development"
app.config["JWT_SECRET_KEY"]= "encrypt"

db.init_app(app)
Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)

@app.route("/signup", methods=["POST"])
def signup():
    #expresion regular para validar email
    email_reg= "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
    #expresion regular para valdiad contraseña (8 caracteres,alphanumerico, 1 simbolo, 1 mayuscula)
    password_reg= "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$"
    #Instancia un nuevo usuario
    persona = Persona()
    #Checar email, el que recibo del front end
    if re.search(email_reg, request.json.get("correo")):
        persona.correo= request.json.get("correo")
    else:
        return jsonify({"msg": "Este correo no tiene un formato válido"}), 401
    #checar contraseña, la que recibo del front end
    if re.search(password_reg, request.json.get("password")):
        password_hash= bcrypt.generate_password_hash(request.json.get("password"))
        persona.password = password_hash
    else:
        return jsonify({"msg":"El formato de la contraseña no es válido"}), 401
    
    persona.username = request.json.get("username", None)
    persona.name = request.json.get("name")
    persona.last_name = request.json.get("last_name")
    persona.codigo = request.json.get("codigo", 3)
    persona.roles_id = request.json.get("roles_id", 3)
    persona.telefono = request.json.get("telefono")


    db.session.add(persona)
    db.session.commit()

    return jsonify({"success":True})


@app.route("/addrestaurant", methods=["POST"])
def addrestaurant():
    #instanciando un nuevo restaurante:
    restaurante= Restaurante()    
    #Procesando las peticiones que recibe del front
    restaurante.nombre= request.json.get("nombre")
    restaurante.direccion= request.json.get("direccion")
    restaurante.telefono= request.json.get("telefono")
    restaurante.cantidad_maxima= request.json.get("numero_mesas")
    restaurante.capacidad_lista_espera= request.json.get("cap_lista")

    db.session.add(restaurante)
    db.session.commit()

    return jsonify({"success":True})

@app.route("/login", methods =["POST"])
def login():
    #Validar que el json o el body del front no este vacia
    if not request.is_json:
        return jsonify({"msg": "El body o contenido esta vacío"}), 400

    correo = request.json.get("correo", None)
    password=request.json.get("password", None)

    if not correo:
        return jsonify({"msg":"Falta enviar el correo"}), 400
    if not password: 
        return jsonify({"msg":"Falta enviar la contraseña"}),400
    
    persona=Persona.query.filter_by(correo=correo).first()  #.first() --> primera coincidencia

    if persona is None:
        return jsonify({"msg":"Este usuario no está registrado"}),404

    if bcrypt.check_password_hash(persona.password, password):
        access_token = create_access_token(identity=correo)
        return jsonify({
            "access_token":access_token,
            "user": persona.serialize(),
            "success":True
        }), 200
    else:
        return jsonify({"msg": "Contraseña erronea"}), 400


if __name__ == "__main__":
    manager.run()