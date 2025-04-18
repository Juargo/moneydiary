module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [
      2,
      'always',
      [
        'proyecciones',
        'metodos',
        'importacion',
        'ui',
        'api',
        'db',
        'auth',
        'docs'
      ]
    ]
  }
};
