import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 bg-slate-900/80 backdrop-blur-lg border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-white">
          AI MedVision
        </Link>
        <Link
          to="/"
          className="text-blue-300 hover:text-white transition-colors"
        >
          Back to Models
        </Link>
      </div>
    </nav>
  );
}
