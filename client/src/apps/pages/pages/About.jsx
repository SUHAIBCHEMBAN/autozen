import { useState, useEffect } from 'react'
import PageLayout from '../components/PageLayout'
import InfoCard from '../components/InfoCard'
import { getPageByType, parsePageContent } from '../services/pagesService'

function About() {
  const [pageData, setPageData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchPageData = async () => {
      try {
        setLoading(true)
        const data = await getPageByType('about')
        if (data) {
          setPageData(data)
        } else {
          setError('Page not found')
        }
      } catch (err) {
        setError('Failed to load page data')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchPageData()
  }, [])

  if (loading) {
    return (
      <PageLayout title="Loading..." subtitle="">
        <div>Loading...</div>
      </PageLayout>
    )
  }

  if (error) {
    return (
      <PageLayout title="Error" subtitle="">
        <div>{error}</div>
      </PageLayout>
    )
  }

  if (!pageData) {
    return (
      <PageLayout title="Not Found" subtitle="">
        <div>Page not found</div>
      </PageLayout>
    )
  }

  // Parse the content if it's JSON, otherwise use as plain text
  const content = parsePageContent(pageData.content)
  
  // Extract structured data if content is JSON, otherwise use fallbacks
  const highlights = content.highlights || [
    { label: '15+ Warehouses', body: 'Fast delivery across major cities with optimized routes.' },
    { label: '3,500+ SKUs', body: 'Curated accessories and parts from trusted OEM/ODM partners.' },
    { label: '24/7 Support', body: 'Friendly experts for fitment, installation, and post-purchase help.' },
  ]

  const values = content.values || [
    'Quality-first sourcing with transparent specs and warranties.',
    'Fitment assurance tailored to your vehicle model and variant.',
    'Hassle-free returns and proactive order tracking updates.',
  ]

  return (
    <PageLayout
      title={pageData.title}
      subtitle={content.subtitle || "We're building the most reliable destination for aftermarket vehicle parts and accessories in India."}
      badge={content.badge || "About"}
    >
      <div className="grid two">
        <div className="stack">
          <h3 className="section-title">Our story</h3>
          <p className="muted">
            {content.story || "AutoZen was started by enthusiasts who wanted better access to dependable parts, transparent pricing, and fast delivery. Today we partner with vetted suppliers and certified installers to keep your vehicle running and looking its best."}
          </p>
          <p className="muted">
            {content.mission || "From daily commuters to weekend builds, we obsess over compatibility, safety, and service so you can shop confidently and get back on the road faster."}
          </p>
        </div>
        <div className="highlight-grid">
          {highlights.map((item, index) => (
            <div key={index} className="highlight-card">
              <span className="pill pill--soft">{item.label}</span>
              <p>{item.body}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid three">
        <InfoCard title="What we do" items={values} />
        <InfoCard
          title="Coverage"
          body={content.coverage || "Interior, exterior, lighting, electronics, care & styling, and core auto parts—all under one roof."}
        />
        <InfoCard
          title="Promise"
          body={content.promise || "Authentic parts, responsive support, and delivery timelines you can rely on."}
          highlight={content.highlight || "Trusted"}
        />
      </div>
    </PageLayout>
  )
}

export default About