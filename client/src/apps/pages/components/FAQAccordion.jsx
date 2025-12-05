import { useState } from 'react'

function FAQAccordion({ faqs }) {
  const [openId, setOpenId] = useState(faqs?.[0]?.id ?? null)

  return (
    <div className="faq">
      {faqs.map((faq) => {
        const isOpen = faq.id === openId
        return (
          <div key={faq.id} className={`faq__item ${isOpen ? 'is-open' : ''}`}>
            <button className="faq__question" onClick={() => setOpenId(isOpen ? null : faq.id)}>
              <span>{faq.question}</span>
              <span className="faq__icon">{isOpen ? '−' : '+'}</span>
            </button>
            {isOpen && <p className="faq__answer">{faq.answer}</p>}
          </div>
        )
      })}
    </div>
  )
}

export default FAQAccordion

