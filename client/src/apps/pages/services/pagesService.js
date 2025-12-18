const BASE_URL = '/api/pages'

// Cache for pages
let pagesCache = {}
let pagesCacheTime = {}
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

async function fetchJson(path) {
  console.log('Fetching:', path);
  const res = await fetch(path, { headers: { 'Content-Type': 'application/json' } })
  if (!res.ok) {
    console.error('Response status:', res.status);
    console.error('Response headers:', [...res.headers.entries()]);
    const text = await res.text();
    console.error('Response body:', text.substring(0, 200));
    throw new Error(`Request failed: ${res.status}`)
  }
  return res.json()
}

export async function getPageByType(type) {
  const now = Date.now()
  const cacheKey = `page_${type}`
  
  // Return cached data if it's still valid
  if (pagesCache[cacheKey] && (now - pagesCacheTime[cacheKey]) < CACHE_DURATION) {
    return pagesCache[cacheKey]
  }
  
  try {
    const data = await fetchJson(`${BASE_URL}/pages/type/${type}/`)
    // Cache the result
    pagesCache[cacheKey] = data
    pagesCacheTime[cacheKey] = now
    return data
  } catch (error) {
    console.error('Failed to fetch page', error)
    // Clear cache on error
    delete pagesCache[cacheKey]
    delete pagesCacheTime[cacheKey]
    return null
  }
}

export async function getFaqs() {
  const now = Date.now()
  const cacheKey = 'faqs'
  
  // Return cached data if it's still valid
  if (pagesCache[cacheKey] && (now - pagesCacheTime[cacheKey]) < CACHE_DURATION) {
    return pagesCache[cacheKey]
  }
  
  try {
    const data = await fetchJson(`${BASE_URL}/faqs/`)
    // Cache the result
    pagesCache[cacheKey] = Array.isArray(data?.faqs) ? data.faqs : []
    pagesCacheTime[cacheKey] = now
    return pagesCache[cacheKey]
  } catch (error) {
    console.error('Failed to fetch FAQs', error)
    // Clear cache on error
    delete pagesCache[cacheKey]
    delete pagesCacheTime[cacheKey]
    return []
  }
}

export async function getAllPages() {
  const now = Date.now()
  const cacheKey = 'all_pages'
  
  // Return cached data if it's still valid
  if (pagesCache[cacheKey] && (now - pagesCacheTime[cacheKey]) < CACHE_DURATION) {
    return pagesCache[cacheKey]
  }
  
  try {
    const data = await fetchJson(`${BASE_URL}/pages/`)
    // Cache the result
    pagesCache[cacheKey] = Array.isArray(data?.pages) ? data.pages : []
    pagesCacheTime[cacheKey] = now
    return pagesCache[cacheKey]
  } catch (error) {
    console.error('Failed to fetch pages', error)
    // Clear cache on error
    delete pagesCache[cacheKey]
    delete pagesCacheTime[cacheKey]
    return []
  }
}

// Helper function to parse page content
export function parsePageContent(content) {
  try {
    return JSON.parse(content);
  } catch (e) {
    // If parsing fails, treat as plain text
    return content;
  }
}