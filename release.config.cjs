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
        [
            '@semantic-release/git',
            {
                assets: ['custom_components/yaml_preprocessor/manifest.json'],
                message: 'chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}',
            }
        ],
        '@semantic-release/github',
    ],
};
