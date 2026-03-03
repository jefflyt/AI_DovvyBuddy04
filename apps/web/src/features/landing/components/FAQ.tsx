'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

const faqs = [
  {
    question: 'How do you ensure the information is accurate?',
    answer:
      'All answers cite official certification standards (PADI, SSI, NAUI) and verified dive site data. When we reference specific requirements or conditions, we provide the source. However, standards can change—always verify with your instructor or dive operator.',
  },
  {
    question: 'Can I use this to plan a dive trip without an instructor?',
    answer:
      'DovvyBuddy helps you research destinations, understand certification requirements, and ask questions. It is not a substitute for professional instruction, medical clearance, or dive planning with a certified divemaster. Always dive with proper training and supervision.',
  },
  {
    question: 'What if I have a medical concern about diving?',
    answer:
      "We provide general information about medical requirements (e.g., when a doctor's clearance is needed), but we cannot give medical advice. Always consult a physician trained in dive medicine before diving if you have any health concerns.",
  },
  {
    question: 'Do you recommend specific dive operators or shops?',
    answer:
      'We provide information about destinations and what to look for in a reputable operator (certifications, safety record, reviews). We do not endorse specific businesses. Always research operators independently and check recent reviews.',
  },
  {
    question: 'Is my conversation data stored or shared?',
    answer:
      'Conversations are stored to improve the service and provide context in ongoing chats. We do not sell your data. See our Privacy Policy for details on data handling and your rights.',
  },
]

export const FAQ = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  const toggle = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Frequently asked questions
            </h2>
            <p className="text-lg text-gray-600">
              Common questions about how DovvyBuddy works and what it can help
              with
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="bg-white/60 backdrop-blur-sm rounded-xl border border-gray-200/50 overflow-hidden"
              >
                <button
                  onClick={() => toggle(index)}
                  className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-white/40 transition-colors"
                  aria-expanded={openIndex === index}
                >
                  <span className="font-semibold text-gray-900 pr-8">
                    {faq.question}
                  </span>
                  <ChevronDown
                    className={`w-5 h-5 text-gray-600 flex-shrink-0 transition-transform duration-200 ${
                      openIndex === index ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                {openIndex === index && (
                  <div className="px-6 pb-4">
                    <p className="text-gray-700 leading-relaxed">
                      {faq.answer}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
