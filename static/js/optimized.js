// Optimized SafeHouse frontend - performance and UX improvements

// Request deduplication
const pendingRequests = new Map();

async function fetchUnique(url, options = {}) {
  const key = `${url}:${JSON.stringify(options)}`;
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key);
  }
  const promise = fetch(url, options);
  pendingRequests.set(key, promise);
  try {
    return await promise;
  } finally {
    pendingRequests.delete(key);
  }
}

// Response caching
const responseCache = new Map();
const CACHE_TTL = 300000; // 5 minutes

function getCached(key) {
  const entry = responseCache.get(key);
  if (entry && Date.now() - entry.time < CACHE_TTL) {
    return entry.data;
  }
  responseCache.delete(key);
  return null;
}

function setCached(key, data) {
  responseCache.set(key, { data, time: Date.now() });
}

// Lazy loading for images
function lazyLoadImages() {
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          observer.unobserve(img);
        }
      });
    });
    document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
  }
}

// Batch URL analysis
async function batchAnalyze(urls) {
  const response = await fetch('/api/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ urls })
  });
  return response.json();
}

// Export results
async function exportResults(format) {
  window.location.href = `/api/export/${format}`;
}

// Virtual scrolling for large lists
function createVirtualList(container, items, itemHeight, renderItem) {
  const visibleCount = Math.ceil(container.clientHeight / itemHeight);
  let scrollTop = 0;

  container.addEventListener('scroll', () => {
    scrollTop = container.scrollTop;
    render();
  });

  function render() {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const visibleItems = items.slice(startIndex, startIndex + visibleCount + 1);
    container.innerHTML = visibleItems.map(renderItem).join('');
  }

  render();
}

// Debounce for search
function debounce(fn, delay) {
  let timeoutId;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

// Initialize optimizations
document.addEventListener('DOMContentLoaded', () => {
  lazyLoadImages();
  // Setup other optimizations as needed
});
