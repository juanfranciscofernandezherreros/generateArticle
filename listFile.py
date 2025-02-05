import os
import random
from datetime import datetime
from pymongo import MongoClient
import openai
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# 📌 Configuración de la API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📌 URI de conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI")

# Conectar a MongoDB
client = MongoClient(MONGO_URI)
db_name = "test"
db = client[db_name]

# 📌 Seleccionar una categoría aleatoria
categories_collection = db["categories"]
categories = list(categories_collection.find({}, {"_id": 1, "name": 1}))

if categories:
    selected_category = random.choice(categories)
    category_id = selected_category["_id"]
    category_name = selected_category["name"]
else:
    print("⚠️ No hay categorías disponibles. Se debe insertar una antes de crear el post.")
    category_id = None
    category_name = None

# 📌 Seleccionar algunos tags aleatorios
tags_collection = db["tags"]
tags = list(tags_collection.find({}, {"_id": 1, "name": 1}))

if tags:
    selected_tags = random.sample(tags, min(len(tags), 3))  # Seleccionar hasta 3 tags
    selected_tags_ids = [tag["_id"] for tag in selected_tags]
    selected_tags_names = [tag["name"] for tag in selected_tags]
else:
    print("⚠️ No hay tags disponibles. Se debe insertar al menos uno antes de crear el post.")
    selected_tags_ids = []
    selected_tags_names = []

# 📌 Asignar el usuario "user1" como autor
user = db["users"].find_one({"username": "user1"}, {"_id": 1})

if user:
    selected_author = user["_id"]
else:
    print("⚠️ No se encontró el usuario 'user1'.")
    selected_author = None

# 📌 Generar un artículo con OpenAI
if category_name and selected_tags_names:
    prompt = (
        f"Escribe un artículo sobre '{category_name}' incluyendo los temas {', '.join(selected_tags_names)}. "
        f"El artículo debe tener 3000 caracteres y ser SEO-friendly."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional content writer specialized in SEO."},
            {"role": "user", "content": prompt}
        ]
    )

    article_content = response["choices"][0]["message"]["content"]
else:
    article_content = None
    print("\n⚠️ No se pudo generar el artículo porque faltan datos de categoría o tags.")

# 📌 Insertar el post en MongoDB si se tienen todos los datos necesarios
if category_id and selected_author and article_content:
    post = {
        "title": f"Artículo sobre {category_name}",
        "body": article_content,
        "category": category_id,
        "tags": selected_tags_ids,
        "author": selected_author,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    result = db["posts"].insert_one(post)
    print(f"\n✅ Post insertado con éxito. ID: {result.inserted_id}")
else:
    print("\n⚠️ No se pudo insertar el post porque faltan datos requeridos.")

# Cerrar conexión
client.close()
print("\n✅ Conexión cerrada.")
