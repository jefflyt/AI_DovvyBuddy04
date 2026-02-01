import Image from 'next/image';

export const OceanBackground = () => {
    return (
        <div className="fixed inset-0 -z-20 overflow-hidden bg-white">
            {/* Watercolor texture background */}
            <Image
                src="/assets/watercolor-bg.png"
                alt=""
                fill
                className="object-cover opacity-60"
                priority
            />

            {/* Bathymetry contour lines overlay */}
            <svg
                className="fixed inset-0 -z-10 w-full h-full opacity-[0.08] pointer-events-none"
                xmlns="http://www.w3.org/2000/svg"
            >
                <defs>
                    <pattern id="contours" x="0" y="0" width="200" height="200" patternUnits="userSpaceOnUse">
                        <path
                            d="M 0 50 Q 50 30 100 50 T 200 50"
                            stroke="currentColor"
                            strokeWidth="1"
                            fill="none"
                            className="text-blue-900"
                        />
                        <path
                            d="M 0 100 Q 50 80 100 100 T 200 100"
                            stroke="currentColor"
                            strokeWidth="1"
                            fill="none"
                            className="text-blue-900"
                        />
                        <path
                            d="M 0 150 Q 50 130 100 150 T 200 150"
                            stroke="currentColor"
                            strokeWidth="1"
                            fill="none"
                            className="text-blue-900"
                        />
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#contours)" />
            </svg>

            {/* Floating Decorative Creatures */}

            {/* Top Left - Jellyfish (Pink) */}
            <div className="absolute top-[8%] left-[5%] w-40 h-40 md:w-56 md:h-56 opacity-50 pointer-events-none animate-float-slow">
                <Image
                    src="/assets/icons/jellyfish.png"
                    alt=""
                    fill
                    className="object-contain transform -rotate-12"
                />
            </div>

            {/* Bottom Right - Seahorse (Brown) */}
            <div className="absolute bottom-[10%] right-[3%] w-48 h-48 md:w-64 md:h-64 opacity-40 pointer-events-none animate-float-slower">
                <Image
                    src="/assets/icons/seahorse.png"
                    alt=""
                    fill
                    className="object-contain transform rotate-6"
                />
            </div>

            {/* Top Right - Turtle (Green) */}
            <div className="absolute top-[12%] right-[8%] w-40 h-40 md:w-60 md:h-60 opacity-30 pointer-events-none animate-float-normal hidden sm:block">
                <Image
                    src="/assets/icons/turtle.png"
                    alt=""
                    fill
                    className="object-contain transform rotate-12"
                />
            </div>

            {/* Bottom Left - Ray (Grey) */}
            <div className="absolute bottom-[15%] left-[5%] w-56 h-56 md:w-80 md:h-80 opacity-25 pointer-events-none animate-float-slow hidden md:block">
                <Image
                    src="/assets/icons/ray.png"
                    alt=""
                    fill
                    className="object-contain transform -rotate-6"
                />
            </div>

            {/* Center Right - Clownfish (Orange) */}
            <div className="absolute top-[50%] right-[2%] w-24 h-24 md:w-32 md:h-32 opacity-40 pointer-events-none animate-float-fast hidden lg:block">
                <Image
                    src="/assets/icons/clownfish.png"
                    alt=""
                    fill
                    className="object-contain transform -rotate-6"
                />
            </div>

            {/* Gradient overlay for text readability - Reduced intensity */}
            <div className="absolute inset-0 bg-gradient-to-b from-white/50 via-white/30 to-transparent mix-blend-overlay"></div>
        </div>
    );
};
