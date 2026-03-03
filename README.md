# 📌 Sistema de Gestión de Clientes, Productos y Ventas

## 1. Descripción general
Este proyecto es una aplicación web para **gestionar clientes, productos e inventario**, diseñada inicialmente para uso **exclusivo del administrador**.  
La app permite **registrar clientes, controlar stock, registrar ventas y generar reportes básicos**.  

En una fase futura, se planea habilitar un **portal de clientes** donde estos podrán ingresar, visualizar el catálogo disponible y realizar pedidos en línea, convirtiendo la aplicación en una **tienda virtual**.

---

## 2. Objetivos principales
- Mantener un **historial de clientes** y sus compras.
- Gestionar un **inventario de productos** con control automático de stock.
- Registrar y administrar **ventas** asociadas a clientes.
- Garantizar que los productos **solo se muestren como disponibles si hay stock**.
- Proveer **reportes de ventas** y productos más vendidos.
- Ofrecer una interfaz **responsiva** accesible desde PC y móviles.

---

## 3. Módulos del sistema

### 🔹 3.1 Clientes
- Registrar, editar y eliminar clientes.
- Almacenar datos básicos: nombre, correo, teléfono, dirección.
- Consultar historial de compras por cliente.

### 🔹 3.2 Productos
- Registrar productos con: nombre, descripción, precio, imagen y stock.
- Descontar stock automáticamente en cada venta.
- Mostrar solo productos con stock disponible.
- (Futuro) Alertar cuando el stock esté bajo.

### 🔹 3.3 Ventas
- Registrar ventas seleccionando cliente y productos.
- Calcular el total automáticamente.
- Guardar fecha, productos y cantidades.
- Consultar ventas por cliente o fecha.

### 🔹 3.4 Reportes
- Ventas por día, semana y mes.
- Productos más vendidos.
- Ingresos totales en un periodo.
- (Futuro) Exportar reportes a Excel o PDF.

---

## 4. Características técnicas
- **Backend**: Django (Python 3.x).
- **Frontend**: Django Templates + Bootstrap 5 (responsivo).
- **Base de datos**: SQLite (fase inicial) → escalable a PostgreSQL/MySQL.
- **Autenticación**: Sistema de usuarios de Django (login de administrador).
- **Diseño**: Responsivo con Bootstrap, adaptable a PC y móviles.

---

## 5. Futuras mejoras
- **Portal de clientes**:
  - Catálogo de productos.
  - Carrito de compras.
  - Registro/Login de clientes.
  - Historial de pedidos.

- **Pagos e integraciones**:
  - MercadoPago, PayPal, Stripe.
  - Notificaciones automáticas (correo/WhatsApp).

- **Aplicación móvil (PWA o app nativa)**:
  - Posibilidad de instalarse en el celular.
  - Funcionamiento offline parcial.

---

## 6. Instalación y uso

### 🔹 Requisitos
- Python 3.10+
- pip
- Virtualenv (recomendado)

### 🔹 Pasos de instalación
```bash
# Clonar repositorio
git clone https://github.com/tuusuario/gestion-clientes-productos.git
cd gestion-clientes-productos

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows

# Instalar dependencias
pip install -r requirements.txt

# Migraciones de base de datos
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
