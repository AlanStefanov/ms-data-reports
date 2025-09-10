import os
import io
import shutil
import tempfile
from flask import Flask, send_file, jsonify, render_template, request, redirect, url_for, session, flash
from main import generate_reports, get_reports_data, get_iqvia_format_data, get_closeup_format_data
import zipfile

app = Flask(__name__)
app.secret_key = 'saludia_farmu_secret_key_2025'

# Usuarios hardcodeados
USERS = {
    'admin': 'farmuengineering',
    'controlling': 'saludia2025!'
}

# Función para verificar si el usuario está logueado
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session['user'] = username
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

# Ruta de logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

# Ruta principal protegida
@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html', user=session.get('user'))

@app.route('/reports', methods=['GET'])
@login_required
def get_reports():
    """Endpoint para generar y descargar los reportes en un archivo ZIP."""
    
    # 1. Crear un directorio temporal para guardar los archivos
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 2. Generar los reportes de Excel usando la función de main.py
        report_filenames = generate_reports(temp_dir)

        # 3. Crear un archivo ZIP para los reportes
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in report_filenames:
                zipf.write(filename, os.path.basename(filename))
        zip_buffer.seek(0)

        # 4. Configurar la respuesta HTTP para la descarga
        return send_file(zip_buffer,
                         mimetype='application/zip',
                         as_attachment=True,
                         download_name='Reportes_Farmu.zip')
        
    finally:
        # 5. Limpiar el directorio temporal
        shutil.rmtree(temp_dir)

@app.route('/reports-json', methods=['GET'])
@login_required
def get_reports_json():
    """Endpoint para obtener los datos de los reportes en formato JSON."""
    try:
        df_base = get_reports_data()
        if df_base.empty:
            return jsonify({"error": "No hay datos para generar el reporte."}), 404

        # Convertir el DataFrame de pandas a un diccionario para JSON
        report_data = df_base.to_dict(orient='records')
        return jsonify(report_data)

    except Exception as e:
        print(f"Error al obtener los datos para el JSON: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/reports-iqvia', methods=['GET'])
@login_required
def get_iqvia_reports():
    """Endpoint para obtener los datos del reporte IQVIA."""
    try:
        iqvia_data = get_iqvia_format_data()
        if not iqvia_data:
            return jsonify({"error": "No hay datos para generar el reporte IQVIA."}), 404
        return jsonify(iqvia_data)
    except Exception as e:
        print(f"Error al obtener los datos IQVIA: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/reports-closeup', methods=['GET'])
@login_required
def get_closeup_reports():
    """Endpoint para obtener los datos del reporte CLOSEUP."""
    try:
        closeup_data = get_closeup_format_data()
        if not closeup_data:
            return jsonify({"error": "No hay datos para generar el reporte CLOSEUP."}), 404
        return jsonify(closeup_data)
    except Exception as e:
        print(f"Error al obtener los datos CLOSEUP: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)