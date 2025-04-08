from dotenv import load_dotenv
import os
import openai
from pgvector.sqlalchemy import Vector
from pgvector.psycopg2 import register_vector  # Importa la función para registrar el adaptador
from sqlalchemy import create_engine,Column, String, Integer, ForeignKey, DateTime,text,select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
import numpy as np

from sqlmodel import Column

# Cargar variables de entorno
load_dotenv()

# Configurar la clave de API de OpenAI (asegúrate de tenerla en tu .env)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Definir la clase base para los modelos
class Base(DeclarativeBase):
    pass

# Modelo que mapea la tabla 'phrase'
class Phrase(Base):
    __tablename__ = "phrase"
    uuid       = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Manejo de UUIDs
    content    = Column(String(1024), nullable=False)
    embedding  = mapped_column(Vector(1536))

# Función para obtener el embedding de un texto usando la API de OpenAI
def get_embedding(text: str) -> list[float]:
    response = openai.embeddings.create(input=text,model="text-embedding-3-small")
    return response.data[0].embedding

# Crear el engine para conectarse a la base de datos PostgreSQL
engine = create_engine('postgresql://vector_test:vector_test@localhost:5432/vector_test')


phrases = ["Ejemplos de desarrollo ","Quiero un helado de fresa","AI Cafe: Conversamos sobre DeepSeek y el desarrollo de la inteligencia Artificial"]

with Session(engine) as session:
    conn = engine.raw_connection()
    # Register vector type using the actual connection
    register_vector(conn)  # This is the key fix
    for p in phrases:
        phrase = Phrase(content=p, embedding=get_embedding(p))
        session.add(phrase)
        session.commit()
        print("Commiting...")
    


    #Preguntarle al usuario un texto, calcular su embedding y buscar frases similares en la base de datos
    input_text = input("Ingresa un texto: ")
    embedding = get_embedding(input_text)
    ###################################    
    # Construir la sentencia de selección con el filtro de similitud
    ####closest_items = session.scalars(select(Phrase).order_by(Phrase.embedding.cosine_distance(embedding)).limit(2))

    
    #print("Frases similares:")
    #for result in closest_items:
    #    print(result.content)
    ###################################    

    sql_query = text("SELECT phrase.uuid, phrase.content, phrase.embedding FROM phrase ORDER BY phrase.embedding <=> :emb LIMIT 3")

   
    np_array = np.array(embedding, dtype=np.float32)

    results = session.execute(sql_query, params={"emb": np_array}).mappings().all()
    print("-------------------------")
    print("Frases similares :")
    for result in results:
        print(type(result))
        print(result.content)

    stmt = select(Phrase).from_statement(
        text("SELECT phrase.uuid, phrase.content, phrase.embedding FROM phrase ORDER BY phrase.embedding <=> :emb LIMIT 3")
    )
    results = session.execute(stmt, {"emb": np_array}).scalars().all()        
    print("------------------------- 3333 ")
    print("Frases similares :")
    for result in results:
        print(type(result))
        print(result.content)