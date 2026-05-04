import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Users, Check } from 'lucide-react';
import { interviewAPI } from '../services/api';

const CandidateCompare = ({ onClose }) => {
  const [candidates, setCandidates] = useState([]);
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(true);
  const [comparison, setComparison] = useState(null);

  useState(() => {
    loadCandidates();
  }, []);

  const loadCandidates = async () => {
    try {
      const response = await interviewAPI.getRecentInterviews(50);
      if (response.success) {
        const completed = response.interviews.filter(i => i.status === 'completed');
        setCandidates(completed);
      }
    } catch (err) {
      console.error('Error loading candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (sessionId) => {
    setSelected(prev => 
      prev.includes(sessionId)
        ? prev.filter(id => id !== sessionId)
        : prev.length < 3
          ? [...prev, sessionId]
          : prev
    );
  };

  const runComparison = async () => {
    if (selected.length < 2) return;
    
    setLoading(true);
    try {
      const reports = await Promise.all(
        selected.map(async (id) => {
          const res = await interviewAPI.getReport(id);
          return res.success ? res.report : null;
        })
      );
      setComparison(reports.filter(Boolean));
    } catch (err) {
      console.error('Error comparing:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 20) return 'text-success';
    if (score >= 15) return 'text-white';
    if (score >= 10) return 'text-warning';
    return 'text-error';
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-black-50 border border-black-200 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-black-200">
          <div className="flex items-center gap-3">
            <Users className="w-5 h-5 text-white" />
            <h2 className="text-lg font-bold text-white">Compare Candidates</h2>
          </div>
          <button onClick={onClose} className="text-white-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {!comparison ? (
            <>
              {/* Selection */}
              <div className="mb-4">
                <p className="text-sm text-white-400 mb-3">Select 2-3 candidates to compare:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {candidates.map(candidate => (
                    <button
                      key={candidate.session_id}
                      onClick={() => toggleSelect(candidate.session_id)}
                      className={`p-3 rounded-lg border text-left transition-colors ${
                        selected.includes(candidate.session_id)
                          ? 'border-white bg-white/10'
                          : 'border-black-200 hover:border-white-400'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-white">{candidate.candidate_name}</p>
                          <p className="text-xs text-white-400">{candidate.target_skills?.join(', ')}</p>
                        </div>
                        <div className={`text-xl font-bold ${getScoreColor(candidate.overall_score)}`}>
                          {candidate.overall_score?.toFixed(1) || 'N/A'}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Compare Button */}
              <div className="text-center">
                <button
                  onClick={runComparison}
                  disabled={selected.length < 2}
                  className="bg-white text-black px-6 py-2 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Compare Selected ({selected.length})
                </button>
              </div>
            </>
          ) : (
            /* Comparison Results */
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {comparison.map((report, index) => (
                <div key={index} className="bg-black rounded-lg border border-black-200 p-4">
                  <h3 className="font-bold text-white mb-2">{report.candidate_name}</h3>
                  
                  <div className="text-center mb-4">
                    <div className={`text-3xl font-bold ${getScoreColor(report.overall_performance?.average_score)}`}>
                      {report.overall_performance?.average_score?.toFixed(1) || 'N/A'}
                    </div>
                    <div className="text-xs text-white-400">/25</div>
                  </div>

                  <div className="space-y-2">
                    {Object.entries(report.skill_breakdown || {}).map(([skill, data]) => (
                      <div key={skill} className="flex justify-between text-xs">
                        <span className="text-white-400 capitalize">{skill.replace('_', ' ')}</span>
                        <span className="text-white">{data.average_score?.toFixed(1)}/25</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default CandidateCompare;
