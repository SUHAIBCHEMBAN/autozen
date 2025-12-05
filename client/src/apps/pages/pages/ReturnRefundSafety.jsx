import { useState, useEffect } from 'react'
import PageLayout from '../components/PageLayout'
import InfoCard from '../components/InfoCard'
import { getPageByType, parsePageContent } from '../services/pagesService'

const fallbackReturnSteps = [
  'Initiate a request from your account within 7 days of delivery.',
  'Share clear photos and order ID for quality checks.',
  'Pack unused items with original tags, manuals, and accessories.',
  'Pickup arranged or drop-off guided based on your pincode.',
]

const fallbackRefundRules = [
  'Refunds processed to the original payment method after inspection.',
  'COD orders refunded via bank transfer or wallet credit.',
  'Electricals and bulbs are returnable only if unopened or DOA.',
  'Custom/painted parts are final sale unless damaged on arrival.',
]

const fallbackSafetyTips = [
  'Disconnect battery when installing electrical parts.',
  'Use torque specs for critical fasteners; avoid over-tightening.',
  'Test fit before painting or removing protective films.',
  'Seek professional installation for airbags, sensors, and wiring.',
]

function ReturnRefundSafety() {
  const [pageData, setPageData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchPageData = async () => {
      try {
        setLoading(true)
        const data = await getPageByType('refund')
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
  const returnSteps = content.returnSteps || fallbackReturnSteps
  const refundRules = content.refundRules || fallbackRefundRules
  const safetyTips = content.safetyTips || fallbackSafetyTips

  return (
    <PageLayout
      title={pageData.title}
      subtitle={content.subtitle || "Straightforward returns with safety-first installation guidance."}
      badge={content.badge || "Returns"}
    >
      <div className="grid three">
        <InfoCard title="Return steps" items={returnSteps} highlight={content.stepsHighlight || "7-day window"} />
        <InfoCard title="Refund policy" items={refundRules} />
        <InfoCard title="Safety tips" items={safetyTips} highlight={content.safetyHighlight || "Read before install"} />
      </div>

      <div className="note-box">
        <strong>{content.noteTitle || "Need help?"}</strong> {content.note || "If a part arrives damaged or doesn't fit, contact support within 48 hours for priority handling. Keep packaging until fitment is confirmed."}
      </div>
    </PageLayout>
  )
}

export default ReturnRefundSafety