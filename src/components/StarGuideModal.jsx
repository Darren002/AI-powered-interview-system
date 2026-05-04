import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

const StarGuideModal = ({ isOpen, onClose }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
          >
            <div className="bg-black-50 border border-white/20 rounded-lg w-full max-w-md pointer-events-auto">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-white/10">
                <h2 className="text-lg font-semibold text-white">THE STAR METHOD</h2>
                <button
                  onClick={onClose}
                  className="text-white-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-white mb-1">
                      <span className="text-white-400">S</span> — Situation
                    </h3>
                    <p className="text-sm text-white-400">
                      Describe the context and background of your experience.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-white mb-1">
                      <span className="text-white-400">T</span> — Task
                    </h3>
                    <p className="text-sm text-white-400">
                      Explain your specific responsibility or objective.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-white mb-1">
                      <span className="text-white-400">A</span> — Action
                    </h3>
                    <p className="text-sm text-white-400">
                      Detail the steps you personally took to address the situation.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-white mb-1">
                      <span className="text-white-400">R</span> — Result
                    </h3>
                    <p className="text-sm text-white-400">
                      Share the measurable outcomes and the impact of your actions.
                    </p>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <p className="text-sm text-white-400">
                    Strong answers include specific metrics, focus on your individual contribution, and demonstrate real-world results.
                  </p>
                </div>
              </div>

              {/* Footer */}
              <div className="p-6 border-t border-white/10 flex justify-end">
                <button
                  onClick={onClose}
                  className="px-6 py-2 bg-white text-black text-sm font-medium rounded-lg hover:bg-white/90 transition-colors"
                >
                  Got it
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default StarGuideModal;
