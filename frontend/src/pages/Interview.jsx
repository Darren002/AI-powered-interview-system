import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { interviewAPI } from '../services/api';
import ChatMessage from '../components/ChatMessage';
import ProgressBar from '../components/ProgressBar';
import StarGuideModal from '../components/StarGuideModal';

const Interview = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const candidateName = location.state?.candidateName || 'Candidate';

  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [interviewComplete, setInterviewComplete] = useState(false);
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [followUpsAnswered, setFollowUpsAnswered] = useState(0);
  const [error, setError] = useState('');
  const [showStarGuide, setShowStarGuide] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const loadInitialMessage = async () => {
      try {
        const status = await interviewAPI.getStatus(sessionId);
        if (status.success && status.session_info) {
          setTotalQuestions(status.session_info.total_skills);
          
          setMessages([{
            id: 'welcome',
            type: 'bot',
            content: `Welcome, ${candidateName}! \n\nI'm ready to begin your interview. We'll be assessing ${status.session_info.total_skills} skills through behavioral questions using the STAR framework.\n\nAre you ready to start?`,
            timestamp: new Date().toISOString(),
          }]);
        }
      } catch (err) {
        console.error('Error loading interview:', err);
        setError('Failed to load interview. Please try again.');
      }
    };

    loadInitialMessage();
  }, [sessionId, candidateName]);

  const handleSendMessage = async () => {
    if (!currentInput.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: currentInput.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentInput('');
    setLoading(true);
    setError('');

    try {
      const response = await interviewAPI.submitResponse(sessionId, currentInput.trim());

      if (response.success && response.result) {
        const result = response.result;

        if (result.type === 'question') {
          setMessages(prev => [...prev, {
            id: Date.now() + 1,
            type: 'bot',
            content: result.content,
            timestamp: new Date().toISOString(),
            metadata: result.metadata,
          }]);
          // Don't increment questionsAnswered - user hasn't answered yet
        }
        else if (result.type === 'feedback_and_next') {
          // Track if this is a follow-up question
          const isFollowUp = !!result.follow_up_notice;
          
          if (isFollowUp) {
            setFollowUpsAnswered(prev => prev + 1);
          } else {
            setQuestionsAnswered(prev => prev + 1);
          }
          
          // Show brief feedback message (not detailed evaluation)
          let briefMessage = "";
          if (result.follow_up_notice) {
            briefMessage = result.follow_up_notice;
          }
          
          // Add brief message and next question
          setMessages(prev => [
            ...prev,
            ...(briefMessage ? [{
              id: Date.now(),
              type: 'bot',
              content: briefMessage,
              timestamp: new Date().toISOString(),
            }] : []),
            {
              id: Date.now() + 1,
              type: 'bot',
              content: result.next_question.content,
              timestamp: new Date().toISOString(),
              metadata: result.next_question.metadata,
            }
          ]);
        }
        else if (result.type === 'completion' || result.type === 'completed') {
          setMessages(prev => [
            ...prev,
            {
              id: Date.now() + 1,
              type: 'bot',
              content: "Interview Complete! Your responses have been recorded. The detailed feedback report will be available to the HR team.",
              timestamp: new Date().toISOString(),
              isCompletion: true,
            }
          ]);
          setInterviewComplete(true);
          setQuestionsAnswered(totalQuestions);
        }
        else if (result.type === 'clarification') {
          setMessages(prev => [...prev, {
            id: Date.now() + 1,
            type: 'bot',
            content: result.content,
            timestamp: new Date().toISOString(),
          }]);
        }
      }
    } catch (err) {
      console.error('Error submitting response:', err);
      console.error('Error response:', err.response?.data);
      console.error('Error status:', err.response?.status);
      setError('Failed to send message. Please try again. (' + (err.response?.status || 'network error') + ')');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen pt-20 pb-4 px-4 bg-black">
      <div className="max-w-4xl mx-auto">
        
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-4"
        >
          <div>
            <h2 className="text-xl font-bold text-white">Interview Session</h2>
            <p className="text-sm text-white-400">Session ID: {sessionId.slice(-8)}</p>
          </div>
          
          <button
            onClick={() => setShowStarGuide(true)}
            className="p-2 text-white-400 hover:text-white transition-colors"
            title="STAR Framework Guide"
          >
            <Info className="w-5 h-5" />
          </button>
        </motion.div>

        {/* Progress Bar */}
        {totalQuestions > 0 && (
          <ProgressBar 
            questionsAnswered={questionsAnswered} 
            totalQuestions={totalQuestions}
            followUpsAnswered={followUpsAnswered}
          />
        )}

        {/* Chat Container */}
        <div className="bg-black-50 border border-black-200 rounded-lg flex flex-col" style={{ height: 'calc(100vh - 14rem)' }}>
          
          {/* Scrollable Messages */}
          <div className="flex-1 overflow-y-auto p-4 chat-container">
            <AnimatePresence>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={{...message, sessionId}} />
              ))}
            </AnimatePresence>

            {loading && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center gap-3 text-white-400"
              >
                <Loader className="w-5 h-5 animate-spin" />
                <span>AI is thinking...</span>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          {!interviewComplete && (
            <div className="flex-shrink-0 border-t border-black-200 p-4 bg-black-50">
              {error && (
                <div className="bg-white/10 border border-white/50 rounded-lg p-3 mb-3 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" />
                  <span className="text-white text-sm">{error}</span>
                </div>
              )}

              <div className="flex gap-3">
                <textarea
                  ref={inputRef}
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your response using the STAR framework..."
                  disabled={loading}
                  rows={3}
                  className="flex-1 bg-black-100 border border-black-300 rounded-lg px-4 py-3 text-white placeholder-white-400 focus:outline-none focus:border-white resize-none"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={loading || !currentInput.trim()}
                  className="bg-white text-black px-6 rounded-lg font-medium hover:bg-white-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>

              <div className="flex items-center justify-between mt-2 text-xs text-white-400">
                <span>Press Enter to send, Shift+Enter for new line</span>
                <span>{currentInput.length} characters</span>
              </div>
            </div>
          )}

          {interviewComplete && (
            <div className="border-t border-black-200 p-6 text-center bg-black-50">
              <CheckCircle className="w-12 h-12 mx-auto mb-3" />
              <p className="text-xl font-bold text-white mb-2">Interview Complete!</p>
              <p className="text-white-400 mb-4">Thank you for completing the assessment</p>
              <a 
                href={`/report/${sessionId}`}
                className="inline-block bg-white text-black px-6 py-3 rounded-lg font-medium hover:bg-white-200"
              >
                View Full Report
              </a>
            </div>
          )}
        </div>
      </div>

      {/* STAR Guide Modal */}
      <StarGuideModal isOpen={showStarGuide} onClose={() => setShowStarGuide(false)} />
    </div>
  );
};

export default Interview;
