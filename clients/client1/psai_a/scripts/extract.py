#!/usr/bin/env python3
"""
PSAI_1 - Culture Current Lite: Content Extraction Module
Purpose: Process harvested content with Ollama models for insights and trends
Last Modified: 2024-12-19 | By: AI Assistant | Completeness: 85/100
"""

import os
import sys
import json
import ollama
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from loguru import logger
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class ExtractedInsight:
    """Structured insight extracted from content"""
    content_id: str
    insight_type: str  # 'trend', 'sentiment', 'key_point', 'citation'
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    source_url: str
    extracted_at: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    trend_name: str
    description: str
    momentum: str  # 'rising', 'stable', 'declining'
    confidence: float
    supporting_evidence: List[str]
    timeframe: str
    impact_assessment: str

class ContentExtractor:
    """Main content extraction class using Ollama models"""
    
    def __init__(self, config_path: str = "config/extract_config.json"):
        self.config = self._load_config(config_path)
        self.ollama_client = ollama.Client(host=self.config.get('ollama_host', 'http://localhost:11434'))
        self.extracted_insights: List[ExtractedInsight] = []
        self.trend_analyses: List[TrendAnalysis] = []
        
        logger.info("ContentExtractor initialized with Ollama integration")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load extraction configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default configuration for extraction"""
        return {
            "models": {
                "primary": "llama3.1",
                "fallback": "mistral",
                "max_tokens": 2000,
                "temperature": 0.7
            },
            "extraction": {
                "batch_size": 5,
                "max_content_length": 4000,
                "min_confidence_threshold": 0.6
            },
            "prompts": {
                "insight_extraction": "prompts/insight_extraction.txt",
                "trend_analysis": "prompts/trend_analysis.txt",
                "sentiment_analysis": "prompts/sentiment_analysis.txt"
            }
        }
    
    def extract_insights_from_harvest(self, harvest_data: List[Dict]) -> List[ExtractedInsight]:
        """Extract insights from harvested content"""
        logger.info(f"Starting insight extraction from {len(harvest_data)} items")
        
        for item in harvest_data:
            try:
                insights = self._extract_item_insights(item)
                self.extracted_insights.extend(insights)
                logger.debug(f"Extracted {len(insights)} insights from {item.get('title', 'Unknown')}")
            except Exception as e:
                logger.error(f"Insight extraction failed for item {item.get('url', 'Unknown')}: {e}")
        
        logger.info(f"Insight extraction complete: {len(self.extracted_insights)} insights generated")
        return self.extracted_insights
    
    def _extract_item_insights(self, item: Dict) -> List[ExtractedInsight]:
        """Extract insights from a single content item"""
        insights = []
        
        # Prepare content for processing
        content = self._prepare_content(item)
        if not content:
            return insights
        
        # Extract key insights
        key_insights = self._extract_key_insights(item, content)
        insights.extend(key_insights)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(item, content)
        if sentiment:
            insights.append(sentiment)
        
        # Extract citations and references
        citations = self._extract_citations(item, content)
        insights.extend(citations)
        
        return insights
    
    def _prepare_content(self, item: Dict) -> str:
        """Prepare content for processing"""
        title = item.get('title', '')
        content = item.get('content', '')
        
        # Truncate if too long
        max_length = self.config.get('extraction', {}).get('max_content_length', 4000)
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return f"Title: {title}\n\nContent: {content}"
    
    def _extract_key_insights(self, item: Dict, content: str) -> List[ExtractedInsight]:
        """Extract key insights using Ollama"""
        prompt = self._load_prompt('insight_extraction')
        
        # Customize prompt with content
        full_prompt = f"{prompt}\n\nContent to analyze:\n{content}"
        
        try:
            response = self._call_ollama(full_prompt)
            insights_data = self._parse_insights_response(response)
            
            insights = []
            for insight_data in insights_data:
                insight = ExtractedInsight(
                    content_id=item.get('url_hash', ''),
                    insight_type='key_point',
                    title=insight_data.get('title', ''),
                    description=insight_data.get('description', ''),
                    confidence=insight_data.get('confidence', 0.5),
                    source_url=item.get('url', ''),
                    extracted_at=datetime.now().isoformat(),
                    metadata={
                        'source_type': item.get('source_type', ''),
                        'original_title': item.get('title', '')
                    }
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Key insight extraction failed: {e}")
            return []
    
    def _analyze_sentiment(self, item: Dict, content: str) -> Optional[ExtractedInsight]:
        """Analyze sentiment using Ollama"""
        prompt = self._load_prompt('sentiment_analysis')
        
        full_prompt = f"{prompt}\n\nContent to analyze:\n{content}"
        
        try:
            response = self._call_ollama(full_prompt)
            sentiment_data = self._parse_sentiment_response(response)
            
            if sentiment_data:
                return ExtractedInsight(
                    content_id=item.get('url_hash', ''),
                    insight_type='sentiment',
                    title=f"Sentiment: {sentiment_data.get('sentiment', 'neutral')}",
                    description=sentiment_data.get('description', ''),
                    confidence=sentiment_data.get('confidence', 0.5),
                    source_url=item.get('url', ''),
                    extracted_at=datetime.now().isoformat(),
                    metadata={
                        'sentiment_score': sentiment_data.get('score', 0),
                        'source_type': item.get('source_type', '')
                    }
                )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
        
        return None
    
    def _extract_citations(self, item: Dict, content: str) -> List[ExtractedInsight]:
        """Extract citations and references"""
        citations = []
        
        # Simple URL extraction (can be enhanced with NLP)
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content)
        
        for url in urls[:3]:  # Limit to 3 citations per item
            citation = ExtractedInsight(
                content_id=item.get('url_hash', ''),
                insight_type='citation',
                title=f"Reference: {url}",
                description=f"External reference found in content",
                confidence=0.9,  # High confidence for URL detection
                source_url=item.get('url', ''),
                extracted_at=datetime.now().isoformat(),
                metadata={
                    'citation_url': url,
                    'source_type': item.get('source_type', '')
                }
            )
            citations.append(citation)
        
        return citations
    
    def analyze_trends(self, insights: List[ExtractedInsight]) -> List[TrendAnalysis]:
        """Analyze trends from extracted insights"""
        logger.info("Starting trend analysis")
        
        # Group insights by topic/theme
        grouped_insights = self._group_insights_by_topic(insights)
        
        trends = []
        for topic, topic_insights in grouped_insights.items():
            if len(topic_insights) >= 2:  # Need at least 2 insights for trend
                trend = self._analyze_topic_trend(topic, topic_insights)
                if trend:
                    trends.append(trend)
        
        self.trend_analyses = trends
        logger.info(f"Trend analysis complete: {len(trends)} trends identified")
        return trends
    
    def _group_insights_by_topic(self, insights: List[ExtractedInsight]) -> Dict[str, List[ExtractedInsight]]:
        """Group insights by topic using simple keyword matching"""
        topics = {}
        
        # Simple topic extraction based on common keywords
        topic_keywords = {
            'AI/ML': ['artificial intelligence', 'machine learning', 'AI', 'ML', 'neural network'],
            'Technology': ['technology', 'tech', 'software', 'hardware', 'digital'],
            'Business': ['business', 'startup', 'company', 'market', 'investment'],
            'Security': ['security', 'privacy', 'cybersecurity', 'hack', 'breach'],
            'Innovation': ['innovation', 'breakthrough', 'discovery', 'research', 'development']
        }
        
        for insight in insights:
            content_lower = (insight.title + ' ' + insight.description).lower()
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    if topic not in topics:
                        topics[topic] = []
                    topics[topic].append(insight)
                    break
        
        return topics
    
    def _analyze_topic_trend(self, topic: str, insights: List[ExtractedInsight]) -> Optional[TrendAnalysis]:
        """Analyze trend for a specific topic"""
        prompt = self._load_prompt('trend_analysis')
        
        # Prepare insights summary
        insights_summary = "\n".join([
            f"- {insight.title}: {insight.description}" 
            for insight in insights[:5]  # Limit to 5 insights
        ])
        
        full_prompt = f"{prompt}\n\nTopic: {topic}\n\nInsights:\n{insights_summary}"
        
        try:
            response = self._call_ollama(full_prompt)
            trend_data = self._parse_trend_response(response)
            
            if trend_data:
                return TrendAnalysis(
                    trend_name=topic,
                    description=trend_data.get('description', ''),
                    momentum=trend_data.get('momentum', 'stable'),
                    confidence=trend_data.get('confidence', 0.5),
                    supporting_evidence=[insight.title for insight in insights],
                    timeframe=trend_data.get('timeframe', 'recent'),
                    impact_assessment=trend_data.get('impact', 'moderate')
                )
            
        except Exception as e:
            logger.error(f"Trend analysis failed for topic {topic}: {e}")
        
        return None
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API with error handling and fallback"""
        model = self.config.get('models', {}).get('primary', 'llama3.1')
        fallback_model = self.config.get('models', {}).get('fallback', 'mistral')
        
        try:
            response = self.ollama_client.generate(
                model=model,
                prompt=prompt,
                options={
                    'temperature': self.config.get('models', {}).get('temperature', 0.7),
                    'num_predict': self.config.get('models', {}).get('max_tokens', 2000)
                }
            )
            return response['response']
            
        except Exception as e:
            logger.warning(f"Primary model {model} failed, trying fallback: {e}")
            
            try:
                response = self.ollama_client.generate(
                    model=fallback_model,
                    prompt=prompt,
                    options={
                        'temperature': self.config.get('models', {}).get('temperature', 0.7),
                        'num_predict': self.config.get('models', {}).get('max_tokens', 2000)
                    }
                )
                return response['response']
                
            except Exception as e2:
                logger.error(f"Both models failed: {e2}")
                raise
    
    def _load_prompt(self, prompt_type: str) -> str:
        """Load prompt template from file"""
        prompt_file = self.config.get('prompts', {}).get(prompt_type, f"prompts/{prompt_type}.txt")
        
        try:
            with open(prompt_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file {prompt_file} not found, using default")
            return self._get_default_prompt(prompt_type)
    
    def _get_default_prompt(self, prompt_type: str) -> str:
        """Default prompts for different extraction types"""
        prompts = {
            'insight_extraction': """
You are an expert content analyst. Extract key insights from the following content.

For each insight, provide:
- title: A concise title for the insight
- description: A detailed description of the insight
- confidence: A confidence score from 0.0 to 1.0

Format your response as JSON with an array of insights:
[
  {
    "title": "Insight Title",
    "description": "Detailed description...",
    "confidence": 0.8
  }
]
""",
            'sentiment_analysis': """
You are a sentiment analysis expert. Analyze the sentiment of the following content.

Provide:
- sentiment: positive, negative, or neutral
- description: Brief explanation of the sentiment
- confidence: Confidence score from 0.0 to 1.0
- score: Numeric score from -1.0 (very negative) to 1.0 (very positive)

Format as JSON:
{
  "sentiment": "positive",
  "description": "The content expresses optimism about...",
  "confidence": 0.8,
  "score": 0.7
}
""",
            'trend_analysis': """
You are a trend analysis expert. Analyze the trend for the given topic based on the insights.

Provide:
- description: Overview of the trend
- momentum: rising, stable, or declining
- confidence: Confidence score from 0.0 to 1.0
- timeframe: When this trend is occurring
- impact: Assessment of potential impact (low, moderate, high)

Format as JSON:
{
  "description": "This trend shows...",
  "momentum": "rising",
  "confidence": 0.7,
  "timeframe": "recent weeks",
  "impact": "moderate"
}
"""
        }
        
        return prompts.get(prompt_type, "Analyze the following content and provide insights.")
    
    def _parse_insights_response(self, response: str) -> List[Dict]:
        """Parse insights from Ollama response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback: create simple insight from response
        return [{
            'title': 'Extracted Insight',
            'description': response[:200] + '...' if len(response) > 200 else response,
            'confidence': 0.5
        }]
    
    def _parse_sentiment_response(self, response: str) -> Optional[Dict]:
        """Parse sentiment from Ollama response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return None
    
    def _parse_trend_response(self, response: str) -> Optional[Dict]:
        """Parse trend analysis from Ollama response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return None
    
    def save_results(self, output_file: str = None):
        """Save extraction results to file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"data/extraction_{timestamp}.json"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'total_insights': len(self.extracted_insights),
            'total_trends': len(self.trend_analyses),
            'insights': [asdict(insight) for insight in self.extracted_insights],
            'trends': [asdict(trend) for trend in self.trend_analyses]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Extraction results saved to {output_file}")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PSAI_1 Content Extractor')
    parser.add_argument('--input', required=True, help='Input harvest data file')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    # Setup logging
    logger.add("logs/extract.log", rotation="1 week", retention="1 month")
    
    # Load harvest data
    with open(args.input, 'r') as f:
        harvest_data = json.load(f)
    
    items = harvest_data.get('items', [])
    if args.test:
        items = items[:3]  # Limit for testing
        logger.info(f"Test mode: processing {len(items)} items")
    
    # Initialize extractor
    extractor = ContentExtractor()
    
    # Extract insights
    insights = extractor.extract_insights_from_harvest(items)
    
    # Analyze trends
    trends = extractor.analyze_trends(insights)
    
    # Save results
    extractor.save_results(args.output)
    
    print(f"Extraction complete: {len(insights)} insights, {len(trends)} trends")
    logger.info(f"Extraction complete: {len(insights)} insights, {len(trends)} trends")

if __name__ == "__main__":
    main()
