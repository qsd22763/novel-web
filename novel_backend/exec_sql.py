import pymysql

conn = pymysql.connect(
    host='localhost', port=3306,
    user='root', password='200486qq.',
    database='novel_fiction',
    charset='utf8mb4'
)
cur = conn.cursor()

sql = r"""
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE `user` (
    `id`              INT NOT NULL AUTO_INCREMENT,
    `password`        VARCHAR(128) NOT NULL DEFAULT '',
    `last_login`      DATETIME(6) NULL DEFAULT NULL,
    `is_superuser`    TINYINT(1) NOT NULL DEFAULT 0,
    `username`        VARCHAR(150) NOT NULL,
    `first_name`      VARCHAR(150) NOT NULL DEFAULT '',
    `last_name`       VARCHAR(150) NOT NULL DEFAULT '',
    `email`           VARCHAR(254) NOT NULL DEFAULT '',
    `is_staff`        TINYINT(1) NOT NULL DEFAULT 0,
    `is_active`       TINYINT(1) NOT NULL DEFAULT 1,
    `date_joined`     DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `avatar`          VARCHAR(255) NOT NULL DEFAULT '',
    `phone`           VARCHAR(20) NOT NULL DEFAULT '',
    `is_vip`          TINYINT(1) NOT NULL DEFAULT 0,
    `vip_expire_date` DATETIME(6) NULL DEFAULT NULL,
    `is_author`       TINYINT(1) NOT NULL DEFAULT 0,
    `pen_name`        VARCHAR(50) NOT NULL DEFAULT '',
    `bio`             VARCHAR(200) NOT NULL DEFAULT '',
    `created_at`      DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_user_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `novel` (
    `id`            INT NOT NULL AUTO_INCREMENT,
    `title`         VARCHAR(100) NOT NULL,
    `author`        VARCHAR(50) NOT NULL,
    `author_user_id`INT NULL DEFAULT NULL,
    `cover`         VARCHAR(500) NOT NULL DEFAULT '',
    `description`   LONGTEXT NOT NULL,
    `category`      VARCHAR(20) NOT NULL,
    `tags`          VARCHAR(200) NOT NULL DEFAULT '',
    `status`        SMALLINT NOT NULL DEFAULT 0,
    `audit_status`  SMALLINT NOT NULL DEFAULT 2,
    `word_count`    INT NOT NULL DEFAULT 0,
    `view_count`    INT NOT NULL DEFAULT 0,
    `recommend`     INT NOT NULL DEFAULT 0,
    `created_at`    DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at`    DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    KEY `idx_novel_category` (`category`),
    KEY `idx_novel_author_user` (`author_user_id`),
    CONSTRAINT `fk_novel_author_user` FOREIGN KEY (`author_user_id`) REFERENCES `user`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `chapter` (
    `id`            INT NOT NULL AUTO_INCREMENT,
    `novel_id`      INT NOT NULL,
    `title`         VARCHAR(100) NOT NULL,
    `content`       LONGTEXT NOT NULL,
    `chapter_order` INT NOT NULL DEFAULT 0,
    `word_count`    INT NOT NULL DEFAULT 0,
    `publish_status`SMALLINT NOT NULL DEFAULT 1,
    `created_at`    DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at`    DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    KEY `idx_chapter_novel` (`novel_id`),
    KEY `idx_chapter_order` (`novel_id`, `chapter_order`),
    CONSTRAINT `fk_chapter_novel` FOREIGN KEY (`novel_id`) REFERENCES `novel`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `favorite` (
    `id`         INT NOT NULL AUTO_INCREMENT,
    `user_id`    INT NOT NULL,
    `novel_id`   INT NOT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_favorite_user_novel` (`user_id`, `novel_id`),
    CONSTRAINT `fk_favorite_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_favorite_novel` FOREIGN KEY (`novel_id`) REFERENCES `novel`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `reading_progress` (
    `id`          INT NOT NULL AUTO_INCREMENT,
    `user_id`     INT NOT NULL,
    `novel_id`    INT NOT NULL,
    `chapter_id`  INT NOT NULL,
    `position`    INT NOT NULL DEFAULT 0,
    `updated_at`  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_progress_user_novel` (`user_id`, `novel_id`),
    CONSTRAINT `fk_rp_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_rp_novel` FOREIGN KEY (`novel_id`) REFERENCES `novel`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_rp_chapter` FOREIGN KEY (`chapter_id`) REFERENCES `chapter`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `bookmark` (
    `id`          INT NOT NULL AUTO_INCREMENT,
    `user_id`     INT NOT NULL,
    `novel_id`    INT NOT NULL,
    `chapter_id`  INT NOT NULL,
    `position`    INT NOT NULL DEFAULT 0,
    `note`        VARCHAR(200) NOT NULL DEFAULT '',
    `created_at`  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    KEY `idx_bm_user` (`user_id`),
    KEY `idx_bm_novel` (`novel_id`),
    CONSTRAINT `fk_bm_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_bm_novel` FOREIGN KEY (`novel_id`) REFERENCES `novel`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_bm_chapter` FOREIGN KEY (`chapter_id`) REFERENCES `chapter`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `comment` (
    `id`          INT NOT NULL AUTO_INCREMENT,
    `novel_id`    INT NOT NULL,
    `user_id`     INT NOT NULL,
    `content`     VARCHAR(500) NOT NULL,
    `rating`      TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `created_at`  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    KEY `idx_comment_novel` (`novel_id`),
    KEY `idx_comment_user` (`user_id`),
    CONSTRAINT `fk_comment_novel` FOREIGN KEY (`novel_id`) REFERENCES `novel`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_comment_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
"""

for stmt in sql.split(';'):
    s = stmt.strip()
    if s and not s.startswith('--'):
        try:
            cur.execute(s)
            conn.commit()
        except Exception as e:
            err = str(e).split('\n')[0]
            print(f"  ERR: {err}")

cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='novel_fiction' AND table_type='BASE TABLE'")
total = cur.fetchone()[0]
print(f"\nTotal tables: {total}")
cur.execute("SHOW TABLES")
for row in cur.fetchall():
    t = row[0]
    cur.execute(f"SELECT COUNT(*) FROM `{t}`")
    cnt = cur.fetchone()[0]
    print(f"  {t}: {cnt} rows")

cur.close()
conn.close()
