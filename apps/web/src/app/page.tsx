import { OceanBackground } from '@/features/landing/components/OceanBackground'
import { Hero } from '@/features/landing/components/Hero'
import { TrustStrip } from '@/features/landing/components/TrustStrip'
import { FeatureGrid } from '@/features/landing/components/FeatureGrid'
import { HowItWorks } from '@/features/landing/components/HowItWorks'
import { FAQ } from '@/features/landing/components/FAQ'
import { Footer } from '@/features/landing/components/Footer'

export default function Home() {
  return (
    <main className="relative min-h-screen">
      <OceanBackground />
      <Hero />
      <TrustStrip />
      <FeatureGrid />
      <HowItWorks />
      <div id="faq">
        <FAQ />
      </div>
      <Footer />
    </main>
  )
}
