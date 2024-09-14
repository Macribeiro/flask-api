import flask
from flask import request, jsonify
import pyodbc
import datetime
import os

app = flask.Flask(__name__)

conn = pyodbc.connect(f"DRIVER={os.environ.get('DRIVER')};SERVER={os.environ.get('SERVER_NAME')};DATABASE={os.environ.get('DATABASE')};UID={os.environ.get('USER')};PWD={os.environ.get('PASSWORD')};TrustServerCertificate=yes")

@app.route('/create_bands_table', methods=['POST'])
def create_bands_table():
    try:
        cursor = conn.cursor()
        cursor.execute("""
                CREATE TABLE Bands (
                    Id INT IDENTITY(1,1) PRIMARY KEY,
                    Name VARCHAR(100) NOT NULL,
                    FavoriteAlbum VARCHAR(100),
                    AddedAt VARCHAR(75),
                    UpdatedDate VARCHAR(75)
                )
            """)
        conn.commit()
        return "DATABASE TABLE CREATED"
    except Exception as e:
        return str(e)


@app.route('/', methods=['GET'])
def Main():
    return "<h1>Minhas bandas favoritas</h1><p>Essa página vai listar as bandas que eu mais ouço</p><br><p> a ordem é Identificador(id); Nome da banda; Álbum Favorito; Data em que adicionei essa info."


@app.route('/bands/all', methods=['GET'])
def get_all():
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Bands")
    rows = cursor.fetchall()
    data = [tuple(row) for row in rows]

    return jsonify(data)


@app.route('/bands/<int:id>')
def get_by_id(id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Bands WHERE Id = ?", (id))
    rows = cursor.fetchone()

    return jsonify(tuple(rows))


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Resource Not Found.</p>", 404


@app.route('/band', methods=['POST'])
def create_new_band():
    data = request.get_json()

    query = """
        INSERT INTO Bands (Name, FavoriteAlbum, AddedDate, UpdatedDate)
        VALUES (?, ?, ?, ?)
    """

    params = (data['name'], data['favoriteAlbum'], datetime.datetime.now(
    ).isoformat(), datetime.datetime.now().isoformat())

    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return jsonify({'message': 'Band added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/band/<int:id>', methods=['DELETE'])
def delete_band_by_id(id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Bands WHERE Id = ?", (id))
        conn.commit()
        return jsonify({'message': 'Band deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/bands', methods=['DELETE'])
def delete_all():
    try:
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE Bands")
        conn.commit()
        return jsonify({'message': 'Deleted all bands successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/band/<int:id>/name/<string:name>', methods=['PUT'])
def change_name(id, name):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Bands SET Name = ?, UpdatedDate = ? WHERE Id = ?",
                       (name, datetime.datetime.now().isoformat(), id))
        conn.commit()
        return jsonify({'message': 'Name updated successfully', 'data': name}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/band/<int:id>/album/<string:album>', methods=['PUT'])
def change_album(id, album):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Bands SET FavoriteAlbum = ?, UpdatedDate = ? WHERE Id = ?",
                       (album, datetime.datetime.now().isoformat(), id))
        conn.commit()
        return jsonify({'message': 'Album updated successfully', 'data': album}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


app.run(debug=True)