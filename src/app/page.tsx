import { OceanBackground } from '@/components/landing/OceanBackground';
import { Hero } from '@/components/landing/Hero';
import { TrustStrip } from '@/components/landing/TrustStrip';
import { FeatureGrid } from '@/components/landing/FeatureGrid';
import { HowItWorks } from '@/components/landing/HowItWorks';
import { FAQ } from '@/components/landing/FAQ';
import { Footer } from '@/components/landing/Footer';

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
  );
}
