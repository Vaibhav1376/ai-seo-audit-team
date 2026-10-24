'''
"""
Seasonal Trends Analysis - Feature #4
Google Trends integration for keyword seasonality
"""
from pytrends.request import TrendReq
import pandas as pd
from typing import Dict, List
import time

def get_keyword_seasonality(keyword: str, timeframe: str = "today 12-m") -> Dict:
    """
    Analyze keyword seasonality using Google Trends
    
    Args:
        keyword: Keyword to analyze
        timeframe: Time range (default: last 12 months)
        
    Returns:
        Dict with trend data and insights
    """
    
    print(f"Analyzing trends for: {keyword}")
    
    try:
        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25))
        
        # Build payload
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='', gprop='')
        
        # Get interest over time
        interest_df = pytrends.interest_over_time()
        
        if interest_df.empty or keyword not in interest_df.columns:
            return {
                "success": False,
                "error": "No trend data available for this keyword"
            }
        
        # Calculate metrics
        values = interest_df[keyword].values
        avg_interest = int(values.mean())
        max_interest = int(values.max())
        min_interest = int(values.min())
        std_dev = float(values.std())
        
        # Find peak month
        peak_idx = values.argmax()
        peak_date = interest_df.index[peak_idx]
        
        # Determine if seasonal (high std deviation)
        is_seasonal = std_dev > 20
        
        # Trend direction (compare recent 3 months vs older 3 months)
        recent_avg = values[-90:].mean() if len(values) >= 90 else values[-30:].mean()
        older_avg = values[:90].mean() if len(values) >= 90 else values[:30].mean()
        
        if recent_avg > older_avg * 1.2:
            trend_direction = "📈 Trending Up"
        elif recent_avg < older_avg * 0.8:
            trend_direction = "📉 Trending Down"
        else:
            trend_direction = "➡️ Stable"
        
        # Get related queries
        time.sleep(1)  # Rate limiting
        related_queries = pytrends.related_queries()
        
        rising_queries = []
        top_queries = []
        
        if keyword in related_queries:
            if related_queries[keyword]['rising'] is not None:
                rising_queries = related_queries[keyword]['rising'].head(5).to_dict('records')
            
            if related_queries[keyword]['top'] is not None:
                top_queries = related_queries[keyword]['top'].head(5).to_dict('records')
        
        # Get regional interest
        time.sleep(1)
        regional_df = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
        
        if not regional_df.empty and keyword in regional_df.columns:
            top_regions = regional_df[keyword].nlargest(5).to_dict()
        else:
            top_regions = {}
        
        return {
            "success": True,
            "keyword": keyword,
            "avg_interest": avg_interest,
            "max_interest": max_interest,
            "min_interest": min_interest,
            "volatility": round(std_dev, 2),
            "is_seasonal": is_seasonal,
            "peak_month": peak_date.strftime("%B %Y"),
            "trend_direction": trend_direction,
            "seasonality_score": int((std_dev / avg_interest) * 100) if avg_interest > 0 else 0,
            "rising_queries": rising_queries,
            "top_queries": top_queries,
            "top_regions": top_regions,
            "recommendation": get_trend_recommendation(is_seasonal, trend_direction, avg_interest)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "note": "Google Trends API might be rate-limited. Try again in a minute."
        }

def get_trend_recommendation(is_seasonal: bool, trend: str, avg_interest: int) -> str:
    """Generate recommendation based on trend data"""
    
    if avg_interest < 10:
        return "⚠️ Low search interest. Consider targeting related keywords with higher volume."
    
    if is_seasonal:
        return "📅 Highly seasonal keyword. Plan content calendar around peak months."
    
    if "Up" in trend:
        return "🚀 Growing interest! Good time to create content and build authority."
    elif "Down" in trend:
        return "⬇️ Declining interest. Monitor closely or pivot to rising related topics."
    else:
        return "✅ Stable search interest. Reliable keyword for consistent traffic."

def batch_analyze_trends(keywords: List[str]) -> List[Dict]:
    """Analyze multiple keywords for seasonality"""
    
    results = []
    
    for i, keyword in enumerate(keywords):
        print(f"Analyzing {i+1}/{len(keywords)}: {keyword}")
        
        result = get_keyword_seasonality(keyword)
        results.append(result)
        
        # Rate limiting (Google Trends allows ~10 requests/min)
        if i < len(keywords) - 1:
            time.sleep(6)  # 6 seconds between requests
    
    return results
'''
from pytrends.request import TrendReq
from typing import List, Dict
import time

def batch_analyze_trends(keywords: List[str]) -> List[Dict]:
    """Analyze multiple keywords efficiently"""
    
    results = []
    # Process in chunks of 5 (Google Trends limit)
    chunk_size = 5
    
    # Initialize pytrends once
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25))

    for i in range(0, len(keywords), chunk_size):
        chunk = keywords[i:i + chunk_size]
        print(f"Analyzing batch: {chunk}")
        
        try:
            # ONE API call for 5 keywords
            pytrends.build_payload(chunk, cat=0, timeframe='today 12-m')
            data = pytrends.interest_over_time()
            
            for kw in chunk:
                if kw in data.columns:
                    avg = int(data[kw].mean())
                    trend_direction = "Up ↗️" if data[kw].iloc[-1] > data[kw].iloc[0] else "Down ↘️"
                    results.append({
                        "keyword": kw,
                        "seasonality_score": avg,
                        "trend": trend_direction,
                        "success": True
                    })
                else:
                    results.append({"keyword": kw, "success": False, "error": "No data"})
                    
            # Small sleep between batches, not individual keywords
            time.sleep(1) 
            
        except Exception as e:
            print(f"Batch error: {e}")
            for kw in chunk:
                results.append({"keyword": kw, "success": False, "error": str(e)})

    return results