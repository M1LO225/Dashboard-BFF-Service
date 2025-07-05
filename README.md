Servicio Dashboard BFF (Backend-for-Frontend)
Visión General
El Dashboard BFF Service es la fuente principal de datos para la interfaz de usuario del frontend de la plataforma. Actúa como un API gateway y agregador de datos, proporcionando un único punto de acceso optimizado para que los clientes obtengan una visión general de un escaneo completado o en proceso.

Sus responsabilidades principales son:

Autenticación: Protege sus endpoints usando JWTs emitidos por el servicio de autenticación (Auth Service).

Agregación de Datos: Recibe una solicitud para un scan_id específico y consulta múltiples tablas de base de datos (scans, assets, vulnerabilities, risks) para recopilar toda la información relevante.

Formateo de Datos: Transforma los datos crudos de la base de datos en un formato estructurado y amigable para la vista, facilitando su consumo por parte del frontend.

Caché: Implementa una capa de caché utilizando Redis para almacenar los resultados de consultas complejas a la base de datos. Esto reduce drásticamente la latencia y la carga del servidor en paneles de control que se consultan frecuentemente.

Al actuar como mediador, el BFF simplifica la lógica del frontend y lo desacopla de la estructura interna compleja de los servicios del backend.

Tecnologías Utilizadas
Framework: FastAPI

Lenguaje: Python 3.11+

Base de datos: PostgreSQL (lectura desde múltiples esquemas/tablas)

Caché: Redis

Contenerización: Docker

Arquitectura
Este servicio es un microservicio basado en APIs que sigue los principios de Clean Architecture:

Dominio: Define las estructuras de datos agregadas Dashboard y la interfaz abstracta del repositorio para lectura de datos.

Aplicación: Contiene el caso de uso GetDashboardDataUseCase, que orquesta la lógica de obtención de datos, incluyendo la verificación de la caché.

Infraestructura: Proporciona el PostgresDashboardRepository (que realiza complejas uniones SQL) y la implementación de caché RedisCache.

API (Presentación): La capa de FastAPI que maneja las solicitudes HTTP, la seguridad y da formato a la respuesta JSON final.

Primeros Pasos
Sigue el procedimiento estándar: clona el repositorio, crea un entorno virtual, instala las dependencias, configura tu archivo .env (apuntando a las bases de datos y Redis correspondientes), y ejecuta:

bash
Copiar
Editar
uvicorn main:app --reload