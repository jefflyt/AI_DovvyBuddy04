import Image from 'next/image';

const features = [
    {
        image: '/assets/icons/ray.png',
        title: 'Dive Site Fit',
        description: 'Match your certification level and interests to destinations worldwide. Get specific guidance on seasons, conditions, and what to expect.',
        example: 'Example: "Where can I see whale sharks as an Advanced diver?"',
        size: 'large',
    },
    {
        image: '/assets/icons/turtle.png',
        title: 'Certification Navigator',
        description: 'Understand prerequisites, costs, and timelines for any certification path.',
        example: 'Example: "What\'s required for Rescue Diver?"',
        size: 'small',
    },
    {
        image: '/assets/icons/clownfish.png',
        title: 'Confidence Building',
        description: 'Ask questions about fears, physical requirements, or gear without judgment.',
        example: 'Example: "I\'m nervous about equalizing. What should I know?"',
        size: 'small',
    },
];

export const FeatureGrid = () => {
    return (
        <section className="py-16 md:py-24">
            <div className="container mx-auto px-4">
                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-12">
                        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                            Your diving questions, answered
                        </h2>
                        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                            From certifications to trip planning, get grounded guidance backed by official sources.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {features.map((feature, index) => {
                            const isLarge = feature.size === 'large';

                            return (
                                <div
                                    key={index}
                                    className={`bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-gray-200/50 hover:border-primary-200 hover:shadow-lg transition-all duration-300 ${isLarge ? 'md:col-span-2' : ''
                                        }`}
                                >
                                    <div className="flex items-start gap-6">
                                        {/* Animal Icon */}
                                        <div className="w-20 h-20 relative flex-shrink-0 -mt-2">
                                            <Image
                                                src={feature.image}
                                                alt={feature.title}
                                                fill
                                                className="object-contain drop-shadow-md"
                                            />
                                        </div>

                                        <div className="flex-1">
                                            <h3 className="text-xl font-bold text-gray-900 mb-2">{feature.title}</h3>
                                            <p className="text-gray-700 leading-relaxed mb-3">{feature.description}</p>
                                            <p className="text-sm text-gray-500 italic">{feature.example}</p>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </section>
    );
};
