from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Envelope(Base):
    __tablename__ = 'envelopes'
    __table_args__ = {'schema': 'app'}
    
    """
    Modelo para representar sobres (envelopes) en el método financiero envelope.
    Los sobres son contenedores de dinero asignado para propósitos específicos.
    """

    id = Column(Integer, primary_key=True, autoincrement=True) # ID del sobre
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) # ID del usuario propietario del sobre
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=True) # ID de subcategoría (opcional, para integración con reportes)
    method_envelope_id = Column(Integer, ForeignKey('method_envelope.id'), nullable=False) # ID de la configuración del método envelope
    name = Column(String, nullable=False) # Nombre específico del sobre (ej: "Comida Familiar", "Gasolina Auto")
    budget_amount = Column(Numeric, nullable=False, default=0) # Monto presupuestado para el sobre
    current_balance = Column(Numeric, nullable=False, default=0) # Saldo actual del sobre
    is_active = Column(Boolean, nullable=False, default=True) # Indica si el sobre está activo
    created_at = Column(TIMESTAMP) # Fecha de creación del sobre
    updated_at = Column(TIMESTAMP) # Fecha de última actualización del sobre

    # ============================
    # Relationships and Foreign Keys
    # ============================
    user = relationship("User", back_populates="envelopes") # Relación con el modelo User
    subcategory = relationship("Subcategory", back_populates="envelopes") # Relación opcional con subcategoría (para reportes integrados)
    method_envelope = relationship("MethodEnvelope", back_populates="envelopes") # Relación con la configuración del método envelope
    transactions = relationship("Transaction", back_populates="envelope") # Transacciones asociadas al sobre
    budget_items = relationship("BudgetItem", back_populates="envelope") # Partidas presupuestarias asociadas al sobre
    
    # Propiedad para acceder a la categoría a través de la subcategoría
    @property
    def category(self):
        return self.subcategory.category if self.subcategory else None
