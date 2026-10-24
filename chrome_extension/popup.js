// Configuration
const API_URL = 'http://localhost:8501';  // Your Streamlit app URL

// On popup open
document.addEventListener('DOMContentLoaded', async () => {
  try {
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = tab.url;
    
    // Call your API
    const response = await fetch(`${API_URL}/api/quick-audit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    
    if (!response.ok) {
      throw new Error('API request failed');
    }
    
    const data = await response.json();
    
    // Display results
    displayResults(data);
    
  } catch (error) {
    showError('Failed to analyze page. Make sure the SEO Audit app is running.');
  }
});

function displayResults(data) {
  document.getElementById('loading').style.display = 'none';
  document.getElementById('results').style.display = 'block';
  
  const scores = data.scores || {};
  
  document.getElementById('overallScore').textContent = scores.overall_score || '--';
  document.getElementById('onpageScore').textContent = scores.onpage_score || '--';
  document.getElementById('technicalScore').textContent = scores.technical_score || '--';
  document.getElementById('contentScore').textContent = scores.content_score || '--';
  document.getElementById('mobileScore').textContent = scores.mobile_score || '--';
  
  // Handle full report button
  document.getElementById('fullReportBtn').addEventListener('click', () => {
    chrome.tabs.create({ url: `${API_URL}?url=${encodeURIComponent(data.url)}` });
  });
}

function showError(message) {
  document.getElementById('loading').style.display = 'none';
  document.getElementById('error').style.display = 'block';
  document.getElementById('error').textContent = message;
}
