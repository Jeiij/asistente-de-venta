# Arquitectura del Sistema - MVP Memi Burger (AI Sales Agent)

## 1. Descripción General del Proyecto
Sistema de agente de ventas autónomo diseñado para una PyME de comida rápida. El bot opera en Telegram, gestiona catálogos, procesa pedidos, resuelve ambigüedades del menú, calcula el total (integrando la tasa del BCV) y delega la validación de pagos (transferencia/efectivo/pago móvil) a un equipo humano mediante un grupo de administradores. 

## 2. Stack Tecnológico Estricto
- **Lenguaje:** Python 3.x
- **Framework Web:** FastAPI (Asíncrono)
- **Base de Datos:** PostgreSQL (Desplegado en Docker)
- **ORM:** SQLAlchemy 2.0 (Sintaxis asíncrona estricta con `asyncpg` y tipado moderno con `Mapped` y `mapped_column`)
- **IA / LLM:** Gemini 1.5 Flash (Vía Google GenAI SDK)
- **Integración Telegram:** Webhooks (Túnel mediante Ngrok para desarrollo local)
- **Manejo de Moneda:** Scraping ligero / API interna para obtener la tasa del BCV (Banco Central de Venezuela).

## 3. Principios de Ingeniería y Restricciones (¡CRÍTICO PARA EL LLM!)
- **Enfoque Code-First Exclusivo:** Se prohíbe terminantemente sugerir o escribir integraciones para plataformas *low-code* (como n8n, Make, etc.). Toda la inteligencia y orquestación vive en el código Python.
- **Diseño para PyMEs:** Las soluciones deben ser ágiles, sin sobreingeniería corporativa (ej. un solo local, sin ruteo satelital).
- **Separación de Capas Obligatoria:** 
  - `models/`: Única fuente de la base de datos (DDL).
  - `services/`: Lógica de negocio pura (cálculos, carritos, CRUD).
  - `agent/`: Orquestación del LLM, *Tools* y generación de prompts.
  - `api/`: Controladores web (Webhooks de Telegram).

## 4. Estructura de la Base de Datos (Relacional)
El esquema central maneja persistencia inmutable para los datos financieros:
- **`Customer`**: Identificados por `chat_id` (Telegram) para retención a largo plazo.
- **`Product` & `Extra`**: Catálogo gestionable (activo/inactivo). Precios base en Euros (€).
- **`Municipality`**: Zonas de delivery con tarifas fijas en Euros (€).
- **`Order`**: Almacena el estado del carrito (`CART`, `PENDING_APPROVAL`). **Regla estricta:** Al cerrar la venta, se "congela" la tasa del BCV y el costo del delivery en esta tabla (`charged_delivery_eur`, `exchange_rate`) para proteger el histórico financiero.
- **`OrderItem` & `OrderItemExtra`**: Soporta notas personalizadas y manejo de ambigüedad de proteínas (ej. "Carne", "Pollo", "Mixto").

## 5. Diseño del Agente de IA y Memoria de Estado
- **Ejecución Stateless:** El LLM no debe procesar historiales masivos de chat.
- **Inyección Dinámica (RAG de Estado):** Antes de cada llamada a Gemini, FastAPI consulta PostgreSQL e inyecta el estado actual del usuario (Nombre, Contenido del Carrito) en el *System Prompt*. 
- **Tool Calling:** Gemini no tiene acceso a la DB. Usa funciones (Tools) como `obtener_menu()`, `agregar_al_carrito()`, `calcular_total()` delegadas a la capa `services/`.
- **Competencias del Bot:** Autorizado para flujo de ventas y para responder Preguntas Frecuentes (FAQs) sobre ubicación, métodos de pago y horarios operacionales (12 PM a 12 AM).

## 6. Flujo de Cierre y Pago (Validación Manual)
1. Bot confirma carrito y calcula el total (Total € + Delivery €) convertido a Bs. según BCV.
2. Bot solicita método de pago (Efectivo, Pago Móvil, Transferencia).
3. Bot solicita comprobante (Foto del billete o capture).
4. El sistema captura el `file_id` del archivo en Telegram y no lo descarga localmente.
5. El sistema envía un resumen de la orden y la foto (usando el `file_id`) al grupo de administradores (identificado por la variable de entorno `ADMIN_GROUP_CHAT_ID`) para su aprobación manual.
6. El bot solicita la ubicación GPS/Google Maps al cliente.