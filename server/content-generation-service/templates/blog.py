from .base import ContentTemplate

class BlogTemplate(ContentTemplate):
    """Blog content templates for personal or business blogs."""
    
    def get_homepage_template(self) -> str:
        return """
        # {{ business_name }} - {{ blog_tagline or "Insights & Perspectives" }}
        
        ## Hero Section
        
        ### Welcome to {{ business_name }}
        
        {{ tagline or "Exploring " + (blog_topic or "Our World") + " Through Fresh Perspectives" }}
        
        {{ welcome_message or "Create an engaging introduction that explains what this blog is about, who it's for, and what value readers will get. Highlight the blog's main topics, unique perspective, and why readers should subscribe or return for more content." }}
        
        ## Featured Articles
        
        Showcase 3-4 featured blog posts with:
        - Compelling title
        - Brief excerpt or summary (1-2 sentences)
        - Publication date
        - Featured image description
        - Topic/category
        - Read time estimate
        
        ## Blog Categories
        
        Create 4-6 main content categories with:
        - Category name
        - Brief description of what readers will find
        - Number of articles (approximate)
        - Example article titles
        
        ## About the Author
        
        Provide a brief introduction to the blog author(s):
        - Name and credentials
        - Area of expertise
        - Writing style and approach
        - Personal connection to the blog topics
        - Photo description (optional)
        
        ## Newsletter Signup
        
        Create a compelling newsletter signup section:
        - Value proposition (what subscribers get)
        - Publication frequency
        - Content preview
        - Privacy reassurance
        """
    
    def get_about_template(self) -> str:
        return """
        # About {{ business_name }}
        
        ## Our Story
        
        Create an engaging origin story for the blog that includes:
        - When and why the blog was started
        - The author's motivation and passion
        - How the blog has evolved over time
        - Mission and vision for the content
        
        ## Meet the Team
        
        Introduce the blog author(s) and contributors:
        - Name and role
        - Professional background and expertise
        - Personal interests related to the blog topics
        - Writing style and perspective
        - Photo description (optional)
        
        ## Our Approach
        
        Explain the blog's content philosophy:
        - Content creation process
        - Research methodology
        - Fact-checking and quality standards
        - Posting schedule and frequency
        - How topics are selected
        
        ## Our Community
        
        Describe the blog's audience and community:
        - Who the typical readers are
        - How readers engage with the content
        - Community features (comments, forums, etc.)
        - Testimonials from regular readers
        - Milestone achievements (views, subscribers, etc.)
        
        ## Editorial Policy
        
        Outline the blog's editorial standards:
        - Content guidelines
        - Sponsored content disclosure
        - Affiliate link policy
        - Privacy and data use
        - Comment moderation approach
        """
    
    def get_services_template(self) -> str:
        return """
        # Content & Services
        
        ## What We Offer
        
        Detail the various content types and services the blog provides:
        - Regular blog posts (frequency and topics)
        - Long-form articles and guides
        - Video content (if applicable)
        - Podcasts (if applicable)
        - Downloadable resources
        
        ## Premium Content
        
        If applicable, describe premium content offerings:
        - Membership benefits
        - Exclusive content types
        - Community access
        - Early access to new content
        - Direct Q&A opportunities
        
        ## Collaboration Opportunities
        
        Outline ways others can collaborate with the blog:
        - Guest posting guidelines
        - Interview opportunities
        - Expert contributions
        - Sponsorship options
        - Cross-promotion possibilities
        
        ## Coaching & Consulting
        
        If offered, detail coaching or consulting services:
        - Areas of expertise
        - Service formats (1:1, group, workshops)
        - Process and methodology
        - Expected outcomes
        - Pricing structure or range
        
        ## Products & Resources
        
        Describe any products or downloadable resources:
        - E-books and guides
        - Templates and worksheets
        - Online courses
        - Physical products
        - Software tools
        """
    
    def get_contact_template(self) -> str:
        return """
        # Contact {{ business_name }}
        
        ## Get In Touch
        
        We'd love to hear from you! Here's how you can reach us:
        
        ## Contact Information
        
        - Email: {{ email or "hello@yourblog.com" }}
        - Social Media: {{ social_handles or "Find us on Twitter, Instagram, and Facebook @yourbloghandle" }}
        - Response time: {{ response_time or "Within 2 business days" }}
        
        ## Topic Suggestions
        
        Have an idea for a blog post you'd like us to cover? We welcome your suggestions!
        
        When suggesting a topic, please include:
        - The main topic or question
        - Why this would be valuable to our audience
        - Any specific angles you're interested in
        - Relevant resources or references (optional)
        
        ## Feedback & Corrections
        
        We strive for accuracy and quality in all our content. If you've spotted an error or have feedback:
        - Specify the article name and issue
        - Provide the correct information (with sources if possible)
        - Let us know if you'd like to be credited for the correction
        
        ## Contact Form
        
        Use our contact form with these fields:
        - Name (required)
        - Email (required)
        - Subject (required)
        - Message (required)
        - Reason for contact (dropdown)
        - How you discovered our blog
        
        ## Media Inquiries
        
        For interviews, quotes, or other media opportunities:
        - Media outlet name
        - Nature of the request
        - Deadline
        - Intended publication date
        - Interview format preference
        """
    
    def get_industry(self) -> str:
        return "blog"