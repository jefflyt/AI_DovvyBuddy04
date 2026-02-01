interface Step {
  number: number
  title: string
  description: string
}

interface HowItWorksProps {
  steps: Step[]
}

export default function HowItWorks({ steps }: HowItWorksProps) {
  return (
    <section className="py-20 relative">
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-primary-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Get started in three simple steps. No signup required.
            </p>
          </div>

          <div className="space-y-8 md:space-y-0 md:grid md:grid-cols-3 md:gap-8">
            {steps.map((step, index) => (
              <div key={index} className="relative group">
                <div className="bg-white/40 backdrop-blur-sm rounded-2xl p-8 shadow-sm border border-white/60 hover:shadow-md transition-all duration-300 hover:-translate-y-1">
                  <div className="flex items-center justify-center w-12 h-12 bg-accent text-accent-foreground rounded-full font-bold text-xl mb-4 shadow-sm group-hover:scale-110 transition-transform">
                    {step.number}
                  </div>
                  <h3 className="text-xl font-semibold text-primary-900 mb-3">
                    {step.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                </div>

                {/* Connector arrow (hidden on mobile, shown on desktop between steps) */}
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 text-primary-200">
                    <svg
                      className="w-8 h-8"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
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
