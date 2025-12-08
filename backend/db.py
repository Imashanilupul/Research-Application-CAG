import chromadb
import config



def get_chroma_client():
    client = chromadb.CloudClient(
        tenant=config.CHROMA_TENENT,
        database=config.CHROMA_DATABSE,
        api_key=config.CHROMA_API_KEY
    )
    return client
