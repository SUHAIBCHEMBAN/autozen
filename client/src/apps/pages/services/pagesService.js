const BASE_URL = '/api/pages'

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
  try {
    const data = await fetchJson(`${BASE_URL}/pages/type/${type}/`)
    return data
  } catch (error) {
    console.error('Failed to fetch page', error)
    return null
  }
}

export async function getFaqs() {
  try {
    const data = await fetchJson(`${BASE_URL}/faqs/`)
    return Array.isArray(data?.faqs) ? data.faqs : []
  } catch (error) {
    console.error('Failed to fetch FAQs', error)
    return []
  }
}

export async function getAllPages() {
  try {
    const data = await fetchJson(`${BASE_URL}/pages/`)
    return Array.isArray(data?.pages) ? data.pages : []
  } catch (error) {
    console.error('Failed to fetch pages', error)
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

