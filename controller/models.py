from controller.database import db


class User(db.Model):
    __tablename__ = 'user'

    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(130), nullable=False)
    mobilenumber = db.Column(db.String(20), unique=True, nullable=False)

    roles = db.relationship('UserRole', backref='user', lazy=True)
    playlists = db.relationship('Playlist', backref='user', lazy=True)



class Role(db.Model):
    __tablename__ = 'role'

    roleid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    users = db.relationship('UserRole', backref='role', lazy=True)



class UserRole(db.Model):
    __tablename__ = 'user_role'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.roleid'))


class Artist(db.Model):
    __tablename__ = 'artist'

    artistid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)

    albums = db.relationship('Album', backref='artist', lazy=True)
    songs = db.relationship('Song', backref='artist', lazy=True)


class Album(db.Model):
    __tablename__ = 'album'

    albumid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.artistid'))
    release_year = db.Column(db.Integer)
    cover_image = db.Column(db.String(255))

    songs = db.relationship('Song', backref='album', lazy=True)


class Song(db.Model):
    __tablename__ = 'song'

    songid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.artistid'))
    album_id = db.Column(db.Integer, db.ForeignKey('album.albumid'))
    genre = db.Column(db.String(50))
    duration = db.Column(db.String(20))
    file_path = db.Column(db.String(255))

    playlist_items = db.relationship('PlaylistSong', backref='song', lazy=True)


class Playlist(db.Model):
    __tablename__ = 'playlist'

    playlistid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'))
    playlist_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    songs = db.relationship('PlaylistSong', backref='playlist', lazy=True)


class PlaylistSong(db.Model):
    __tablename__ = 'playlist_song'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.playlistid'))
    song_id = db.Column(db.Integer, db.ForeignKey('song.songid'))
