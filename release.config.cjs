/**
 * @type {import('semantic-release').GlobalConfig}
 */
module.exports = {
    plugins: [
        '@semantic-release/commit-analyzer',
        '@semantic-release/release-notes-generator',
        [
            "@semantic-release/exec",
            {
                "prepareCmd": "./scripts/version ${nextRelease.version}"
            }
        ],
        '@semantic-release/git',
        '@semantic-release/github',
    ],
};
