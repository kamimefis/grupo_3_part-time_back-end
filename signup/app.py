import os
import re
#from flask_mysqldb import MySQL
# import pymysql
# pymysql.install_as_MySQLdb()
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt 
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import Personas, db, Restaurantes#, Roles, Lista_de_espera, Paginas, Relacion, db

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

@app.route("/registro", methods=["POST"])
def signup():
    #expresion regular para validar email
    correo_reg= "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
    #expresion regular para valdiad contraseña (8 caracteres,alphanumerico, 1 simbolo, 1 mayuscula)
    contraseña_reg= "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$"
    #Instancia un nuevo usuario
    persona = Personas()
    #Checar email, el que recibo del front end
    if re.search(correo_reg, request.json.get("correo")):
        persona.correo= request.json.get("correo")
    else:
        return jsonify({"msg": "Este correo no tiene un formato válido"}), 401
    #checar contraseña, la que recibo del front end
    if re.search(contraseña_reg, request.json.get("contraseña")):
        contraseña_hash= bcrypt.generate_password_hash(request.json.get("contraseña"))
        persona.contraseña = contraseña_hash
    else:
        return jsonify({"msg":"El formato de la contraseña no es válido"}), 401
    
    persona.usuario = request.json.get("usuario", None)
    persona.nombre = request.json.get("nombre")
    persona.apellido = request.json.get("apellido")
    persona.codigo = request.json.get("codigo", 3)
    persona.roles_id = request.json.get("roles_id", 3)
    persona.telefono = request.json.get("telefono")


    db.session.add(persona)
    db.session.commit()

    return jsonify({"success":True}), 200


@app.route("/nuevo_restaurante", methods=["POST"])
def addrestaurant():
    #instanciando un nuevo restaurante:
    restaurante= Restaurantes()    
    #Procesando las peticiones que recibe del front
    restaurante.nombre= request.json.get("nombre")
    restaurante.direccion= request.json.get("direccion")
    restaurante.telefono= request.json.get("telefono")
    restaurante.cantidad_maxima= request.json.get("numero_mesas")
    restaurante.capacidad_lista_espera= request.json.get("cap_lista")

    db.session.add(restaurante)
    db.session.commit()

    return jsonify({"success":True}), 200

#obtener la lista de restaurantes
@app.route('/restaurantes',methods=['GET'])
def getRestaurantes():
    restaurantes = Restaurantes.query.all()
    restaurantesArr = []
    for restaurante in restaurantes:
        restaurantesArr.append(restaurante.toDict()) 
    return jsonify(restaurantesArr), 200

#obtener la informacion de un restaurante
@app.route('/restaurantes/<int:id>',methods=['GET'])
def getRestaurante(id):
    restaurante = Restaurantes.query.get(id)
    return jsonify({
    "restaurante": restaurante.serialize(),
    "success":True
    }), 200

#modifica un restaurante especifico
@app.route('/restaurantes/<int:id>',methods=['PUT'])
@cross_origin()
def putRestaurante(id):
    restaurante = Restaurantes.query.get(id)
    print("restaurante conseguido", restaurante)

    restaurante.nombre= request.json.get("nombre")
    restaurante.direccion= request.json.get("direccion")
    restaurante.telefono= request.json.get("telefono")
    restaurante.cantidad_maxima= request.json.get("numero_mesas")
    restaurante.capacidad_lista_espera= request.json.get("cap_lista")

    print("nuevo restaurante", restaurante)
    db.session.add(restaurante)
    db.session.commit()
    return jsonify({
        "success":True
        }), 200
@app.route("/restaurantes/<int:id>", methods=["DELETE"])
@cross_origin()
def deleteRestaurant(id):
    restaurante = Restaurantes.query.get(id)

    db.session.delete(restaurante)
    db.session.commit()
    return jsonify({"success":True}), 200

@app.route("/ingreso", methods =["POST"])
def login():
    #Validar que el json o el body del front no este vacia
    if not request.is_json:
        return jsonify({"msg": "El body o contenido esta vacío"}), 400

    correo = request.json.get("correo", None)
    contraseña=request.json.get("contraseña", None)

    if not correo:
        return jsonify({"msg":"Falta enviar el correo"}), 400
    if not contraseña: 
        return jsonify({"msg":"Falta enviar la contraseña"}),400
    
    persona=Personas.query.filter_by(correo=correo).first()  #.first() --> primera coincidencia

    if persona is None:
        return jsonify({"msg":"Este usuario no está registrado"}),404

    if bcrypt.check_password_hash(persona.contraseña, contraseña):
        access_token = create_access_token(identity=correo)
        return jsonify({
            "token_acceso":access_token,
            "usuario": persona.serialize(),
            "success":True
        }), 200
    else:
        return jsonify({"msg": "Contraseña erronea"}), 400


if __name__ == "__main__":
    manager.run()