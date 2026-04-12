from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Many-to-Many relationship table for Knowledge Graph connections
knowledge_links = Table(
    'knowledge_links', Base.metadata,
    Column('source_archive_id', Integer, ForeignKey('archives.id'), primary_key=True),
    Column('target_archive_id', Integer, ForeignKey('archives.id'), primary_key=True),
    Column('relationship_type', String(50)),
    Column('strength', Integer, default=1)
)

class Archive(Base):
    """Stores the physical/logical metadata of a study record."""
    __tablename__ = 'archives'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(String(50))
    file_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    connections = relationship(
        'Archive', 
        secondary=knowledge_links,
        primaryjoin=id == knowledge_links.c.source_archive_id,
        secondaryjoin=id == knowledge_links.c.target_archive_id,
        backref='back_connections'
    )

class ChatMessage(Base):
    """Stores persistent Socratic conversation history."""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    role = Column(String(10), nullable=False) 
    content = Column(Text, nullable=False)
    topic_tag = Column(String(100), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
