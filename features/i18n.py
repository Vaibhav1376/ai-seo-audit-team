from typing import Dict

TRANSLATIONS = {
    "en": {
        "app_title": "AI-Powered SEO Audit Agent",
        "run_audit": "Run Audit",
        "overall_score": "Overall Score",
        "onpage_seo": "On-Page SEO",
        "technical_seo": "Technical SEO",
        "content_quality": "Content Quality",
        "mobile_score": "Mobile Score",
        "audit_report": "Audit Report",
        "download_report": "Download Report",
        "enter_url": "Enter website URL to audit",
        "audit_complete": "Audit completed successfully!",
        "audit_failed": "Audit failed",
        "critical_issues": "Critical Issues",
        "recommendations": "Recommendations"
    },
    "es": {
        "app_title": "Agente de Auditoría SEO con IA",
        "run_audit": "Ejecutar Auditoría",
        "overall_score": "Puntuación General",
        "onpage_seo": "SEO On-Page",
        "technical_seo": "SEO Técnico",
        "content_quality": "Calidad del Contenido",
        "mobile_score": "Puntuación Móvil",
        "audit_report": "Informe de Auditoría",
        "download_report": "Descargar Informe",
        "enter_url": "Ingrese URL del sitio web",
        "audit_complete": "¡Auditoría completada con éxito!",
        "audit_failed": "La auditoría falló",
        "critical_issues": "Problemas Críticos",
        "recommendations": "Recomendaciones"
    },
    "fr": {
        "app_title": "Agent d'Audit SEO Alimenté par IA",
        "run_audit": "Lancer l'Audit",
        "overall_score": "Score Global",
        "onpage_seo": "SEO On-Page",
        "technical_seo": "SEO Technique",
        "content_quality": "Qualité du Contenu",
        "mobile_score": "Score Mobile",
        "audit_report": "Rapport d'Audit",
        "download_report": "Télécharger le Rapport",
        "enter_url": "Entrez l'URL du site web",
        "audit_complete": "Audit terminé avec succès!",
        "audit_failed": "L'audit a échoué",
        "critical_issues": "Problèmes Critiques",
        "recommendations": "Recommandations"
    },
    "de": {
        "app_title": "KI-gestützter SEO-Audit-Agent",
        "run_audit": "Audit Starten",
        "overall_score": "Gesamtbewertung",
        "onpage_seo": "On-Page-SEO",
        "technical_seo": "Technisches SEO",
        "content_quality": "Inhaltsqualität",
        "mobile_score": "Mobile Bewertung",
        "audit_report": "Auditbericht",
        "download_report": "Bericht Herunterladen",
        "enter_url": "Website-URL eingeben",
        "audit_complete": "Audit erfolgreich abgeschlossen!",
        "audit_failed": "Audit fehlgeschlagen",
        "critical_issues": "Kritische Probleme",
        "recommendations": "Empfehlungen"
    },
    "hi": {
        "app_title": "AI-संचालित SEO ऑडिट एजेंट",
        "run_audit": "ऑडिट चलाएं",
        "overall_score": "समग्र स्कोर",
        "onpage_seo": "ऑन-पेज SEO",
        "technical_seo": "तकनीकी SEO",
        "content_quality": "सामग्री गुणवत्ता",
        "mobile_score": "मोबाइल स्कोर",
        "audit_report": "ऑडिट रिपोर्ट",
        "download_report": "रिपोर्ट डाउनलोड करें",
        "enter_url": "वेबसाइट URL दर्ज करें",
        "audit_complete": "ऑडिट सफलतापूर्वक पूर्ण हुआ!",
        "audit_failed": "ऑडिट विफल रहा",
        "critical_issues": "महत्वपूर्ण समस्याएं",
        "recommendations": "सिफारिशें"
    }
}

def get_text(key: str, language: str = "en") -> str:
    """Get translated text"""
    return TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(key, key)

def get_language_prompt_suffix(language: str) -> str:
    """Get prompt suffix for AI to generate in specific language"""
    
    language_names = {
        "en": "English",
        "es": "Spanish (Español)",
        "fr": "French (Français)",
        "de": "German (Deutsch)",
        "hi": "Hindi (हिंदी)"
    }
    
    lang_name = language_names.get(language, "English")
    
    if language == "en":
        return ""
    
    return f"\n\nIMPORTANT: Generate the entire report in {lang_name}. All text, headings, and recommendations must be in {lang_name}."
