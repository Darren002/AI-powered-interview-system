import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Info } from 'lucide-react';
import { interviewAPI } from '../services/api';
import StarGuideModal from '../components/StarGuideModal';

const Home = () => {
  const navigate = useNavigate();
  const [candidateName, setCandidateName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showStarGuide, setShowStarGuide] = useState(false);

  const handleStartInterview = async () => {
    if (!candidateName.trim()) {
      setError('Please enter your name');
      return;
    }
    if (!email.trim()) {
      setError('Please enter your email');
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError('Please enter a valid email');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const response = await interviewAPI.startInterview(
        candidateName.trim(),
        null,
        email.trim()
      );

      if (response.success) {
        navigate(`/interview/${response.session_id}`, {
          state: { candidateName: candidateName.trim() }
        });
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to start. Please try again.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md"
      >
        {/* Logo / Title */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">CyberHire</h1>
          <p className="text-white-400">AI-Powered Soft Skills Assessment</p>
        </div>

        {/* Form */}
        <div className="space-y-4">
          {error && (
            <div className="bg-white/10 border border-white/30 rounded-lg p-3 text-white text-sm text-center">
              {error}
            </div>
          )}

          <input
            type="text"
            value={candidateName}
            onChange={(e) => setCandidateName(e.target.value)}
            placeholder="Your Name"
            className="w-full bg-black-50 border border-black-200 rounded-lg px-4 py-3 text-white placeholder-white-400 focus:outline-none focus:border-white"
            disabled={loading}
          />

          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email Address"
            className="w-full bg-black-50 border border-black-200 rounded-lg px-4 py-3 text-white placeholder-white-400 focus:outline-none focus:border-white"
            disabled={loading}
          />

          <button
            onClick={handleStartInterview}
            disabled={loading}
            className="w-full bg-white text-black font-medium py-3 rounded-lg hover:bg-white-200 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <span>Starting...</span>
            ) : (
              <>
                <span>Start Assessment</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

        {/* Info */}
        <div className="mt-8 text-center">
          <p className="text-white-400 text-sm">
            4 Skills  •  4 Questions  •  Are you ready?
          </p>
          <button
            onClick={() => setShowStarGuide(true)}
            className="mt-2 text-white-400 hover:text-white text-xs transition-colors inline-flex items-center gap-1"
          >
            Learn about the STAR Framework
            <Info className="w-3 h-3" />
          </button>
        </div>

        {/* Links */}
        <div className="mt-6 flex justify-center gap-6 text-sm">
          <a href="/dashboard" className="text-white-400 hover:text-white transition-colors">
            HR Dashboard
          </a>
        </div>

        {/* STAR Guide Modal */}
        <StarGuideModal isOpen={showStarGuide} onClose={() => setShowStarGuide(false)} />
      </motion.div>
    </div>
  );
};

export default Home;
