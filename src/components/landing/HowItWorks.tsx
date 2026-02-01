const steps = [
  {
    number: 1,
    title: 'Ask your question',
    description: 'Type anything about certifications, dive sites, or trip planning. No signup required.',
  },
  {
    number: 2,
    title: 'Get grounded answers',
    description: 'Receive accurate information with citations from official certification guides and dive site data.',
  },
  {
    number: 3,
    title: 'Make informed decisions',
    description: 'Use the guidance to plan your next dive trip or certification with confidence.',
  },
];

export const HowItWorks = () => {
  return (
    <section className="py-16 md:py-24 bg-white/40 backdrop-blur-sm">
      <div className="container mx-auto px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How it works
            </h2>
            <p className="text-lg text-gray-600">
              Get started in three simple steps
            </p>
          </div>

          {/* Desktop: Horizontal timeline */}
          <div className="hidden md:block relative">
            {/* Timeline line */}
            <div className="absolute top-7 left-[10%] right-[10%] h-0.5 bg-gradient-to-r from-primary-200 via-primary-400 to-primary-200" />

            <div className="grid grid-cols-3 gap-8 relative">
              {steps.map((step) => (
                <div key={step.number} className="text-center">
                  <div className="flex justify-center mb-6">
                    <div className="relative">
                      <div className="absolute inset-0 bg-primary-200 rounded-full scale-150 blur-xl opacity-50" />
                      <div className="relative w-14 h-14 bg-primary text-white rounded-full font-bold text-2xl flex items-center justify-center shadow-lg">
                        {step.number}
                      </div>
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">{step.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{step.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Mobile: Vertical timeline */}
          <div className="md:hidden space-y-8">
            {steps.map((step, index) => (
              <div key={step.number} className="flex gap-6">
                <div className="flex flex-col items-center">
                  <div className="relative">
                    <div className="absolute inset-0 bg-primary-200 rounded-full scale-150 blur-xl opacity-50" />
                    <div className="relative w-12 h-12 bg-primary text-white rounded-full font-bold text-xl flex items-center justify-center shadow-lg">
                      {step.number}
                    </div>
                  </div>
                  {index < steps.length - 1 && (
                    <div className="w-0.5 h-full bg-gradient-to-b from-primary-400 to-primary-200 mt-4" />
                  )}
                </div>
                <div className="flex-1 pb-8">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{step.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
