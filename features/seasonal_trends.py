"""
Seasonal Trends & Trending Topics
Uses Google Trends (pytrends) to detect seasonality
"""
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict

def analyze_seasonal_trends(keywords: List[str], timeframe: str = "today 12-m") -> Dict:
    """
    Analyze seasonal trends for keywords
    
    Args:
        keywords: List of keywords (max 5)
        timeframe: Time range (e.g., 'today 12-m', 'today 5-y')
        
    Returns:
        Dict with trend data
    """
    print(f"📈 Analyzing seasonal trends for {len(keywords)} keywords...")
    
    if len(keywords) > 5:
        keywords = keywords[:5]
        print(f"   ⚠️ Limited to 5 keywords: {keywords}")
    
    try:
        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Build payload
        pytrends.build_payload(keywords, timeframe=timeframe, geo='US')
        
        # Get interest over time
        interest_over_time = pytrends.interest_over_time()
        
        if interest_over_time.empty:
            return {
                "success": False,
                "error": "No trend data available for these keywords"
            }
        
        # Analyze each keyword
        trends = []
        for keyword in keywords:
            if keyword in interest_over_time.columns:
                data = interest_over_time[keyword]
                
                # Calculate trend metrics
                current_interest = data.iloc[-1]
                avg_interest = data.mean()
                max_interest = data.max()
                min_interest = data.min()
                
                # Detect seasonality
                is_seasonal = max_interest > (avg_interest * 1.5)
                
                # Find peak months
                monthly_avg = data.resample('M').mean()
                peak_month = monthly_avg.idxmax().strftime('%B') if not monthly_avg.empty else "N/A"
                
                # Trend direction
                recent_trend = data.iloc[-30:].mean() if len(data) >= 30 else data.mean()
                older_trend = data.iloc[:30].mean() if len(data) >= 30 else data.mean()
                
                if recent_trend > older_trend * 1.2:
                    trend_direction = "Rising ↗️"
                elif recent_trend < older_trend * 0.8:
                    trend_direction = "Declining ↘️"
                else:
                    trend_direction = "Stable →"
                
                trends.append({
                    "keyword": keyword,
                    "current_interest": int(current_interest),
                    "average_interest": round(avg_interest, 1),
                    "peak_interest": int(max_interest),
                    "is_seasonal": is_seasonal,
                    "peak_month": peak_month,
                    "trend_direction": trend_direction,
                    "volatility": round((max_interest - min_interest) / avg_interest, 2)
                })
        
        # Get related queries
        related_queries = pytrends.related_queries()
        
        print(f"   ✅ Trends analyzed for {len(trends)} keywords")
        
        return {
            "success": True,
            "timeframe": timeframe,
            "trends": trends,
            "related_queries": _format_related_queries(related_queries, keywords),
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ❌ Trends analysis failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_trending_topics(geo: str = "US", count: int = 10) -> Dict:
    """
    Get currently trending topics
    
    Args:
        geo: Geographic region (e.g., 'US', 'GB', 'IN')
        count: Number of trends to return
        
    Returns:
        Dict with trending topics
    """
    print(f"🔥 Fetching trending topics for {geo}...")
    
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Get trending searches
        trending = pytrends.trending_searches(pn=geo.lower())
        
        topics = trending.head(count).values.flatten().tolist()
        
        print(f"   ✅ Found {len(topics)} trending topics")
        
        return {
            "success": True,
            "geo": geo,
            "topics": topics,
            "count": len(topics),
            "fetched_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ❌ Trending topics failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _format_related_queries(related_queries: Dict, keywords: List[str]) -> Dict:
    """Format related queries for output"""
    formatted = {}
    
    for keyword in keywords:
        if keyword in related_queries:
            top_queries = related_queries[keyword].get('top', pd.DataFrame())
            if not top_queries.empty and 'query' in top_queries.columns:
                formatted[keyword] = top_queries['query'].head(5).tolist()
            else:
                formatted[keyword] = []
    
    return formatted
