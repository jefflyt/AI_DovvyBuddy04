import Link from 'next/link'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-neutral-900 text-neutral-300 py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            {/* Brand */}
            <div>
              <h3 className="text-white font-bold text-xl mb-3">DovvyBuddy</h3>
              <p className="text-neutral-400 leading-relaxed">
                Your AI diving companion for certification guidance and trip planning.
              </p>
            </div>

            {/* Links */}
            <div>
              <h4 className="text-white font-semibold mb-3">Resources</h4>
              <ul className="space-y-2">
                <li>
                  <Link
                    href="/chat"
                    className="text-neutral-400 hover:text-white transition-colors"
                  >
                    Start Chat
                  </Link>
                </li>
                <li>
                  <Link
                    href="#"
                    className="text-neutral-400 hover:text-white transition-colors"
                  >
                    About
                  </Link>
                </li>
                <li>
                  <Link
                    href="#"
                    className="text-neutral-400 hover:text-white transition-colors"
                  >
                    FAQ
                  </Link>
                </li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="text-white font-semibold mb-3">Legal</h4>
              <ul className="space-y-2">
                <li>
                  <Link
                    href="#"
                    className="text-neutral-400 hover:text-white transition-colors"
                  >
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link
                    href="#"
                    className="text-neutral-400 hover:text-white transition-colors"
                  >
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link
                    href="#"
                    className="text-neutral-400 hover:text-white transition-colors"
                  >
                    Contact
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom bar */}
          <div className="border-t border-neutral-800 pt-8 text-center">
            <p className="text-neutral-500 text-sm">
              &copy; {currentYear} DovvyBuddy. All rights reserved. | V1 - Web Chat Only | Guest Sessions (24h)
            </p>
            <p className="text-neutral-600 text-xs mt-2">
              Always consult certified professionals for dive training and medical advice.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
