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


def  neuigkeit(message , url ,kurs):
     Daten3=Read("neuigkeit_lehrer.json")
     Liste =Daten3.get(kurs)
     Data = {
                "name":message,
                "url":url
            }
     if not  Liste:
                Liste =stack([] , Data)
     else:
                Liste =stack(Liste , Data)

     Daten3[kurs] = Liste
     Write("neuigkeit_lehrer.json" , Daten3)
     return 0


def always():
     information={}
     user_id=session.get("user_id")
     if not user_id:
         return render_template("login.html")
     infos= read_more()
     for id , info in infos.items():
         if id == str(user_id):
             information = info
     return information

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
    user_id=session.get("user_id")
    if user_id:
        return render_template("apologize.html", top=code, bottom=escape(message) , info=always()), code
    return render_template("apologize.html", top=code, bottom=escape(message) ), code
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

USERS_FILE = "users_lehrer.json"
More = "more_lehrer.json"
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
         render_template("layout.html" ,  info = information)
         Kursinf = Read("../kursinfo.json")
         Kursinf = Kursinf.get(information["course"])
         Datens=Read("../neuigkeit_student.json")
         daten=Datens.get(information["course"])
         count = 0
         for info in infos.values():
            if info["course"]== information["course"]:
                    count+=1

         return   render_template("index.html" , info = information  , data = daten , kursinfo = Kursinf , count=count)





@login_required
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

@login_required
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any u<ser_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@login_required
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
        anrede =request.form.get("anrede")
        nachname = request.form.get("nachname")
        vorname = request.form.get("vorname")
        geburtsdatum= request.form.get("geburt")
        geburtsort= request.form.get("geburtsort")
        nummer= request.form.get("nummer")
        email= request.form.get("email")
        adresse= request.form.get("adresse")
        wohnort = request.form.get("wohnort")
        course = request.form.get("course")
        #if not ( nachname and vorname and geburtsdatum and  geburtsort and nummer and email  and level and sprache and course ):
         #       return apology("you didn't fill every inputsfields", 403)
        datens=Read("../kurs.json")
        daten=datens["courses"][course]
        daten["teacher"]=f"{vorname} {nachname}"
        datens["courses"][course] =daten
        Write("../kurs.json" , datens )
        more= read_more()
        new_user_id = len(more) + 1
        more[ new_user_id] = {
                 "anrede"  : anrede ,
                 "nachname": nachname ,
                 "vorname" : vorname ,
                 "geburtsdatum":geburtsdatum ,
                 "geburtsort" : geburtsort ,
                 "nummer"  : nummer ,
                 "email" : email ,
                 "wohnort":wohnort ,
                 "adresse": adresse ,
                 "course" :course
             }
        write_more(more)
        session["user_id"] = new_user_id
        return redirect("/")




    else:
        return render_template("more.html")


@login_required
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



@login_required
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

@login_required
@app.route("/kurs", methods={"GET","POST"})
def  kurs():

    if request.method == "POST":
        ubung = request.form.get("übung")
        stand = request.form.get("stand")
        if not ( ubung or stand):
            return apology("At least one field have to be filled" , 403)
        daten=Read("news.json")
        data = always()
        kurs = data["course"]
        daten[kurs] = {

            "uebung":ubung ,
            "stand" :stand

        }
        Write("new.json" , daten)
        return render_template("kurs.html" , info = always() )
    else:
       return render_template("kurs.html" , info = always() )

@login_required
@app.route("/verwaltung", methods={"GET","POST"})
def  verwalter():
      return render_template("verwaltung.html" , info=always())

@app.route("/change", methods={"GET","POST"})
@login_required
def  change():
     if  request.method == "POST":
         start=request.form.get("startsdatum")
         end=request.form.get("endsdatum")
         preis=request.form.get("preis")
         course=request.form.get("course")
         uebung=request.form.get("uebung")
         ort=request.form.get("ort")
         datens2=Read("../kurs.json")
         datens=Read("../kursinfo.json")
         daten3=always()
         kurs=daten3["course"]
         daten=datens[kurs]
         if start :
             daten["Zeitraum"]["von"] = start
             datens[kurs]=daten
             Write("../kursinfo.json" , datens)
             neuigkeit("Das Start des Kurses wurde geändert" , f"/kursinfo_{kurs}" , kurs)
             return render_template("verwaltung.html" , info=always() , message="Das Startsdatum  wurde erfolgreich geändert !")

         if end :
              daten["Zeitraum"]["end"] = end
              datens[kurs]=daten
              Write("../kursinfo.json" , datens)
              neuigkeit("Das End des Kurses wurde geändert" , f"/kursinfo_{kurs}" , kurs)
              return render_template("verwaltung.html" , info=always() , message="Das Endsdatum  wurde erfolgreich geändert !")
         if  preis:
                daten["Preis"] = preis
                datens[kurs]=daten
                Write("../kursinfo.json" , datens)
                neuigkeit("Der Preis des Kurses wurde geändert" , f"/kursinfo_{kurs}" , kurs)
                return render_template("verwaltung.html" , info=always() , message="Der Preis wurde erfolgreich geändert !")
         if  ort:
                daten["Ort"] = ort
                datens[kurs]=daten
                Write("../kursinfo.json" , datens)
                neuigkeit("Der Ort  des Kurses wurde geändert" , f"/kursinfo_{kurs}" , kurs)
                return render_template("verwaltung.html" , info=always() , message="Der Standort wurde erfolgreich geändert !")
         daten2 = datens2["courses"][kurs]
         if course:
             daten2["course_time"]=course
             datens2["courses"][kurs] =daten2
             Write("../kurs.json" , datens2)
             neuigkeit("die Uhrzeit des Kurses wurde geändert" , f"/kursinfo_{kurs}" , kurs)
             return render_template("verwaltung.html" , info=always() , message="Die Kursuhrzeit wurde erfolgreich geändert !")
         if uebung:
                daten2["exersice_time"]=uebung
                datens2["courses"][kurs] =daten2
                Write("../kurs.json" , datens2)
                neuigkeit("die Übunszeit des Kurses wurde geändert" , f"/kursinfo_{kurs}" , kurs)
                return render_template("verwaltung.html" , info=always() , message="Die Übungsuhrzeit wurde erfolgreich geändert !")
         Write("exam.json" , daten)
         return render_template("verwaltung.html" , info=always() , messages="Ein Fehler ist aufgetreten")
@login_required
@app.route("/teilnehmer", methods={"GET","POST"})
def teilnahme():

    if request.method == "POST" :
        key=request.form.get("entfernung")
        datens= Read("../more.json")
        datens[key]["course"]="None"
        Write("../more.json", datens)
        return  redirect("/teilnehmer")

    else:
        daten3=always()
        course=daten3["course"]
        datens= Read("../more.json")
        Liste=[]
        for key , data in datens.items():
             if data["course"] == course:
                 my = {
                        "name":f"{data["vorname"]} {data["nachname"]}" ,
                        "key":key
                    }
                 Liste.append(my)
        return  render_template("teilnehmer.html" , info=always() , liste=Liste)

@app.route("/anfrage", methods={"GET","POST"})
@login_required
def anfrage():
    data=always()
    kurs=data["course"]
    if request.method == "POST":
       confirm=request.form.get("bestaetigung")
       key=request.form.get("key")
       remove= request.form.get("entfernung")
       datens2=Read("../more.json")
       new_name=""
       for schlüssel ,data in datens2.items():
           if  schlüssel  == key:
                new_name=f"{data["vorname"]} {data["nachname"]}"
                break
       if confirm:
           datens= Read("../more.json")
           datens[key]["course"]=kurs
           Write("../more.json", datens)
           datens=Read("../anfrage.json")
           daten=datens.get(kurs)
           remove={
                     "name":new_name ,
                     "key":key
                 }
           print(remove)
           daten.remove(remove)
           datens[kurs]=daten
           neuigkeit("Deine Teilnahme wurde bestätigt" , "/kurs" , kurs)
           Write("../anfrage.json" ,datens)
           return render_template("anfrage.html"  , anfragen=daten , info=always())
       elif remove:
           datens=Read("../anfrage.json")
           daten=datens.get(kurs)
           remove={
                 "name":new_name ,
                 "key":key
             }
           neuigkeit("Deine Teilnahme wurde abgelehnt" , "/kurs" , kurs)
           daten.remove(remove)
           datens[kurs]=daten
           Write("../anfrage.json" ,datens)
           return render_template("anfrage.html"  , anfragen=daten , info=always())

    else:
          datens=Read("../anfrage.json")
          daten=datens.get(kurs)
          return render_template("anfrage.html"  , anfragen=daten , info=always() )



@app.route("/pruefung", methods={"GET","POST"})
@login_required
def exam():

    if request.method == "POST":

        date =request.form.get("date")
        ort =request.form.get("ort")
        time_w =request.form.get("time_w")
        room_w =request.form.get("room_w")
        time_h =request.form.get("time_h")
        room_h =request.form.get("room_h")
        time_s =request.form.get("time_s")
        room_s =request.form.get("room_s")
        time_l =request.form.get("time_l")
        room_l =request.form.get("room_l")
        modules =request.form.getlist("module")
        modul_detail= {
               "Lesen":{ "time":time_l , "room":room_l},
               "Sprechen":{ "time":time_s , "room":room_s},
               "Hören":{ "time":time_h , "room":room_h},
               "Schreiben":{ "time":time_w , "room":room_w},
              }
        info ={
              "detail":modul_detail,
              "date":date ,
              "ort":ort,
              "modules":modules
        }

        data = always()
        kurs = data["course"]
        daten = Read("exam.json")

        if daten.get(kurs):
               Liste_exam = daten[kurs]
               exam_id=f"exam123{len(Liste_exam)}"
               info["exam_id"]=exam_id
               Liste_exam.append(info)
        else:
                Liste_exam = []
                exam_id=f"exam123{len(Liste_exam)}"
                info["exam_id"]=exam_id
                Liste_exam.append(info)

        daten[kurs] =Liste_exam

        Write("exam.json" , daten)
        neuigkeit("Neue Prüfung Verfügbar" , "/prüfung" , kurs)
        return render_template("prüfung.html", info=always())
    else:
        return render_template("prüfung.html", info=always())


@app.route("/ergebnis", methods={"GET","POST"})
@login_required
def result():
    if request.method == "POST":
        exam = request.form.get("prüfung")
        session["exam"] = exam
        return redirect("/p_teilnahme")
    else:
        Daten = Read("exam.json")
        data=always()
        kurs=data["course"]
        Daten=Daten.get(kurs)
        return render_template("ergebnisse.html"  , daten = Daten , info=always())





@app.route("/p_teilnahme", methods={"GET","POST"})
@login_required
def p_teilnahme():
     if not session.get("exam"):
         return redirect("/ergebnis")
     if request.method == "POST":
         student = request.form.get("prüfung_student")
         session["student_id"] = student
         return redirect("/p_vergabe")


     else:
       Daten =Read("../exam_teilnahme.json")
       data=always()
       kurs=data.get("course")
       Daten=Daten.get(kurs)
       Daten_exam=""
       if Daten:
          Daten_exam=Daten.get(session["exam"])
       return render_template("prüfung_teilnahme.html" , Daten=Daten_exam , info=always())

@app.route("/p_vergabe", methods={"GET","POST"})
def vergabe():
    if not session.get("student_id"):
       return redirect("/p_teilnahme")
    Daten1 = Read("exam.json")
    data=always()
    kurs=data["course"]
    Daten1=Daten1.get(kurs)
    modules=""
    if Daten1:
      for element in Daten1:
         if element["exam_id"] == session["exam"]:
            modules = element["modules"]
    if request.method == "POST":
       dic={ module:request.form.get(module) for module in modules }
       Datei={
           "user_id":session["student_id"],
           "ergebnis":dic
           }
       data=always()
       kurs=data["course"]
       Daten = Read("ergebnis.json")
       if Daten.get(kurs):
           Daten_dic=Daten[kurs]
           if Daten_dic.get(session["exam"]):
               Liste = Daten_dic[session["exam"]]
               can_überschreiben=False
               for i , element in enumerate(Liste):
                       if Datei["user_id"] == element["user_id"]:
                           Liste[i]=Datei
                           can_überschreiben =True
                           break
               if not can_überschreiben:
                 Liste.append(Datei)
               Daten_dic[session["exam"]] = Liste

           else:
               Liste=[]
               Liste.append(Datei)
               Daten_dic[session["exam"]] = Liste


       else:
           Daten_dic={}
           Liste=[]
           Liste.append(Datei)
           Daten_dic[session["exam"]] = Liste

       Daten[kurs]=Daten_dic
       Write("ergebnis.json",Daten )
       neuigkeit("Neue Ergebnisse Verfügbar !" , "/prüfung" , kurs)
       return redirect("/p_vergabe")




    else:
         Daten =Read("../exam_teilnahme.json")
         data=always()
         kurs=data["course"]
         Daten=Daten[kurs]
         Daten=Daten[session["exam"]]
         name=""
         for element in Daten:
             if element["id"] == str(session["student_id"]):
                  name = element["name"]

         data = {
                "exam_id":session["exam"],
                "name":name,
                "modules":modules
              }
         return render_template("vergabe.html" , info=always() , daten=data )

