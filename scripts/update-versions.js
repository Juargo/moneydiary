const fs = require('fs');
const { version } = require('../package.json');

// Asegurar que los directorios existan
const ensureDir = (path) => {
  const dir = path.substring(0, path.lastIndexOf('/'));
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
};

// Actualizar versión en frontend
const frontendPath = 'apps/web/src/version.ts';
ensureDir(frontendPath);
fs.writeFileSync(frontendPath, );
console.log(`✅ Updated frontend version: ${frontendPath}`);

// Actualizar versión en backend
const backendPath = 'apps/api/app/version.py';
ensureDir(backendPath);
fs.writeFileSync(backendPath, `__version__ = ""\n`);
console.log(`✅ Updated backend version: ${backendPath}`);

console.log(`✅ Version ${version} propagated to all components`);
