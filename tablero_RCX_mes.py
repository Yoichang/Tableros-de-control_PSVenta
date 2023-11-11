import pandas as pd
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc


# Lee el archivo de Excel
df = pd.read_excel('Tablero183Base.xlsx')

# Lista de vendedores y meses
vendedores = ['ERNESTO', 'LUCIANO', 'FERNANDO', 'CARLOS']
meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto']

# Lista de tipos de facturación que nos interesan
tipos_or = ['8EN', '8CB', '7CD', '7CE', '7CM', '7CP', '8CS']

# Filtrar DataFrame para quedarnos solo con las filas que nos interesan
df = df[df['Tipo O.R'].isin(tipos_or)]

app = dash.Dash(__name__)

def compute_data():
    data = []
    
    for mes in meses:
        row = {'Mes': mes}
      
        for vendedor in vendedores:
            total_factura_mes = df[(df['RC-Nombre'] == vendedor) & (df['Mes'] == mes)]['Total factura'].sum()
            total_general_mes = df[df['Mes'] == mes]['Total factura'].sum()
            porcentaje = (total_factura_mes / total_general_mes) * 100 if total_general_mes != 0 else 0
            row[vendedor] = f'{porcentaje:.0f}%'
            
        data.append(row)
        
    return data

def compute_totals():
    data = []
    
    for mes in meses:
        row = {'Mes': mes}
        
        for vendedor in vendedores:
            total_factura_mes = df[(df['RC-Nombre'] == vendedor) & (df['Mes'] == mes)]['Total factura'].sum()
            row[vendedor] = "${:,.2f}".format(total_factura_mes)
            
        data.append(row)
        
    return data

#Preparación de Datos:de gráfico de barras y gráfico de líneas 

def compute_graph_data():
    
    # Filtramos el DataFrame según los vendedores y tipos de orden deseados
    filtered_df = df[df['RC-Nombre'].isin(vendedores) & df['Tipo O.R'].isin(tipos_or)]

    # Calcular totales por mes
    totals_by_month = filtered_df.groupby('Mes')['Total factura'].sum().reindex(meses).fillna(0)

    # Calcular crecimiento porcentual
    growth_percentage = totals_by_month.pct_change() * 100
    growth_percentage[0] = 0  # Para que el primer mes no tenga NaN

    return totals_by_month, growth_percentage



def style_data():
    styles = []

    for vendedor in vendedores:
        for mes in meses:
            # Obtenemos el porcentaje numérico (sin el %)
            porcentaje = float(df[(df['RC-Nombre'] == vendedor) & (df['Mes'] == mes)]['Total factura'].sum() / df[df['Mes'] == mes]['Total factura'].sum() * 100)

            # Generamos el estilo con gradientes lineales
            styles.append({
                'if': {'column_id': vendedor, 'row_index': meses.index(mes)},
                'background': (
                    f"linear-gradient(90deg, #4DB6AC  {porcentaje}%, transparent {porcentaje}%)"
                    if porcentaje <= 25 else
                    f"linear-gradient(90deg, #2E86C1 {porcentaje}%, #2fe6b9 {porcentaje}%, #85C1E9 100%)"
                ),
                'padding-left': '10px',
                'color': '#E1F5FE' if porcentaje > 25 else '#212121',
                'border': '1px solid red' if porcentaje > 25 else 'none'
                
            })

    return styles

totals_by_month, growth_percentage = compute_graph_data()

# Diseño de la interfaz gráfica

app.layout = html.Div(style={'backgroundColor': '#E3F2FD'}, children=[
    
    html.H2('Tablero de Control: Facturacion Cargo Cliente', style={'color': '#0c0d0d'}),
    dash_table.DataTable(
        id='table',
        columns=[{'name': 'Mes', 'id': 'Mes'}] + [{'name': vendedor, 'id': vendedor} for vendedor in vendedores],
        data=compute_data(),
        style_data_conditional=style_data() + [
            {
                'if': {'column_id': 'Mes'},
                'textAlign': 'center'
            }
        ],
        style_cell={
            'border': '1px solid #3d5c5c',
            'fontSize': 14,  # Cambia el tamaño de la fuente
        },
        style_header={
            'border': '1px solid #3d5c5c',
            'textAlign': 'center'
        }
    ),
    # Aquí añadimos un espacio entre las tablas
    html.Br(),

    # Aquí añadimos el título para la nueva tabla
    html.H2('Totales Facturados por Vendedor', style={'color': '#0c0d0d'}),

    # Aquí añadimos la nueva tabla
    dash_table.DataTable(
        id='totals_table',
        columns=[{'name': 'Mes', 'id': 'Mes'}] + [{'name': vendedor, 'id': vendedor} for vendedor in vendedores],
        data=compute_totals(),
        style_cell={
            'border': '1px solid #3d5c5c',
            'fontSize': 12,  # Cambia el tamaño de la fuente
            'textAlign': 'center',
            'minWidth': '50px', 'width': '50px', 'maxWidth': '80px',  # Estos ajustes definen el ancho de las celdas
        },
        style_header={
            'border': '1px solid #3d5c5c',
            'textAlign': 'center',
            'fontWeight': 'bold',  # Hace el texto de los encabezados en negrita
        },
        page_size=5  # Define cuántas filas quieres mostrar por página
    ),

    dcc.Graph(
    id='sales_growth_graph',
         
    figure={
        'data': [
            # Gráfico de Barras
            {'x': meses, 'y': totals_by_month, 'type': 'bar', 'name': 'Total Facturado', 'yaxis': 'y1'},
            # Gráfico de Líneas
            {'x': meses, 'y': growth_percentage, 'type': 'scatter', 'mode': 'lines+markers', 'name': 'Crecimiento (%)', 'yaxis': 'y2'}
        ],

            'layout': {
            'title': 'Total Facturado y Crecimiento Por Mes',
            'xaxis': {
                'title': 'Mes'
            },
            'yaxis': {
                'title': 'Total Facturado',
            },
            'yaxis2': {
                'title': 'Crecimiento (%)',
                'overlaying': 'y',
                'side': 'right'
            }
        }
    }
)

])

# Ejecuta la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)