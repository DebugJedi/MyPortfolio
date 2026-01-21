"""Analytics Routes"""
from fastapi import APIRouter, HTTPException
from app.database.connection import get_db, get_table_counts
from app.database.models import (
    Visitor, ChatSession, ContactMessage, ChatQuery,
    EmailGeneration, ProjectView, ApiUsage
)
from sqlalchemy import func
from datetime import datetime, timedelta


router = APIRouter()

@router.get("/summary")
async def get_analytics():
    """
    Get overall analytics summary
    Returns:
    - Total counts of all tables
    - Today's visitor count
    - Top pages
    - Device breakdown
    - Unread messages count
    """

    try: 
        # Get all tables counts
        counts = get_table_counts()

        with get_db() as db:
            # Visitor today
            today = datetime.now(datetime.timezone.utc)
            today_visitors = db.query(Visitor).filter(
                func.date(Visitor.timestamp) == today
            ).count()

            # Visitor this week
            week_ago = datetime.now(datetime.timezone.utc) - timedelta(days=7)
            week_visitors = db.query(Visitor).filter(
                func.date(Visitor.timestamp) >= week_ago
            ).count()

            # Most Viewed pages ( last 30 days)
            thirty_days_ago = datetime.now(datetime.timezone.utc)-timedelta(days=30)
            top_pages = db.qeury(
                Visitor.page,
                func.count(Visitor.id).lable('views')

            ).filter(Visitor.timestamp >= thirty_days_ago)\
            .group_by(Visitor.page)\
            .order_by(func.count(Visitor.id).desc())\
            .limit(10)\
            .all()

            # Device breakdown
            devices = db.query(
                Visitor.device_type,
                func.count(Visitor.id).label('count')
            ).group_by(Visitor.device_type)\
            .all()

            # Unread messages
            unread_messages = db.query(ContactMessage).filter_by(read=False).count()

            # Active chat sessions (with queries)
            active_sessions = db.query(ChatSession)\
                .filter(ChatSession.queries_count > 0)\
                .count()
            
            # Average response time for chatbot
            avg_response = db.query(
                func.avg(ChatSession.avg_respone_time_ms)
            ).scalar()

        return {
            "status": "success",
            "totals": counts,
            "visitors": {
                "today": today_visitors,
                "this_week": week_visitors,
                "all_time": counts['visitors']
            },
            "top_pages": [
                {"page": page, "views": views}
                for page, views in top_pages
            ],
            "devices": [
                {"type": device or "unknown" , "count": count}
                for device, count in devices
            ],
            "messages": {
                "unread": unread_messages,
                "total": counts['contact_messages']
            },
            "chatbot": {
                "acitve_sessions": active_sessions,
                "avg_response_time_ms": round(avg_response or 0,2),
                "total_generations": counts['email_generations']
            }

        }
    
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    

@router.get("/visitors/trend")
async def visitor_trend(days: int=30):
    """
    Get visitor trend for last N days

    Query params:
    - days: Number of days to include (default: 30)

    """
    try: 
        if days < 1 or days > 365:
            raise HTTPException(400, detail="Days must be between 1 and 365")
        with get_db() as db:
            start_date = datetime.now(datetime.timezone.utc) - timedelta(days=days)

            trend = db.query(
                func.date(Visitor.timestamp).label('date'),
                func.count(Visitor.id).label('visitor')
            ).filter(Visitor.timestamp >= start_date)\
            .group_by(func.date(Visitor.timestamp))\
            .order_by(func.date(Visitor.timestamp))\
            .all()

            return {
                "status": "success",
                "days": days,
                "data": [
                    {"date": str(date), "visitors": visitors}
                    for date, visitors in trend
                ]
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    
@router.get("/pages/views")
async def page_views(days: int= 30):
    """
    Get page view statistics
    """
    try:
        with get_db as db:
            start_date = datetime.now(datetime.timezone.utc) - timedelta(days=days)

            page_stats = db.query(
                Visitor.page,
                func.count(Visitor,id).label('total_views'),
                func.count(func.distinct(Visitor.ip_hash)).label('unique_visitors')
            ).filter(Visitor.page)\
            .group_by(Visitor.page)\
            .order_by(func.count(Visitor.id).desc())\
            .all()

            return {
                "status": "success",
                "days": days,
                "pages": [
                    {
                        "page": page,
                        "total_views": total,
                        "unique_visitors": unique
                    }
                    for page, total, unique in page_stats
                ]
            }
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    

@router.get('/projects/popular')
async def popular_projects():
    """Get most viewed projects"""
    try:
        with get_db as db:
            project_stats = db.query(
                ProjectView.project_slug,
                ProjectView.project_name,
                func.count(ProjectView.id).label('views')
            ).group_by(ProjectView.project_slug, ProjectView.project_name)\
            .order_by(func.count(ProjectView.id).desc())\
            .limit(10)\
            .all()

            return {
                "status":"success",
                "projects": [
                    {
                        "slug": slug,
                        "name": name,
                        "views": views
                    }
                    for slug, name, views in project_stats
                ]
            }
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    

@router.get("/chatbot/sats")
async def chatbot_stats():
    """Get chatbot usage stats"""

    try:
        with get_db as db:
            
            total_sessions = db.query(ChatSession).count()
            total_queries = db.query(ChatQuery).count()

            avg_queries = db.query(
                func.avg(ChatSession.avg_response_time_ms)
            ).scalar()

            avg_response_time = db.query(
                func.avg(ChatSession.avg_response_time_ms)
            ).scalar()

            top_sessions = db.query(ChatSession)\
                            .order_by(ChatSession.queries_count.desc())\
                            .limit(5)\
                            .all()
            
            recent_sessions = db.query(ChatSession)\
                            .order_by(ChatSession.created_at.desc())\
                            .limit(10)\
                            .all()
            
            return {
                "status": "success",
                "overview": {
                    "total_sessions": total_sessions,
                    "total_queries": total_queries,
                    "avg_queries_per_session": round(avg_queries or 0,2),
                    "avg_response_time_ms": round(avg_response_time or 0,2)
                },
                "top_sessions": [s.to_dict() for s in top_sessions],
                "recent_sessions": [s.to_dict() for s in recent_sessions]
            }
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    

@router.get("/email/stats")
async def email_generator_status():
    """Get email generator stats"""
    try:
        with get_db as db:

            total = db.query(EmailGeneration).count()
            successful = db.query(EmailGeneration).filter_by(success=True).count()
            failed = db.qeury(EmailGeneration).filter_by(success=False).count()

            avg_time = db.query(
                func.avg(EmailGeneration.generation_time_ms)
            ).filter_by(success=True).scalar()

            top_companies = db.query(
                EmailGeneration.company_name,
                func.count(EmailGeneration.id).label('count')
            ).filter(EmailGeneration.company_name != "")\
            .group_by(EmailGeneration.company_name)\
            .order_by(func.count(EmailGeneration.id).desc())\
            .limit(10)\
            .all()

            recent = db.query(EmailGeneration)\
                    .filter_by(success=True)\
                    .order_by(EmailGeneration.created_at.desc())\
                    .limit(10)\
                    .all()
            
            return {
                "status": "success",
                "overview": {
                    "total_generations": total,
                    "successfull": successful,
                    "failed": failed,
                    "success_rate": round((successful/total*100) if total > 0 else 0, 2),
                    "avg_generation_time_ms": round(avg_time or 0, 2)
                },
                "top_companies": [
                    {"comapny": company, "count": count}
                    for company, count in top_companies
                ],
                "recent_generations": [g.to_dict() for g in recent]
            }
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    
@router.get('/api/performance')
async def api_performance():
    """Get API endpoint performance metrics"""
    try:
        with get_db() as db:

            endpoint_stats = db.qeury(
                ApiUsage.endpoint,
                func.count(ApiUsage.id).label('request'),
                func.avg(ApiUsage.response_time_ms).label('avg_response_time'),
                func.count(func.distinct(ApiUsage.ip_hash)).label('unique_users')
            ).group_by(ApiUsage.endpoint)\
            .order_by(func.count(ApiUsage.id).desc())\
            .all()

            total_requests = db.query(ApiUsage).count()
            error_requests = db.query(ApiUsage)\
                    .filter(ApiUsage.status_code>=400)\
                    .count()
            
            return {
                "status": "success",
                "overview": {
                    "total_requests": total_requests,
                    "error_requests": error_requests,
                    "error_rate": round((error_requests / total_requests*100)if total_requests >0 else 0, 2)
                },
                "endpoints": [
                    {
                        "endpoint": endpoint,
                        "requests": requests,
                        "avg_response_time_ms": round(avg_time or 0, 2),
                        "unique_users": unique
                    }
                    for endpoint, requests, avg_time, unique in endpoint_stats
                ]
            }
    except Exception as e:
        raise HTTPException(500, detail=str(e)) 