import UploadForm from '@/components/UploadForm';

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Analyze Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-purple-400">SUNO Tracks</span>
          </h1>
          <p className="text-xl text-gray-300 mb-4">
            Upload your AI-generated music and get instant feedback on:
          </p>
          <div className="grid md:grid-cols-3 gap-4 mt-8 text-left">
            <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="font-semibold text-white mb-2">Hit Potential</h3>
              <p className="text-sm text-gray-400">
                AI-powered prediction of commercial success
              </p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <div className="text-3xl mb-3">👥</div>
              <h3 className="font-semibold text-white mb-2">10 Personas</h3>
              <p className="text-sm text-gray-400">
                Reactions from diverse listener types
              </p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <div className="text-3xl mb-3">🎚️</div>
              <h3 className="font-semibold text-white mb-2">Audio Quality</h3>
              <p className="text-sm text-gray-400">
                Technical analysis of mix and mastering
              </p>
            </div>
          </div>
        </div>

        {/* Upload Form */}
        <UploadForm />

        {/* Info Section */}
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold text-white mb-6">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6 text-sm">
            <div>
              <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                1
              </div>
              <p className="text-gray-300">Upload your MP3 file</p>
            </div>
            <div>
              <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                2
              </div>
              <p className="text-gray-300">AI analyzes audio quality</p>
            </div>
            <div>
              <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                3
              </div>
              <p className="text-gray-300">10 personas evaluate</p>
            </div>
            <div>
              <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                4
              </div>
              <p className="text-gray-300">Get detailed insights</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
