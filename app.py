from flask import Flask, jsonify,render_template
from sqlalchemy import create_engine, text
from sshtunnel import SSHTunnelForwarder
import json
import pandas as pd
from datetime import datetime 
app = Flask(__name__)

def create_engine_with_ssh():
    # SSH tunneling configuration
    server = SSHTunnelForwarder(
        ('185.151.213.119', 7025),
        ssh_username="konatus_site",
        ssh_password="nHcLM9$vfh9_wql9",
        remote_bind_address=('localhost', 5432)
    )

    server.start()

    # Create SQLAlchemy engine with SSH tunnel
    local_port = str(server.local_bind_port)
    db_uri = f"postgresql://postgres:postgres@127.0.0.1:{local_port}/Konatus_DATABASE_bakup"
    engine = create_engine(db_uri)

    return engine, server

def execute_select_query(engine, query):
    with engine.connect() as connection:
        result_proxy = connection.execute(text(query))
        return result_proxy
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', message="API en cours de développement")
@app.route('/test', methods=['GET'])
def test_query():
    engine, server = create_engine_with_ssh()

    try:
        # Test SELECT query
        select_query = """
SELECT
    public.organization.id,
    public.organization.title,
    public.unit.id,
    public.unit.name,
    public.program_backlog.id,
    public.program_backlog.programname,
    public.team.id,
    public.team.libelle,
    public.team.name
FROM
    public.organization
JOIN
    public.unit ON public.organization.id = public.unit.organization_id
JOIN
    public.program_backlog ON public.unit.id = CAST(public.program_backlog.id AS INTEGER)
JOIN
    public.team ON public.unit.id = public.team."idUnit";
"""

        result_proxy = execute_select_query(engine, select_query)

        # Obtenez les noms de colonnes directement à partir de l'objet ResultProxy
        column_names = result_proxy.keys()

        # Récupérez les résultats sous forme de dictionnaires
        data = [dict(zip(column_names, row)) for row in result_proxy.fetchall()]

        # Utilisez jsonify pour créer une réponse JSON
        return jsonify({"data": data})
    finally:
        server.stop()

@app.route('/screen1', methods=['GET'])
def test_query():
    engine, server = create_engine_with_ssh()

    try:
        # Test SELECT query
        select_query = """
SELECT * FROM program_backlog;
"""
        result_proxy = execute_select_query(engine, select_query)
        column_names = result_proxy.keys()
        data = [dict(zip(column_names, row)) for row in result_proxy.fetchall()]
        return jsonify({"data": data})
    finally:
        server.stop()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
