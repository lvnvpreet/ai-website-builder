from typing import Dict, Optional, List
import logging
from .base import ContentTemplate
from .ecommerce import EcommerceTemplate
from .portfolio import PortfolioTemplate
from .blog import BlogTemplate  # Add this import

logger = logging.getLogger("content_generation.templates")

# Add more template classes as they are created
_TEMPLATES = {
    "ecommerce": EcommerceTemplate(),
    "portfolio": PortfolioTemplate(),
    "blog": BlogTemplate(),  # Add this line
    # Add more here
}

def get_template(industry: str) -> ContentTemplate:
    """Get the appropriate template for the industry."""
    industry = industry.lower()
    
    if industry in _TEMPLATES:
        return _TEMPLATES[industry]
    
    # Try to find a close match
    for template_industry, template in _TEMPLATES.items():
        if template_industry in industry or industry in template_industry:
            logger.info(f"Using {template_industry} template for {industry} industry")
            return template
    
    # Default to portfolio as it's more generic
    logger.warning(f"No template found for industry '{industry}', using portfolio template")
    return _TEMPLATES["portfolio"]

def get_available_industries() -> List[str]:
    """Get a list of available industry templates."""
    return list(_TEMPLATES.keys())