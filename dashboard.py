import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 1. CONEXIÓN Y CREACIÓN DE DATOS (Simulamos nuestra base de datos unificada)
conexion = sqlite3.connect(':memory:')
cursor = conexion.cursor()

cursor.execute('''
CREATE TABLE productos (
    sku TEXT PRIMARY KEY,
    nombre TEXT,
    stock_actual INTEGER,
    precio REAL
)''')

cursor.execute('''
CREATE TABLE ventas (
    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT,
    cantidad_vendida INTEGER,
    fecha TEXT
)''')

# Insertamos datos de prueba con stock bajo para activar las alertas
cursor.executemany("INSERT INTO productos VALUES (?, ?, ?, ?)", [
    ('SKU-100', 'Laptop Pro 15', 3, 1200.00),   # Stock crítico (menor a 5)
    ('SKU-200', 'Monitor 4K', 15, 350.00),       # Stock saludable
    ('SKU-300', 'Teclado Mecánico', 2, 80.00),   # Stock crítico (menor a 5)
    ('SKU-400', 'Mouse Ergonómico', 25, 50.00)   # Stock saludable
])

cursor.executemany("INSERT INTO ventas (sku, cantidad_vendida, fecha) VALUES (?, ?, ?)", [
    ('SKU-100', 2, '2026-06-25'),
    ('SKU-200', 5, '2026-06-26'),
    ('SKU-300', 8, '2026-06-27'),
    ('SKU-400', 10, '2026-06-28')
])
conexion.commit()

# 2. EXTRACCIÓN DE DATOS CON SQL
query = '''
SELECT 
    p.nombre AS producto,
    p.stock_actual,
    SUM(v.cantidad_vendida) AS unidades_vendidas
FROM productos p
LEFT JOIN ventas v ON p.sku = v.sku
GROUP BY p.sku
'''
df = pd.read_sql_query(query, conexion)
conexion.close()

# 3. CREACIÓN DEL DASHBOARD VISUAL (GRÁFICOS)
# Creamos una figura con dos gráficos (uno al lado del otro)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Gráfico 1: Alerta de Stock Crítico (Resaltamos en ROJO los que tienen menos de 5 unidades)
colores = ['#e74c3c' if x < 5 else '#2ecc71' for x in df['stock_actual']]
ax1.bar(df['producto'], df['stock_actual'], color=colores, edgecolor='black')
ax1.axhline(y=5, color='orange', linestyle='--', label='Línea Crítica (5 un.)')
ax1.set_title('🚨 Alerta de Inventario: Niveles de Stock', fontsize=12, fontweight='bold')
ax1.set_ylabel('Unidades Disponibles')
ax1.legend()
ax1.grid(axis='y', linestyle=':', alpha=0.6)

# Gráfico 2: Rendimiento de Ventas (Top Productos)
ax2.bar(df['producto'], df['unidades_vendidas'], color='#3498db', edgecolor='black')
ax2.set_title('📈 Rendimiento: Unidades Vendidas por Producto', fontsize=12, fontweight='bold')
ax2.set_ylabel('Cantidad Vendida')
ax2.grid(axis='y', linestyle=':', alpha=0.6)

plt.tight_layout()

# Guardar el dashboard automáticamente como imagen para el reporte
plt.savefig('dashboard_compras.png', dpi=300)
plt.show()

print("¡Dashboard generado con éxito y guardado como 'dashboard_compras.png'!")
