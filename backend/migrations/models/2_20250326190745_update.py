from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `user_banks` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `balance` DECIMAL(15,2) NOT NULL DEFAULT 0,
    `description` LONGTEXT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `bank_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_user_banks_user_id_5c99b1` (`user_id`, `bank_id`),
    CONSTRAINT `fk_user_ban_bank_df8832ee` FOREIGN KEY (`bank_id`) REFERENCES `bank` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_user_ban_user_c07fedf5` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='Model for User Bank relationship ';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `user_banks`;"""
