from .base import ContentTemplate

class EcommerceTemplate(ContentTemplate):
    """E-commerce content templates."""
    
    def get_homepage_template(self) -> str:
        return """
        # {{ business_name }} - Your Online Shopping Destination
        
        ## Hero Section
        
        ### Welcome to {{ business_name }}
        
        {{ tagline or "Quality Products, Delivered Fast" }}
        
        {{ welcome_message or "Create a compelling welcome message that highlights what makes this e-commerce store unique and why customers should shop here. Focus on unique selling points like product quality, selection range, delivery speed, or customer service excellence." }}
        
        ## Featured Products
        
        Create 3-4 featured products with:
        - Product name
        - Brief description (1-2 sentences)
        - Key benefit or feature
        - Pricing information
        
        ## Why Choose Us
        
        Describe 3-4 key advantages of shopping with {{ business_name }}:
        - Fast delivery
        - Quality products
        - Customer satisfaction
        - Any unique selling points mentioned in the business description
        
        ## Special Offers
        
        Create a compelling special offer section with:
        - Current promotion
        - Discount code if applicable
        - Limited time offer framing
        
        ## Customer Testimonials
        
        Create 2-3 realistic customer testimonials highlighting positive experiences with:
        - Customer name
        - Product purchased
        - Specific positive feedback
        - Star rating (if applicable)
        """
    
    def get_about_template(self) -> str:
        return """
        # About {{ business_name }}
        
        ## Our Story
        
        Create a compelling origin story for the e-commerce business that aligns with its values and mission. Include:
        - When and why the business started
        - The founder's motivation
        - The problem the business aims to solve
        - Growth journey to current state
        
        ## Our Mission
        
        Create a mission statement that captures the purpose of {{ business_name }}. The mission should address:
        - Value provided to customers
        - Business philosophy
        - Long-term vision
        
        ## Our Team
        
        Create 3-4 key team members with:
        - Name and position
        - Brief professional background
        - Special expertise related to the products
        - Personal connection to the business mission
        
        ## Our Commitment
        
        Describe the business's commitments to:
        - Product quality
        - Customer satisfaction
        - Ethical sourcing (if applicable)
        - Sustainability (if applicable)
        - Community involvement
        """
    
    def get_services_template(self) -> str:
        return """
        # Our Products & Services
        
        ## Product Categories
        
        Create 4-6 main product categories that {{ business_name }} offers. For each category:
        - Category name
        - Brief description
        - Types of products included
        - Key benefits or features
        
        ## Shopping Experience
        
        Describe the shopping experience with {{ business_name }}, including:
        - User-friendly website features
        - Mobile app capabilities (if applicable)
        - Product search and filtering options
        - Recommendation system
        
        ## Customer Support
        
        Detail the customer support services offered:
        - Support channels (email, phone, chat)
        - Hours of availability
        - Types of assistance provided
        - Return and exchange policy highlights
        
        ## Shipping & Delivery
        
        Explain the shipping and delivery process:
        - Delivery options and timeframes
        - Shipping providers used
        - Order tracking capabilities
        - International shipping information (if applicable)
        
        ## Special Services
        
        Highlight any special services that differentiate the business:
        - Gift wrapping
        - Personalization
        - Subscription options
        - Loyalty program
        """
    
    def get_contact_template(self) -> str:
        return """
        # Contact {{ business_name }}
        
        ## Get In Touch
        
        We'd love to hear from you! Here's how you can reach us:
        
        ## Customer Support
        
        - Email: support@{{ business_domain or "yourbusiness.com" }}
        - Phone: (555) 123-4567
        - Hours: Monday-Friday, 9am-5pm
        
        ## Returns & Exchanges
        
        For information about our returns and exchanges process:
        - Email: returns@{{ business_domain or "yourbusiness.com" }}
        - Phone: (555) 123-4568
        
        ## Visit Our Office
        
        {{ business_name }}
        123 E-Commerce Avenue
        Shopping District, ST 12345
        
        ## Connect With Us
        
        Follow us on social media for updates, sales, and more:
        - Facebook: {{ business_name }}
        - Instagram: @{{ business_name | lower | replace(" ", "") }}
        - Twitter: @{{ business_name | lower | replace(" ", "") }}
        
        ## Contact Form
        
        Use our contact form to send us a message directly:
        - Name (required)
        - Email (required)
        - Order Number (optional)
        - Message (required)
        - Preferred contact method
        """
    
    def get_industry(self) -> str:
        return "ecommerce"