import os
import re
#from flask_mysqldb import MySQL
import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS 
from flask_bcrypt import Bcrypt 
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import Persona, db#, Roles, Lista_de_espera, Paginas, Restaurante, Relacion, db

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://uugolckfi3r7ndi8:uFPEk5YYKRbyuhfRaKYr@bt0g90jhwshtofahhgs4-mysql.services.clever-cloud.com/bt0g90jhwshtofahhgs4'
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


    db.session.add(persona)
    db.session.commit()

    return jsonify({"success":True})



if __name__ == "__main__":
    manager.run()