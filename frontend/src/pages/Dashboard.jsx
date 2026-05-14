import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Users, Calendar, Search,
  Eye, ChevronDown, ChevronUp,
  CheckCircle, Star
} from 'lucide-react';
import { interviewAPI } from '../services/api';
import { formatDate, formatSkillName, getPerformanceLevel } from '../utils/formatters';

const HR_WHITELIST = [
  'darrenraj1234@gmail.com',
  'hr@company.com',
  'admin@cyberhire.ai'
];

const Dashboard = () => {
  const [interviews, setInterviews] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // HR Email Verification
  const [hrEmail, setHrEmail] = useState('');
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [authError, setAuthError] = useState('');
  
  // Search and filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [filterScore, setFilterScore] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedInterviews, setSelectedInterviews] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [interviewsData] = await Promise.all([
        interviewAPI.getRecentInterviews(100),
      ]);

      if (interviewsData.success) {
        setInterviews(interviewsData.interviews);
        
        // Calculate stats from actual data
        const calculatedStats = calculateStats(interviewsData.interviews);
        setStats(calculatedStats);
      }
    } catch (err) {
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (interviewsList) => {
    const completed = interviewsList.filter(i => i.status === 'completed');
    const totalScore = completed.reduce((acc, i) => acc + (i.overall_score || 0), 0);
    const avgScore = completed.length > 0 ? totalScore / completed.length : 0;
    
    // Score distribution
    const scoreRanges = {
      excellent: completed.filter(i => i.overall_score >= 20).length,
      good: completed.filter(i => i.overall_score >= 15 && i.overall_score < 20).length,
      average: completed.filter(i => i.overall_score >= 10 && i.overall_score < 15).length,
      poor: completed.filter(i => i.overall_score < 10).length,
    };

    // Skills distribution
    const skillsCount = {};
    completed.forEach(i => {
      (i.target_skills || []).forEach(skill => {
        skillsCount[skill] = (skillsCount[skill] || 0) + 1;
      });
    });

    return {
      total_interviews: interviewsList.length,
      completed_interviews: completed.length,
      avg_score: avgScore,
      score_ranges: scoreRanges,
      skills_distribution: skillsCount,
    };
  };

  // Filter and sort interviews
  const filteredInterviews = interviews
    .filter(interview => {
      // Search filter
      if (searchTerm) {
        const search = searchTerm.toLowerCase();
        if (!interview.candidate_name.toLowerCase().includes(search)) {
          return false;
        }
      }
      
      // Score filter
      if (filterScore !== 'all') {
        const score = interview.overall_score || 0;
        if (filterScore === 'excellent' && score < 20) return false;
        if (filterScore === 'good' && (score < 15 || score >= 20)) return false;
        if (filterScore === 'average' && (score < 10 || score >= 15)) return false;
        if (filterScore === 'poor' && score >= 10) return false;
      }
      
      // Status filter
      if (filterStatus !== 'all' && interview.status !== filterStatus) {
        return false;
      }
      
      return true;
    })
    .sort((a, b) => {
      let comparison = 0;
      
      if (sortBy === 'date') {
        comparison = new Date(a.created_at) - new Date(b.created_at);
      } else if (sortBy === 'score') {
        comparison = (a.overall_score || 0) - (b.overall_score || 0);
      } else if (sortBy === 'name') {
        comparison = a.candidate_name.localeCompare(b.candidate_name);
      }
      
      return sortOrder === 'desc' ? -comparison : comparison;
    });

  // Export to CSV
  const handleExportCSV = () => {
    const headers = ['Candidate', 'Date', 'Skills', 'Score', 'Status', 'Session ID'];
    const rows = filteredInterviews.map(i => [
      i.candidate_name,
      formatDate(i.created_at),
      (i.target_skills || []).join(', '),
      i.overall_score?.toFixed(1) || 'N/A',
      i.status,
      i.session_id
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interviews_export_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  // Toggle sort
  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center bg-black">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white-400">Loading...</p>
        </div>
      </div>
    );
  }

  // HR Email Authorization Check
  if (!isAuthorized) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 bg-black">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-sm text-center"
        >
          <h2 className="text-2xl font-bold mb-2">HR Dashboard</h2>
          <p className="text-white-400 mb-6">Enter your authorized email</p>
          
          {authError && (
            <div className="bg-white/10 border border-white/30 rounded-lg p-3 mb-4 text-white text-sm">
              {authError}
            </div>
          )}
          
          <input
            type="email"
            value={hrEmail}
            onChange={(e) => setHrEmail(e.target.value)}
            placeholder="Email"
            className="w-full bg-black-50 border border-black-200 rounded-lg px-4 py-3 mb-4 focus:outline-none focus:border-white"
          />
          
          <button
            onClick={() => {
              const email = hrEmail.toLowerCase().trim();
              if (HR_WHITELIST.includes(email)) {
                setIsAuthorized(true);
                setAuthError('');
              } else {
                setAuthError('Access denied');
              }
            }}
            className="w-full bg-white text-black font-medium py-3 rounded-lg hover:bg-white-200 transition-colors"
          >
            Access
          </button>
          
          <p className="text-white-400 text-sm mt-4">
            HR login : darrenraj1234@gmail.com
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-20 pb-12 px-4 bg-black">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold mb-1">HR Dashboard</h1>
              <p className="text-white-400">Manage candidates</p>
            </div>
            <button 
              onClick={handleExportCSV}
              className="bg-white text-black px-4 py-2 rounded-lg text-sm font-medium hover:bg-white-200 transition-colors"
            >
              Export CSV
            </button>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid md:grid-cols-4 gap-6 mb-8"
        >
          <div className="glass-card p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-black" />
              </div>
              <div>
                <p className="text-white-400 text-sm">Total Interviews</p>
                <p className="text-2xl font-bold">{stats?.total_interviews || 0}</p>
              </div>
            </div>
          </div>

          <div className="glass-card p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-black" />
              </div>
              <div>
                <p className="text-white-400 text-sm">Completed</p>
                <p className="text-2xl font-bold">{stats?.completed_interviews || 0}</p>
              </div>
            </div>
          </div>

          <div className="glass-card p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center">
                <Star className="w-6 h-6 text-black" />
              </div>
              <div>
                <p className="text-white-400 text-sm">Average Score</p>
                <p className="text-2xl font-bold">{(stats?.avg_score || 0).toFixed(1)}/25</p>
              </div>
            </div>
          </div>

          <div className="glass-card p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-black" />
              </div>
              <div>
                <p className="text-white-400 text-sm">Excellent (20+)</p>
                <p className="text-2xl font-bold">{stats?.score_ranges?.excellent || 0}</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Score Distribution & Skills */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Score Distribution */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card p-6"
          >
            <h3 className="text-lg font-bold mb-4">Score Distribution</h3>
            <div className="space-y-3">
              {[
                { label: 'Excellent (20-25)', count: stats?.score_ranges?.excellent || 0, percent: stats?.completed_interviews ? ((stats?.score_ranges?.excellent || 0) / stats.completed_interviews * 100) : 0 },
                { label: 'Good (15-19)', count: stats?.score_ranges?.good || 0, percent: stats?.completed_interviews ? ((stats?.score_ranges?.good || 0) / stats.completed_interviews * 100) : 0 },
                { label: 'Average (10-14)', count: stats?.score_ranges?.average || 0, percent: stats?.completed_interviews ? ((stats?.score_ranges?.average || 0) / stats.completed_interviews * 100) : 0 },
                { label: 'Poor (<10)', count: stats?.score_ranges?.poor || 0, percent: stats?.completed_interviews ? ((stats?.score_ranges?.poor || 0) / stats.completed_interviews * 100) : 0 },
              ].map((item, i) => (
                <div key={i}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-white-300">{item.label}</span>
                    <span className="text-white-400">{item.count} ({item.percent.toFixed(0)}%)</span>
                  </div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${item.percent}%` }}
                      transition={{ delay: 0.3 + i * 0.1 }}
                      className="h-full bg-white"
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Skills Distribution */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card p-6"
          >
            <h3 className="text-lg font-bold mb-4">Skills Assessed</h3>
            <div className="space-y-3">
              {Object.entries(stats?.skills_distribution || {}).map(([skill, count], i) => (
                <div key={skill}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-white-300">{formatSkillName(skill)}</span>
                    <span className="text-white-400">{count} assessments</span>
                  </div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${(count / stats.completed_interviews * 100)}%` }}
                      transition={{ delay: 0.4 + i * 0.1 }}
                      className="h-full bg-white"
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Filters & Search */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6 mb-6"
        >
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white-400" />
              <input
                type="text"
                placeholder="Search by candidate name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-10"
              />
            </div>

            {/* Filters */}
            <select
              value={filterScore}
              onChange={(e) => setFilterScore(e.target.value)}
              className="input-field w-auto"
            >
              <option value="all">All Scores</option>
              <option value="excellent">Excellent (20+)</option>
              <option value="good">Good (15-19)</option>
              <option value="average">Average (10-14)</option>
              <option value="poor">Poor (&lt;10)</option>
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input-field w-auto"
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="in_progress">In Progress</option>
            </select>
          </div>
        </motion.div>

        {/* Candidates Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card overflow-hidden"
        >
          <div className="p-6 border-b border-white/10">
            <h2 className="text-xl font-bold">Candidates ({filteredInterviews.length})</h2>
          </div>

          {filteredInterviews.length === 0 ? (
            <div className="text-center py-16">
              <Users className="w-16 h-16 text-white-600 mx-auto mb-4" />
              <p className="text-white-400 mb-4">No interviews found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-4 px-6 text-white-400 font-semibold">
                      <button 
                        onClick={() => handleSort('name')}
                        className="flex items-center gap-1 hover:text-white"
                      >
                        Candidate
                        {sortBy === 'name' && (
                          sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        )}
                      </button>
                    </th>
                    <th className="text-left py-4 px-6 text-white-400 font-semibold">
                      <button 
                        onClick={() => handleSort('date')}
                        className="flex items-center gap-1 hover:text-white"
                      >
                        Date
                        {sortBy === 'date' && (
                          sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        )}
                      </button>
                    </th>
                    <th className="text-left py-4 px-6 text-white-400 font-semibold">Skills</th>
                    <th className="text-left py-4 px-6 text-white-400 font-semibold">
                      <button 
                        onClick={() => handleSort('score')}
                        className="flex items-center gap-1 hover:text-white"
                      >
                        Score
                        {sortBy === 'score' && (
                          sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        )}
                      </button>
                    </th>
                    <th className="text-left py-4 px-6 text-white-400 font-semibold">Status</th>
                    <th className="text-right py-4 px-6 text-white-400 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredInterviews.map((interview, index) => {
                    const performanceLevel = interview.overall_score 
                      ? getPerformanceLevel(interview.overall_score)
                      : null;

                    return (
                      <motion.tr
                        key={interview.session_id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.6 + index * 0.02 }}
                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                      >
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                              <span className="text-black font-semibold">
                                {interview.candidate_name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <p className="font-semibold">{interview.candidate_name}</p>
                              <p className="text-xs text-white-500">ID: {interview.session_id.slice(-8)}</p>
                            </div>
                          </div>
                        </td>
                        
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-2 text-white-300">
                            <Calendar className="w-4 h-4 text-white-400" />
                            <span className="text-sm">{formatDate(interview.created_at)}</span>
                          </div>
                        </td>
                        
                        <td className="py-4 px-6">
                          <div className="flex flex-wrap gap-1">
                            {(interview.target_skills || []).slice(0, 2).map(skill => (
                              <span
                                key={skill}
                                className="px-2 py-1 bg-white/10 text-white rounded text-xs"
                              >
                                {formatSkillName(skill)}
                              </span>
                            ))}
                            {(interview.target_skills || []).length > 2 && (
                              <span className="px-2 py-1 bg-white/10 text-white-400 rounded text-xs">
                                +{(interview.target_skills || []).length - 2}
                              </span>
                            )}
                          </div>
                        </td>
                        
                        <td className="py-4 px-6">
                          {interview.overall_score ? (
                            <div>
                              <p className={`text-xl font-bold ${performanceLevel?.color || 'text-white'}`}>
                                {interview.overall_score.toFixed(1)}
                                <span className="text-gray-500 text-sm">/25</span>
                              </p>
                              {performanceLevel && (
                                <p className={`text-xs ${performanceLevel.color}`}>
                                  {performanceLevel.level}
                                </p>
                              )}
                            </div>
                          ) : (
                            <span className="text-gray-500">—</span>
                          )}
                        </td>
                        
                        <td className="py-4 px-6">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            interview.status === 'completed'
                              ? 'bg-white/20 text-white'
                              : interview.status === 'in_progress'
                              ? 'bg-white/10 text-white-400'
                              : 'bg-white/5 text-white-300'
                          }`}>
                            {interview.status.replace('_', ' ')}
                          </span>
                        </td>
                        
                        <td className="py-4 px-6 text-right">
                          {interview.status === 'completed' && (
                            <div className="flex items-center justify-end gap-3">
                              <Link
                                to={`/hr/candidate/${interview.session_id}`}
                                className="inline-flex items-center gap-1 text-white hover:text-white-400 text-sm font-semibold"
                              >
                                <Eye className="w-4 h-4" />
                                View
                              </Link>
                            </div>
                          )}
                        </td>
                      </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
