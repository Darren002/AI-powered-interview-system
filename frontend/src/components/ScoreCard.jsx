import { motion } from 'framer-motion';
import { Target, CheckCircle } from 'lucide-react';
import { getPerformanceLevel } from '../utils/formatters';

const ScoreCard = ({ skill, data }) => {
  const performanceLevel = getPerformanceLevel(data.average_score);

  return (
    <motion.div 
      whileHover={{ scale: 1.02 }}
      className="glass-card p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div>
            <h3 className="text-lg font-bold">{data.skill_name}</h3>
            <p className="text-sm text-white-400">{data.num_responses} response{data.num_responses !== 1 ? 's' : ''}</p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-3xl font-bold">
            {data.average_score}
          </div>
          <div className="text-xs text-white-400">/25</div>
        </div>
      </div>

      <div className="mb-4">
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${data.percentage}%` }}
            transition={{ duration: 1, delay: 0.2 }}
            className="h-full bg-white rounded-full"
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
            performanceLevel.level === 'Excellent' ? 'bg-white/20 text-white' :
            performanceLevel.level === 'Good' ? 'bg-white/15 text-white' :
            performanceLevel.level === 'Average' ? 'bg-white/10 text-white-400' :
            'bg-white/5 text-white-300'
          }`}>
            {data.level}
          </div>
        </div>
        
        <div className="flex items-center gap-1 text-xs text-white-400">
          <Target className="w-3 h-3" />
          <span>{data.percentage}%</span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-white/10">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-1 text-white-400">
            <CheckCircle className="w-3 h-3" />
            <span>{(data.confidence * 100).toFixed(0)}% confidence</span>
          </div>
          <div className="flex items-center gap-1 text-white-400">
            <span>Score: {Math.round(data.percentage)}%</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ScoreCard;
