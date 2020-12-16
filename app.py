from dotenv import load_dotenv
import os
import re
from twilio.rest import Client
#from flask_mysqldb import MySQL
from models import Personas,db, Restaurantes, Listas_de_espera, Personas_lista#, Roles, Lista_de_espera, Paginas, Relacion, db
# import pymysql
# pymysql.install_as_MySQLdb()
from flask import Flask, jsonify, request, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, decode_token
from flask_mail import Mail, Message
import datetime
from sqlalchemy  import create_engine, text

BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://uugolckfi3r7ndi8:uFPEk5YYKRbyuhfRaKYr@bt0g90jhwshtofahhgs4-mysql.services.clever-cloud.com:3306/bt0g90jhwshtofahhgs4'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
app.config["ENV"] = "development"
app.config["JWT_SECRET_KEY"]= "23123nsdngh234341"
app.secret_key = "97682sbdvffdvshg2662tvsncgaf25"
app.config['JWT_TOKEN_LOCATION'] = ['headers']

engine = create_engine('mysql://uugolckfi3r7ndi8:uFPEk5YYKRbyuhfRaKYr@bt0g90jhwshtofahhgs4-mysql.services.clever-cloud.com:3306/bt0g90jhwshtofahhgs4')
conn = engine.connect()

db.init_app(app)
Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'ingreso'
login_manager.login_message_category = 'info'

CORS(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']= os.environ["EMAIL_ACCOUNT"]
app.config['MAIL_PASSWORD']= os.environ["EMAIL_PASSWORD"]
app.config['MAIL_DEFAULT_SENDER'] = ('Restaurant App', os.environ["EMAIL_ACCOUNT"])
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail = Mail(app)

account_sid = os.environ["TWILIO_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]

@app.route("/ws", methods=["POST"])
def ws():
    usuario = request.json.get("usuario").capitalize()
    restaurante = request.json.get("restaurante").capitalize()
    numero = 971843668
    direccion = request.json.get("direccion").capitalize()

    client = Client(account_sid, auth_token)
    message = client.messages.create(
         body=f"Saludos {usuario}, esta proximo su turno para entrar al establecimiento! \n{restaurante}, ubicacion: {direccion} \n--Restaurant App--",
         from_='whatsapp:+14155238886',
         to=f'whatsapp:+56{numero}'
     )
    print("ws msg",message.sid)
    return jsonify({"success":True}), 200


@login_manager.user_loader
def load_user(user_id):
    return Personas.query.get(int(user_id))
# @app.route('/')
# def hello():
#     return redirect("https://3000-eb757d8f-9d8d-44ab-9c5c-853c08773fa5.ws-us02.gitpod.io/home", code=302)
######CRUD PERSONAS######

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

@app.route("/registro", methods=["GET"])
def getPersonas():
     persona = Personas()
     personas = persona.query.all() 
     personaArr = [] 
     for persona in personas: 
        personaArr.append(persona.toDict()) 
     return jsonify(personaArr), 200

     return jsonify({"success":True}), 200


@app.route("/registro/<int:id>", methods=["GET"])
def getPersona(id):
     persona = Personas()
     getpersona = persona.query.get(id) 
     return jsonify(getpersona.toDict()), 200

@app.route("/registro/<int:id>", methods=["DELETE"])
def deletePersona(id):
     persona = Personas()
     delpersona = persona.query.get(id) 
     db.session.delete(delpersona)
     db.session.commit()
     return jsonify({"done": True}), 200

##LOGIN PERSONAS##
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
    if current_user.is_authenticated:
         return jsonify({"msg":"Authenticated"})
    
    persona= Personas.query.filter_by(correo=correo).first()  #.first() --> primera coincidencia
    if persona is None:
        return jsonify({"msg":"Este usuario no está registrado"}),404
    if bcrypt.check_password_hash(persona.contraseña, contraseña):
        expiracion = datetime.timedelta(hours=24)
        access_token = create_access_token(identity=correo, expires_delta=expiracion)
        login_user(persona)
        
        return jsonify({
            "token_acceso":access_token,
            "usuario": persona.serialize(),
            "success":True
        }), 200
    else:
        return jsonify({"msg": "Contraseña erronea"}), 400
# @app.route("/logout")
# def logout():
#     logout_user()
#     return jsonify({"msg": "Ha cerrado sesión correctamente"})

######CRUD RESTAURANTE######

@app.route("/nuevo_restaurante", methods=["POST"])
def addrestaurant():
    #instanciando un nuevo restaurante:
    restaurante= Restaurantes()    
    #Procesando las peticiones que recibe del front
    restaurante.nombre= request.json.get("nombre")
    restaurante.direccion= request.json.get("direccion")
    restaurante.telefono= request.json.get("telefono")
    restaurante.numero_mesas= request.json.get("numero_mesas")
    restaurante.capacidad_lista_espera= request.json.get("cap_lista")
    restaurante.descripcion_rest= request.json.get("descripcion_rest")

    db.session.add(restaurante)
    db.session.commit()

    return jsonify({"success":True})

#obtener la lista de restaurantes
@app.route('/restaurantes',methods=['GET'])
@jwt_required
def getRestaurantes():
    restaurantes = Restaurantes.query.all()
    restaurantesArr = []
    for restaurante in restaurantes:
        restaurantesArr.append(restaurante.toDict()) 
    usuario_actual = get_jwt_identity() 
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


#-----recuperar contraseña-----
@app.route('/olvide_contraseña', methods=["POST"])
def olvide_contrasena():
    url = 'http://localhost:3000/restablecer_contraseña/'
    correo = request.json.get("correo") 
    if not correo:
        return jsonify({"msg":"El correo no ha sido agregado"}), 400
    persona = Personas.query.filter_by(correo=correo).first()
    if persona is None:
        return jsonify({"msg":"El correo ingresado no es valido"}),404
    expiracion = datetime.timedelta(minutes=15)
    restablecer_token = create_access_token(identity=str(persona.correo), expires_delta=expiracion)
    usuario = persona.nombre
    mensaje = Message('Restablecer contraseña ', recipients=[persona.correo])

    mensaje.html = render_template('email/reset_password.html', usuario=usuario, url=url + restablecer_token)
    mensaje.body = render_template('email/reset_password.txt', usuario=usuario, url=url + restablecer_token)

    mail.send(mensaje)
    return jsonify({
        "success":True
    })

@app.route('/restablecer_contraseña', methods=["POST"])
@jwt_required
def restablecer_contraseña():
    usuario_actual = get_jwt_identity()
    contraseña = request.json.get('contraseña')
    if not contraseña:
       return jsonify({"msg":"No se ha indicado una contraseña"}), 400
    persona = Personas.query.filter_by(correo=usuario_actual).first()
    persona.contraseña = bcrypt.generate_password_hash(contraseña)
    expiracion = datetime.timedelta(hours=24)
    token_acceso = create_access_token(identity=persona.correo, expires_delta=expiracion)
    db.session.add(persona)
    db.session.commit()
    
    mensaje = Message('Restablecer contraseña ', recipients=[persona.correo])
    mensaje.html = f'<p style="font-size:16px;font-weight:400;font-family:"Lato",Tahoma,Verdana,Segoe,sans-serif;color:#000">\
                    {persona.nombre}, su contraseña se ha restablecido exitosamente</p>'
    mensaje.body = 'Su contraseña se ha restablecido exitosamente'
    mail.send(mensaje)

    return jsonify({
            "token_acceso": token_acceso,
            "usuario": persona.serialize(),
            "success":True
        }), 200

#-----lista de espera-----

@app.route("/nuevalista", methods=["POST"])
def nuevalista():
    listaesp = Listas_de_espera()
    listaesp.restaurante_id= request.json.get("restaurante_id")
    db.session.add(listaesp)
    db.session.commit()
    return jsonify({"success":True})

@app.route('/listasespera',methods=['GET'])
def getListas():
    listasesp = Listas_de_espera.query.all()
    
    listasArr = []
    for lista in listasesp:
        listasArr.append(lista.toDict()) 
    return jsonify(listasArr), 200

@app.route('/listasespera/<int:id>',methods=['GET'])
def getLista(id):
     sql =text (f"SELECT listas_de_espera.id_lista,listas_de_espera.restaurante_id, listas_de_espera.fecha FROM listas_de_espera WHERE listas_de_espera.restaurante_id = {id}")
     
     result = db.engine.execute(sql)
     getlista=[]
     for r in result:
        getlista.append(dict(r))     
     return jsonify(getlista)
     
     return jsonify(getlista.toDict()), 200
    
@app.route("/listas_persona", methods=["POST"])
def listapersonas():
    listapersonas = Personas_lista()
    listapersonas.id_lista = request.json.get("id_lista")
    listapersonas.id_personas = request.json.get("id_personas")
    listapersonas.hora = request.json.get("hora")
    db.session.add(listapersonas)
    db.session.commit()
    return jsonify({"success":True})

@app.route('/listas_persona',methods=['GET'])
def getListaspersonas():
    listapersonas = Personas_lista.query.all()
    
    listapersonasArr = []
    for listap in listapersonas:
        listapersonasArr.append(listap.toDict()) 
    print(listapersonasArr)
    return jsonify(listapersonasArr), 200

@app.route('/listapersonas', methods=['GET'])
def getListapersona():

    sql = text("SELECT restaurantes.nombre, listas_de_espera.id_lista, personas_lista.id_personalista, personas.nombre FROM listas_de_espera INNER JOIN restaurantes ON restaurantes.id_restaurante = listas_de_espera.restaurante_id INNER JOIN personas_lista ON personas_lista.id_lista = listas_de_espera.id_lista INNER JOIN personas ON personas.id_persona = personas_lista.id_personas")
    result = db.engine.execute(sql)
    listas=[]
    for r in result:
        listas.append(dict(r))     
    return jsonify(listas)

@app.route('/listapersonas/<int:id>', methods=['GET'])
def getlistaperso(id):
    sq="SELECT personas.id_persona, restaurantes.nombre, listas_de_espera.id_lista, personas_lista.id_personalista, personas.nombre FROM listas_de_espera INNER JOIN restaurantes ON restaurantes.id_restaurante = listas_de_espera.restaurante_id"
    sql = text(f"{sq} INNER JOIN personas_lista ON personas_lista.id_lista = listas_de_espera.id_lista INNER JOIN personas ON personas.id_persona = personas_lista.id_personas WHERE listas_de_espera.restaurante_id = {id}")

    result = db.engine.execute(sql)
    listas=[]
    for r in result:
        listas.append(dict(r))     
    return jsonify(listas)

@app.route('/deletelistapersonas/<int:idlista>/<int:idpersonas>', methods=['DELETE'])
def deletelistaperso(idlista,idpersonas):
    
    sql = text(f"DELETE personas_lista FROM personas_lista WHERE id_lista = {idlista} AND id_personas= {idpersonas}")
    result = db.engine.execute(sql)
  
    return jsonify({"success":True}), 200


    
    
    
    # names = [row[3] for row in result]

    
    
if __name__ == "__main__":
    manager.run()