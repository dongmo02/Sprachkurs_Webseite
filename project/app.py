import os
import json
from functools import wraps
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Configure application
app = Flask(__name__)
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
def stack(Liste , element ):
       liste_ohne = []
       for i , ele in enumerate(Liste):
           name =ele["name"]
           if '(' in name :
              realname ,frequency = name.split('(')
              realname = realname.strip()
              data ={
                     "name":realname ,
                     "url" :ele["url"]
                   }
              liste_ohne.append(data)

           else:
               liste_ohne.append(ele)


       if element not in liste_ohne:
          if len(Liste) == 0:
              Liste.append(element)
              return Liste
          liste_copie =[]
          liste_copie.insert(0 , "None")
          i=1
          u=0
          count =len(Liste)
          while i < 5 :
              if u >= count:
                  break
              liste_copie.insert(i, Liste[u])
              u+=1
              i+=1
          liste_copie.insert(0 ,element)
          return liste_copie
       else:
           for i , ele in enumerate(Liste):
               name =ele["name"]
               if '(' in name :
                 realname ,frequency = name.split('(')  #Beipliel name= you received a new participation request (x3)
                                                        #(3x)  bedeutet you have already received three.
                 realname = realname.strip()
                 length = len(frequency)
                 number= frequency[1:length-1]
                 number = int(number)
                 number+=1
                 realname =f"{realname} (x{number})"
                 ele["name"] =realname
                 Liste[i] = ele
                 return Liste
               else:
                    ele["name"] =f"Du hast eine neue Anfrage erhalten! (x2)"
                    Liste[i] = ele
                    return Liste

       return []

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apologize.html", top=code, bottom=escape(message)), code
#Login required
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is  None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function
# Path to the JSON file storing user data
def Read(filename):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return { }

def Write(filename , mores):
    with open(filename , "w") as file:
        json.dump(mores, file)

USERS_FILE = "users.json"
More = "more.json"
def read_more():
    if os.path.exists(More):
        with open(More, "r") as file:
            return json.load(file)
    return {}

# Helper function to write users to the JSON file
def write_more(mores):
    with open(More, "w") as file:
        json.dump(mores, file)


# Helper function to read users from the JSON file
def read_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    return {}

# Helper function to write users to the JSON file
def write_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
@login_required
@app.route("/", methods=["GET", "POST"])
def index():
         information={}
         user_id=session.get("user_id")
         if not user_id:
             return   render_template("login.html")
         infos= read_more()
         for id , info in infos.items():
             if id == str(user_id):
                 information = info
         #render_template("layout.html" ,  info = information)
         Daten2 = Read("lehrer/neuigkeit_lehrer.json")
         kurs = information["course"]
         Daten2 = Daten2.get(kurs)
         count = 0
         kurs = information["course"]
         Kursinf = Read("kursinfo.json")
         Kursinf = Kursinf[kurs]
         count = 0
         for info in infos.values():
              if info["course"]== information["course"]:
                       count+=1

         return   render_template("index.html" , info = information , number=count, kursinfo=Kursinf , data=Daten2 ,count=count)






@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Read users from JSON file
        users = read_users()

        # Find user by username
        user = None
        for user_id, user_data in users.items():
            if user_data["username"] == request.form.get("username"):
                user = user_data
                break

        # Ensure username exists and password is correct
        if user is None or not check_password_hash(user["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user_id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any u<ser_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 403)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 403)

        # Read users from JSON file
        users = read_users()

        # Ensure username doesn't already exist
        for user_id, user_data in users.items():
            if user_data["username"] == request.form.get("username"):
                return apology("username already exists", 403)

        # Hash the password
        hashed_password = generate_password_hash(request.form.get("password"))

        # Generate a new user id (this can be improved)
        users = read_users()
        new_user_id = len(users) + 1

        # Add new user to users dictionary with a starting cash of $10,000
        users[new_user_id] = {
            "username": request.form.get("username"),
            "hash": hashed_password,
        }

        # Write updated users to JSON file
        write_users(users)

        # Remember which user has logged in
      #  session["user_id"] = new_user_id

        # Redirect user to home page
        return redirect("/more")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
#@app.route("/daten", methods=["GET", "POST"])
#def daten_eingabe():




@login_required
@app.route("/more", methods=["GET", "POST"])
def more():

    if request.method == "POST" :

        nachname = request.form.get("nachname")
        vorname = request.form.get("vorname")
        geburtsdatum= request.form.get("geburt")
        geburtsort= request.form.get("geburtsort")
        nummer= request.form.get("nummer")
        email= request.form.get("email")
        einmal = request.form.get("einmal")
        level = request.form.get("level")
        if  ( not level ) and  (einmal == "No"):
            level = "Anfänger"
        sprache = request.form.get("sprache")
        course = request.form.get("course")
        #if not ( nachname and vorname and geburtsdatum and  geburtsort and nummer and email  and level and sprache and course ):
         #       return apology("you didn't fill every inputsfields", 403)

        more= read_more()
        new_user_id = len(more) + 1
        new_user_id = str(new_user_id)
        more[ new_user_id] = {
                 "nachname": nachname ,
                 "vorname" : vorname ,
                 "geburtsdatum":geburtsdatum ,
                 "geburtsort" : geburtsort ,
                 "nummer"  : nummer ,
                 "email" : email ,
                 "level":level ,
                 "sprache": sprache ,
                 "course" :course
             }
        write_more(more)
        session["user_id"] = new_user_id
        return redirect("/")




    else:
        return render_template("more.html")

@app.route("/pass", methods={"GET","POST"})
def through():
 if request.method == "POST":
    username=request.form.get("username")
    if not username:
         return apology("you must enter an username" ,403)
    users=read_users()
    user_id = "-1"
    for i in range(len(users)+1):
         if  str(i) in users.keys():
                user=users[str(i)]
                if  user["username"]==username:
                        user_id = str(i)

    if user_id == "-1":
        return apology("There isn't an account with this username" , 403)
    session["user_id"]=user_id
    return redirect("/reset")

 else:
     return render_template("pass.html")




@app.route("/reset", methods={"GET","POST"})
def andern():
    if request.method == "POST":
          password=request.form.get("password")
          old_password=request.form.get("oldpassword")
          confirmation=request.form.get("confirmation")
          if password is None or confirmation is None:
              return apology("must be filled" ,403)
          if password != confirmation:
              return apology("must be the same with the password")
          hash_password=generate_password_hash(password)
          user_id=session["user_id"]
          users=read_users()
          user=users[user_id]
          if not check_password_hash(user["hash"],old_password):
                    return apology( "The old password unfortunately  wrong " ,403)
          if check_password_hash(user["hash"],password):
                    return apology("the new one and old one should be different ")
          user["hash"]=hash_password
          users[user_id]=user
          write_users(users)
          return redirect("/login")

    else:
        return render_template("reset.html")


@app.route("/profil", methods=["GET", "POST"])
def  profil():
             information={}
             user_id=session.get("user_id")
             if not user_id:
                 return   render_template("login.html")
             infos= read_more()
             for id , info in infos.items():
                 if id == str(user_id):
                     information = info
             return render_template("profil.html" ,  info = information)

def always():
    information={}
    user_id=session.get("user_id")
    if not user_id:
            return   render_template("login.html")
    infos= read_more()
    for id , info in infos.items():
      if id == str(user_id):
        information = info
    return information

@app.route("/kurs", methods=["GET", "POST"])
def kurs():
    return render_template("kurs.html" , info =always())

@app.route("/kursinfo_A1", methods=["GET", "POST"])
def info1():
     infos=Read("kursinfo.json")
     session["aktuell"] ="A1"
     return render_template("kurs_info.html"  , kurs=infos["A1"], info=always()  , key="A1" )

@app.route("/kursinfo_A2", methods=["GET", "POST"])
def info2():
     infos=Read("kursinfo.json")
     session["aktuell"] ="A2"
     return render_template("kurs_info.html"  , kurs=infos["A2"] , info=always()  , key="A2" )


@app.route("/kursinfo_B1", methods=["GET", "POST"])
def info3():
     infos=Read("kursinfo.json")
     session["aktuell"] ="B1"
     return render_template("kurs_info.html"  , kurs=infos["B1"] , info=always()  , key="B1" )



@app.route("/kursinfo_B2", methods=["GET", "POST"])
def info4():
     infos=Read("kursinfo.json")
     session["aktuell"] ="B2"
     return render_template("kurs_info.html"  , kurs=infos["B2"] , info=always()  , key="B2" )

@app.route("/kursinfo_C1", methods=["GET", "POST"])
def info5():
     infos=Read("kursinfo.json")
     session["aktuell"] ="C1"
     return render_template("kurs_info.html"  , kurs=infos["C1"] , info=always()  , key="C1" )


@app.route("/programm", methods=["GET", "POST"])
def programm():
     c_kurs=session["aktuell"]
     infos=Read("kurs.json")
     infos=infos["courses"]
     return render_template("programm.html" , kurs=infos.get(str(c_kurs)) , info=always() , key=c_kurs )


@app.route("/buchen", methods=["GET", "POST"])
def  buchen():
     more=always()
     mores=read_more()
     can_message =True
     infos=Read("kursinfo.json")
     c_kurs=session["aktuell"]
     if  more["course"] == "None":
         c_kurs=session["aktuell"]
         more["course"]=c_kurs
         Datens=Read("anfrage.json")
         if len(Datens) == 0:
            daten=[]
            data={
                 "name":f"{more["vorname"]} {more["nachname"]}",
                 "key":session["user_id"]
            }
            daten.append( data)
            Datens[c_kurs]=daten
         else:
             daten=Datens.get(c_kurs)
             if daten:
                data={
                        "name":f"{more["vorname"]} {more["nachname"]}",
                        "key":session["user_id"]
                    }
                if data not in Datens[c_kurs]:
                     Datens[c_kurs]=daten
                     daten.append(data)
                else:
                    can_message=False
             else:
                daten=[]
                data={
                        "name":f"{more["vorname"]} {more["nachname"]}",
                        "key":session["user_id"]
                      }
                daten.append( data)
                Datens[c_kurs]=daten
         if  can_message:
             Daten3=Read("neuigkeit_student.json")
             Liste =Daten3.get(c_kurs)
             Data = {
                      "name":"Du hast eine neue Anfrage erhalten!",
                      "url":"/anfrage"
                     }
             if not  Liste:
                 Liste =stack([] , Data)
             else:
                 Liste =stack(Liste , Data)
             Daten3[c_kurs] = Liste
             Write("neuigkeit_student.json" , Daten3)

         Write("anfrage.json",Datens)
         return render_template("kurs_info.html"  , kurs=infos[c_kurs] , info=always()  , key=c_kurs , message=f"Deine Anmeldung für diesen {c_kurs}-Kurs war erfolgreich \n jetzt warte auf Bestätigung" )
     else:
         c_kurs=session["aktuell"]
         return  render_template("kurs_info.html"  , kurs=infos[c_kurs] , info=always()  , key=c_kurs , messages=f"Du kannst dich gerade nicht für diesen Kurs anmelden" )

@app.route("/mykurs", methods=["GET", "POST"])
def  mykurs():
     daten = Read("lehrer/new.json")
     info = always()
     kurs = info["course"]
     data = daten[kurs]
     return render_template("mykurs.html" , info=always()  , data = data)

@app.route("/prüfung", methods=["GET", "POST"])
def exam():
 Datens = Read("lehrer/exam.json")
 info=always()
 kurs = info["course"]
 Daten = Datens[kurs]
 Ergebnisse = Read("lehrer/ergebnis.json")
 Ergebnisse=Ergebnisse.get(kurs)
 print(session["user_id"])
 Real_Daten={}
 if Ergebnisse:
    for key ,exam in Ergebnisse.items():
      for teilnehmer in exam:
         if teilnehmer["user_id"] == str(session["user_id"]):
             Real_Daten[key] = teilnehmer.get("ergebnis")
 if request.method ==  "POST":
    choise = request.form.get("choise")
    index  = request.form.get("index")
    Datei = Daten[int(index)]
    data={
          "name": f"{info["nachname"]} {info["vorname"]}",
          "id":session["user_id"],
          "choise":choise ,
        }

    Daten3=Read("neuigkeit_student.json")
    Liste =Daten3.get(kurs)
    if choise == "teilnehmen":
      Data1 = {
                 "name":f"Ein Student hat seine Teilnahme an Prüfung {Datei["exam_id"]} bestätigt",
                 "url":"/p_teilnahme"
              }
    elif choise == "verwerfen":
        Data1 = {
                    "name":f"Ein Student hat seine Teilnahme an Prüfung {Datei["exam_id"]} verworfen!",
                    "url":"/p_teilnahme"
                }

    if not  Liste:
        Liste =stack([] , Data1)
    else:
        Liste =stack(Liste , Data1)

    Daten3[kurs] = Liste
    Write("neuigkeit_student.json" , Daten3)

    Datens = Read("exam_teilnahme.json")
    dict = Datens.get(kurs)
    if dict:
        if dict.get(Datei["exam_id"]):
            teilnehmer = dict[Datei["exam_id"]]
            if data not in teilnehmer:
               teilnehmer.append(data)
            dict[Datei["exam_id"]]=teilnehmer
        else:
            teilnehmer = []
            teilnehmer.append(data)
            dict[Datei["exam_id"]] = teilnehmer

        Datens[kurs] = dict

    else:
        teilnehmer = []
        teilnehmer.append(data)
        dict = {}
        dict[Datei["exam_id"]] = teilnehmer
        Datens[kurs]= dict
    Write("exam_teilnahme.json" , Datens)
    return redirect("/prüfung")

 else:
     Daten1 = Read("exam_teilnahme.json")
     if Daten1.get(kurs):
        Liste_ver=[]
        Liste_Teil=[]
        dic = Daten1[kurs]
        for elem in Daten:
          if dic.get(elem["exam_id"]):
            liste =dic[elem["exam_id"]]
            for  element in liste:
                if element["id"] == session["user_id"]:
                    if  element["choise"] ==  "verwerfen":
                       Liste_ver.append(elem["exam_id"])
                    elif  element["choise"] ==  "teilnehmen":
                          Liste_Teil.append(elem["exam_id"])
        exam_liste={
            "verwerfen":Liste_ver,
            "teilnehmen":Liste_Teil
        }
        message1=""
        if not Liste_Teil:
            message1="Keine Verfügbare Prüfungen"
        message=""
        if (len(Liste_Teil)+len(Liste_ver)) == len(Daten):
            message ="keine Neue Prüfung"
        return render_template("prüfung.html" ,info=always() , Daten=Daten ,  exam_liste=exam_liste , message1=message1 , message=message,ergebnis=Real_Daten)

     return render_template("prüfung.html" ,info=always() , Daten=Daten ,  exam_liste={"verwerfen":[], "teilnehmen":[] } )


