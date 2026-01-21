"""
Database Models
SQLAlchemy models for the portfolio application with comprehensive tracking
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

class ContactMessage(Base):
    """Store contact form submissions with privacy-compliant tracking"""
    __tablename__ = 'contact_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(200), nullable=False, index=True)
    message = Column(Text, nullable=False)
    
    # Privacy-compliant tracking
    ip_hash = Column(String(64), index=True)  # SHA256 hashed IP
    user_agent = Column(String(500))
    referrer = Column(String(500))
    
    # Metadata
    submitted_at = Column(DateTime, default=func.now(), index=True)
    read = Column(Boolean, default=False, index=True)
    replied = Column(Boolean, default=False)
    notes = Column(Text)  # Admin notes
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_contact_unread', 'read', 'submitted_at'),
        Index('idx_contact_recent', 'submitted_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'read': self.read,
            'replied': self.replied
        }
    
    def __repr__(self):
        return f"<ContactMessage(id={self.id}, name='{self.name}', email='{self.email}')>"


class ChatSession(Base):
    """Track GraphRAG chatbot sessions"""
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # File information
    pdf_filename = Column(String(500))
    file_size_bytes = Column(Integer)
    
    # Session statistics
    queries_count = Column(Integer, default=0)
    avg_response_time_ms = Column(Float)
    total_response_time_ms = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), index=True)
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now(), index=True)
    
    # Tracking
    ip_hash = Column(String(64))
    user_agent = Column(String(500))
    
    __table_args__ = (
        Index('idx_session_activity', 'last_activity'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'pdf_filename': self.pdf_filename,
            'queries_count': self.queries_count,
            'avg_response_time_ms': round(self.avg_response_time_ms, 2) if self.avg_response_time_ms else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }
    
    def update_stats(self, response_time_ms: float):
        """Update session statistics with new query"""
        self.queries_count += 1
        self.total_response_time_ms += response_time_ms
        self.avg_response_time_ms = self.total_response_time_ms / self.queries_count
        self.last_activity = datetime.utcnow()
    
    def __repr__(self):
        return f"<ChatSession(session_id='{self.session_id}', queries={self.queries_count})>"


class ChatQuery(Base):
    """Store individual chat queries and responses"""
    __tablename__ = 'chat_queries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    
    # Query and response
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    
    # Performance tracking
    response_time_ms = Column(Float)
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Error tracking
    error = Column(Boolean, default=False)
    error_message = Column(Text)
    
    __table_args__ = (
        Index('idx_chat_session_time', 'session_id', 'timestamp'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'session_id': self.session_id,
            'query': self.query,
            'response': self.response,
            'response_time_ms': round(self.response_time_ms, 2) if self.response_time_ms else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'error': self.error
        }
    
    def __repr__(self):
        return f"<ChatQuery(id={self.id}, session='{self.session_id[:8]}...')>"


class EmailGeneration(Base):
    """Track cold email generations"""
    __tablename__ = 'email_generations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Job posting information
    job_url = Column(String(1000), index=True)
    job_title = Column(String(500))
    company_name = Column(String(500))
    
    # Generation details
    resume_filename = Column(String(500))
    generated_email = Column(Text)
    generation_time_ms = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), index=True)
    ip_hash = Column(String(64))
    user_agent = Column(String(500))
    
    # Success tracking
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    __table_args__ = (
        Index('idx_email_company', 'company_name', 'created_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'job_url': self.job_url,
            'job_title': self.job_title,
            'company_name': self.company_name,
            'resume_filename': self.resume_filename,
            'generation_time_ms': round(self.generation_time_ms, 2) if self.generation_time_ms else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'success': self.success
        }
    
    def __repr__(self):
        return f"<EmailGeneration(id={self.id}, company='{self.company_name}')>"


class Visitor(Base):
    """Analytics - track page visits with device information"""
    __tablename__ = 'visitors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Page information
    page = Column(String(200), nullable=False, index=True)
    
    # Visitor information (privacy-compliant)
    ip_hash = Column(String(64), index=True)
    user_agent = Column(String(500))
    referrer = Column(String(500))
    
    # Device detection
    device_type = Column(String(50))  # mobile, desktop, tablet
    browser = Column(String(100))
    os = Column(String(100))
    
    # Location (optional - from IP if available)
    country = Column(String(100))
    city = Column(String(100))
    
    # Session information
    timestamp = Column(DateTime, default=func.now(), index=True)
    session_duration_seconds = Column(Integer)
    
    __table_args__ = (
        Index('idx_visitor_page_time', 'page', 'timestamp'),
        Index('idx_visitor_ip_time', 'ip_hash', 'timestamp'),
        Index('idx_visitor_device', 'device_type', 'timestamp'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'page': self.page,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f"<Visitor(id={self.id}, page='{self.page}', device='{self.device_type}')>"


class ProjectView(Base):
    """Track individual project views"""
    __tablename__ = 'project_views'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Project information
    project_slug = Column(String(200), nullable=False, index=True)
    project_name = Column(String(500))
    
    # Visitor information
    ip_hash = Column(String(64))
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Referrer tracking
    source_page = Column(String(200))  # Where they came from
    
    __table_args__ = (
        Index('idx_project_slug_time', 'project_slug', 'timestamp'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'project_slug': self.project_slug,
            'project_name': self.project_name,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source_page': self.source_page
        }
    
    def __repr__(self):
        return f"<ProjectView(project='{self.project_slug}')>"


class ApiUsage(Base):
    """Track API endpoint usage and performance"""
    __tablename__ = 'api_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Endpoint information
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10))  # GET, POST, etc.
    
    # Response information
    status_code = Column(Integer, index=True)
    response_time_ms = Column(Float)
    
    # Tracking
    ip_hash = Column(String(64))
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Error tracking
    error_message = Column(Text)
    
    __table_args__ = (
        Index('idx_api_endpoint_time', 'endpoint', 'timestamp'),
        Index('idx_api_errors', 'status_code', 'timestamp'),
        Index('idx_api_performance', 'response_time_ms'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'response_time_ms': round(self.response_time_ms, 2) if self.response_time_ms else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f"<ApiUsage(endpoint='{self.endpoint}', status={self.status_code})>"
 