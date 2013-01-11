ALTER TABLE topics_document MODIFY COLUMN title varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE topics_document MODIFY COLUMN content LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
