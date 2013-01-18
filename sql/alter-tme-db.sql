ALTER TABLE topics_phrase MODIFY COLUMN phrase varchar(123) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE topics_token MODIFY COLUMN token varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE topics_document MODIFY COLUMN title varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE topics_document MODIFY COLUMN content LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE corpus_project MODIFY COLUMN title varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE corpus_project MODIFY COLUMN content LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE corpus_project MODIFY COLUMN source LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
