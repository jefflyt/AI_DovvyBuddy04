export const WatercolorBackground = () => {
    return (
        <div className="fixed inset-0 -z-10 overflow-hidden bg-gradient-to-b from-cyan-100 via-cyan-200 to-blue-300">
            {/* Light overlay for better text readability */}
            <div className="absolute inset-0 bg-gradient-to-b from-white/70 via-white/60 to-white/50"></div>

            {/* Subtle light rays effect */}
            <div className="absolute inset-0 opacity-30">
                <div className="absolute top-0 left-1/4 w-1 h-full bg-gradient-to-b from-white/60 to-transparent transform -skew-x-12"></div>
                <div className="absolute top-0 left-1/2 w-1 h-full bg-gradient-to-b from-white/40 to-transparent transform -skew-x-12"></div>
                <div className="absolute top-0 left-3/4 w-1 h-full bg-gradient-to-b from-white/50 to-transparent transform -skew-x-12"></div>
            </div>
        </div>
    );
};
