from .base import ContentTemplate

class PortfolioTemplate(ContentTemplate):
    """Portfolio content templates for professionals and creatives."""
    
    def get_homepage_template(self) -> str:
        return """
        # {{ business_name }} - {{ profession or "Professional Portfolio" }}
        
        ## Hero Section
        
        ### {{ tagline or "Creating Excellence in " + (profession or "My Field") }}
        
        {{ welcome_message or "Create a compelling introduction that highlights the professional's expertise, unique approach, and value proposition. This should immediately communicate their specialty, experience level, and the problems they solve for clients." }}
        
        ## Expertise Areas
        
        Detail 3-4 core expertise areas with:
        - Area name/specialty
        - Brief description of capabilities
        - Why the professional excels in this area
        - Relevant accomplishments or approach
        
        ## Featured Projects
        
        Showcase 3-4 standout projects or works with:
        - Project name
        - Client (if applicable)
        - Brief description of the project
        - Challenge that was addressed
        - Solution provided
        - Outcomes or results
        
        ## Professional Approach
        
        Describe the professional's unique approach or methodology:
        - Work philosophy
        - Process highlights
        - Collaborative style
        - What makes their approach unique
        
        ## Testimonials
        
        Create 2-3 realistic client testimonials:
        - Client name and position
        - Project they collaborated on
        - Specific positive feedback about results
        - Why they would recommend the professional
        """
    
    def get_about_template(self) -> str:
        return """
        # About {{ name or business_name }}
        
        ## Professional Background
        
        Create a compelling professional biography that includes:
        - Career journey and progression
        - Key educational credentials
        - Professional philosophy
        - Areas of expertise development
        - Significant career milestones
        
        ## Skills & Expertise
        
        Detail professional skills in 3-4 categories:
        - Technical skills
        - Soft skills
        - Industry-specific competencies
        - Tools and technologies mastered
        
        ## Professional Philosophy
        
        Articulate the professional's approach to their work:
        - Core values in professional practice
        - Client relationship philosophy
        - Quality standards and commitment
        - Continuous improvement approach
        
        ## Awards & Recognition
        
        Highlight professional accomplishments:
        - Industry awards or nominations
        - Certifications and specialized training
        - Published works or speaking engagements
        - Professional memberships
        
        ## Personal Touch
        
        Add a personal element that humanizes the professional:
        - Outside interests related to professional work
        - Origin story or motivation for entering the field
        - Personal values that inform professional work
        """
    
    def get_services_template(self) -> str:
        return """
        # Services Offered
        
        ## Core Services
        
        Detail 4-6 primary services offered with:
        - Service name
        - Comprehensive description
        - Problems this service solves for clients
        - Process or methodology overview
        - Deliverables included
        - Typical timeframes
        
        ## Service Packages
        
        Create 3 service tiers or packages:
        - Package name
        - Services included
        - Ideal client for this package
        - Key benefits
        - Starting price range (if applicable)
        
        ## Custom Solutions
        
        Explain the process for custom work:
        - Types of custom projects accepted
        - Consultation process
        - Needs assessment approach
        - Proposal development
        - Implementation methodology
        
        ## Industries Served
        
        List 4-5 industries or client types served:
        - Industry name
        - Specific benefits for this client type
        - Relevant experience
        - Example results achieved
        
        ## Collaboration Process
        
        Outline the client journey from inquiry to delivery:
        - Initial consultation
        - Discovery phase
        - Proposal and agreement
        - Production/delivery process
        - Review and refinement
        - Completion and follow-up
        """
    
    def get_contact_template(self) -> str:
        return """
        # Contact {{ name or business_name }}
        
        ## Get In Touch
        
        I'd love to discuss your project needs! Here's how you can reach me:
        
        ## Contact Information
        
        - Email: {{ email or "hello@yourdomain.com" }}
        - Phone: {{ phone or "(555) 123-4567" }}
        - Best time to call: Weekdays 9am-5pm
        
        ## Schedule a Consultation
        
        I offer complimentary initial consultations to discuss your project needs and how I can help.
        
        The consultation process includes:
        - 30-minute discovery call
        - Discussion of your goals and needs
        - Initial ideas and approach
        - Next steps and proposal timeline
        
        ## Project Inquiry Form
        
        Use this form to provide details about your project:
        - Name (required)
        - Email (required)
        - Phone (optional)
        - Project type
        - Project description
        - Timeline
        - Budget range
        - How you heard about my services
        
        ## Location
        
        Based in {{ location or "City, State" }}
        Available for {{ availability or "remote collaboration worldwide" }}
        
        ## Response Time
        
        I typically respond to all inquiries within 1-2 business days.
        """
    
    def get_industry(self) -> str:
        return "portfolio"