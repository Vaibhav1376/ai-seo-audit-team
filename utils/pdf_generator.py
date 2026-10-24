"""
Enhanced PDF generation with branding support and SEO Scorecard
"""
from fpdf import FPDF
import tempfile
import os
from datetime import datetime


class BrandedPDF(FPDF):
    """Custom PDF with branding, better formatting, and Scorecard support"""
    
    def __init__(self, brand_name="AI SEO Audit Pro", brand_tagline="", **kwargs):
        super().__init__(**kwargs)
        self.brand_name = brand_name
        self.brand_tagline = brand_tagline
        
    def header(self):
        """Add branded header"""
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 102, 204)
        self.cell(0, 10, self.brand_name, ln=True, align='C')
        
        if self.brand_tagline:
            self.set_font('Helvetica', 'I', 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, self.brand_tagline, ln=True, align='C')
        
        self.ln(5)
        
    def footer(self):
        """Add page footer"""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%B %d, %Y")}', align='C')
    
    def draw_scorecard(self, scores):
        """Draws a professional Scorecard Table at the top of the report"""
        if not scores:
            return

        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, "SEO Audit Scorecard", ln=True)
        self.ln(2)

        # Table Header
        self.set_fill_color(240, 242, 246)  # Soft UI Gray
        self.set_font('Helvetica', 'B', 11)
        self.cell(60, 10, "Metric", border=1, align='C', fill=True)
        self.cell(40, 10, "Score", border=1, ln=True, align='C', fill=True)

        # Table Content - Fixed metric names to match actual keys
        metrics = [
            ("Overall Health Score", scores.get('overall_score', 0)),
            ("On-Page Optimization", scores.get('onpage_score', 0)),
            ("Technical SEO Health", scores.get('technical_score', 0)),
            ("Content Quality & Depth", scores.get('content_score', 0))
        ]

        self.set_font('Helvetica', '', 11)
        for metric, value in metrics:
            self.set_text_color(0, 0, 0)
            self.cell(60, 10, f" {metric}", border=1)
            
            # Dynamic Color Coding for Scores
            if value >= 80:
                self.set_text_color(0, 128, 0)  # Green
            elif value >= 50:
                self.set_text_color(255, 140, 0)  # Dark Orange
            else:
                self.set_text_color(200, 0, 0)  # Red
                
            self.cell(40, 10, f"{value}/100", border=1, ln=True, align='C')
        
        self.set_text_color(0, 0, 0)  # Reset to black
        self.ln(10)

    def chapter_title(self, title):
        """Add formatted chapter title"""
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 102, 204)
        self.cell(0, 10, title, ln=True)
        self.ln(2)
        
    def chapter_body(self, body):
        """Add chapter body text"""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, body)
        self.ln()


def generate_pdf(markdown_text, brand_name="AI SEO Audit Pro", brand_tagline="Powered by Advanced AI Analysis", scores=None):
    """
    Generate PDF from markdown report with branding and optional scorecard.
    Main function used by the application.
    
    Args:
        markdown_text: Markdown formatted text
        brand_name: Brand name for header
        brand_tagline: Tagline for header
        scores: Dictionary with score data (overall_score, technical_score, etc.)
    
    Returns:
        PDF bytes or None on error
    """
    return markdown_to_pdf(markdown_text, brand_name, brand_tagline, scores)


def markdown_to_pdf(markdown_text, brand_name="AI SEO Audit Pro", brand_tagline="Powered by Advanced AI Analysis", scores=None):
    """
    Convert markdown report to branded PDF with an optional Scorecard.
    
    Args:
        markdown_text: Markdown formatted text
        brand_name: Brand name for header
        brand_tagline: Tagline for header
        scores: Dictionary with score data
    
    Returns:
        PDF bytes or None on error
    """
    try:
        pdf = BrandedPDF(brand_name=brand_name, brand_tagline=brand_tagline)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # 1. DRAW SCORECARD FIRST (if provided)
        if scores:
            pdf.draw_scorecard(scores)
        
        # 2. PROCESS MARKDOWN CONTENT
        lines = markdown_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                pdf.ln(2)
                continue
            
            # Detect headers
            if line.startswith('# '):
                # H1 - Main title
                pdf.set_font('Helvetica', 'B', 18)
                pdf.set_text_color(0, 51, 102)  # Darker Navy
                clean_line = line.replace('# ', '').strip()
                pdf.multi_cell(0, 10, clean_line)
                pdf.ln(3)
                
            elif line.startswith('## '):
                # H2 - Section
                pdf.ln(3)
                pdf.chapter_title(line.replace('## ', '').strip())
                
            elif line.startswith('### '):
                # H3 - Subsection
                pdf.set_font('Helvetica', 'B', 11)
                pdf.set_text_color(50, 50, 50)
                clean_line = line.replace('### ', '').strip()
                pdf.multi_cell(0, 6, clean_line)
                pdf.ln(1)
                
            elif line.startswith('- ') or line.startswith('* '):
                # Bullet point
                pdf.set_font('Helvetica', '', 10)
                pdf.set_text_color(0, 0, 0)
                # Use standard bullet char for Latin-1 compatibility
                clean_line = '  * ' + line[2:].replace('**', '').replace('*', '').strip()
                try:
                    clean_line = clean_line.encode('latin-1', errors='replace').decode('latin-1')
                    pdf.multi_cell(0, 5, clean_line)
                except Exception:
                    # Skip lines that can't be encoded
                    pass
                    
            elif line.startswith('---'):
                # Horizontal line
                pdf.ln(2)
                pdf.set_draw_color(200, 200, 200)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(2)
                
            else:
                # Regular text - clean markdown formatting
                pdf.set_font('Helvetica', '', 10)
                pdf.set_text_color(0, 0, 0)
                clean_line = line.replace('**', '').replace('*', '').replace('`', '')
                try:
                    clean_line = clean_line.encode('latin-1', errors='replace').decode('latin-1')
                    pdf.multi_cell(0, 5, clean_line)
                except Exception:
                    # Skip lines that can't be encoded
                    pass
        
        # 3. GENERATE PDF BYTES
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            pdf.output(tmp.name)
            tmp_path = tmp.name
        
        # Read the generated PDF
        with open(tmp_path, 'rb') as f:
            pdf_bytes = f.read()
        
        # Clean up temp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass  # Ignore cleanup errors
            
        return pdf_bytes
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        return None