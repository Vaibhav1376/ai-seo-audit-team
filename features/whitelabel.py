import os
import json
from typing import Dict

class WhiteLabelConfig:
    def __init__(self, config_path="whitelabel_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load white-label configuration"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Default config
        return {
            "brand_name": "AI SEO Audit Pro",
            "tagline": "Powered by Advanced AI Analysis",
            "logo_path": None,
            "primary_color": "#0066CC",
            "secondary_color": "#00CC66",
            "accent_color": "#FF6600",
            "font_family": "Inter",
            "company_name": "",
            "website": "",
            "email": "",
            "phone": "",
            "custom_footer": "",
            "show_powered_by": True
        }
    
    def save_config(self, config: Dict):
        """Save white-label configuration"""
        self.config.update(config)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_streamlit_theme(self) -> str:
        """Generate Streamlit theme config"""
        return f"""
[theme]
primaryColor="{self.config['primary_color']}"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="{self.config['font_family']}"
"""
    
    def save_streamlit_theme(self):
        """Save theme to .streamlit/config.toml"""
        os.makedirs(".streamlit", exist_ok=True)
        
        with open(".streamlit/config.toml", 'w') as f:
            f.write(self.get_streamlit_theme())
    
    def get_pdf_config(self) -> Dict:
        """Get config for PDF branding"""
        return {
            "brand_name": self.config['brand_name'],
            "tagline": self.config['tagline'],
            "logo_path": self.config.get('logo_path'),
            "primary_color": self.config['primary_color'],
            "footer_text": self.config.get('custom_footer', 
                f"{self.config['brand_name']} | {self.config.get('website', '')}")
        }

def apply_whitelabel_styling(config: Dict) -> str:
    """Generate custom CSS for Streamlit"""
    
    css = f"""
    <style>
    /* Custom branding */
    .main .block-container {{
        max-width: 1200px;
    }}
    
    /* Primary color overrides */
    .stButton>button[kind="primary"] {{
        background-color: {config['primary_color']};
        border-color: {config['primary_color']};
    }}
    
    .stButton>button[kind="primary"]:hover {{
        background-color: {config['secondary_color']};
        border-color: {config['secondary_color']};
    }}
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {{
        color: {config['primary_color']};
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {config['primary_color']};
        font-family: {config.get('font_family', 'Inter')}, sans-serif;
    }}
    
    /* Custom footer */
    .custom-footer {{
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        padding: 10px;
        text-align: center;
        font-size: 12px;
        border-top: 1px solid #ddd;
    }}
    </style>
    """
    
    return css
