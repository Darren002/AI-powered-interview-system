// Format score percentage
export const formatPercentage = (score, maxScore = 25) => {
  return Math.round((score / maxScore) * 100);
};

// Get performance level
export const getPerformanceLevel = (score, maxScore = 25) => {
  const percentage = (score / maxScore) * 100;
  
  if (percentage >= 80) return { level: 'Outstanding', color: 'text-white' };
  if (percentage >= 60) return { level: 'Strong', color: 'text-white-300' };
  if (percentage >= 40) return { level: 'Qualified', color: 'text-white-400' };
  return { level: 'Needs Development', color: 'text-white-500' };
};

// Format duration
export const formatDuration = (minutes) => {
  if (minutes < 60) return `${Math.round(minutes)} min`;
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  return `${hours}h ${mins}m`;
};

// Format date
export const formatDate = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Skill name formatter
export const formatSkillName = (skill) => {
  return skill
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};