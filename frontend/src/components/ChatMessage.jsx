import { motion } from 'framer-motion';
import { Bot, User, CheckCircle } from 'lucide-react';

const ChatMessage = ({ message }) => {
  const isBot = message.type === 'bot';
  const isCompletion = message.isCompletion;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex ${isBot ? 'flex-row' : 'flex-row-reverse'} gap-3 mb-4`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isBot ? 'bg-white' : 'bg-black-300'
      }`}>
        {isBot ? (
          <Bot className="w-4 h-4 text-black" />
        ) : (
          <User className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-[85%] ${isBot ? 'text-left' : 'text-right'}`}>
        {/* Question/Answer Label */}
        {isBot && message.metadata?.question_number && (
          <div className="mb-2">
            <span className="inline-block px-2 py-0.5 text-xs font-medium bg-white/10 text-white-400 rounded">
              Question {message.metadata.question_number}
              {message.metadata.skill && ` • ${message.metadata.skill.replace('_', ' ')}`}
            </span>
          </div>
        )}
        
        {!isBot && (
          <div className="mb-2 text-right">
            <span className="inline-block px-2 py-0.5 text-xs font-medium bg-white/10 text-white-400 rounded">
              Your Answer
            </span>
          </div>
        )}

        {/* Message Bubble */}
        <div className={`inline-block p-4 rounded-2xl text-left ${
          isBot 
            ? 'bg-black-50 border border-white/10' 
            : 'bg-white text-black'
        }`}>
          <div className={`whitespace-pre-wrap leading-relaxed ${
            isBot ? 'text-white' : 'text-black'
          }`}>
            {message.content}
          </div>
        </div>

        {/* Completion Message */}
        {isCompletion && (
          <div className="mt-4 pt-4 border-t border-white/10">
            <div className="flex items-center justify-center gap-2 text-white py-3">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm font-medium">Interview Complete!</span>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ChatMessage;
