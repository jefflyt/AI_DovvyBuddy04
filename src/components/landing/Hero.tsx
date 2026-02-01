'use client';

import Link from 'next/link';
import { ArrowRight, AlertCircle } from 'lucide-react';
import { ChatPreview } from './ChatPreview';

export const Hero = () => {
  const scrollToPreview = () => {
    const preview = document.getElementById('chat-preview');
    preview?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  return (
    <section className="pt-20 pb-16 md:pt-32 md:pb-24">
      <div className="container mx-auto px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* Left: Copy + CTAs */}
            <div>
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-[1.1]">
                Your AI Diving Companion
              </h1>
              <p className="text-xl md:text-2xl text-gray-700 mb-8 max-w-xl leading-relaxed">
                Get judgment-free guidance on certifications, dive sites, and trip planning—backed by official sources.
              </p>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <Link
                  href="/chat"
                  className="inline-flex items-center justify-center gap-2 bg-primary hover:bg-primary-600 text-white font-semibold px-8 py-4 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5"
                >
                  Start Chatting
                  <ArrowRight className="w-5 h-5" />
                </Link>
                <button
                  onClick={scrollToPreview}
                  className="inline-flex items-center justify-center gap-2 bg-white hover:bg-gray-50 text-gray-900 font-semibold px-8 py-4 rounded-lg border-2 border-gray-200 hover:border-primary-300 transition-all duration-200"
                >
                  Try an example
                </button>
              </div>

              {/* Safety note */}
              <div className="flex gap-3 items-start text-sm text-gray-600 max-w-xl">
                <AlertCircle className="w-5 h-5 flex-shrink-0 text-gray-400 mt-0.5" />
                <p>
                  DovvyBuddy provides research and guidance. Always consult certified instructors and medical professionals before diving.
                </p>
              </div>
            </div>

            {/* Right: ChatPreview */}
            <div id="chat-preview">
              <ChatPreview />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
