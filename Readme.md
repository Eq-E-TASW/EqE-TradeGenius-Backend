# TradeGenius Backend 📊🚀

¡Bienvenido al repositorio del Backend del Sistema de Apoyo a las Decisiones en Bolsa de Valores "TradeGenius"!

## Descripción

Este backend proporciona las funcionalidades clave del sistema **TradeGenius**, incluyendo ingestión de datos, predicción de valores bursátiles, ejecución simulada de trading, análisis de sentimientos de titulares y soporte de chatbot. Está desarrollado utilizando **FastAPI** para garantizar una arquitectura escalable, eficiente y moderna.


## Funcionalidades

1. **📥 Ingesta de Datos**:
   - Endpoint para consultar y visualizar datos históricos de acciones.
   - Función de graficación de precios y volúmenes históricos.
   - Conexión con una base de datos SQL para almacenar información relevante del mercado.

2. **📈 Predicción de Acciones**:
   - Implementación de modelos de Machine Learning (SVM y LSTM).
   - Generación de gráficos predictivos y valores futuros basados en datos históricos.
   - Endpoint dedicado para realizar predicciones por activo.

3. **💹 Módulo de Trading**:
   - Gestión de activos simulados con endpoints para consultar y actualizar posiciones.
   - Simulación de órdenes de compra y venta con validación automática.
   - Actualización en tiempo real de los activos del usuario.

4. **🤖 Chatbot Financiero**:
   - Implementación de un asistente basado en IA para responder preguntas relacionadas con el sistema.
   - Interacción en tiempo real mediante procesamiento de lenguaje natural.
   - Endpoint para enviar y recibir mensajes.

5. **🖼 Análisis de Sentimientos**:
   - Implementación de un analizador de sentimientos de titulares basado en Tavily y GPT
   - Endpoint para busqueda de titulares y análiis de sentimientos de los mismos.


## Endpoints Principales

### Ingesta de Datos
- **`GET /api/data_ingestion/historical_data`**: Devuelve data histórica para un ticker.
- **`GET /api/data_ingestion/tickers`**: Devuelve los tickers disponibles y sus datos más recientes.
- **`GET /api/data_ingestion/plot`**: Genera gráficos de líneas comparativos de precios históricos.
- **`GET /api/data_ingestion/plot_last_volume`**: Genera gráficos de barras del último volumen de los activos seleccionados.

### Predicción
- **`POST /api/prediction/predict`**: Realiza predicciones usando los modelos SVM o LSTM.
- **`GET /api/prediction/images/{image_name}`**: Devuelve imágenes generadas de predicciones.

### Trading
- **`GET /api/trading/get_assets/{user_id}`**: Consulta los activos del usuario.
- **`POST /api/trading/trade`**: Simula una operación de compra o venta.

### Chatbot
- **`GET /api/chatbot/messages`**: Obtiene la historia de mensajes del chatbot.
- **`POST /api/chatbot/send-message`**: Envía un mensaje y devuelve la respuesta del bot.

### Sentimientos
- **`GET /api/sentiment/analyze-news`**: Busca titulares sobre un tema y analiza el sentimiento de los mismos.


## Requisitos
Para levantar el backend en local, es necesario tener instalado Docker, o:
- **Python 3.10+**
- Base de datos PostgreSQL (despliegue local opcional).
- Librerías necesarias listadas en `requirements.txt`.


### Video de Demostración despliegue local
Para ver una demostración de cómo desplegar el Backend del proyecto en local, y cómo funcionan los endpoints, puedes acceder al siguiente video de presentación:

💻💾 [**Ver Video Instalación y Demo**](https://www.youtube.com/)


### Despliegue en nube
El sistema ha sido desplegado en nube usando **Cloud SQL, Cloud Build y Cloud Run** para su fácil acceso y uso. Puedes acceder a la versión en la nube del backend del proyecto a través del siguiente enlace:

🚀☁️ [**Acceder a TradeGenius Backend**](https://tradegeniusbackcloud-registry-194080380757.southamerica-west1.run.app/docs)


## Equipo E-2024-2:

- Alberto Ramos, Harold Giusseppi
- Azucena Huamantuma, José Antonio
- Chiara Arcos, Bryan Miguel
- Laos Carrasco, Rafael Alonso
- Marcelo Salinas, Moises Enrique
- Mauricio Montes, Jorge Luis
- Montes Perez, Josue Justi
