import Link from 'next/link';

export const Footer = () => {
  return (
    <footer className="border-t border-gray-200/50 bg-white/40 backdrop-blur-sm py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Product</h3>
              <ul className="space-y-2">
                <li>
                  <Link href="/chat" className="text-gray-600 hover:text-primary-600 transition-colors">
                    Start Chat
                  </Link>
                </li>
                <li>
                  <Link href="/#faq" className="text-gray-600 hover:text-primary-600 transition-colors">
                    FAQ
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Legal</h3>
              <ul className="space-y-2">
                <li>
                  <Link href="/privacy" className="text-gray-600 hover:text-primary-600 transition-colors">
                    Privacy
                  </Link>
                </li>
                <li>
                  <Link href="/terms" className="text-gray-600 hover:text-primary-600 transition-colors">
                    Terms
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Support</h3>
              <ul className="space-y-2">
                <li>
                  <Link href="/contact" className="text-gray-600 hover:text-primary-600 transition-colors">
                    Contact
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">DovvyBuddy</h3>
              <p className="text-sm text-gray-600">
                Your AI diving companion for certifications, dive sites, and trip planning.
              </p>
            </div>
          </div>
          <div className="pt-8 border-t border-gray-200/50">
            <p className="text-sm text-gray-600 text-center">
              © {new Date().getFullYear()} DovvyBuddy. Not a substitute for professional instruction or medical advice.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};
