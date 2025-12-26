from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for 
from controller.config import Config
from controller.database import db
from controller.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"
app.config.from_object(Config)

# ================== UPLOAD PATHS ====================
app.config["SONG_UPLOAD_FOLDER"] = "static/uploads/songs"
app.config["COVER_UPLOAD_FOLDER"] = "static/uploads/covers"

# Create folders if not exist
os.makedirs(app.config["SONG_UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["COVER_UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)

# ======================= CREATE TABLES + HARD CODE ========================
with app.app_context():
    db.create_all()

    # --- Create default roles ---
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)

    creator_role = Role.query.filter_by(name='creator').first()
    if not creator_role:
        creator_role = Role(name='creator')
        db.session.add(creator_role)

    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user')
        db.session.add(user_role)

    db.session.commit()

    # --- HARD CODE ADMIN USER ---
    admin_user = User.query.filter_by(email="admin@gmail.com").first()

    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@gmail.com",
            mobilenumber="9999999999",
            password_hash=generate_password_hash("admin123")
        )
        db.session.add(admin_user)
        db.session.commit()

        # assign admin role
        link = UserRole(user_id=admin_user.userid, role_id=admin_role.roleid)
        db.session.add(link)
        db.session.commit()

    # ================= ADD GENRES ONLY (POP, CLASSICAL, MELODY) ==================
    default_genres = ["Pop", "Classical", "Melody"]
    for g in default_genres:
        if not Genre.query.filter_by(name=g).first():
            db.session.add(Genre(name=g))
    db.session.commit()
    

# ============================= HOME ===============================
@app.route("/")
def home():
    return render_template("home.html")

# =============================== USER SIGNUP ===============================
@app.route("/signup_user", methods=["GET", "POST"])
def signup_user():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            flash("Password does not match!")
            return redirect("/signup_user")

        if EndUser.query.filter_by(email=email).first():
            flash("Email already registered!")
            return redirect("/signup_user")

        new_user = EndUser(
            username=username,
            email=email,
            mobilenumber=phone,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        role = Role.query.filter_by(name="user").first()
        role_link = UserRole(user_id=new_user.enduserid, role_id=role.roleid)
        db.session.add(role_link)
        db.session.commit()

        flash("Signup successful! Please login.")
        return redirect("/login_user")

    return render_template("signup_user.html")

# =============================== USER LOGIN ===============================
@app.route("/login_user", methods=["GET", "POST"])
def login_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = EndUser.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password!")
            return redirect("/login_user")

        flash("User login successful!")
        return "USER LOGGED IN SUCCESSFULLY 🎉"

    return render_template("login_user.html")

# =============================== CREATOR SIGNUP ===============================
@app.route("/signup_creator", methods=["GET", "POST"])
def signup_creator():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            flash("Password does not match!")
            return redirect("/signup_creator")

        if Creator.query.filter_by(email=email).first():
            flash("Email already registered!")
            return redirect("/signup_creator")

        new_creator = Creator(
            name=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_creator)
        db.session.commit()

        role = Role.query.filter_by(name="creator").first()
        role_link = UserRole(user_id=new_creator.artistid, role_id=role.roleid)
        db.session.add(role_link)
        db.session.commit()

        flash("Creator Signup successful! Please login.")
        return redirect("/login_creator")

    return render_template("signup_creator.html")

# =============================== CREATOR LOGIN ===============================
@app.route("/login_creator", methods=["GET", "POST"])
def login_creator():
    # FIXED: correct POST check
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        creator = Creator.query.filter_by(name=username).first()

        if not creator or not check_password_hash(creator.password_hash, password):
            flash("Invalid creator credentials!")
            return redirect("/login_creator")

        session["creator_id"] = creator.artistid
        session["creator_name"] = creator.name

        flash("Creator login successful!")
        return redirect("/creator_dashboard")

    return render_template("login_creator.html")

# =============================== CREATOR DASHBOARD ===============================
@app.route("/creator_dashboard")
def creator_dashboard():
    if "creator_id" not in session:
        return redirect("/login_creator")

    creator_id = session["creator_id"]
    creator_name = session["creator_name"]

    songs = Song.query.filter_by(creator_id=creator_id).all()
    genres = Genre.query.all()

    return render_template("creator_dashboard.html",
                           creator_name=creator_name,
                           songs=songs,
                           genres=genres)

# =============================== ADD SONG (WITH COVER) ===============================
# =============================== ADD SONG (WITH COVER) ===============================
@app.route("/add_song", methods=["POST"])
def add_song():

    if "creator_id" not in session:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "not_logged_in"}), 401
        return redirect("/login_creator")

    title = request.form.get("title", "").strip()

    # 🔧 GENRE FIX (ONLY CHANGE)
    genre_name = request.form.get("genre")
    genre_id = None
    if genre_name:
        genre_obj = Genre.query.filter_by(name=genre_name).first()
        if genre_obj:
            genre_id = genre_obj.genreid

    audio = request.files.get("song_file") or request.files.get("audio") or request.files.get("file")
    cover = request.files.get("cover")

    audio_filename = None
    cover_filename = None

    if audio and audio.filename != "":
        original = secure_filename(audio.filename)
        audio_filename = f"{int(datetime.utcnow().timestamp())}_{original}"
        audio.save(os.path.join(app.config["SONG_UPLOAD_FOLDER"], audio_filename))

    if cover and cover.filename != "":
        original_cover = secure_filename(cover.filename)
        cover_filename = f"{int(datetime.utcnow().timestamp())}_{original_cover}"
        cover.save(os.path.join(app.config["COVER_UPLOAD_FOLDER"], cover_filename))

    new_song = Song(
        title=title or "Untitled",
        description="",
        audio_file=audio_filename,
        cover_image=cover_filename,
        creator_id=session["creator_id"],
        genre_id=genre_id   # ✅ FIXED
    )

    db.session.add(new_song)
    db.session.commit()

    flash("Song Added Successfully!")
    return redirect("/creator_dashboard")

# =============================== GET SONGS (detailed JSON) ===============================
@app.route("/get_songs")
def get_songs():
    if "creator_id" not in session:
        return jsonify([])

    creator_id = session["creator_id"]
    songs = Song.query.filter_by(creator_id=creator_id).order_by(Song.uploaded_at.desc()).all()

    out = []
    for s in songs:
        creator = Creator.query.filter_by(artistid=s.creator_id).first()
        genre_name = s.genre.name if s.genre else None
        out.append({
            "id": s.songid,
            "title": s.title,
            "genre": genre_name,
            "audio_url": url_for('static', filename=f"uploads/songs/{s.audio_file}") if s.audio_file else None,
            "cover_url": url_for('static', filename=f"uploads/covers/{s.cover_image}") if s.cover_image else None,
            "uploaded_date": s.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if s.uploaded_at else None,
            "creator_name": creator.name if creator else session.get("creator_name"),
            "plays": s.plays,
            "likes": s.likes
        })

    return jsonify(out)

# =============================== DELETE SONG ===============================
@app.route("/delete_song/<int:id>", methods=["GET", "DELETE"])
def delete_song(id):

    if "creator_id" not in session:
        # AJAX delete
        if request.method == "DELETE":
            return jsonify({"error": "not_logged_in"}), 401
        return redirect("/login_creator")

    song = Song.query.filter_by(songid=id, creator_id=session["creator_id"]).first()

    if not song:
        if request.method == "DELETE":
            return jsonify({"error": "not_found"}), 404
        return redirect("/creator_dashboard")

    # Remove files from disk (if they exist)
    try:
        if song.audio_file:
            af = os.path.join(app.root_path, "static", "uploads", "songs", song.audio_file)
            if os.path.exists(af):
                os.remove(af)
        if song.cover_image:
            cf = os.path.join(app.root_path, "static", "uploads", "covers", song.cover_image)
            if os.path.exists(cf):
                os.remove(cf)
    except Exception:
        # ignore file delete errors
        pass

    db.session.delete(song)
    db.session.commit()

    if request.method == "DELETE":
        return jsonify({"success": True})

    flash("Song Deleted Successfully!")
    return redirect("/creator_dashboard")

# ====================================================================

@app.route("/edit_song/<int:id>", methods=["POST"])
def edit_song(id):

    if "creator_id" not in session:
        return redirect("/login_creator")

    song = Song.query.filter_by(
        songid=id,
        creator_id=session["creator_id"]
    ).first()

    if not song:
        flash("Song not found")
        return redirect("/creator_dashboard")

    title = request.form.get("title")
    genre_name = request.form.get("genre")
    description = request.form.get("description")

    cover = request.files.get("cover")
    audio = request.files.get("song_file")

    if title:
        song.title = title

    # ✅ GENRE FIX (same as add song)
    if genre_name:
        genre_obj = Genre.query.filter_by(name=genre_name).first()
        if genre_obj:
            song.genre_id = genre_obj.genreid

    if description:
        song.description = description

    # ✅ UPDATE COVER (ONLY IF NEW FILE SELECTED)
    if cover and cover.filename != "":
        cover_name = secure_filename(cover.filename)
        cover_filename = f"{int(datetime.utcnow().timestamp())}_{cover_name}"
        cover.save(os.path.join(app.config["COVER_UPLOAD_FOLDER"], cover_filename))
        song.cover_image = cover_filename

    # ✅ UPDATE SONG FILE (ONLY IF NEW FILE SELECTED)
    if audio and audio.filename != "":
        audio_name = secure_filename(audio.filename)
        audio_filename = f"{int(datetime.utcnow().timestamp())}_{audio_name}"
        audio.save(os.path.join(app.config["SONG_UPLOAD_FOLDER"], audio_filename))
        song.audio_file = audio_filename

    db.session.commit()

    flash("Song Updated Successfully!")
    return redirect("/creator_dashboard")



if __name__ == "__main__":
    app.run(debug=True)