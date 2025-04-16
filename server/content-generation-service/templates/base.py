from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import jinja2
import logging

class ContentTemplate(ABC):
    """Base class for content templates."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"content_generation.templates.{self.__class__.__name__}")
        self.jinja_env = jinja2.Environment(
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    @abstractmethod
    def get_homepage_template(self) -> str:
        """Get template for homepage."""
        pass
    
    @abstractmethod
    def get_about_template(self) -> str:
        """Get template for about page."""
        pass
    
    @abstractmethod
    def get_services_template(self) -> str:
        """Get template for services page."""
        pass
    
    @abstractmethod
    def get_contact_template(self) -> str:
        """Get template for contact page."""
        pass
    
    @abstractmethod
    def get_industry(self) -> str:
        """Get the industry this template is for."""
        pass
    
    def render_template(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a Jinja2 template with the given context."""
        try:
            template = self.jinja_env.from_string(template_str)
            return template.render(**context)
        except jinja2.exceptions.TemplateError as e:
            self.logger.error(f"Template rendering error: {str(e)}")
            return template_str  # Return the original template string if rendering fails