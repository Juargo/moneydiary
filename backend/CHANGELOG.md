# Changelog

## [0.3.0](https://github.com/Juargo/moneydiary/compare/v0.2.0...v0.3.0) (2025-04-08)


### Features

* **api:** add bulk transaction input model and endpoint for mass transaction registration ([a5eacc2](https://github.com/Juargo/moneydiary/commit/a5eacc22c03ce91f15f51a60f58fd60d3112e7d3))
* **api:** add create pattern endpoint with request and response examples in README ([e8f5c28](https://github.com/Juargo/moneydiary/commit/e8f5c28bc8c4478e68eccf90049f30afd447b96c))
* **api:** add endpoints for managing Pattern Ignore records and integrate with GraphQL schema ([784b8b4](https://github.com/Juargo/moneydiary/commit/784b8b47736a7a613391d38763cee053671942a8))
* **api:** add GraphQL types and queries for banks and user banks ([968e3a2](https://github.com/Juargo/moneydiary/commit/968e3a203fe03c5f4a6730124fd9c26100a23b29))
* **api:** add patterns API with delete functionality and update main router ([468ebec](https://github.com/Juargo/moneydiary/commit/468ebec5fb134f3420191d8f3d9e6d28eb5b36d0))
* **api:** add subcategory endpoints for creation, update, and deletion ([f76a0a4](https://github.com/Juargo/moneydiary/commit/f76a0a417c2978acf3b690b1ff8bffdba9055d56))
* **api:** add TransactionData type and user_transactions query for fetching user transactions with related data ([a0b98d5](https://github.com/Juargo/moneydiary/commit/a0b98d5ebb27a6f5f3dfa7891ead4546806525b7))
* **api:** add transactions router and Pydantic schemas for transaction validation and serialization ([6613fe4](https://github.com/Juargo/moneydiary/commit/6613fe4888c83cd4ee595f1de19251501e4ccbe1))
* **api:** add update pattern endpoint with request and response examples in README ([8217d83](https://github.com/Juargo/moneydiary/commit/8217d83019492bd32173c994b762624ba4048120))
* **api:** enhance transaction categorization by normalizing text for pattern matching ([c39c90c](https://github.com/Juargo/moneydiary/commit/c39c90cf45e12c7a3dff3ff641165a99fb11cfc1))
* **api:** implement pattern ignore functionality in bank report processing ([30eaad2](https://github.com/Juargo/moneydiary/commit/30eaad2826cdb835f0d13181e95fa3e857dc9da1))
* **api:** update PatternIgnoreResponse to use datetime fields and improve JSON serialization ([9e47741](https://github.com/Juargo/moneydiary/commit/9e477416abb5614842ca28bd75e719c155b929fa))
* **budget:** optimize budget summary query and restructure data processing ([bd74328](https://github.com/Juargo/moneydiary/commit/bd74328640209e57c54ee31beec3c7e2f4675424))
* **db:** add PatternIgnore model and update user model for reverse relation ([5156e5e](https://github.com/Juargo/moneydiary/commit/5156e5eb06dc14ac0743ecf2e85c00115cf34979))
* **transactions:** add debug logging for budget summary processing ([1d5127f](https://github.com/Juargo/moneydiary/commit/1d5127f0b36ac0eaaf52e2775796166cc459b6ac))
* **transactions:** add year-month filtering for bulk transactions and budget summary ([abc1a96](https://github.com/Juargo/moneydiary/commit/abc1a967f1bb8359f14ebc14bb602c495f8250d7))
* **transactions:** add year-month filtering to user transactions query and update frontend to support filtering ([27342e3](https://github.com/Juargo/moneydiary/commit/27342e3f9794af8fc11e97c4fd94720b09cf1630))
* **transactions:** enhance bulk transaction creation with duplicate check and enriched transaction info ([7fd91c2](https://github.com/Juargo/moneydiary/commit/7fd91c2c020c22eb682713d4c21be7d24f697b0f))
* **ui:** add budget summary tab with detailed budget and category breakdowns ([123efa5](https://github.com/Juargo/moneydiary/commit/123efa5993b39f0ceedb89a64501d20491de2887))
* **ui:** streamline bank report upload process by removing bank_id and enhancing file handling ([32c7d5a](https://github.com/Juargo/moneydiary/commit/32c7d5a19a344d8a84f01a3e12981073a1384a32))


### Bug Fixes

* **api:** correct endpoint for bank report upload ([3c8818e](https://github.com/Juargo/moneydiary/commit/3c8818efc8b0882658de77278a65715afbbc0164))
* **api:** improve header detection logic by ensuring minimum match criteria ([22b9d49](https://github.com/Juargo/moneydiary/commit/22b9d497c8c3e122ec1954dc35fd6cb00e64349e))
* **api:** update fetch URL for bank report upload to use the correct endpoint ([260686f](https://github.com/Juargo/moneydiary/commit/260686f35819eec78ae5447e0377b5bed6b7a13f))
* **api:** update get_user_patterns to remove non-existent fields and adjust result processing ([9f0a3c0](https://github.com/Juargo/moneydiary/commit/9f0a3c0824823977ba36fd1382ad868f822568b5))

## [0.2.0](https://github.com/Juargo/moneydiary/compare/0.1.0...v0.2.0) (2025-04-02)


### Features

* **backend:** agregar scripts para la creación y siembra de la base de datos ([6647cd4](https://github.com/Juargo/moneydiary/commit/6647cd4f42a29c879b69c9cdc09a11bf06ea306f))
* **deploy:** actualizar configuración de GitHub Actions y estructura del proyecto para el backend en Python ([a29ab04](https://github.com/Juargo/moneydiary/commit/a29ab043e9542e867fcec26719f28fe378ef7002))
* **deploy:** agregar configuración de Docker y scripts de conexión para la API de MoneyDiary ([52da64a](https://github.com/Juargo/moneydiary/commit/52da64adf3b9aaf544970360e9f2c0f685c8ff1d))
* **deploy:** agregar configuración de servicios en Docker y script de instalación para DigitalOcean ([04f3b46](https://github.com/Juargo/moneydiary/commit/04f3b46a84516d14429efc2378d9efa9e36f2dd7))
* **deploy:** agregar configuración WSGI y .htaccess para backend Python en Hostinger ([dd78833](https://github.com/Juargo/moneydiary/commit/dd78833a3936c77cd9336c531c7a04fff943675c))
* **models:** add Budget, Category, and Pattern models with relationships; update Subcategory model ([83a738c](https://github.com/Juargo/moneydiary/commit/83a738cc482e6c96928e4db1180bac1d66c2b950))
* **models:** add transaction and subcategory models with relationships ([bfc33a8](https://github.com/Juargo/moneydiary/commit/bfc33a807f2249a3b580086ad07cd704b3ca8aa1))


### Bug Fixes

* **backend:** agregar la dependencia cryptography en requirements.txt ([767e0df](https://github.com/Juargo/moneydiary/commit/767e0dfae10c76c29f0d2c20a97cb6655f39b4e9))
* **docker:** corregir el nombre del archivo de requisitos en el Dockerfile ([d819e4c](https://github.com/Juargo/moneydiary/commit/d819e4c7cdc057b6c1b65cc4233ab9defb342ce7))
* **docker:** corregir la ruta de copia del código de la aplicación en el Dockerfile ([1f3bf93](https://github.com/Juargo/moneydiary/commit/1f3bf9313468eeb7c1f0ec439e6a998052e5d492))
* **docker:** corregir la ruta del archivo de requisitos en el Dockerfile ([dae2c2a](https://github.com/Juargo/moneydiary/commit/dae2c2aad5fb01a593ce3dc098944487c2aa858e))
* **docker:** corregir rutas de copia y comando de ejecución en Dockerfile ([056b320](https://github.com/Juargo/moneydiary/commit/056b32054e4ff7c78709573c49072d3a5f457bfd))
* **requirements:** actualizar y reorganizar dependencias en requirements.txt ([5cafe0b](https://github.com/Juargo/moneydiary/commit/5cafe0b42ef2dec0733d18ae120a450ea053c23a))

## 0.1.0 (2025-03-28)


### Features

* Refactor backend configuration and enhance GraphQL user queries ([1135012](https://github.com/Juargo/moneydiary/commit/113501230ed1df0b4387a7eed5ba28d9424329fe))
* Refactor backend configuration and enhance GraphQL user queries ([233981b](https://github.com/Juargo/moneydiary/commit/233981b7096b2286ffead0d6e212ce24eac4b61f))
