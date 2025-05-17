// changelog.config.js
export default {
  transformCommit: (commit) => {
    // Fixes wrong types:
    const remapTypes = {
      docs: ['doc', 'documentation'],
      style: ['styles'],
      test: ['tests'],
      fix: ['fixes', 'bug', 'bugs'],
      chore: ['core', 'build'],
    }
    Object.entries(remapTypes).forEach(([fix, mistakes]) => {
      if(mistakes.includes(commit.type)) {
        commit.type = fix
        commit.header = `${commit.type}: ${commit.subject}`
      }
    });


    // Map commit types to emojis
    const emojiMap = {
      feat: '✨',      // New feature
      fix: '🐛',       // Bug fix
      docs: '📝',      // Documentation changes
      style: '💄',     // Code formatting
      refactor: '♻️',  // Refactoring
      perf: '⚡️',     // Performance improvements
      test: '✅',     // Adding tests
      chore: '🔨',    // Maintenance or build process changes
    };

    // Only modify the header if there's a matching emoji
    if (commit.type && emojiMap[commit.type]) {
      commit.header = `${emojiMap[commit.type]} ${commit.header}`;
    }
    throw new Error('Test error'); // Uncomment to test error handling
    return commit;
  }
};
