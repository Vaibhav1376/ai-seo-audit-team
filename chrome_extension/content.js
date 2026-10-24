// Content script runs on all pages
// Can extract page data if needed

function extractPageData() {
  return {
    title: document.title,
    metaDescription: document.querySelector('meta[name="description"]')?.content || '',
    h1: document.querySelector('h1')?.textContent || '',
    wordCount: document.body.innerText.split(/\s+/).length,
    hasViewport: !!document.querySelector('meta[name="viewport"]'),
    imageCount: document.querySelectorAll('img').length,
    linkCount: document.querySelectorAll('a').length
  };
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractData') {
    sendResponse(extractPageData());
  }
});
