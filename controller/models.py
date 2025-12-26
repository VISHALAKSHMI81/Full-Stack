from controller.database import db

# ------------------------- USER TABLE (ADMIN) -------------------------
class User(db.Model):
    __tablename__ = 'user'

    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(130), nullable=False)
    mobilenumber = db.Column(db.String(20), unique=True, nullable=False)


# ------------------------- ROLE TABLE -------------------------
class Role(db.Model):
    __tablename__ = 'role'

    roleid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    users = db.relationship('UserRole', backref='role', lazy=True)


# ------------------------- USER-ROLE JOIN TABLE -------------------------
class UserRole(db.Model):
    __tablename__ = 'user_role'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Can store ID of EndUser or Creator
    user_id = db.Column(db.Integer, nullable=False)

    # Role link
    role_id = db.Column(db.Integer, db.ForeignKey('role.roleid'), nullable=False)


# ------------------------- CREATOR TABLE -------------------------
class Creator(db.Model):
    __tablename__ = "creator"

    artistid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(130), nullable=False)

    # relationship
    songs = db.relationship("Song", backref="creator", lazy=True)


# ------------------------- END USER TABLE -------------------------
class EndUser(db.Model):
    __tablename__ = 'end_user'

    enduserid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobilenumber = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(130), nullable=False)

    likes = db.relationship("SongLike", backref="user", lazy=True)
    playlists = db.relationship("Playlist", backref="user", lazy=True)


# ===========================================================
#        ADDITIONAL TABLES FOR CREATOR DASHBOARD
# ===========================================================

# ------------------------- SONG GENRE / CATEGORY -------------------------
class Genre(db.Model):
    __tablename__ = "genre"

    genreid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    songs = db.relationship("Song", backref="genre", lazy=True)


# ------------------------- SONG TABLE -------------------------
class Song(db.Model):
    __tablename__ = "song"

    songid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    audio_file = db.Column(db.String(200), nullable=False)
    cover_image = db.Column(db.String(200), nullable=True)

    # Foreign Keys
    creator_id = db.Column(db.Integer, db.ForeignKey("creator.artistid"), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.genreid"), nullable=True)

    # Analytics
    plays = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=db.func.now())

    like_records = db.relationship("SongLike", backref="song", lazy=True)
    playlist_items = db.relationship("PlaylistSong", backref="song", lazy=True)


# ------------------------- USER LIKES -------------------------
class SongLike(db.Model):
    __tablename__ = "song_like"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("end_user.enduserid"), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey("song.songid"), nullable=False)


# ------------------------- PLAYLIST -------------------------
class Playlist(db.Model):
    __tablename__ = "playlist"

    playlistid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("end_user.enduserid"), nullable=False)

    songs = db.relationship("PlaylistSong", backref="playlist", lazy=True)


# ------------------------- PLAYLIST SONGS -------------------------
class PlaylistSong(db.Model):
    __tablename__ = "playlist_song"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.playlistid"), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey("song.songid"), nullable=False)
