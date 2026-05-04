import { motion } from 'framer-motion';
import { Target } from 'lucide-react';

const ProgressBar = ({ questionsAnswered, totalQuestions, followUpsAnswered = 0 }) => {
  // questionsAnswered = how many main questions have been answered
  // totalQuestions = total main questions in interview
  // followUpsAnswered = how many follow-up questions have been answered
  
  // Progress calculation:
  // Each main question = 1 unit
  // Each follow-up = 0.25 units (bonus for extra effort)
  const baseProgress = questionsAnswered;
  const followUpBonus = followUpsAnswered * 0.25;
  const totalProgress = baseProgress + followUpBonus;
  
  // Percentage based on total questions
  const percentage = totalQuestions > 0 
    ? Math.min((totalProgress / totalQuestions) * 100, 100) 
    : 0;

  // Current question number (next one to answer)
  const currentQuestionNum = questionsAnswered + 1;

  return (
    <div className="bg-black-50 border border-black-200 rounded-lg p-3 mb-4">
      <div className="flex justify-between items-center text-sm mb-2">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-white" />
          <span className="text-white-300">
            Question {Math.min(currentQuestionNum, totalQuestions)} of {totalQuestions}
            {followUpsAnswered > 0 && (
              <span className="text-white-400 ml-1">(+{followUpsAnswered} follow-up{followUpsAnswered > 1 ? 's' : ''})</span>
            )}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-white font-semibold">{percentage.toFixed(0)}%</span>
          <span className="text-white-400">Complete</span>
        </div>
      </div>
      
      <div className="relative">
        {/* Background Track */}
        <div className="h-1.5 bg-black-300 rounded-full overflow-hidden">
          {/* Progress */}
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="h-full bg-white rounded-full"
          />
        </div>
        
        {/* Progress Markers - show main questions only */}
        <div className="flex justify-between mt-2">
          {Array.from({ length: totalQuestions }, (_, i) => (
            <div 
              key={i}
              className={`w-2 h-2 rounded-full transition-colors ${
                i < questionsAnswered 
                  ? 'bg-white' 
                  : i === questionsAnswered
                    ? 'bg-white ring-2 ring-white ring-offset-2 ring-offset-black-50'
                    : 'bg-black-300'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;
