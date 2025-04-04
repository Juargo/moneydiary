from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `bank` DROP INDEX `name`;
        ALTER TABLE `bank` DROP COLUMN `description`;
        ALTER TABLE `bank` MODIFY COLUMN `name` VARCHAR(100) NOT NULL;
        CREATE TABLE IF NOT EXISTS `budget` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `description` VARCHAR(255),
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_budget_name_9060e1` (`name`, `user_id`),
    CONSTRAINT `fk_budget_user_0269c8c1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='Model for Budget ';
        CREATE TABLE IF NOT EXISTS `category` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `description` VARCHAR(255),
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `budget_id` INT NOT NULL,
    UNIQUE KEY `uid_category_name_d16d4f` (`name`, `budget_id`),
    CONSTRAINT `fk_category_budget_f985db0f` FOREIGN KEY (`budget_id`) REFERENCES `budget` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='Model for Category ';
        CREATE TABLE IF NOT EXISTS `pattern` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `exp_name` VARCHAR(255) NOT NULL COMMENT 'Pattern expression for identification',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `subcategory_id` INT NOT NULL,
    UNIQUE KEY `uid_pattern_exp_nam_8294fa` (`exp_name`, `subcategory_id`),
    CONSTRAINT `fk_pattern_subcateg_564e0b11` FOREIGN KEY (`subcategory_id`) REFERENCES `subcategory` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='Model for identification patterns ';
        CREATE TABLE IF NOT EXISTS `pattern_ignore` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `exp_name` VARCHAR(255) NOT NULL,
    `description` LONGTEXT NOT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_pattern__user_1e7e531f` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='Model for Pattern Ignore ';
        CREATE TABLE IF NOT EXISTS `subcategory` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `description` VARCHAR(255),
    `amount` INT NOT NULL COMMENT 'Amount in CLP without decimals',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `category_id` INT NOT NULL,
    UNIQUE KEY `uid_subcategory_name_211ae3` (`name`, `category_id`),
    CONSTRAINT `fk_subcateg_category_09976a38` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='Model for Subcategory ';
        CREATE TABLE IF NOT EXISTS `transaction` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `transaction_date` DATETIME(6) NOT NULL,
    `description` VARCHAR(255) NOT NULL,
    `amount` DECIMAL(15,0) NOT NULL,
    `type` VARCHAR(7) NOT NULL COMMENT 'INGRESO: Ingreso\nGASTO: Gasto',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `subcategory_id` INT NOT NULL,
    `user_bank_id` INT NOT NULL,
    CONSTRAINT `fk_transact_subcateg_db14857c` FOREIGN KEY (`subcategory_id`) REFERENCES `subcategory` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_transact_user_ban_c790ae4c` FOREIGN KEY (`user_bank_id`) REFERENCES `user_bank` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='Model for Transaction ';
        ALTER TABLE `user_banks` RENAME TO `user_bank`;
        ALTER TABLE `user_bank` MODIFY COLUMN `balance` DECIMAL(15,0) NOT NULL DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `bank` ADD `description` VARCHAR(255);
        ALTER TABLE `bank` MODIFY COLUMN `name` VARCHAR(50) NOT NULL;
        ALTER TABLE `user_bank` RENAME TO `user_banks`;
        ALTER TABLE `user_bank` MODIFY COLUMN `balance` DECIMAL(15,2) NOT NULL DEFAULT 0;
        DROP TABLE IF EXISTS `pattern_ignore`;
        DROP TABLE IF EXISTS `transaction`;
        DROP TABLE IF EXISTS `subcategory`;
        DROP TABLE IF EXISTS `category`;
        DROP TABLE IF EXISTS `budget`;
        DROP TABLE IF EXISTS `pattern`;
        ALTER TABLE `bank` ADD UNIQUE INDEX `name` (`name`);"""
