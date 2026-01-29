'use client'

import { Hero, ValueProposition, HowItWorks, SocialProof, Footer } from '@/components/landing'
import { trackEvent } from '@/lib/analytics'

export default function Home() {
  const handleCtaClick = () => {
    trackEvent('cta_click', { location: 'hero' })
  }

  const features = [
    {
      icon: '🎓',
      title: 'Certification Navigator',
      description:
        'Understand PADI, SSI, and other certification pathways without judgment. Get clear answers about prerequisites, costs, and what to expect.',
    },
    {
      icon: '💪',
      title: 'Confidence Building',
      description:
        'Ask questions about fears, physical requirements, or gear without shame. We provide grounded, supportive guidance to help you make informed decisions.',
    },
    {
      icon: '🗺️',
      title: 'Trip Research',
      description:
        'Discover dive destinations and sites that match your skill level. Get insights on seasons, conditions, and what makes each location special.',
    },
  ]

  const steps = [
    {
      number: 1,
      title: 'Ask Your Question',
      description:
        'Type anything about certifications, dive sites, or trip planning. No question is too basic.',
    },
    {
      number: 2,
      title: 'Get Grounded Answers',
      description:
        'Receive accurate information based on official certification guides and real dive site data.',
    },
    {
      number: 3,
      title: 'Connect with Pros',
      description:
        'When you\'re ready, we can connect you with certified instructors and reputable dive shops.',
    },
  ]

  return (
    <main>
      <Hero
        headline="Your AI Diving Companion"
        subheadline="Get judgment-free guidance on certifications, dive sites, and trip planning — no pressure, just support."
        ctaText="Start Chatting"
        ctaLink="/chat"
        onCtaClick={handleCtaClick}
      />
      <ValueProposition features={features} />
      <HowItWorks steps={steps} />
      <SocialProof />
      <Footer />
    </main>
  )
}
