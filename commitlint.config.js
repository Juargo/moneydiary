module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'body-max-line-length': [2, 'always', 150],  // Aumentar el límite de caracteres
    'scope-enum': [2, 'always', [
      'proyecciones', 
      'metodos', 
      'importacion', 
      'ui', 
      'api', 
      'db', 
      'auth',
      'docs'
    ]]
  }
};
