import { useState, useEffect } from 'react'
import PageLayout from '../components/PageLayout'
import InfoCard from '../components/InfoCard'
import { getPageByType, parsePageContent } from '../services/pagesService'

const fallbackCommitments = [
  'Authentic products with clear specifications, warranties, and return eligibility.',
  'Transparent pricing inclusive of taxes; shipping shown before checkout.',
  'Service levels for dispatch, tracking, and resolution timelines.',
]

const fallbackResponsibilities = [
  'Provide accurate vehicle details for fitment assurance.',
  'Use products as intended; follow installation and safety guidance.',
  'Respect intellectual property and avoid misuse of the platform.',
]

const fallbackLimitations = [
  'Liability limited to the order value; indirect or consequential losses are excluded.',
  'Warranty coverage depends on brand terms; misuse or improper installs are excluded.',
  'Platform availability may vary during maintenance and upgrades.',
]

function TermsConditions() {
  const [pageData, setPageData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchPageData = async () => {
      try {
        setLoading(true)
        const data = await getPageByType('terms')
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
  const commitments = content.commitments || fallbackCommitments
  const responsibilities = content.responsibilities || fallbackResponsibilities
  const limitations = content.limitations || fallbackLimitations

  return (
    <PageLayout
      title={pageData.title}
      subtitle={content.subtitle || "Our mutual commitments for a reliable, transparent shopping experience."}
      badge={content.badge || "Terms"}
    >
      <div className="grid three">
        <InfoCard title="Our commitments" items={commitments} />
        <InfoCard title="Your responsibilities" items={responsibilities} highlight={content.highlight || "Fitment ready"} />
        <InfoCard title="Limitations" items={limitations} />
      </div>

      <div className="note-box">
        <strong>Updates:</strong> {content.note || "Terms may change as we launch new services. We'll post revisions here with effective dates. Continued use implies acceptance."}
      </div>
    </PageLayout>
  )
}

export default TermsConditions