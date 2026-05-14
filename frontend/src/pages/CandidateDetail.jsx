import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, User, Mail, Calendar,
  Award, Clock, FileText, CheckCircle, XCircle,
  ChevronDown, ChevronUp, BarChart3, Target,
  Brain, Shield, Users, MessageSquare
} from 'lucide-react';
import { interviewAPI } from '../services/api';
import { formatDate, getPerformanceLevel } from '../utils/formatters';

const skillIcons = {
  communication: MessageSquare,
  leadership: Users,
  decision_making: Target,
  critical_thinking: Brain
};

const CandidateDetail = () => {
  const { sessionId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedQuestions, setExpandedQuestions] = useState({});

  useEffect(() => {
    loadReport();
  }, [sessionId]);

  const loadReport = async () => {
    try {
      console.log('Loading report for:', sessionId);
      const response = await interviewAPI.getReport(sessionId);
      console.log('Report response:', response);
      
      if (response.success && response.report) {
        setReport(response.report);
      } else {
        setError('Report not found');
      }
    } catch (err) {
      console.error('Error loading report:', err);
      setError(err.message || 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const toggleQuestion = (index) => {
    setExpandedQuestions(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center bg-black">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white-400">Loading report...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center bg-black">
        <div className="text-center">
          <h2 className="text-xl font-bold mb-2">Report Not Found</h2>
          <p className="text-white-400 mb-4">{error || 'Unable to load report'}</p>
          <Link to="/dashboard" className="btn-primary">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const performance = getPerformanceLevel(report.overall_performance?.average_score || 0);

  return (
    <div className="min-h-screen py-8 bg-black">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Link 
            to="/dashboard" 
            className="inline-flex items-center gap-2 text-white-400 hover:text-white mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                {report.candidate_name}
              </h1>
              <div className="flex flex-wrap gap-4 text-white-400">
                {report.candidate_email && (
                  <span className="flex items-center gap-1">
                    <Mail className="w-4 h-4" />
                    {report.candidate_email}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {formatDate(report.interview_date)}
                </span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Overall Score Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-8 mb-8"
        >
          <div className="text-center">
            <h2 className="text-white-400 mb-4">Overall Assessment Score</h2>
            <div className="flex items-baseline justify-center gap-2 mb-4">
              <span className="text-6xl font-bold">
                {report.overall_performance?.average_score?.toFixed(1) || 'N/A'}
              </span>
              <span className="text-3xl text-white-500">/25</span>
            </div>
            
            <div className="text-2xl font-semibold mb-4">
              {performance.level}
            </div>
            
            <div className="w-full max-w-md mx-auto bg-white/10 rounded-full h-4 mb-4">
              <div
                className="bg-white h-4 rounded-full transition-all duration-1000"
                style={{ width: `${report.overall_performance?.percentage || 0}%` }}
              />
            </div>
            
            <div className="flex justify-center gap-6 text-sm text-white-400">
              <span>{report.statistics?.total_questions || 0} Questions</span>
              <span>{report.duration_minutes || 0} min</span>
              <span>{report.statistics?.avg_response_length || 0} avg words</span>
            </div>
          </div>
        </motion.div>

        {/* Skills Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <h2 className="text-2xl font-bold mb-6">Skills Assessment</h2>
          
          <div className="grid md:grid-cols-2 gap-4">
            {Object.values(report.skill_breakdown || {}).map((skill) => {
              const skillKey = Object.keys(report.skill_breakdown || {}).find(k => report.skill_breakdown[k] === skill);
              const Icon = skillIcons[skillKey] || Shield;
              const perf = getPerformanceLevel(skill.average_score);
              
              return (
                <div key={skillKey} className="glass-card p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-white flex items-center justify-center">
                      <Icon className="w-5 h-5 text-black" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold capitalize">
                        {skill.skill_name || skillKey?.replace('_', ' ')}
                      </h3>
                      <p className="text-sm text-white-400">{skill.num_responses || skill.question_count || 1} questions</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold">
                        {skill.average_score?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-sm text-white-400">/25</div>
                    </div>
                  </div>
                  
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div
                      className="bg-white h-2 rounded-full"
                      style={{ width: `${skill.percentage || 0}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>

        {/* Questions & Responses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-2xl font-bold mb-6">Detailed Responses</h2>
          
          <div className="space-y-4">
            {(report.responses || []).map((response, index) => (
              <div key={index} className="glass-card overflow-hidden">
                <button
                  onClick={() => toggleQuestion(index)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-white/5 transition"
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      (response.percentage || 0) >= 60 ? 'bg-white/20 text-white' :
                      (response.percentage || 0) >= 40 ? 'bg-white/10 text-white-400' :
                      'bg-white/5 text-white-300'
                    }`}>
                      {index + 1}
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold capitalize">
                        {response.skill_name?.replace('_', ' ') || 'Unknown'}
                      </h3>
                      <p className="text-sm text-white-400">
                        Score: {response.score?.toFixed(1) || response.average_score?.toFixed(1) || 'N/A'}/25
                      </p>
                    </div>
                  </div>
                  
                  {expandedQuestions[index] ? (
                    <ChevronUp className="w-5 h-5 text-white-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-white-400" />
                  )}
                </button>
                
                {expandedQuestions[index] && (
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: 'auto' }}
                    className="border-t border-white/10"
                  >
                    <div className="p-6 space-y-4">
                      {/* Question */}
                      <div>
                        <h4 className="text-sm font-medium text-white-400 mb-2">Question:</h4>
                        <p className="text-white">{response.question}</p>
                      </div>
                      
                      {/* Answer */}
                      <div>
                        <h4 className="text-sm font-medium text-white-400 mb-2">Answer:</h4>
                        <div className="bg-white/5 rounded-lg p-4 text-white-300 whitespace-pre-wrap">
                          {response.response}
                        </div>
                      </div>
                      
                      {/* Feedback */}
                      {response.feedback && (
                        <div>
                          <h4 className="text-sm font-medium text-white-400 mb-2">Feedback:</h4>
                          <div className="bg-white/10 border border-white/20 rounded-lg p-4 text-white-300 whitespace-pre-wrap">
                            {response.feedback}
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default CandidateDetail;
