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
    db_uri = f"postgresql://postgres:postgres@127.0.0.1:{local_port}/Konatus6.4QF"
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
        # Test SELECT query for /test route
        select_query = """
            SELECT
                public.organisation.id,
                public.organisation.title,
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
                public.unit ON public.organisation.id = public.unit.organisation_id
            JOIN
                public.program_backlog ON public.unit.id = CAST(public.program_backlog.id AS INTEGER)
            JOIN
                public.team ON public.unit.id = public.team."idUnit";
        """
        result_proxy = execute_select_query(engine, select_query)
        column_names = result_proxy.keys()
        data = [dict(zip(column_names, row)) for row in result_proxy.fetchall()]
        return jsonify({"data": data})
    finally:
        server.stop()

@app.route('/screen1', methods=['GET'])
def screen1_query():
    engine, server = create_engine_with_ssh()

    try:
        # Test SELECT query for /screen1 route
        select_query = """
            SELECT * FROM program_backlog;
        """
        result_proxy = execute_select_query(engine, select_query)
        column_names = result_proxy.keys()
        data = [dict(zip(column_names, row)) for row in result_proxy.fetchall()]
        return jsonify(data)
    finally:
        server.stop()
@app.route('/organisation_team', methods=['GET'])
def organisation_team():
    engine, server = create_engine_with_ssh()

    try:
        # SQL Query
        select_query = """
            SELECT
                org.org_id,
                org.org_name,
                unit.id AS unit_id,
                unit.name AS unit_name,
                team.id AS team_id,
                team.libelle AS team_libelle,
                team.name AS team_name,
                ressource.id AS ressource_id,
                ressource.name AS ressource_name
            FROM
                public.organisation org
            JOIN
                public.unit unit ON org.org_id::text = unit.organization_id
            JOIN
                public.team team ON unit.id = team."idUnit"
            JOIN
                public.team_ressources tr ON team.id = tr.idteam
            JOIN
                public.ressources ressource ON tr.idressource = ressource.id;
        """
        result_proxy = execute_select_query(engine, select_query)
        column_names = result_proxy.keys()
        data = [dict(zip(column_names, row)) for row in result_proxy.fetchall()]

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)})

    finally:
        server.stop()
@app.route('/organisation_unit', methods=['GET'])
def organisation_unit():
    engine, server = create_engine_with_ssh()

    try:
        # SQL Query
        select_query = """
            SELECT
                org.org_id,
                org.org_name,
                unit.id AS unit_id,
                unit.name AS unit_name,
                pb.prbg_id AS program_backlog_id,
                pb.prbg_name,
                t.id AS team_id,
                t.libelle AS team_libelle,
                t.name AS team_name
            FROM
                public.organisation org
            JOIN
                public.unit unit ON org.org_id = unit.id
            JOIN
                public.program_backlog pb ON unit.id = pb.prbg_id::integer
            JOIN
                public.team t ON unit.id = t."idUnit";
        """
        result_proxy = execute_select_query(engine, select_query)
        column_names = result_proxy.keys()
        data = [dict(zip(column_names, row)) for row in result_proxy.fetchall()]

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)})

    finally:
        server.stop()
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
