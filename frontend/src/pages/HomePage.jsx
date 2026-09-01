import { Link } from "react-router-dom";
import { models } from "../data/models";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 relative">
      {/* Hero Section */}
      <div className="text-center pt-20 pb-16 px-4">
        <h1 className="text-5xl font-bold text-white mb-4">
          AI Medical Imaging Platform
        </h1>
        <p className="text-xl text-blue-200 max-w-2xl mx-auto">
          Select a model below to analyze medical images using state-of-the-art
          deep learning
        </p>
      </div>

      {/* Model Cards Grid */}
      <div className="max-w-6xl mx-auto px-4 pb-32 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {models.map((model) => (
          <div key={model.id} className="relative">
            {model.status === "coming-soon" && (
              <div className="absolute -top-2 -right-2 bg-yellow-500 text-white text-xs font-bold px-3 py-1 rounded-full z-10">
                Coming Soon
              </div>
            )}
            <div
              className={`rounded-2xl p-8 bg-white/10 backdrop-blur-lg border border-white/20 
                          hover:scale-105 transition-all duration-300 cursor-pointer
                          ${model.status === "active" ? "hover:shadow-2xl hover:shadow-blue-500/20" : "opacity-60"}`}
            >
              <div
                className={`w-16 h-16 rounded-xl bg-gradient-to-r ${model.color} 
                            flex items-center justify-center text-3xl mb-6`}
              >
                {model.icon}
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">
                {model.name}
              </h3>
              <p className="text-blue-200 mb-4">{model.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-sm text-green-400 font-semibold">
                  Accuracy: {model.accuracy}
                </span>
                {model.status === "active" && (
                  <Link
                    to={`/model/${model.id}`}
                    className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 
                                text-white rounded-lg font-semibold hover:from-blue-600 hover:to-cyan-600 
                                transition-all"
                  >
                    Use Model →
                  </Link>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Team Section - Bottom Center */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 flex gap-6">
        {/* Your Card - Separate */}
        <div className="flex flex-col items-center gap-3 bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl px-8 py-8 hover:bg-white/15 transition-all duration-300 shadow-2xl shadow-blue-500/10">
          <img
            src="/Yug_CV_Photo.jpg"
            alt="Yug G. Lakhani"
            className="w-36 h-36 rounded-full object-cover border-4 border-cyan-400 shadow-lg shadow-cyan-500/30"
          />
          <p className="text-white font-bold text-base">Yug G. Lakhani</p>
          <p className="text-blue-300 text-xs">Developer & Researcher</p>
          <p className="text-blue-400/60 text-xs">Gyanmanjari University</p>
        </div>

        {/* Team Member 2 - Separate Card */}
        {/* <div className="flex flex-col items-center gap-3 bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl px-8 py-8 hover:bg-white/15 transition-all duration-300 shadow-2xl shadow-purple-500/10">
          <img
            src="/member2-photo.jpg"
            alt="Member 2"
            className="w-36 h-36 rounded-full object-cover border-4 border-purple-400 shadow-lg shadow-purple-500/30"
          />
          <p className="text-white font-bold text-base">Member Name</p>
          <p className="text-blue-300 text-xs">Role</p>
          <p className="text-blue-400/60 text-xs">University</p>
        </div> */}

        {/* Team Member 3 - Separate Card */}
        {/* <div className="flex flex-col items-center gap-3 bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl px-8 py-8 hover:bg-white/15 transition-all duration-300 shadow-2xl shadow-green-500/10">
          <img
            src="/member3-photo.jpg"
            alt="Member 3"
            className="w-36 h-36 rounded-full object-cover border-4 border-green-400 shadow-lg shadow-green-500/30"
          />
          <p className="text-white font-bold text-base">Member Name</p>
          <p className="text-blue-300 text-xs">Role</p>
          <p className="text-blue-400/60 text-xs">University</p>
        </div> */}
      </div>
    </div>
  );
}
