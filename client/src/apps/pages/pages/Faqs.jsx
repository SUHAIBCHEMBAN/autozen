import { useState, useEffect } from 'react'
import PageLayout from '../components/PageLayout'
import FAQAccordion from '../components/FAQAccordion'
import { getPageByType, getFaqs } from '../services/pagesService'

const fallbackFaqs = [
  {
    id: 1,
    question: 'How do I ensure the part fits my car?',
    answer: 'Use the vehicle selector before adding to cart and verify the VIN/variant notes on the product page. Our team double-checks fitment post-purchase.',
  },
  {
    id: 2,
    question: 'When will my order ship?',
    answer: 'Most orders ship within 24-48 hours from the nearest warehouse. You’ll receive tracking updates by SMS and email.',
  },
  {
    id: 3,
    question: 'What if a part arrives damaged?',
    answer: 'Report within 48 hours with photos. We’ll arrange a pickup/replacement or issue a refund after inspection.',
  },
  {
    id: 4,
    question: 'Can I return electrical components?',
    answer: 'Unopened electricals are returnable. If DOA, we’ll replace after validating installation steps and packaging condition.',
  },
  {
    id: 5,
    question: 'Do you offer installation?',
    answer: 'Yes, for select cities we can connect you to vetted installers. Ask support to schedule after your order is placed.',
  },
]

function Faqs() {
  const [pageData, setPageData] = useState(null)
  const [faqs, setFaqs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        // Fetch the FAQ page data
        const pageResult = await getPageByType('faq')
        if (pageResult) {
          setPageData(pageResult)
        }

        // Fetch the actual FAQs
        const faqsResult = await getFaqs()
        if (faqsResult && faqsResult.length > 0) {
          setFaqs(faqsResult)
        } else {
          setFaqs(fallbackFaqs)
        }
      } catch (err) {
        setError('Failed to load FAQ data')
        console.error(err)
        // Use fallback data on error
        setFaqs(fallbackFaqs)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
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

  return (
    <PageLayout 
      title={pageData?.title || "FAQs"} 
      subtitle={pageData?.content || "Quick answers to the most common questions from AutoZen shoppers."} 
      badge={pageData?.page_type === 'faq' ? "FAQs" : "FAQ"}
    >
      <FAQAccordion faqs={faqs.length ? faqs : fallbackFaqs} />
      <div className="note-box">
        <strong>Still need help?</strong> Chat with us or email support@autozen.com with your order ID for priority
        assistance.
      </div>
    </PageLayout>
  )
}

export default Faqs