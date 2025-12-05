import { useState, useEffect } from 'react'
import PageLayout from '../components/PageLayout'
import InfoCard from '../components/InfoCard'
import { getPageByType, parsePageContent } from '../services/pagesService'

const fallbackPrivacyPoints = [
  'We collect only what’s needed to process orders, personalize recommendations, and improve the experience.',
  'Payment details are processed via PCI-compliant gateways; we never store raw card data.',
  'You can access, update, or delete your data anytime by contacting support.',
]

const fallbackDataUsage = [
  'Order fulfillment: addresses, contact numbers, and preferences.',
  'Personalization: recent searches, vehicle selections, and wishlist items.',
  'Security: fraud prevention, device/IP checks, and audit logs.',
]

const fallbackCommitments = [
  'Cookies limited to session continuity and analytics; opt-out options available.',
  'Data sharing only with logistics, payments, and vetted partners needed to deliver your order.',
  'Breach response with clear notifications and remediation steps.',
]

function PrivacyPolicy() {
  const [pageData, setPageData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchPageData = async () => {
      try {
        setLoading(true)
        const data = await getPageByType('privacy')
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
  const privacyPoints = content.privacyPoints || fallbackPrivacyPoints
  const dataUsage = content.dataUsage || fallbackDataUsage
  const commitments = content.commitments || fallbackCommitments

  return (
    <PageLayout
      title={pageData.title}
      subtitle={content.subtitle || "Your trust matters. We keep your data lean, encrypted in transit, and shared only when essential to serve you."}
      badge={content.badge || "Privacy"}
    >
      <div className="grid two">
        <InfoCard title="What we collect" items={privacyPoints} />
        <InfoCard title="How we use it" items={dataUsage} highlight={content.highlight || "Operational use only"} />
      </div>

      <div className="grid two">
        <InfoCard
          title="Your controls"
          items={content.controls || [
            'Download or delete your profile data on request.',
            'Manage marketing preferences from your account.',
            'Unsubscribe links in every campaign email.',
          ]}
        />
        <InfoCard title="Our commitments" items={commitments} />
      </div>

      <div className="note-box">
        <strong>{content.noteTitle || "Need changes?"}</strong> {content.note || "Reach us at support@autozen.com for data access, correction, or deletion requests. We respond within 72 hours."}
      </div>
    </PageLayout>
  )
}

export default PrivacyPolicy