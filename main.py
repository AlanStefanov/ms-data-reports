import pandas as pd
import datetime
import os
import pymysql
import xlsxwriter
import openpyxl
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Función para obtener datos de MySQL
def get_mysql_data(query: str) -> pd.DataFrame:
    """Ejecuta una consulta en MySQL y devuelve un DataFrame de pandas."""
    print("Conectando a la base de datos MySQL...")
    try:
        connection = pymysql.connect(
            host=os.environ.get('MYSQL_HOST'),
            port=int(os.environ.get('MYSQL_PORT')),
            user=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASSWORD'),
            database=os.environ.get('MYSQL_DB'),
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Conexión exitosa. Ejecutando la consulta...")
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            df = pd.DataFrame(result)
        connection.close()
        print("Datos obtenidos de MySQL.")
        return df
    except pymysql.MySQLError as e:
        print(f"Error al conectar a la base de datos MySQL: {e}")
        return pd.DataFrame() # Devuelve un DataFrame vacío en caso de error

def create_excel_report(df: pd.DataFrame, report_type: str, file_path: str):
    """Genera un solo archivo de Excel para IQVIA o CLOSEUP."""
    print(f"Generando el reporte de {report_type.upper()}...")
    
    # === Nuevo código de depuración ===
    if df.empty:
        print("El DataFrame está vacío. No se puede generar el reporte.")
        return
    print("Columnas en el DataFrame:", df.columns.tolist())
    # === Fin del código de depuración ===

    if report_type == 'iqvia':
        CLIENTES = df[['COD_CLI', 'NOMBRE_CLI', 'DIRECCION', 'CIUDAD', 'DEPARTAMENTO']].copy()
        CLIENTES = CLIENTES.sort_values('COD_CLI')
        FACMES = df[['COD_PROD', 'DESCRIPCION_PROD', 'COD_CLI', 'NOMBRE_CLI', 'UNIDADES', 'PRECIO_UNITARIO', 'FECHA', 'CANAL_VENTA']].copy()
        FACMES = FACMES.sort_values('FECHA')
        PRODUCTOS = df[['COD_PROD', 'DESCRIPCION_PROD', 'LABORATORIO', 'PRECIO_UNITARIO', 'COD_BARRA']].copy()
        PRODUCTOS = PRODUCTOS.sort_values('DESCRIPCION_PROD')

        sheets = {'PRODUCTOS': PRODUCTOS, 'CLIENTES': CLIENTES, 'FACMES': FACMES}
    elif report_type == 'closeup':
        CLIENTES = df[['COD_CLI', 'NOMBRE_CLI', 'DIRECCION', 'CIUDAD', 'DEPARTAMENTO']].copy()
        CLIENTES = CLIENTES.rename(columns={'COD_CLI': 'CODIGO_CLIENTE', 'NOMBRE_CLI': 'RAZON_SOCIAL'})
        CLIENTES = CLIENTES.sort_values('CODIGO_CLIENTE')
        FACMES = df[['COD_CLI', 'COD_PROD', 'UNIDADES', 'PRECIO_UNITARIO', 'FECHA']].copy()
        FACMES = FACMES.rename(columns={'COD_CLI': 'CODIGO_CLIENTE', 'COD_PROD': 'CODIGO_PRODUCTO'})
        FACMES = FACMES.sort_values('FECHA', ascending=False)
        PRODUCTOS = df[['COD_PROD', 'COD_BARRA', 'DESCRIPCION_PROD', 'LABORATORIO', 'PRECIO_UNITARIO']].copy()
        PRODUCTOS = PRODUCTOS.rename(columns={'COD_PROD': 'CODIGO_PRODUCTO', 'COD_BARRA': 'EAN', 'DESCRIPCION_PROD': 'NOMBRE_PRODUCTO', 'PRECIO_UNITARIO': 'PRECIO'})
        PRODUCTOS = PRODUCTOS.sort_values('NOMBRE_PRODUCTO')

        sheets = {'CLIENTES': CLIENTES, 'FACMES': FACMES, 'PRODUCTOS': PRODUCTOS}
    else:
        print(f"Tipo de reporte desconocido: {report_type}")
        return
    
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        for sheet_name, df_sheet in sheets.items():
            df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Ajuste de ancho de columnas
    workbook = openpyxl.load_workbook(file_path)
    for sheet_name in workbook.sheetnames:
        worksheet = workbook[sheet_name]
        for column in worksheet.columns:
            max_length = 0
            column_name = column[0].column_letter
            for cell in column:
                try:
                    cell_value_str = str(cell.value)
                    if len(cell_value_str) > max_length:
                        max_length = len(cell_value_str)
                except TypeError:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            worksheet.column_dimensions[column_name].width = adjusted_width
    workbook.save(file_path)
    print(f"Reporte '{file_path}' generado exitosamente.")


def get_reports_data():
    """Genera los datos de los reportes y los devuelve como un diccionario de DataFrames."""
    # Lógica para obtener el mes y año del reporte
    meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    current_month = datetime.datetime.now().month
    previous_month = current_month - 1 if current_month > 1 else 12
    spanish_month = meses[previous_month]
    current_year = datetime.datetime.now().year

    # Tu nueva consulta SQL
    query = """
        SELECT
            p.barcode AS COD_PROD,
            UPPER(p.name) AS DESCRIPCION_PROD,
            p.laboratory AS LABORATORIO,
            p.barcode AS COD_BARRA,
            csl.shopify_customer_id AS COD_CLI,
            d.name AS NOMBRE_CLI,
            od.final_quantity AS UNIDADES,
            od.price AS PRECIO_UNITARIO,
            'Tradicional' AS CANAL_VENTA,
            UPPER(a.address_complement) AS DIRECCION,
            UPPER(a.city) AS CIUDAD,
            CASE
                      WHEN (a.department) IN ('BOGOTÃ, D.C.', 'BOGOTÃ', 'BOGOTA', 'BOGOTA / PUENTE ARANDA') THEN 'BOGOTÃ, D.C.'
                      WHEN (a.department) IN ('BARRANQUILLA', 'BARRAQUILLA') THEN 'ATLÃNTICO'
                      WHEN (a.department) IN ('SOACHA', 'CHOCONTÃ') THEN 'CUNDINAMARCA'
                      ELSE UPPER(a.department)
            END AS DEPARTAMENTO
        FROM orders o
        JOIN sub_orders s ON o.id = s.order_id
        JOIN order_details od on (od.sub_order_id = s.id)
        JOIN products_market p on (p.id = od.product_market_id)
        JOIN order_checkouts oc on (o.id = oc.order_id)
        JOIN co_back_account.employees e on (oc.email = e.email)
        JOIN co_back_account.drugstores d on (d.id = e.drugstore_id)
        JOIN co_back_account.customer_shopify_legacies csl on (csl.account_id = d.account_id)
        JOIN co_back_address.addresses a on (a.id = oc.address_id)
        WHERE o.created_at >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
          AND o.created_at < DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
          AND o.status != 'cancelled'
          AND od.final_quantity > 0;
    """
    
    df_base = get_mysql_data(query)

    # Nombres de los archivos
    iqvia_file = os.path.join(temp_dir, f'Data Farmu {spanish_month} {current_year} iqvia.xlsx')
    closeup_file = os.path.join(temp_dir, f'Data Farmu {spanish_month} {current_year} closeup.xlsx')

    create_excel_report(df_base, 'iqvia', iqvia_file)
    create_excel_report(df_base, 'closeup', closeup_file)

    return [iqvia_file, closeup_file]
