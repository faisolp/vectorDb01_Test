"""
โมดูลสำหรับการสร้าง embeddings
"""
import torch
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    """
    คลาสสำหรับการสร้าง embeddings จากข้อความ
    """
    def __init__(self, model_name='sentence-transformers/LaBSE'):
        """
        สร้าง instance ของโมเดล
        
        Args:
            model_name (str): ชื่อของโมเดลที่ใช้สร้าง embeddings
        """
        self.model = SentenceTransformer(model_name)
        self.model.eval()
        
        # รับขนาด dimension ของโมเดล
        self.dimension = self.model.get_sentence_embedding_dimension()
        
    def get_embedding(self, text):
        """
        สร้าง embedding จากข้อความ
        
        Args:
            text (str): ข้อความที่ต้องการสร้าง embedding
            
        Returns:
            numpy.ndarray: embedding vector
        """
        embedding = self.model.encode(text)
        return embedding